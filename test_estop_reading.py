#!/usr/bin/env python3
"""
Test script to verify E Stop tag reading functionality
"""

def test_estop_tag_reading():
    """Test that E Stop tags can be read correctly"""
    try:
        from plc_communication import EnhancedPLCValidator
        print("✓ EnhancedPLCValidator imported successfully")
        
        # Test with a dummy IP (won't actually connect)
        validator = EnhancedPLCValidator("127.0.0.1")
        print("✓ EnhancedPLCValidator created successfully")
        
        # Test the safety status reading method
        print("\nTesting safety status reading...")
        try:
            safety_status = validator.get_safety_status()
            print("✓ get_safety_status() method exists and can be called")
        except Exception as e:
            print(f"✗ get_safety_status() failed: {e}")
            return False
        
        # Test E Stop monitor integration
        print("\nTesting E Stop monitor integration...")
        try:
            estop_status = validator.get_estop_status()
            print("✓ get_estop_status() method exists and can be called")
            if "error" in estop_status:
                print(f"  Expected error (no PLC connection): {estop_status['error']}")
            else:
                print(f"  E Stop status retrieved: {len(estop_status.get('estops', {}))} E Stops")
        except Exception as e:
            print(f"✗ get_estop_status() failed: {e}")
            return False
        
        # Test E Stop monitor direct reading
        print("\nTesting E Stop monitor direct reading...")
        try:
            estop_states = validator.estop_monitor.read_current_states()
            print("✓ E Stop monitor read_current_states() method exists")
            print(f"  Retrieved {len(estop_states)} E Stop states")
            
            for estop_id, status in estop_states.items():
                print(f"  - {status.name}: {status.state.value}")
                if status.read_error:
                    print(f"    Error: {status.read_error}")
        except Exception as e:
            print(f"✗ E Stop monitor read_current_states() failed: {e}")
            return False
        
        validator.close()
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_safety_tags_consistency():
    """Test that all modules use the same safety tags"""
    try:
        from estop_monitor import EStopMonitor
        print("\nTesting safety tags consistency...")
        
        # Get tags from E Stop monitor
        monitor = EStopMonitor(None)
        estop_tags = []
        for estop_info in monitor.estop_definitions.values():
            if estop_info.is_dual_channel:
                estop_tags.extend([estop_info.channel_a_tag, estop_info.channel_b_tag])
            else:
                estop_tags.append(estop_info.tag)
        
        # Expected tags from Starting Script
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
        
        print(f"✓ E Stop monitor has {len(estop_tags)} tags")
        print(f"✓ Expected {len(expected_tags)} tags")
        
        # Check if all expected tags are present
        missing_tags = []
        for expected_tag in expected_tags:
            if expected_tag not in estop_tags:
                missing_tags.append(expected_tag)
        
        if missing_tags:
            print(f"✗ Missing tags: {missing_tags}")
            return False
        else:
            print("✓ All expected tags are present in E Stop monitor")
            return True
            
    except Exception as e:
        print(f"✗ Safety tags consistency test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("E Stop Tag Reading Test")
    print("=" * 50)
    
    tests = [
        ("E Stop Tag Reading", test_estop_tag_reading),
        ("Safety Tags Consistency", test_safety_tags_consistency),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 20)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! E Stop tag reading should work correctly.")
        print("\nTo test with a real PLC:")
        print("1. Run the enhanced toolkit")
        print("2. Go to E Stop Monitor tab")
        print("3. Enter your PLC IP address")
        print("4. Click 'Get Status' to see current E Stop states")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()