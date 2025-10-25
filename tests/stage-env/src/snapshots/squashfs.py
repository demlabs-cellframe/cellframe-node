"""
Squashfs snapshot mode - read-only image with overlay filesystem.

This mode creates compressed read-only images using squashfs and uses
overlay filesystem for writes. Provides maximum speed with minimal overhead.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import subprocess

from ..utils.logger import get_logger
from .base import BaseSnapshot

logger = get_logger(__name__)


class SquashfsSnapshot(BaseSnapshot):
    """
    Squashfs mode - read-only image with overlay.
    
    Creates compressed read-only squashfs images of clean state.
    Uses overlay filesystem to provide writable layer on top of read-only base.
    
    Estimated performance: ~2s for snapshot creation, ~1s for restore.
    Compression optional (can be disabled for even faster creation).
    """
    
    def __init__(self, base_path: Path, config: Dict[str, Any]):
        """
        Initialize squashfs snapshot handler.
        
        Args:
            base_path: Base path to stage-env directory
            config: Configuration dictionary
            
        Raises:
            RuntimeError: If squashfs tools are not available (fail-fast)
        """
        super().__init__(base_path, config)
        
        # Check if required tools are available
        self.has_mksquashfs = self._check_tool("mksquashfs")
        self.has_unsquashfs = self._check_tool("unsquashfs")
        self.has_overlayfs = self._check_overlayfs()
        
        # Fail-fast: squashfs mode requires tools to be installed
        if not self.has_mksquashfs or not self.has_unsquashfs:
            missing = []
            if not self.has_mksquashfs:
                missing.append("mksquashfs")
            if not self.has_unsquashfs:
                missing.append("unsquashfs")
            
            error_msg = (
                f"Squashfs mode selected but required tools are missing: {', '.join(missing)}. "
                f"Install squashfs-tools package: sudo apt install squashfs-tools"
            )
            logger.error("squashfs_tools_missing",
                        has_mksquashfs=self.has_mksquashfs,
                        has_unsquashfs=self.has_unsquashfs,
                        missing=missing)
            raise RuntimeError(error_msg)
        
        # Compression mode from config
        compression = config.get('squashfs_compression', 'none')
        self.compression = compression if compression != 'none' else None
        
        # Overlay directories
        self.overlay_base = self.snapshots_path / ".overlays"
        self.overlay_base.mkdir(parents=True, exist_ok=True)
        
        logger.info("squashfs_mode_initialized",
                   tools_available=True,
                   overlayfs_available=self.has_overlayfs,
                   compression=self.compression or "none")
    
    def _check_tool(self, tool: str) -> bool:
        """Check if a command-line tool is available."""
        try:
            # Try to run the tool - squashfs tools use -version (not --version)
            result = subprocess.run(
                [tool, "-version"],
                capture_output=True,
                timeout=5
            )
            # squashfs tools print version to stderr and may return 0 or 1
            # Check if output contains version info
            output = result.stdout.decode() + result.stderr.decode()
            return "version" in output.lower() and tool in output.lower()
        except FileNotFoundError:
            return False
        except subprocess.TimeoutExpired:
            return False
    
    def _check_overlayfs(self) -> bool:
        """Check if overlay filesystem is available."""
        # Check if overlay is supported by the kernel
        # Method 1: Check /proc/filesystems (most reliable)
        try:
            with open("/proc/filesystems", "r") as f:
                filesystems = f.read()
                if "overlay" in filesystems:
                    return True
        except (FileNotFoundError, PermissionError):
            pass
        
        # Method 2: Try modprobe (if available)
        try:
            result = subprocess.run(
                ["modprobe", "-n", "overlay"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Method 3: Check if overlay module is loaded
        try:
            result = subprocess.run(
                ["lsmod"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0 and b"overlay" in result.stdout:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return False
    
    async def create(self, name: str) -> bool:
        """
        Create squashfs snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if snapshot created successfully
        """
        if not self.has_mksquashfs:
            logger.error("squashfs_mksquashfs_not_available")
            return False
        
        logger.info("squashfs_create_start",
                   name=name,
                   compression=self.compression or "none")
        
        snapshot_file = self.snapshots_path / f"{name}.sqfs"
        
        # Remove existing snapshot if present
        if snapshot_file.exists():
            logger.debug("squashfs_overwriting_existing", name=name)
            snapshot_file.unlink()
        
        # Get source data directory
        data_path = self.cache_path / "data"
        if not data_path.exists():
            logger.warning("squashfs_no_data_to_snapshot")
            return False
        
        try:
            # Build mksquashfs command
            cmd = ["mksquashfs", str(data_path), str(snapshot_file)]
            
            # Add compression
            if self.compression:
                cmd.extend(["-comp", self.compression])
            else:
                cmd.extend(["-noI", "-noD", "-noF", "-noX"])  # Disable all compression
            
            # Add other options for speed
            cmd.extend([
                "-no-progress",
                "-processors", "4",  # Use 4 processors for parallel compression
            ])
            
            # Run mksquashfs
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.error("squashfs_create_failed",
                            name=name,
                            error=stderr.decode())
                return False
            
            # Create metadata
            metadata = {
                "name": name,
                "type": "squashfs",
                "compression": self.compression or "none",
                "size_bytes": snapshot_file.stat().st_size,
            }
            
            metadata_file = self.snapshots_path / f"{name}.metadata"
            metadata_file.write_text(str(metadata))
            
            logger.info("squashfs_create_complete",
                       name=name,
                       size=snapshot_file.stat().st_size,
                       compression=self.compression or "none")
            return True
            
        except Exception as e:
            logger.error("squashfs_create_error", name=name, error=str(e))
            if snapshot_file.exists():
                snapshot_file.unlink()
            return False
    
    async def restore(self, name: str) -> bool:
        """
        Restore from squashfs snapshot using overlay.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if restore successful
        """
        if not self.has_unsquashfs:
            logger.error("squashfs_unsquashfs_not_available")
            return False
        
        logger.info("squashfs_restore_start", name=name)
        
        snapshot_file = self.snapshots_path / f"{name}.sqfs"
        
        if not snapshot_file.exists():
            logger.error("squashfs_snapshot_not_found", name=name)
            return False
        
        data_path = self.cache_path / "data"
        
        try:
            # Clean existing data (use sudo rm -rf for bind-mounted volumes)
            if data_path.exists():
                logger.debug("squashfs_cleaning_existing_data")
                # Use docker exec to clean from inside container if available
                # Otherwise use sudo rm -rf as files are owned by root
                try:
                    proc = await asyncio.create_subprocess_exec(
                        "sudo", "rm", "-rf", str(data_path),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await proc.communicate()
                except Exception:
                    # Fallback to shutil with ignore_errors
                    await asyncio.to_thread(shutil.rmtree, data_path, ignore_errors=True)
            
            data_path.mkdir(parents=True, exist_ok=True)
            
            # Extract squashfs - need sudo as files are owned by root
            # Also add -no-xattrs to avoid permission issues
            proc = await asyncio.create_subprocess_exec(
                "sudo", "unsquashfs",
                "-f",  # force overwrite
                "-no-xattrs",  # don't restore extended attributes
                "-d", str(data_path),  # destination
                str(snapshot_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.error("squashfs_restore_failed",
                            name=name,
                            error=stderr.decode())
                return False
            
            # Fix ownership to current user (files were extracted as root)
            import os
            uid = os.getuid()
            gid = os.getgid()
            
            proc = await asyncio.create_subprocess_exec(
                "sudo", "chown", "-R", f"{uid}:{gid}", str(data_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            logger.info("squashfs_restore_complete", name=name)
            return True
            
        except Exception as e:
            logger.error("squashfs_restore_error", name=name, error=str(e))
            return False
    
    async def delete(self, name: str) -> bool:
        """
        Delete a squashfs snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if deleted successfully
        """
        snapshot_file = self.snapshots_path / f"{name}.sqfs"
        metadata_file = self.snapshots_path / f"{name}.metadata"
        
        deleted = False
        
        if snapshot_file.exists():
            snapshot_file.unlink()
            deleted = True
        
        if metadata_file.exists():
            metadata_file.unlink()
        
        if deleted:
            logger.info("squashfs_snapshot_deleted", name=name)
        else:
            logger.debug("squashfs_snapshot_not_found", name=name)
        
        return True
    
    async def list(self) -> List[str]:
        """
        List available squashfs snapshots.
        
        Returns:
            List of snapshot names
        """
        if not self.snapshots_path.exists():
            return []
        
        snapshots = []
        for snapshot_file in self.snapshots_path.glob("*.sqfs"):
            snapshots.append(snapshot_file.stem)
        
        return sorted(snapshots)
    
    def get_info(self, name: str) -> Dict[str, Any]:
        """Get squashfs snapshot information."""
        snapshot_file = self.snapshots_path / f"{name}.sqfs"
        metadata_file = self.snapshots_path / f"{name}.metadata"
        
        info = {
            "name": name,
            "type": "squashfs",
            "path": str(snapshot_file),
            "exists": snapshot_file.exists(),
        }
        
        if snapshot_file.exists():
            info["size_bytes"] = snapshot_file.stat().st_size
            info["created"] = snapshot_file.stat().st_mtime
        
        # Read metadata if available
        if metadata_file.exists():
            try:
                metadata = eval(metadata_file.read_text())
                info.update(metadata)
            except Exception:
                pass
        
        return info

