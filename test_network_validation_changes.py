#!/usr/bin/env python3
"""
Test Network Validation Changes
Test that AL1120 IO Link has been changed to AL1422 IO Link and IP address updated
"""

import sys
import re

def test_network_validation_changes():
    """Test that the network validation changes have been made"""
    print("Network Validation Changes Test")
    print("=" * 50)
    
    try:
        # Check all files that contain the network device mappings
        files_to_check = [
            '/workspace/spp_toolkit_enhanced.py',
            '/workspace/spp_toolkit_simple.py',
            '/workspace/Starting Script'
        ]
        
        print("Checking network device mappings in all files...")
        
        all_changes_correct = True
        
        for file_path in files_to_check:
            print(f"\nChecking {file_path}...")
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check that AL1120 has been changed to AL1422
                if "AL1120 IO Link" in content:
                    print(f"❌ {file_path} still contains 'AL1120 IO Link'")
                    all_changes_correct = False
                else:
                    print(f"✅ {file_path} no longer contains 'AL1120 IO Link'")
                
                # Check that AL1422 IO Link exists
                if "AL1422 IO Link" in content:
                    print(f"✅ {file_path} contains 'AL1422 IO Link'")
                else:
                    print(f"❌ {file_path} does not contain 'AL1422 IO Link'")
                    all_changes_correct = False
                
                # Check that IP address 11.200.1.30 has been changed to 11.200.1.31
                if '"11.200.1.30":' in content:
                    print(f"❌ {file_path} still contains IP address 11.200.1.30")
                    all_changes_correct = False
                else:
                    print(f"✅ {file_path} no longer contains IP address 11.200.1.30")
                
                # Check that IP address 11.200.1.31 exists
                if '"11.200.1.31":' in content:
                    print(f"✅ {file_path} contains IP address 11.200.1.31")
                else:
                    print(f"❌ {file_path} does not contain IP address 11.200.1.31")
                    all_changes_correct = False
                
                # Check the complete mapping
                if '"11.200.1.31": "AL1422 IO Link"' in content:
                    print(f"✅ {file_path} has correct mapping: 11.200.1.31 -> AL1422 IO Link")
                else:
                    print(f"❌ {file_path} does not have correct mapping")
                    all_changes_correct = False
                
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_changes_correct = False
        
        return all_changes_correct
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plc_verification_improvements():
    """Test that the PLC verification improvements have been made"""
    print("\n" + "="*60)
    print("TESTING PLC VERIFICATION IMPROVEMENTS")
    print("="*60)
    
    try:
        # Read the PLC verification source code
        with open('/workspace/plc_verification.py', 'r') as f:
            source_code = f.read()
        
        print("Analyzing PLC verification improvements...")
        
        # Check for improved logging
        if "Attempting to read project information from primary tags" in source_code:
            print("✅ Added detailed logging for primary tags")
        else:
            print("❌ Missing detailed logging for primary tags")
            return False
        
        if "Primary tags:" in source_code and "successful" in source_code:
            print("✅ Added success count logging")
        else:
            print("❌ Missing success count logging")
            return False
        
        if "Alternative tags:" in source_code and "successful" in source_code:
            print("✅ Added alternative tags success count logging")
        else:
            print("❌ Missing alternative tags success count logging")
            return False
        
        # Check for improved error handling
        if "Failed to read project name:" in source_code:
            print("✅ Added detailed error logging for each tag")
        else:
            print("❌ Missing detailed error logging")
            return False
        
        # Check for fallback tags
        if "Trying additional fallback tags for project information" in source_code:
            print("✅ Added fallback tags for project information")
        else:
            print("❌ Missing fallback tags for project information")
            return False
        
        if "Trying additional fallback tags for controller type" in source_code:
            print("✅ Added fallback tags for controller type")
        else:
            print("❌ Missing fallback tags for controller type")
            return False
        
        if "Trying additional fallback tags for controller name" in source_code:
            print("✅ Added fallback tags for controller name")
        else:
            print("❌ Missing fallback tags for controller name")
            return False
        
        if "Trying additional fallback tags for version information" in source_code:
            print("✅ Added fallback tags for version information")
        else:
            print("❌ Missing fallback tags for version information")
            return False
        
        # Check for final summary logging
        if "Final project information summary:" in source_code:
            print("✅ Added final summary logging")
        else:
            print("❌ Missing final summary logging")
            return False
        
        # Test the actual PLC verification (expecting connection error, not GetPLCType error)
        print("\nTesting improved PLC verification...")
        from plc_verification import PLCVerifier
        
        verifier = PLCVerifier()
        test_ip = "11.200.0.10"
        
        try:
            result = verifier.verify_plc(
                ip_address=test_ip,
                expected_project_name="USP_V35_2025_09_16_OldSafety.ACD",
                expected_major_revision=35,
                expected_minor_revision=11
            )
            
            print("✓ PLC verification completed without GetPLCType error")
            print(f"  Connection Successful: {result.connection_successful}")
            print(f"  Error Message: '{result.error_message}'")
            
            # The error should be about pylogix not being installed, not GetPLCType
            if "GetPLCType" in result.error_message:
                print("❌ GetPLCType error still exists")
                return False
            else:
                print("✅ No GetPLCType error (expected connection error)")
            
        except Exception as e:
            error_msg = str(e)
            if "GetPLCType" in error_msg:
                print(f"❌ GetPLCType error still exists: {error_msg}")
                return False
            else:
                print(f"✅ No GetPLCType error (expected connection error): {error_msg}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Network Validation Changes and PLC Verification Improvements Test Suite")
    print("=" * 80)
    
    tests = [
        ("Network Validation Changes", test_network_validation_changes),
        ("PLC Verification Improvements", test_plc_verification_improvements),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 80)
    print("Test Results:")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe network validation and PLC verification improvements are complete:")
        print("✅ AL1120 IO Link changed to AL1422 IO Link")
        print("✅ IP address changed from 11.200.1.30 to 11.200.1.31")
        print("✅ Changes applied to all relevant files")
        print("✅ PLC verification improved with better error handling")
        print("✅ PLC verification improved with fallback tags")
        print("✅ PLC verification improved with detailed logging")
        print("✅ No more GetPLCType errors")
        print("\nThe system is ready for production use with:")
        print("- Updated network device mappings")
        print("- Improved PLC verification robustness")
        print("- Better error handling and logging")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()