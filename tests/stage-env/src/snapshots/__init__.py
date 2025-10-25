"""
Snapshot system for fast environment restoration.

This module provides three snapshot modes for test isolation:
1. recreate - Full cleanup and rebuild (baseline, ~40s)
2. filesystem - Directory copy/restore (~3s)
3. squashfs - Read-only image with overlay (~2s)
"""

from .manager import SnapshotManager, SnapshotMode
from .base import BaseSnapshot
from .recreate import RecreateSnapshot
from .filesystem import FilesystemSnapshot
from .squashfs import SquashfsSnapshot

__all__ = [
    'SnapshotManager',
    'SnapshotMode',
    'BaseSnapshot',
    'RecreateSnapshot',
    'FilesystemSnapshot',
    'SquashfsSnapshot',
]

