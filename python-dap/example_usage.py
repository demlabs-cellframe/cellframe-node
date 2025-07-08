#!/usr/bin/env python3
"""
🧬 DAP SDK Usage Example

Demonstrates the new streamlined architecture:
- Python handles all memory management automatically
- DAP SDK provides only type integration and C function wrappers
- No manual memory allocation/deallocation needed
"""

import dap
from dap import (
    Dap, DapLogging, DapLogLevel, DapTime, DapType,
    format_bytes, now_dap, to_rfc822, format_duration
)


def main():
    """Main example function"""
    print("🧬 DAP SDK Example - Streamlined Architecture")
    print("=" * 50)
    
    # Initialize DAP systems using context manager
    with Dap() as dap:
        print("✅ DAP Core initialized successfully")
        
        # Access logging system
        logging = dap.logging
        print(f"📊 Current log level: {logging.get_level()}")
        
        # Access type helpers
        type_helper = dap.type
        print(f"💾 Format 1GB: {type_helper.format_bytes(1024**3)}")
        
        # Access time helpers
        time_helper = dap.time
        current_time = time_helper.now_dap()
        print(f"⏰ Current DAP time: {current_time}")
        print(f"📅 RFC822 format: {time_helper.to_rfc822(current_time)}")
        
        # Use convenience functions
        print("\n🛠️  Convenience Functions:")
        print(f"📦 Format bytes: {format_bytes(1024*1024)}")
        print(f"🕐 Current time: {now_dap()}")
        print(f"📆 RFC822 time: {to_rfc822(current_time)}")
        print(f"⏳ Duration: {format_duration(3661)}")
        
        # Show status
        print("\n📊 DAP Status:")
        status = dap.status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print("\n🎯 Key Benefits:")
        print("  ✅ No manual memory management")
        print("  ✅ Python handles all allocations")
        print("  ✅ Type integration with DAP C functions")
        print("  ✅ Automatic resource cleanup")
        print("  ✅ Thread-safe operations")
        print("  ✅ Simplified API")
        
    print("\n✨ DAP Core automatically deinitialized")


if __name__ == "__main__":
    main() 