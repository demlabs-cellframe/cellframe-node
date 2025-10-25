"""
Base interface for snapshot implementations.

Defines the common interface that all snapshot modes must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseSnapshot(ABC):
    """
    Abstract base class for snapshot implementations.
    
    All snapshot modes (recreate, filesystem, squashfs) inherit from this
    and implement the required methods.
    """
    
    def __init__(self, base_path: Path, config: Dict[str, Any]):
        """
        Initialize snapshot handler.
        
        Args:
            base_path: Base path to stage-env directory
            config: Configuration dictionary
        """
        self.base_path = base_path
        self.config = config
        
        # Paths from config
        cache_dir = config.get('cache_dir', '../testing/cache')
        self.cache_path = (base_path / cache_dir).resolve()
        
        # Snapshot storage directory
        snapshots_dir = config.get('snapshots_dir', '../testing/snapshots')
        self.snapshots_path = (base_path / snapshots_dir).resolve()
        self.snapshots_path.mkdir(parents=True, exist_ok=True)
        
        logger.debug("snapshot_handler_initialized",
                    type=self.__class__.__name__,
                    cache_path=str(self.cache_path),
                    snapshots_path=str(self.snapshots_path))
    
    @abstractmethod
    async def create(self, name: str) -> bool:
        """
        Create a snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def restore(self, name: str) -> bool:
        """
        Restore from snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def delete(self, name: str) -> bool:
        """
        Delete a snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def list(self) -> list[str]:
        """
        List available snapshots.
        
        Returns:
            List of snapshot names
        """
        pass
    
    def get_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get snapshot information.
        
        Args:
            name: Snapshot name
            
        Returns:
            Dictionary with snapshot metadata
        """
        # Base implementation - can be overridden by subclasses
        snapshot_path = self.snapshots_path / name
        if not snapshot_path.exists():
            return None
        
        return {
            "name": name,
            "path": str(snapshot_path),
            "exists": snapshot_path.exists(),
            "type": self.__class__.__name__,
        }
    
    def get_data_dirs(self) -> list[Path]:
        """
        Get list of data directories to snapshot.
        
        Returns:
            List of Path objects for directories to include in snapshot
        """
        data_path = self.cache_path / "data"
        
        # Get all node directories
        if not data_path.exists():
            return []
        
        return [d for d in data_path.iterdir() if d.is_dir()]

