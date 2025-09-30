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
        
        # Generate final report
        print("\n📋 Generating final report...")
        report = validator.generate_estop_report()
        print(report)
        
        # Export changes to file
        export_filename = f"estop_changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        print(f"\n💾 Exporting state changes to {export_filename}...")
        validator.export_estop_changes(export_filename)
        print(f"✅ Export complete: {export_filename}")
        
        # Close connection
        validator.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n✅ E Stop monitoring completed successfully!")

if __name__ == "__main__":
    main()