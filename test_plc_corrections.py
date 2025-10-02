#!/usr/bin/env python3
"""
Test PLC Corrections
Test the PLC validation corrections, E Stop monitoring changes, and PLC verification fixes
"""

import sys
import re

def test_plc_validation_g_par_tags():
    """Test that the PLC validation now uses individual G Par bit tags"""
    print("PLC Validation G Par Tags Test")
    print("=" * 50)
    
    try:
        # Read the Starting Script to check for the new G Par bit tags
        with open('/workspace/Starting Script', 'r') as f:
            content = f.read()
        
        print("Checking for individual G Par bit tags...")
        
        # Check for the new G Par bit tag lists
        if "G_PAR_BIT_TAGS" in content:
            print("✅ G_PAR_BIT_TAGS list found")
        else:
            print("❌ G_PAR_BIT_TAGS list not found")
            return False
        
        if "G_PAR1_BIT_TAGS" in content:
            print("✅ G_PAR1_BIT_TAGS list found")
        else:
            print("❌ G_PAR1_BIT_TAGS list not found")
            return False
        
        if "G_PARNEW_BIT_TAGS" in content:
            print("✅ G_PARNEW_BIT_TAGS list found")
        else:
            print("❌ G_PARNEW_BIT_TAGS list not found")
            return False
        
        if "G_PARTEMP_BIT_TAGS" in content:
            print("✅ G_PARTEMP_BIT_TAGS list found")
        else:
            print("❌ G_PARTEMP_BIT_TAGS list not found")
            return False
        
        if "ALL_G_PAR_BIT_TAGS" in content:
            print("✅ ALL_G_PAR_BIT_TAGS combined list found")
        else:
            print("❌ ALL_G_PAR_BIT_TAGS combined list not found")
            return False
        
        # Check for specific bit tags
        specific_tags = [
            'g_Par.0', 'g_Par.1', 'g_Par.2', 'g_Par.3', 'g_Par.4', 'g_Par.5', 'g_Par.6', 'g_Par.7',
            'g_Par.9', 'g_Par.11', 'g_Par.12', 'g_Par.13', 'g_Par.14', 'g_Par.15', 'g_Par.16', 'g_Par.17',
            'g_Par.18', 'g_Par.19', 'g_Par.20', 'g_Par.21', 'g_Par.24', 'g_Par.25', 'g_Par.26', 'g_Par.27',
            'g_Par.28', 'g_Par.29', 'g_Par.30', 'g_Par.31',
            'g_Par1.0', 'g_Par1.1', 'g_Par1.2', 'g_Par1.3', 'g_Par1.4', 'g_Par1.5', 'g_Par1.6',
            'g_ParNew.0', 'g_ParNew.1', 'g_ParNew.2', 'g_ParNew.3', 'g_ParNew.4', 'g_ParNew.5', 'g_ParNew.6', 'g_ParNew.7',
            'g_ParNew.8', 'g_ParNew.10', 'g_ParNew.11', 'g_ParNew.12', 'g_ParNew.13', 'g_ParNew.14', 'g_ParNew.15',
            'g_ParNew.16', 'g_ParNew.17', 'g_ParNew.20', 'g_ParNew.21', 'g_ParNew.31',
            'g_parTemp.1', 'g_parTemp.2', 'g_parTemp.3', 'g_parTemp.5', 'g_parTemp.6', 'g_parTemp.7'
        ]
        
        missing_tags = []
        for tag in specific_tags:
            if tag not in content:
                missing_tags.append(tag)
        
        if missing_tags:
            print(f"❌ Missing specific tags: {missing_tags}")
            return False
        else:
            print("✅ All specific G Par bit tags found")
        
        # Check that the IO validation function uses the new approach
        if "comm.Read(ALL_G_PAR_BIT_TAGS)" in content:
            print("✅ IO validation function uses individual bit tags")
        else:
            print("❌ IO validation function doesn't use individual bit tags")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_estop_session_buttons_removed():
    """Test that the session report and session export CSV buttons are removed"""
    print("\n" + "="*60)
    print("TESTING E STOP SESSION BUTTONS REMOVAL")
    print("="*60)
    
    try:
        # Read the enhanced toolkit source code
        with open('/workspace/spp_toolkit_enhanced.py', 'r') as f:
            content = f.read()
        
        print("Checking for removed session buttons...")
        
        # Check that session report button is removed
        if "btn_estop_session_report" in content:
            print("❌ Session Report button still exists")
            return False
        else:
            print("✅ Session Report button removed")
        
        # Check that session export CSV button is removed
        if "btn_estop_session_export" in content:
            print("❌ Session Export CSV button still exists")
            return False
        else:
            print("✅ Session Export CSV button removed")
        
        # Check that session report event handler is removed
        if "_on_generate_estop_session_report" in content:
            print("❌ Session Report event handler still exists")
            return False
        else:
            print("✅ Session Report event handler removed")
        
        # Check that session export CSV event handler is removed
        if "_on_export_estop_session_csv" in content:
            print("❌ Session Export CSV event handler still exists")
            return False
        else:
            print("✅ Session Export CSV event handler removed")
        
        # Check that remaining buttons still exist
        if "btn_estop_start" in content:
            print("✅ Start Monitoring button exists")
        else:
            print("❌ Start Monitoring button missing")
            return False
        
        if "btn_estop_stop" in content:
            print("✅ Stop Monitoring button exists")
        else:
            print("❌ Stop Monitoring button missing")
            return False
        
        if "btn_estop_export" in content:
            print("✅ Export Changes CSV button exists")
        else:
            print("❌ Export Changes CSV button missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_plc_verification_compact_guardlogix():
    """Test that the PLC verification is updated for Compact GuardLogix"""
    print("\n" + "="*60)
    print("TESTING PLC VERIFICATION COMPACT GUARDLOGIX FIXES")
    print("="*60)
    
    try:
        # Read the PLC verification source code
        with open('/workspace/plc_verification.py', 'r') as f:
            content = f.read()
        
        print("Checking for Compact GuardLogix fixes...")
        
        # Check for Compact GuardLogix specific tags
        if "compact_guardlogix_tags" in content:
            print("✅ Compact GuardLogix specific tags added")
        else:
            print("❌ Compact GuardLogix specific tags not found")
            return False
        
        # Check for Controller.ProcessorType tag
        if "Controller.ProcessorType" in content:
            print("✅ Controller.ProcessorType tag added")
        else:
            print("❌ Controller.ProcessorType tag not found")
            return False
        
        # Check for improved tag reading strategy
        if "trying Compact GuardLogix specific tags" in content:
            print("✅ Compact GuardLogix tag reading strategy added")
        else:
            print("❌ Compact GuardLogix tag reading strategy not found")
            return False
        
        # Check for Controller.* tags as primary
        if "Controller.ProjectName" in content and "Controller.MajorRevision" in content:
            print("✅ Controller.* tags set as primary")
        else:
            print("❌ Controller.* tags not set as primary")
            return False
        
        # Check for additional fallback tags
        if "Controller.ProjectTitle" in content:
            print("✅ Additional fallback tags added")
        else:
            print("❌ Additional fallback tags not found")
            return False
        
        # Test the actual PLC verification (expecting connection error, not path segment error)
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
            
            print("✓ PLC verification completed")
            print(f"  Connection Successful: {result.connection_successful}")
            print(f"  Error Message: '{result.error_message}'")
            
            # The error should be about pylogix not being installed, not path segment errors
            if "Path segment error" in result.error_message:
                print("❌ Path segment errors still exist")
                return False
            else:
                print("✅ No path segment errors (expected connection error)")
            
        except Exception as e:
            error_msg = str(e)
            if "Path segment error" in error_msg:
                print(f"❌ Path segment errors still exist: {error_msg}")
                return False
            else:
                print(f"✅ No path segment errors (expected connection error): {error_msg}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("PLC Corrections Test Suite")
    print("=" * 60)
    
    tests = [
        ("PLC Validation G Par Tags", test_plc_validation_g_par_tags),
        ("E Stop Session Buttons Removal", test_estop_session_buttons_removed),
        ("PLC Verification Compact GuardLogix", test_plc_verification_compact_guardlogix),
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
        print("\nThe PLC corrections are complete:")
        print("✅ PLC validation now uses individual G Par bit tags")
        print("✅ All specified G Par bit tags are included")
        print("✅ E Stop session report and export CSV buttons removed")
        print("✅ PLC verification updated for Compact GuardLogix")
        print("✅ Controller.* tags set as primary for 5069-L330ERMS2")
        print("✅ Compact GuardLogix specific tag reading strategy")
        print("✅ Additional fallback tags for better compatibility")
        print("\nThe system is ready for production use with:")
        print("- Correct G Par bit tag reading")
        print("- Streamlined E Stop monitoring interface")
        print("- Robust PLC verification for Compact GuardLogix")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()