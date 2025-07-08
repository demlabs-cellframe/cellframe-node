#!/usr/bin/env python3
"""
Minimal Python plugin для тестирования cellframe-node Python support
"""

def init():
    """Plugin initialization function"""
    print("✅ SUCCESS: Python plugin loaded successfully!")
    print("✅ Python version and CellFrame integration working!")
    return 0

def deinit():
    """Plugin deinitialization function"""
    print("✅ Python plugin deinitialized successfully!")
    return 0

if __name__ == "__main__":
    print("Test plugin loaded")
    init()
