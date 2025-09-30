#!/usr/bin/env python3
"""
E Stop Monitor Command Line Interface
Provides E Stop monitoring functionality without GUI dependencies
"""

import sys
import time
import signal
from datetime import datetime

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nStopping E Stop monitoring...")
    sys.exit(0)

def main():
    """Main CLI function"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("E Stop Monitor - Command Line Interface")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    monitor_interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    
    print(f"PLC IP: {plc_ip}")
    print(f"Monitor Interval: {monitor_interval} seconds")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from plc_communication import EnhancedPLCValidator
        from estop_monitor import EStopStateChange
        
        # Create PLC validator
        print("Connecting to PLC...")
        validator = EnhancedPLCValidator(plc_ip)
        
        # Callback for state changes
        def on_estop_change(change: EStopStateChange):
            timestamp = change.timestamp.strftime('%H:%M:%S')
            channel_info = f" [Channel {change.channel}]" if change.channel else ""
            duration_info = f" (Duration: {change.duration_seconds:.1f}s)" if change.duration_seconds else ""
            
            print(f"[{timestamp}] {change.estop_name}: {change.old_state.value} -> {change.new_state.value}"
                  f"{channel_info}{duration_info}")
        
        # Add callback
        validator.add_estop_change_callback(on_estop_change)
        
        # Get initial status
        print("Getting initial E Stop status...")
        status = validator.get_estop_status()
        
        if "error" in status:
            print(f"Error: {status['error']}")
            return
        
        print("\nInitial E Stop Status:")
        print("-" * 30)
        for estop_id, estop_data in status['estops'].items():
            print(f"{estop_data['name']} ({estop_data['location']}): {estop_data['current_state'].upper()}")
            if estop_data['is_dual_channel']:
                print(f"  Channel A: {estop_data['channel_a_state'].upper() if estop_data['channel_a_state'] else 'UNKNOWN'}")
                print(f"  Channel B: {estop_data['channel_b_state'].upper() if estop_data['channel_b_state'] else 'UNKNOWN'}")
        print()
        
        # Start monitoring
        print(f"Starting E Stop monitoring ({monitor_interval}s interval)...")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        validator.start_estop_monitoring(monitor_interval)
        
        # Monitor indefinitely
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        # Stop monitoring
        validator.stop_estop_monitoring()
        
        # Get final status
        print("\nFinal E Stop Status:")
        print("-" * 30)
        final_status = validator.get_estop_status()
        for estop_id, estop_data in final_status['estops'].items():
            print(f"{estop_data['name']}: {estop_data['current_state'].upper()} "
                  f"(Total Changes: {estop_data['total_changes']})")
        
        # Generate comprehensive summary
        print("\nGenerating monitoring session summary...")
        summary = validator.generate_estop_summary()
        
        # Display summary
        print("\n" + "="*60)
        print("E STOP MONITORING SESSION SUMMARY")
        print("="*60)
        
        session_info = summary["session_info"]
        print(f"Session End Time: {session_info['end_time']}")
        if session_info['start_time']:
            print(f"Session Start Time: {session_info['start_time']}")
            if session_info['duration_seconds']:
                duration_min = session_info['duration_seconds'] / 60
                print(f"Session Duration: {duration_min:.1f} minutes")
        print(f"Monitoring Interval: {session_info['monitoring_interval']}s")
        print(f"Total Reads: {session_info['total_reads']}")
        
        # Change statistics
        change_stats = summary["change_statistics"]
        print(f"\nCHANGE STATISTICS:")
        print(f"  Total State Changes: {change_stats['total_changes']}")
        
        if change_stats['changes_by_estop']:
            print(f"  Changes by E Stop:")
            for estop_name, count in change_stats['changes_by_estop'].items():
                print(f"    - {estop_name}: {count} changes")
        
        # Export options
        print(f"\nEXPORT OPTIONS:")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON export
        json_filename = f"estop_changes_{timestamp}.json"
        print(f"Exporting state changes to JSON: {json_filename}")
        validator.export_estop_changes(json_filename)
        print(f"  JSON export complete")
        
        # CSV export
        csv_filename = f"estop_changes_{timestamp}.csv"
        print(f"Exporting state changes to CSV: {csv_filename}")
        validator.export_estop_changes_csv(csv_filename)
        print(f"  CSV export complete")
        
        # Summary export
        summary_filename = f"estop_summary_{timestamp}.json"
        print(f"Exporting session summary: {summary_filename}")
        import json
        with open(summary_filename, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  Summary export complete")
        
        print(f"\nAll exports saved with timestamp: {timestamp}")
        
        # Generate detailed report
        print("\nGenerating detailed E Stop monitoring report...")
        report = validator.generate_estop_report()
        print(report)
        
        # Close connection
        validator.close()
        
    except Exception as e:
        print(f"Error: {e}")
        return
    
    print("\nE Stop monitoring completed successfully!")

if __name__ == "__main__":
    main()