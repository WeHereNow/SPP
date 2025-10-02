#!/usr/bin/env python3
"""
Test HMI Config Fix
Verify that the HMI configuration error has been resolved
"""

import sys
from datetime import datetime

def test_hmi_config_fix():
    """Test that the HMI configuration is now available"""
    print("HMI Config Fix Test")
    print("=" * 50)
    
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test importing config
        print("1. Testing config import...")
        from config import config
        print("✓ Config imported successfully")
        
        # Test accessing HMI config
        print("\n2. Testing HMI config access...")
        hmi_config = config.hmi
        print("✓ config.hmi accessed successfully")
        
        # Test HMI config attributes
        print("\n3. Testing HMI config attributes...")
        print(f"   default_port: {hmi_config.default_port}")
        print(f"   connection_timeout: {hmi_config.connection_timeout}")
        print(f"   read_timeout: {hmi_config.read_timeout}")
        print(f"   max_retries: {hmi_config.max_retries}")
        print(f"   retry_delay: {hmi_config.retry_delay}")
        print("✓ All HMI config attributes accessible")
        
        # Test that all expected attributes exist
        expected_attributes = ['default_port', 'connection_timeout', 'read_timeout', 'max_retries', 'retry_delay']
        missing_attributes = []
        
        for attr in expected_attributes:
            if not hasattr(hmi_config, attr):
                missing_attributes.append(attr)
        
        if missing_attributes:
            print(f"❌ Missing attributes: {missing_attributes}")
            return False
        else:
            print("✓ All expected HMI config attributes present")
        
        return True
        
    except AttributeError as e:
        if "'AppConfig' object has no attribute 'hmi'" in str(e):
            print(f"❌ HMI config error still exists: {e}")
            return False
        else:
            print(f"❌ Unexpected AttributeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hmi_verification_import():
    """Test that HMI verification can now import config without error"""
    print(f"\n" + "="*60)
    print("HMI VERIFICATION IMPORT TEST")
    print("="*60)
    
    try:
        print("Testing HMI verification import...")
        
        # This should now work without the AttributeError
        from hmi_verification import HMIVerifier
        print("✓ HMI verification imported successfully")
        
        # Test creating HMI verifier
        print("\nTesting HMI verifier creation...")
        verifier = HMIVerifier()
        print("✓ HMI verifier created successfully")
        
        # Test that it can access config.hmi
        print("\nTesting config.hmi access from HMI verifier...")
        from hmi_verification import config as hmi_config
        hmi_settings = hmi_config.hmi
        print(f"✓ HMI config accessible: port={hmi_settings.default_port}")
        
        return True
        
    except AttributeError as e:
        if "'AppConfig' object has no attribute 'hmi'" in str(e):
            print(f"❌ HMI config error still exists in HMI verification: {e}")
            return False
        else:
            print(f"❌ Unexpected AttributeError in HMI verification: {e}")
            return False
    except Exception as e:
        print(f"❌ Error importing HMI verification: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_config_sections():
    """Test that all config sections are accessible"""
    print(f"\n" + "="*60)
    print("ALL CONFIG SECTIONS TEST")
    print("="*60)
    
    try:
        from config import config
        
        config_sections = {
            'network': 'Network configuration',
            'plc': 'PLC configuration', 
            'cognex': 'Cognex configuration',
            'estop': 'E Stop configuration',
            'hmi': 'HMI configuration',
            'ui': 'UI configuration'
        }
        
        print("Testing all configuration sections:")
        
        all_accessible = True
        for section_name, description in config_sections.items():
            try:
                section = getattr(config, section_name)
                print(f"✓ {section_name}: {description} - OK")
            except AttributeError as e:
                print(f"❌ {section_name}: {description} - MISSING ({e})")
                all_accessible = False
        
        if all_accessible:
            print(f"\n✅ All {len(config_sections)} configuration sections accessible!")
        else:
            print(f"\n❌ Some configuration sections are missing!")
        
        return all_accessible
        
    except Exception as e:
        print(f"❌ Error testing config sections: {e}")
        return False

def main():
    """Run all tests"""
    print("HMI Config Fix Test Suite")
    print("=" * 60)
    
    tests = [
        ("HMI Config Fix", test_hmi_config_fix),
        ("HMI Verification Import", test_hmi_verification_import),
        ("All Config Sections", test_all_config_sections),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 SUCCESS! HMI configuration error has been fixed!")
        print("\nChanges Made:")
        print("✅ Added HMIConfig dataclass to config.py")
        print("✅ Added hmi attribute to AppConfig class")
        print("✅ HMI verification can now access config.hmi")
        print("\nHMI Configuration Settings:")
        print("• default_port: 2222 (FactoryTalk View SE)")
        print("• connection_timeout: 5.0 seconds")
        print("• read_timeout: 10.0 seconds") 
        print("• max_retries: 3")
        print("• retry_delay: 1.0 seconds")
        print("\nThe 'AppConfig' object has no attribute 'hmi' error is now resolved!")
    else:
        print("❌ Some tests failed. The HMI configuration error may still exist.")
    
    return all_passed

if __name__ == "__main__":
    main()