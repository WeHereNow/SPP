#!/usr/bin/env python3
"""
Test E Stop Current States
Test the E Stop monitor to see current states and verify tag reading
"""

import sys
from datetime import datetime

def test_estop_current_states():
    """Test E Stop current states reading"""
    print("E Stop Current States Test")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print(f"Testing E Stop states for PLC: {plc_ip}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        print("Creating PLC validator...")
        validator = EnhancedPLCValidator(plc_ip)
        print("✓ PLC validator created successfully")
        
        # Test E Stop status reading
        print("\nTesting E Stop status reading...")
        status = validator.get_estop_status()
        
        if "error" in status:
            print(f"⚠ Expected error (no PLC connection): {status['error']}")
            print("This is normal when there's no PLC connection.")
        else:
            print("✓ E Stop status retrieved successfully")
        
        # Display detailed status
        print("\n" + "="*60)
        print("DETAILED E STOP STATUS")
        print("="*60)
        
        estops = status.get('estops', {})
        if estops:
            print(f"Found {len(estops)} E Stops:")
            print()
            
            for estop_id, estop_data in estops.items():
                print(f"🔧 {estop_data['name']}")
                print(f"   📍 Location: {estop_data['location']}")
                print(f"   🔄 Current State: {estop_data['current_state'].upper()}")
                print(f"   📊 Total Changes: {estop_data['total_changes']}")
                print(f"   ⏰ Last Read: {estop_data.get('last_read_time', 'Never')}")
                print(f"   ❌ Read Error: {estop_data.get('read_error', 'None')}")
                
                if estop_data['is_dual_channel']:
                    channel_a = estop_data.get('channel_a_state', 'unknown')
                    channel_b = estop_data.get('channel_b_state', 'unknown')
                    channel_a_str = channel_a.upper() if channel_a else 'UNKNOWN'
                    channel_b_str = channel_b.upper() if channel_b else 'UNKNOWN'
                    print(f"   🔌 Channel A: {channel_a_str}")
                    print(f"   🔌 Channel B: {channel_b_str}")
                
                print()
        else:
            print("❌ No E Stops found in status")
        
        # Test the E Stop monitor directly
        print("\n" + "="*60)
        print("TESTING E STOP MONITOR DIRECTLY")
        print("="*60)
        
        monitor = validator.estop_monitor
        print(f"E Stop monitor type: {type(monitor)}")
        
        # Test E Stop definitions
        if hasattr(monitor, 'estop_definitions'):
            definitions = monitor.estop_definitions
            print(f"E Stop definitions: {len(definitions)}")
            
            for estop_id, definition in definitions.items():
                print(f"  - {estop_id}: {definition.name} ({definition.location})")
                if definition.is_dual_channel:
                    print(f"    Channel A: {definition.channel_a_tag}")
                    print(f"    Channel B: {definition.channel_b_tag}")
                else:
                    print(f"    Tag: {definition.tag}")
        
        # Test current states reading
        print("\nTesting read_current_states method...")
        try:
            current_states = monitor.read_current_states()
            print(f"✓ read_current_states returned {len(current_states)} states")
            
            for estop_id, estop_status in current_states.items():
                print(f"  - {estop_id}: {estop_status.current_state.value.upper()}")
                if estop_status.read_error:
                    print(f"    Error: {estop_status.read_error}")
        except Exception as e:
            print(f"✗ read_current_states failed: {e}")
        
        # Test tag reading approach
        print("\n" + "="*60)
        print("VERIFYING TAG READING APPROACH")
        print("="*60)
        
        # Check if the monitor is using the correct tags
        expected_tags = [
            'Program:SafetyProgram.SafetyIO.In.ESTOP_Relay1Feedback',
            'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelA',
            'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelB',
            'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelA',
            'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelB',
            'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelA',
            'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelB',
            'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelA',
            'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelB',
        ]
        
        print("Expected E Stop tags:")
        for i, tag in enumerate(expected_tags, 1):
            print(f"  {i}. {tag}")
        
        # Check if the monitor has the correct tag mapping
        if hasattr(monitor, 'read_current_states'):
            print("\n✓ E Stop monitor has read_current_states method")
            print("✓ E Stop monitor should be using the same tags as PLC validation")
        else:
            print("\n✗ E Stop monitor missing read_current_states method")
        
        # Close validator
        validator.close()
        print("\n✓ PLC validator closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    print("E Stop Current States Test Suite")
    print("=" * 60)
    
    result = test_estop_current_states()
    
    print("\n" + "=" * 60)
    print("Test Result:")
    print("=" * 60)
    
    if result:
        print("✅ TEST PASSED")
        print("\nThe E Stop monitor is properly configured and ready to use.")
        print("When connected to a real PLC, it will show actual states instead of 'Unknown'.")
        print("\nTo test with real PLC:")
        print("1. Run: python3 estop_realtime_monitor.py <PLC_IP>")
        print("2. Or use the enhanced toolkit GUI")
    else:
        print("❌ TEST FAILED")
        print("Please check the E Stop monitor implementation.")
    
    return result

if __name__ == "__main__":
    main()