#!/usr/bin/env python3
"""
E Stop Monitor Example Script
Demonstrates how to use the E Stop monitoring functionality
"""

import time
import sys
from datetime import datetime

# Try to import the enhanced modules
try:
    from plc_communication import EnhancedPLCValidator
    from estop_monitor import EStopStateChange
    ENHANCED_AVAILABLE = True
except ImportError:
    print("Enhanced modules not available. Please ensure estop_monitor.py and plc_communication.py are in the same directory.")
    ENHANCED_AVAILABLE = False

def estop_change_callback(change: EStopStateChange):
    """Callback function for E Stop state changes"""
    timestamp = change.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    channel_info = f" [Channel {change.channel}]" if change.channel else ""
    duration_info = f" (Duration: {change.duration_seconds:.1f}s)" if change.duration_seconds else ""
    
    print(f"[{timestamp}] E Stop State Change:")
    print(f"  E Stop: {change.estop_name}")
    print(f"  Change: {change.old_state.value} -> {change.new_state.value}")
    if change.channel:
        print(f"  Channel: {change.channel}")
    if change.duration_seconds:
        print(f"  Previous State Duration: {change.duration_seconds:.1f}s")
    print()

def main():
    """Main example function"""
    if not ENHANCED_AVAILABLE:
        return
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print("E Stop Monitor Example")
    print("=" * 50)
    print(f"PLC IP: {plc_ip}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Create PLC validator
        print("Connecting to PLC...")
        validator = EnhancedPLCValidator(plc_ip)
        
        # Add callback for state changes
        validator.add_estop_change_callback(estop_change_callback)
        
        # Get initial status
        print("Getting initial E Stop status...")
        status = validator.get_estop_status()
        
        if "error" in status:
            print(f"Error: {status['error']}")
            return
        
        print("Initial E Stop Status:")
        print("-" * 30)
        for estop_id, estop_data in status['estops'].items():
            print(f"{estop_data['name']} ({estop_data['location']}): {estop_data['current_state'].upper()}")
            if estop_data['is_dual_channel']:
                print(f"  Channel A: {estop_data['channel_a_state'].upper() if estop_data['channel_a_state'] else 'UNKNOWN'}")
                print(f"  Channel B: {estop_data['channel_b_state'].upper() if estop_data['channel_b_state'] else 'UNKNOWN'}")
        print()
        
        # Start monitoring
        print("Starting E Stop monitoring (1 second interval)...")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        validator.start_estop_monitoring(1.0)
        
        # Monitor for 60 seconds or until interrupted
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
        
        # Stop monitoring
        validator.stop_estop_monitoring()
        
        # Get final status and report
        print("\nFinal E Stop Status:")
        print("-" * 30)
        final_status = validator.get_estop_status()
        for estop_id, estop_data in final_status['estops'].items():
            print(f"{estop_data['name']}: {estop_data['current_state'].upper()} "
                  f"(Total Changes: {estop_data['total_changes']})")
        
        # Generate report
        print("\nGenerating E Stop monitoring report...")
        report = validator.generate_estop_report()
        print(report)
        
        # Export changes to file
        export_filename = f"estop_changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        print(f"Exporting state changes to {export_filename}...")
        validator.export_estop_changes(export_filename)
        print(f"Export complete: {export_filename}")
        
        # Close connection
        validator.close()
        
    except Exception as e:
        print(f"Error: {e}")
        return
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()