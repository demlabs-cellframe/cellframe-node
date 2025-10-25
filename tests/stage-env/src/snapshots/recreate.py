"""
Recreate snapshot mode - full environment cleanup and rebuild.

This is the baseline mode that provides maximum isolation by completely
recreating the environment from scratch. Slowest but most reliable.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any

from ..utils.logger import get_logger
from .base import BaseSnapshot

logger = get_logger(__name__)


class RecreateSnapshot(BaseSnapshot):
    """
    Recreate mode - no actual snapshots, just marks for full recreation.
    
    This mode doesn't store any data - it simply marks that a full cleanup
    and rebuild is needed. Used as baseline for measuring other modes.
    """
    
    def __init__(self, base_path: Path, config: Dict[str, Any]):
        """
        Initialize recreate snapshot handler.
        
        Args:
            base_path: Base path to stage-env directory
            config: Configuration dictionary
        """
        super().__init__(base_path, config)
        
        # Recreate mode doesn't need snapshot storage
        # It just triggers full cleanup in NetworkManager
        logger.info("recreate_mode_initialized",
                   note="No snapshots stored, uses full cleanup/rebuild")
    
    async def create(self, name: str) -> bool:
        """
        Create a snapshot marker (no actual data stored).
        
        Args:
            name: Snapshot name (used for logging only)
            
        Returns:
            Always True (marker created)
        """
        logger.debug("recreate_create_marker", name=name)
        
        # Create marker file
        marker_path = self.snapshots_path / f"{name}.marker"
        marker_path.touch()
        
        logger.info("recreate_marker_created",
                   name=name,
                   note="Full cleanup will be performed on restore")
        return True
    
    async def restore(self, name: str) -> bool:
        """
        Restore by triggering full cleanup (no data restored).
        
        Args:
            name: Snapshot name (used for logging only)
            
        Returns:
            Always True (cleanup will be done by NetworkManager)
        """
        logger.info("recreate_restore_triggered",
                   name=name,
                   note="Full cleanup will be performed by NetworkManager")
        
        # Check marker exists
        marker_path = self.snapshots_path / f"{name}.marker"
        if not marker_path.exists():
            logger.warning("recreate_marker_not_found",
                          name=name,
                          action="will_create_new")
            marker_path.touch()
        
        # No actual restoration - NetworkManager will call clean_test_data()
        return True
    
    async def delete(self, name: str) -> bool:
        """
        Delete snapshot marker.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if deleted or didn't exist
        """
        marker_path = self.snapshots_path / f"{name}.marker"
        
        if marker_path.exists():
            marker_path.unlink()
            logger.info("recreate_marker_deleted", name=name)
        else:
            logger.debug("recreate_marker_not_found", name=name)
        
        return True
    
    async def list(self) -> list[str]:
        """
        List available snapshot markers.
        
        Returns:
            List of marker names (without .marker extension)
        """
        if not self.snapshots_path.exists():
            return []
        
        markers = []
        for marker in self.snapshots_path.glob("*.marker"):
            markers.append(marker.stem)
        
        return sorted(markers)
    
    def get_info(self, name: str) -> Dict[str, Any]:
        """
        Get marker information.
        
        Args:
            name: Marker name
            
        Returns:
            Dictionary with marker metadata
        """
        marker_path = self.snapshots_path / f"{name}.marker"
        
        info = {
            "name": name,
            "type": "recreate",
            "path": str(marker_path),
            "exists": marker_path.exists(),
            "size_bytes": 0,
            "note": "Recreate mode uses full cleanup/rebuild - no data stored",
        }
        
        if marker_path.exists():
            info["created"] = marker_path.stat().st_mtime
        
        return info

