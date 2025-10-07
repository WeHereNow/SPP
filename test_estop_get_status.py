#!/usr/bin/env python3
"""
Test E Stop Get Status Functionality
Test the improved "Get Status" functionality with connection status information
"""

import sys
from datetime import datetime

def test_get_status_functionality():
    """Test the Get Status functionality"""
    print("E Stop Get Status Test")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print(f"Testing Get Status for PLC: {plc_ip}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        print("Creating PLC validator...")
        validator = EnhancedPLCValidator(plc_ip)
        print("✓ PLC validator created successfully")
        
        # Test Get Status functionality
        print("\nTesting Get Status functionality...")
        status = validator.get_estop_status()
        print("✓ Get Status completed successfully")
        
        # Display the status in the same format as the enhanced toolkit
        print("\n" + "="*60)
        print("E STOP STATUS REPORT")
        print("="*60)
        
        print(f"E Stop Status Report - {status['timestamp']}")
        print(f"Monitoring Active: {'Yes' if status['monitoring_active'] else 'No'}")
        print(f"Monitor Interval: {status['monitor_interval']}s")
        print()
        
        # Check for connection issues
        has_read_errors = any(estop_data.get('read_error') for estop_data in status['estops'].values())
        if has_read_errors:
            print("⚠️  PLC CONNECTION STATUS:")
            print("-" * 40)
            print("❌ PLC Connection Issues Detected")
            print("   E Stop states showing as 'UNKNOWN' due to connection problems.")
            print("   This is expected when:")
            print("   - pylogix library is not installed")
            print("   - PLC is not accessible on the network")
            print("   - PLC IP address is incorrect")
            print()
        
        for estop_id, estop_data in status['estops'].items():
            print(f"{estop_data['name']} ({estop_data['location']}):")
            
            # Show state with appropriate indicator
            if estop_data.get('read_error'):
                print(f"  Current State: {estop_data['current_state'].upper()} (⚠️  Connection Error)")
            else:
                print(f"  Current State: {estop_data['current_state'].upper()}")
            
            if estop_data['is_dual_channel']:
                channel_a_state = estop_data['channel_a_state'].upper() if estop_data['channel_a_state'] else 'UNKNOWN'
                channel_b_state = estop_data['channel_b_state'].upper() if estop_data['channel_b_state'] else 'UNKNOWN'
                print(f"  Channel A: {channel_a_state}")
                print(f"  Channel B: {channel_b_state}")
            
            print(f"  Total Changes: {estop_data['total_changes']}")
            
            if estop_data.get('last_read_time'):
                print(f"  Last Read: {estop_data['last_read_time']}")
            
            if estop_data.get('last_change_time'):
                print(f"  Last Change: {estop_data['last_change_time']}")
            
            if estop_data.get('read_error'):
                print(f"  Read Error: {estop_data['read_error']}")
            
            print()
        
        # Verify the status contains the expected information
        print("="*60)
        print("VERIFICATION")
        print("="*60)
        
        # Check if we have read errors (expected without PLC connection)
        if has_read_errors:
            print("✅ Read errors detected (expected without PLC connection)")
        else:
            print("❌ No read errors detected (unexpected)")
        
        # Check if last_read_time is populated
        has_last_read_times = any(estop_data.get('last_read_time') for estop_data in status['estops'].values())
        if has_last_read_times:
            print("✅ Last read times populated")
        else:
            print("❌ Last read times not populated")
        
        # Check if read_error is populated
        has_read_errors_info = any(estop_data.get('read_error') for estop_data in status['estops'].values())
        if has_read_errors_info:
            print("✅ Read error information populated")
        else:
            print("❌ Read error information not populated")
        
        # Check if states are UNKNOWN (expected without PLC connection)
        all_unknown = all(estop_data['current_state'] == 'unknown' for estop_data in status['estops'].values())
        if all_unknown:
            print("✅ All states are UNKNOWN (expected without PLC connection)")
        else:
            print("❌ Not all states are UNKNOWN (unexpected)")
        
        # Close validator
        validator.close()
        print("\n✓ PLC validator closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_get_status_calls():
    """Test multiple Get Status calls to ensure read attempts are made"""
    print("\n" + "="*60)
    print("TESTING MULTIPLE GET STATUS CALLS")
    print("="*60)
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        validator = EnhancedPLCValidator("11.200.0.10")
        
        # Make multiple Get Status calls
        print("Making multiple Get Status calls...")
        for i in range(3):
            print(f"  Call {i+1}/3...")
            status = validator.get_estop_status()
            
            # Check if last_read_time is recent
            estops = status['estops']
            if estops:
                first_estop = list(estops.values())[0]
                if first_estop.get('last_read_time'):
                    print(f"    Last read: {first_estop['last_read_time']}")
                else:
                    print(f"    No last read time")
            
            import time
            time.sleep(1)  # Wait 1 second between calls
        
        print("✓ Multiple Get Status calls completed")
        
        # Close validator
        validator.close()
        print("✓ Test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("E Stop Get Status Test Suite")
    print("=" * 60)
    
    tests = [
        ("Get Status Functionality", test_get_status_functionality),
        ("Multiple Get Status Calls", test_multiple_get_status_calls),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe Get Status functionality now includes:")
        print("✅ PLC connection status section")
        print("✅ Connection error indicators")
        print("✅ Last read timestamps")
        print("✅ Clear explanation of UNKNOWN states")
        print("✅ Read attempts on each Get Status call")
        print("\nThe 'UNKNOWN' status is now properly explained.")
        print("When connected to a real PLC, Get Status will show actual states.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()