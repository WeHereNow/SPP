#!/usr/bin/env python3
"""
Test E Stop Buttons Removed
Test that the Get Status and Generate Report buttons have been removed from E Stop monitoring
"""

import sys
import time
from datetime import datetime

def test_estop_buttons_removed():
    """Test that the Get Status and Generate Report buttons are removed"""
    print("E Stop Buttons Removal Test")
    print("=" * 50)
    
    try:
        # Import the enhanced toolkit
        from spp_toolkit_enhanced import SPPToolkitEnhanced
        
        print("Creating SPP Toolkit Enhanced instance...")
        app = SPPToolkitEnhanced()
        print("✓ SPP Toolkit Enhanced created successfully")
        
        # Check if the buttons exist
        print("\nChecking for removed buttons...")
        
        # Check if Get Status button exists
        if hasattr(app, 'btn_estop_status'):
            print("❌ Get Status button still exists")
            return False
        else:
            print("✅ Get Status button successfully removed")
        
        # Check if Generate Report button exists
        if hasattr(app, 'btn_estop_report'):
            print("❌ Generate Report button still exists")
            return False
        else:
            print("✅ Generate Report button successfully removed")
        
        # Check if the event handler methods exist
        if hasattr(app, '_on_get_estop_status'):
            print("❌ _on_get_estop_status method still exists")
            return False
        else:
            print("✅ _on_get_estop_status method successfully removed")
        
        if hasattr(app, '_on_generate_estop_report'):
            print("❌ _on_generate_estop_report method still exists")
            return False
        else:
            print("✅ _on_generate_estop_report method successfully removed")
        
        # Check that remaining buttons still exist
        print("\nChecking remaining buttons...")
        
        if hasattr(app, 'btn_estop_start'):
            print("✅ Start Monitoring button exists")
        else:
            print("❌ Start Monitoring button missing")
            return False
        
        if hasattr(app, 'btn_estop_stop'):
            print("✅ Stop Monitoring button exists")
        else:
            print("❌ Stop Monitoring button missing")
            return False
        
        if hasattr(app, 'btn_estop_export'):
            print("✅ Export Changes CSV button exists")
        else:
            print("❌ Export Changes CSV button missing")
            return False
        
        if hasattr(app, 'btn_estop_session_report'):
            print("✅ Session Report button exists")
        else:
            print("❌ Session Report button missing")
            return False
        
        if hasattr(app, 'btn_estop_session_export'):
            print("✅ Export Session CSV button exists")
        else:
            print("❌ Export Session CSV button missing")
            return False
        
        # Check that remaining event handlers exist
        print("\nChecking remaining event handlers...")
        
        if hasattr(app, '_on_start_estop_monitoring'):
            print("✅ _on_start_estop_monitoring method exists")
        else:
            print("❌ _on_start_estop_monitoring method missing")
            return False
        
        if hasattr(app, '_on_stop_estop_monitoring'):
            print("✅ _on_stop_estop_monitoring method exists")
        else:
            print("❌ _on_stop_estop_monitoring method missing")
            return False
        
        if hasattr(app, '_on_export_estop_changes'):
            print("✅ _on_export_estop_changes method exists")
        else:
            print("❌ _on_export_estop_changes method missing")
            return False
        
        if hasattr(app, '_on_generate_estop_session_report'):
            print("✅ _on_generate_estop_session_report method exists")
        else:
            print("❌ _on_generate_estop_session_report method missing")
            return False
        
        if hasattr(app, '_on_export_estop_session_csv'):
            print("✅ _on_export_estop_session_csv method exists")
        else:
            print("❌ _on_export_estop_session_csv method missing")
            return False
        
        # Close the app
        app.destroy()
        print("\n✓ SPP Toolkit Enhanced closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plc_verification_fix():
    """Test that the PLC verification GetPLCType error is fixed"""
    print("\n" + "="*60)
    print("TESTING PLC VERIFICATION FIX")
    print("="*60)
    
    try:
        from plc_verification import PLCVerifier
        
        print("Creating PLC Verifier...")
        verifier = PLCVerifier()
        print("✓ PLC Verifier created successfully")
        
        # Test with a mock IP (won't actually connect)
        print("\nTesting PLC verification (expecting connection error, not GetPLCType error)...")
        test_ip = "11.200.0.10"
        
        # This should fail with connection error, not GetPLCType error
        try:
            result = verifier.verify_plc(test_ip)
            print("✓ PLC verification completed without GetPLCType error")
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
    print("E Stop Buttons Removal and PLC Verification Fix Test Suite")
    print("=" * 70)
    
    tests = [
        ("E Stop Buttons Removal", test_estop_buttons_removed),
        ("PLC Verification Fix", test_plc_verification_fix),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 70)
    print("Test Results:")
    print("=" * 70)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe E Stop monitoring interface has been cleaned up:")
        print("✅ Get Status button removed")
        print("✅ Generate Report button removed")
        print("✅ Corresponding event handler methods removed")
        print("✅ Remaining buttons and handlers intact")
        print("✅ PLC verification GetPLCType error fixed")
        print("\nThe E Stop monitoring interface now has a cleaner, more focused design:")
        print("- Start Monitoring")
        print("- Stop Monitoring") 
        print("- Export Changes CSV")
        print("- Session Report")
        print("- Export Session CSV")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()