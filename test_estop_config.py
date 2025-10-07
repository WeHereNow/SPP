#!/usr/bin/env python3
"""
Test script to verify E Stop monitoring configuration
"""

def test_config():
    """Test that the configuration is properly set up"""
    try:
        from config import config
        print("✓ Config imported successfully")
        
        # Check if estop config exists
        if hasattr(config, 'estop'):
            print("✓ EStop config found")
            estop_config = config.estop
            print(f"  - Default monitor interval: {estop_config.default_monitor_interval}")
            print(f"  - Change detection enabled: {estop_config.change_detection_enabled}")
            print(f"  - Log all changes: {estop_config.log_all_changes}")
            print(f"  - Max history size: {estop_config.max_history_size}")
            print(f"  - Auto start monitoring: {estop_config.auto_start_monitoring}")
        else:
            print("✗ EStop config not found")
            return False
            
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    return True

def test_estop_monitor():
    """Test that the E Stop monitor can be imported and initialized"""
    try:
        from estop_monitor import EStopMonitor, EStopStateChange, EStopState
        print("✓ E Stop monitor imported successfully")
        
        # Test E Stop definitions
        monitor = EStopMonitor(None)  # No PLC connection for test
        definitions = monitor.estop_definitions
        
        print(f"✓ E Stop definitions loaded: {len(definitions)} E Stops")
        for estop_id, estop_info in definitions.items():
            print(f"  - {estop_info.name}: {estop_info.location}")
            if estop_info.is_dual_channel:
                print(f"    Channels: A={estop_info.channel_a_tag}, B={estop_info.channel_b_tag}")
            else:
                print(f"    Tag: {estop_info.tag}")
        
        # Verify the specific tags mentioned by the user
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
        
        all_tags = []
        for estop_info in definitions.values():
            if estop_info.is_dual_channel:
                all_tags.extend([estop_info.channel_a_tag, estop_info.channel_b_tag])
            else:
                all_tags.append(estop_info.tag)
        
        print(f"✓ All expected tags found: {len(expected_tags)}")
        for tag in expected_tags:
            if tag in all_tags:
                print(f"  ✓ {tag}")
            else:
                print(f"  ✗ Missing: {tag}")
                return False
        
    except Exception as e:
        print(f"✗ E Stop monitor test failed: {e}")
        return False
    
    return True

def test_plc_communication():
    """Test that PLC communication module can import E Stop monitor"""
    try:
        from plc_communication import EnhancedPLCValidator
        print("✓ PLC communication module imported successfully")
        
        # Test that the validator can be created (without actual PLC connection)
        validator = EnhancedPLCValidator("127.0.0.1")  # Dummy IP
        print("✓ EnhancedPLCValidator created successfully")
        
        # Test E Stop monitor integration
        if hasattr(validator, 'estop_monitor'):
            print("✓ E Stop monitor integrated into PLC validator")
        else:
            print("✗ E Stop monitor not integrated into PLC validator")
            return False
            
    except Exception as e:
        print(f"✗ PLC communication test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("E Stop Monitoring Configuration Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("E Stop Monitor", test_estop_monitor),
        ("PLC Communication", test_plc_communication),
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
        print("✓ All tests passed! E Stop monitoring is ready to use.")
    else:
        print("✗ Some tests failed. Please check the configuration.")
    
    return all_passed

if __name__ == "__main__":
    main()