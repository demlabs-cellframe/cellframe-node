"""
Filesystem snapshot mode - directory copy/restore using rsync.

This mode creates snapshots by copying the entire data directory tree.
Provides good balance between speed and simplicity.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any, List
import subprocess

from ..utils.logger import get_logger
from .base import BaseSnapshot

logger = get_logger(__name__)


class FilesystemSnapshot(BaseSnapshot):
    """
    Filesystem mode - full directory copy using rsync.
    
    Creates snapshots by copying all node data directories using rsync
    for efficient incremental copying. Restoration is done by rsync'ing back.
    
    Estimated performance: ~3s for snapshot/restore on typical test data.
    """
    
    def __init__(self, base_path: Path, config: Dict[str, Any]):
        """
        Initialize filesystem snapshot handler.
        
        Args:
            base_path: Base path to stage-env directory
            config: Configuration dictionary
            
        Raises:
            RuntimeError: If rsync is not available (fail-fast)
        """
        super().__init__(base_path, config)
        
        # Check if rsync is available (required, not optional)
        if not self._check_rsync():
            error_msg = (
                "Filesystem mode selected but rsync is not installed. "
                "Install rsync: sudo apt install rsync"
            )
            logger.error("rsync_not_found", 
                        note="rsync is required for filesystem snapshot mode")
            raise RuntimeError(error_msg)
        
        logger.info("filesystem_mode_initialized",
                   rsync_available=True,
                   snapshots_dir=str(self.snapshots_path))
    
    def _check_rsync(self) -> bool:
        """Check if rsync is available on the system."""
        try:
            result = subprocess.run(
                ["rsync", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except subprocess.TimeoutExpired:
            return False
    
    async def create(self, name: str) -> bool:
        """
        Create snapshot by copying data directory.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if snapshot created successfully
        """
        logger.info("filesystem_create_start", name=name)
        
        snapshot_dir = self.snapshots_path / name
        
        # Remove existing snapshot if present
        if snapshot_dir.exists():
            logger.warning("filesystem_overwriting_existing", name=name)
            await self.delete(name)
        
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Get source data directory
        data_dirs = self.get_data_dirs()
        if not data_dirs:
            logger.warning("filesystem_no_data_to_snapshot")
            return False
        
        # Copy each node directory
        try:
            for node_dir in data_dirs:
                target_dir = snapshot_dir / node_dir.name
                
                # Use rsync for efficient copying
                await self._rsync_copy(node_dir, target_dir)
            
            # Create metadata file
            metadata = self._create_metadata(name, data_dirs)
            metadata_file = snapshot_dir / ".snapshot_metadata"
            metadata_file.write_text(str(metadata))
            
            logger.info("filesystem_create_complete",
                       name=name,
                       nodes=len(data_dirs),
                       size=self._get_dir_size(snapshot_dir))
            return True
            
        except Exception as e:
            logger.error("filesystem_create_failed", name=name, error=str(e))
            # Cleanup partial snapshot
            if snapshot_dir.exists():
                await asyncio.to_thread(shutil.rmtree, snapshot_dir, ignore_errors=True)
            return False
    
    async def restore(self, name: str) -> bool:
        """
        Restore data from snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if restore successful
        """
        logger.info("filesystem_restore_start", name=name)
        
        snapshot_dir = self.snapshots_path / name
        
        if not snapshot_dir.exists():
            logger.error("filesystem_snapshot_not_found", name=name)
            return False
        
        # Get target data directory
        data_path = self.cache_path / "data"
        
        try:
            # Clean existing data first
            if data_path.exists():
                logger.debug("filesystem_cleaning_existing_data")
                await asyncio.to_thread(shutil.rmtree, data_path, ignore_errors=True)
            
            data_path.mkdir(parents=True, exist_ok=True)
            
            # Restore each node directory
            node_dirs = [d for d in snapshot_dir.iterdir() 
                        if d.is_dir() and not d.name.startswith('.')]
            
            for node_dir in node_dirs:
                target_dir = data_path / node_dir.name
                
                # Use rsync for efficient restoration
                await self._rsync_copy(node_dir, target_dir)
            
            logger.info("filesystem_restore_complete",
                       name=name,
                       nodes=len(node_dirs))
            return True
            
        except Exception as e:
            logger.error("filesystem_restore_failed", name=name, error=str(e))
            return False
    
    async def delete(self, name: str) -> bool:
        """
        Delete a filesystem snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if deleted successfully
        """
        snapshot_dir = self.snapshots_path / name
        
        if not snapshot_dir.exists():
            logger.debug("filesystem_snapshot_not_found", name=name)
            return True
        
        try:
            await asyncio.to_thread(shutil.rmtree, snapshot_dir)
            logger.info("filesystem_snapshot_deleted", name=name)
            return True
        except Exception as e:
            logger.error("filesystem_delete_failed", name=name, error=str(e))
            return False
    
    async def list(self) -> List[str]:
        """
        List available snapshots.
        
        Returns:
            List of snapshot names
        """
        if not self.snapshots_path.exists():
            return []
        
        snapshots = []
        for snapshot_dir in self.snapshots_path.iterdir():
            if snapshot_dir.is_dir() and not snapshot_dir.name.startswith('.'):
                snapshots.append(snapshot_dir.name)
        
        return sorted(snapshots)
    
    async def _rsync_copy(self, source: Path, target: Path):
        """
        Copy directory using rsync.
        
        Args:
            source: Source directory
            target: Target directory
        """
        # Ensure target parent exists
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Run rsync
        proc = await asyncio.create_subprocess_exec(
            "rsync",
            "-a",  # archive mode
            "--delete",  # delete files in target not in source
            str(source) + "/",  # trailing slash important!
            str(target) + "/",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise RuntimeError(f"rsync failed: {stderr.decode()}")
    
    def _create_metadata(self, name: str, data_dirs: list[Path]) -> Dict[str, Any]:
        """Create metadata for snapshot."""
        return {
            "name": name,
            "type": "filesystem",
            "nodes": [d.name for d in data_dirs],
            "created": asyncio.get_event_loop().time(),
        }
    
    def _get_dir_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception:
            pass
        return total
    
    def get_info(self, name: str) -> Dict[str, Any]:
        """Get snapshot information."""
        snapshot_dir = self.snapshots_path / name
        
        info = {
            "name": name,
            "type": "filesystem",
            "path": str(snapshot_dir),
            "exists": snapshot_dir.exists(),
        }
        
        if snapshot_dir.exists():
            info["size_bytes"] = self._get_dir_size(snapshot_dir)
            info["created"] = snapshot_dir.stat().st_mtime
            
            # Read metadata if available
            metadata_file = snapshot_dir / ".snapshot_metadata"
            if metadata_file.exists():
                try:
                    metadata = eval(metadata_file.read_text())
                    info.update(metadata)
                except Exception:
                    pass
        
        return info

