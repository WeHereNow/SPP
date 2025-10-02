#!/usr/bin/env python3
"""
E Stop Real-time Monitor
Shows current E Stop states and detects changes in real-time
"""

import sys
import time
import signal
from datetime import datetime
from typing import Dict, Any

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nStopping E Stop monitoring...")
    sys.exit(0)

def format_estop_state(state: str) -> str:
    """Format E Stop state for display"""
    if state == "active":
        return "🔴 ACTIVE"
    elif state == "inactive":
        return "🟢 INACTIVE"
    else:
        return "❓ UNKNOWN"

def display_estop_status(status: Dict[str, Any]):
    """Display current E Stop status in a formatted way"""
    print("\n" + "="*80)
    print(f"E STOP STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    if "error" in status:
        print(f"❌ ERROR: {status['error']}")
        return
    
    estops = status.get('estops', {})
    if not estops:
        print("❌ No E Stops found")
        return
    
    print(f"📊 Total E Stops: {len(estops)}")
    print(f"📈 Total State Changes: {status.get('total_changes', 0)}")
    print()
    
    for estop_id, estop_data in estops.items():
        name = estop_data['name']
        location = estop_data['location']
        current_state = estop_data['current_state']
        total_changes = estop_data['total_changes']
        last_change = estop_data.get('last_change_time', 'Never')
        
        print(f"🔧 {name}")
        print(f"   📍 Location: {location}")
        print(f"   🔄 Current State: {format_estop_state(current_state)}")
        print(f"   📊 Total Changes: {total_changes}")
        print(f"   ⏰ Last Change: {last_change}")
        
        if estop_data['is_dual_channel']:
            channel_a = estop_data.get('channel_a_state', 'unknown')
            channel_b = estop_data.get('channel_b_state', 'unknown')
            print(f"   🔌 Channel A: {format_estop_state(channel_a)}")
            print(f"   🔌 Channel B: {format_estop_state(channel_b)}")
        
        print()

def display_recent_changes(changes: list):
    """Display recent E Stop state changes"""
    if not changes:
        return
    
    print("\n" + "="*80)
    print("RECENT E STOP STATE CHANGES")
    print("="*80)
    
    for change in changes[-10:]:  # Show last 10 changes
        timestamp = change['timestamp'].strftime('%H:%M:%S')
        estop_name = change['estop_name']
        old_state = change['old_state'].upper()
        new_state = change['new_state'].upper()
        channel_info = f" [Channel {change['channel']}]" if change['channel'] else ""
        duration_info = f" (Duration: {change['duration_seconds']:.1f}s)" if change['duration_seconds'] else ""
        
        print(f"[{timestamp}] {estop_name}: {old_state} → {new_state}{channel_info}{duration_info}")

def main():
    """Main monitoring function"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("E Stop Real-time Monitor")
    print("="*50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    monitor_interval = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    
    print(f"PLC IP: {plc_ip}")
    print(f"Monitor Interval: {monitor_interval} seconds")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        from plc_communication import EnhancedPLCValidator
        from estop_monitor import EStopStateChange
        
        # Create PLC validator
        print("🔌 Connecting to PLC...")
        validator = EnhancedPLCValidator(plc_ip)
        
        # Track previous states for change detection
        previous_states = {}
        
        # Callback for state changes
        def on_estop_change(change: EStopStateChange):
            timestamp = change.timestamp.strftime('%H:%M:%S')
            channel_info = f" [Channel {change.channel}]" if change.channel else ""
            duration_info = f" (Duration: {change.duration_seconds:.1f}s)" if change.duration_seconds else ""
            
            print(f"\n🚨 E STOP STATE CHANGE DETECTED!")
            print(f"   ⏰ Time: {timestamp}")
            print(f"   🔧 E Stop: {change.estop_name}")
            print(f"   🔄 Change: {change.old_state.value.upper()} → {change.new_state.value.upper()}")
            if channel_info:
                print(f"   🔌 Channel: {channel_info}")
            if duration_info:
                print(f"   ⏱️  Duration: {duration_info}")
            print()
        
        # Add callback
        validator.add_estop_change_callback(on_estop_change)
        
        # Get initial status
        print("📊 Getting initial E Stop status...")
        status = validator.get_estop_status()
        display_estop_status(status)
        
        if "error" in status:
            print(f"❌ Error getting initial status: {status['error']}")
            print("This is expected if there's no PLC connection.")
            print("The system will continue to show 'Unknown' states.")
            print()
        
        # Start monitoring
        print(f"🔄 Starting E Stop monitoring ({monitor_interval}s interval)...")
        validator.start_estop_monitoring(monitor_interval)
        
        # Monitor loop
        try:
            while True:
                time.sleep(monitor_interval)
                
                # Get current status
                current_status = validator.get_estop_status()
                
                # Check for changes in display
                if "estops" in current_status:
                    current_states = {estop_id: estop_data['current_state'] 
                                    for estop_id, estop_data in current_status['estops'].items()}
                    
                    # Detect changes for display purposes
                    if previous_states:
                        for estop_id, current_state in current_states.items():
                            if estop_id in previous_states and previous_states[estop_id] != current_state:
                                estop_name = current_status['estops'][estop_id]['name']
                                old_state = previous_states[estop_id]
                                print(f"🔄 {estop_name}: {old_state.upper()} → {current_state.upper()}")
                    
                    previous_states = current_states
                
                # Display current status
                display_estop_status(current_status)
                
                # Display recent changes
                recent_changes = validator.get_estop_recent_changes(10)
                display_recent_changes(recent_changes)
                
        except KeyboardInterrupt:
            pass
        
        # Stop monitoring
        print("\n🛑 Stopping E Stop monitoring...")
        validator.stop_estop_monitoring()
        
        # Get final status
        print("\n📊 Final E Stop Status:")
        final_status = validator.get_estop_status()
        display_estop_status(final_status)
        
        # Generate comprehensive summary
        print("\n📊 Generating monitoring session summary...")
        summary = validator.generate_estop_summary()
        
        # Display summary
        print("\n" + "="*80)
        print("E STOP MONITORING SESSION SUMMARY")
        print("="*80)
        
        session_info = summary["session_info"]
        print(f"📅 Session End Time: {session_info['end_time']}")
        if session_info['start_time']:
            print(f"📅 Session Start Time: {session_info['start_time']}")
            if session_info['duration_seconds']:
                duration_min = session_info['duration_seconds'] / 60
                print(f"⏱️  Session Duration: {duration_min:.1f} minutes")
        print(f"🔄 Monitoring Interval: {session_info['monitoring_interval']}s")
        print(f"📊 Total Reads: {session_info['total_reads']}")
        print(f"🔄 Monitoring Active: {'Yes' if session_info['monitoring_active'] else 'No'}")
        
        # Change statistics
        change_stats = summary["change_statistics"]
        print(f"\n📈 CHANGE STATISTICS:")
        print(f"   Total State Changes: {change_stats['total_changes']}")
        
        if change_stats['changes_by_estop']:
            print(f"   Changes by E Stop:")
            for estop_name, count in change_stats['changes_by_estop'].items():
                print(f"     - {estop_name}: {count} changes")
        
        if change_stats['changes_by_state']['active'] > 0 or change_stats['changes_by_state']['inactive'] > 0:
            print(f"   Changes by State:")
            print(f"     - ACTIVE: {change_stats['changes_by_state']['active']}")
            print(f"     - INACTIVE: {change_stats['changes_by_state']['inactive']}")
        
        if any(change_stats['changes_by_channel'].values()):
            print(f"   Changes by Channel:")
            for channel, count in change_stats['changes_by_channel'].items():
                if count > 0:
                    print(f"     - Channel {channel}: {count} changes")
        
        # Current E Stop states
        print(f"\n🔧 CURRENT E STOP STATES:")
        for estop_id, estop_data in summary["estop_summary"].items():
            state_emoji = "🔴" if estop_data['current_state'] == 'active' else "🟢" if estop_data['current_state'] == 'inactive' else "❓"
            print(f"   {state_emoji} {estop_data['name']}: {estop_data['current_state'].upper()}")
            if estop_data['total_changes'] > 0:
                print(f"      Total Changes: {estop_data['total_changes']}")
                if estop_data['last_change_time']:
                    print(f"      Last Change: {estop_data['last_change_time']}")
        
        # Export options
        print(f"\n💾 EXPORT OPTIONS:")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON export
        json_filename = f"estop_changes_{timestamp}.json"
        print(f"📄 Exporting state changes to JSON: {json_filename}")
        validator.export_estop_changes(json_filename)
        print(f"   ✅ JSON export complete")
        
        # CSV export
        csv_filename = f"estop_changes_{timestamp}.csv"
        print(f"📊 Exporting state changes to CSV: {csv_filename}")
        validator.export_estop_changes_csv(csv_filename)
        print(f"   ✅ CSV export complete")
        
        # Summary export
        summary_filename = f"estop_summary_{timestamp}.json"
        print(f"📋 Exporting session summary: {summary_filename}")
        import json
        with open(summary_filename, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"   ✅ Summary export complete")
        
        print(f"\n📁 All exports saved with timestamp: {timestamp}")
        
        # Generate final report
        print("\n📋 Generating detailed report...")
        report = validator.generate_estop_report()
        print(report)
        
        # Close connection
        validator.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n✅ E Stop monitoring completed successfully!")

if __name__ == "__main__":
    main()