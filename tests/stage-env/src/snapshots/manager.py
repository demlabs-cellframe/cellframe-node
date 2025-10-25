"""
Snapshot Manager - orchestrates different snapshot modes.

Coordinates snapshot creation, restoration, and cleanup across all modes.
"""

from __future__ import annotations

import asyncio
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..utils.logger import get_logger
from .base import BaseSnapshot
from .recreate import RecreateSnapshot
from .filesystem import FilesystemSnapshot
from .squashfs import SquashfsSnapshot

logger = get_logger(__name__)


class SnapshotMode(Enum):
    """Available snapshot isolation modes."""
    DISABLED = "disabled"
    RECREATE = "recreate"
    FILESYSTEM = "filesystem"
    SQUASHFS = "squashfs"


class SnapshotManager:
    """
    Manager for test environment snapshots.
    
    Provides fast environment restoration via different snapshot strategies:
    - recreate: Full cleanup and rebuild (~40s, maximum isolation)
    - filesystem: Directory copy using rsync (~3s, balanced)
    - squashfs: Read-only image with overlay (~2s, maximum speed)
    """
    
    def __init__(
        self,
        base_path: Path,
        mode: SnapshotMode = SnapshotMode.FILESYSTEM,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize snapshot manager.
        
        Args:
            base_path: Base path to stage-env directory
            mode: Snapshot mode to use
            config: Optional configuration dictionary
        """
        self.base_path = base_path
        self.mode = mode
        self.config = config or {}
        
        # Initialize snapshot handler based on mode
        self.snapshot: Optional[BaseSnapshot] = None
        if mode != SnapshotMode.DISABLED:
            self._initialize_handler()
        
        logger.info("snapshot_manager_initialized",
                   mode=mode.value,
                   base_path=str(base_path),
                   config=self.config)
    
    def _initialize_handler(self):
        """Initialize appropriate snapshot handler based on mode."""
        if self.mode == SnapshotMode.RECREATE:
            self.snapshot = RecreateSnapshot(self.base_path, self.config)
        elif self.mode == SnapshotMode.FILESYSTEM:
            self.snapshot = FilesystemSnapshot(self.base_path, self.config)
        elif self.mode == SnapshotMode.SQUASHFS:
            self.snapshot = SquashfsSnapshot(self.base_path, self.config)
        else:
            raise ValueError(f"Unknown snapshot mode: {self.mode}")
    
    async def create_snapshot(self, name: str = "clean_state") -> bool:
        """
        Create a snapshot of current environment state.
        
        Args:
            name: Name for the snapshot
            
        Returns:
            True if snapshot created successfully
        """
        if self.mode == SnapshotMode.DISABLED:
            logger.debug("snapshot_disabled_create_skipped")
            return True
        
        logger.info("creating_snapshot", name=name, mode=self.mode.value)
        
        try:
            result = await self.snapshot.create(name)
            if result:
                logger.info("snapshot_created_successfully", name=name)
            else:
                logger.error("snapshot_creation_failed", name=name)
            return result
        except Exception as e:
            logger.error("snapshot_creation_error", name=name, error=str(e))
            return False
    
    async def restore_snapshot(self, name: str = "clean_state") -> bool:
        """
        Restore environment to snapshot state.
        
        Args:
            name: Name of snapshot to restore
            
        Returns:
            True if restore successful
        """
        if self.mode == SnapshotMode.DISABLED:
            logger.debug("snapshot_disabled_restore_skipped")
            return True
        
        logger.info("restoring_snapshot", name=name, mode=self.mode.value)
        
        try:
            result = await self.snapshot.restore(name)
            if result:
                logger.info("snapshot_restored_successfully", name=name)
            else:
                logger.error("snapshot_restore_failed", name=name)
            return result
        except Exception as e:
            logger.error("snapshot_restore_error", name=name, error=str(e))
            return False
    
    async def delete_snapshot(self, name: str) -> bool:
        """
        Delete a snapshot.
        
        Args:
            name: Name of snapshot to delete
            
        Returns:
            True if deletion successful
        """
        if self.mode == SnapshotMode.DISABLED:
            logger.debug("snapshot_disabled_delete_skipped")
            return True
        
        logger.info("deleting_snapshot", name=name)
        
        try:
            result = await self.snapshot.delete(name)
            if result:
                logger.info("snapshot_deleted_successfully", name=name)
            else:
                logger.error("snapshot_deletion_failed", name=name)
            return result
        except Exception as e:
            logger.error("snapshot_deletion_error", name=name, error=str(e))
            return False
    
    async def list_snapshots(self) -> List[str]:
        """
        List available snapshots.
        
        Returns:
            List of snapshot names
        """
        if self.mode == SnapshotMode.DISABLED:
            return []
        
        try:
            return await self.snapshot.list()
        except Exception as e:
            logger.error("snapshot_list_error", error=str(e))
            return []
    
    async def cleanup_old_snapshots(self, keep_count: int = 5) -> int:
        """
        Clean up old snapshots, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent snapshots to keep
            
        Returns:
            Number of snapshots deleted
        """
        if self.mode == SnapshotMode.DISABLED:
            return 0
        
        try:
            snapshots = await self.list_snapshots()
            if len(snapshots) <= keep_count:
                return 0
            
            # Sort by name (assuming timestamp-based names)
            snapshots.sort()
            to_delete = snapshots[:-keep_count]
            
            deleted = 0
            for name in to_delete:
                if await self.delete_snapshot(name):
                    deleted += 1
            
            logger.info("old_snapshots_cleaned", deleted=deleted, kept=keep_count)
            return deleted
        except Exception as e:
            logger.error("snapshot_cleanup_error", error=str(e))
            return 0
    
    def get_snapshot_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            Dictionary with snapshot info, or None if not found
        """
        if self.mode == SnapshotMode.DISABLED:
            return None
        
        try:
            return self.snapshot.get_info(name)
        except Exception as e:
            logger.error("snapshot_info_error", name=name, error=str(e))
            return None

