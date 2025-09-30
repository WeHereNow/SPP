#!/usr/bin/env python3
"""
Test E Stop Buttons Removed - Simple Version
Test that the Get Status and Generate Report buttons have been removed from E Stop monitoring
"""

import sys
import re

def test_estop_buttons_removed():
    """Test that the Get Status and Generate Report buttons are removed by checking source code"""
    print("E Stop Buttons Removal Test (Source Code Analysis)")
    print("=" * 60)
    
    try:
        # Read the enhanced toolkit source code
        with open('/workspace/spp_toolkit_enhanced.py', 'r') as f:
            source_code = f.read()
        
        print("Analyzing source code for removed buttons...")
        
        # Check for Get Status button creation
        get_status_button_pattern = r'btn_estop_status.*=.*ttk\.Button.*text.*Get Status'
        if re.search(get_status_button_pattern, source_code):
            print("❌ Get Status button creation still exists in source code")
            return False
        else:
            print("✅ Get Status button creation successfully removed")
        
        # Check for Generate Report button creation
        generate_report_button_pattern = r'btn_estop_report.*=.*ttk\.Button.*text.*Generate Report'
        if re.search(generate_report_button_pattern, source_code):
            print("❌ Generate Report button creation still exists in source code")
            return False
        else:
            print("✅ Generate Report button creation successfully removed")
        
        # Check for Get Status event handler method
        get_status_method_pattern = r'def _on_get_estop_status\(self\):'
        if re.search(get_status_method_pattern, source_code):
            print("❌ _on_get_estop_status method still exists in source code")
            return False
        else:
            print("✅ _on_get_estop_status method successfully removed")
        
        # Check for Generate Report event handler method
        generate_report_method_pattern = r'def _on_generate_estop_report\(self\):'
        if re.search(generate_report_method_pattern, source_code):
            print("❌ _on_generate_estop_report method still exists in source code")
            return False
        else:
            print("✅ _on_generate_estop_report method successfully removed")
        
        # Check that remaining buttons still exist
        print("\nChecking remaining buttons...")
        
        # Check for Start Monitoring button
        start_button_pattern = r'btn_estop_start.*=.*ttk\.Button.*text.*Start Monitoring'
        if re.search(start_button_pattern, source_code):
            print("✅ Start Monitoring button exists")
        else:
            print("❌ Start Monitoring button missing")
            return False
        
        # Check for Stop Monitoring button
        stop_button_pattern = r'btn_estop_stop.*=.*ttk\.Button.*text.*Stop Monitoring'
        if re.search(stop_button_pattern, source_code):
            print("✅ Stop Monitoring button exists")
        else:
            print("❌ Stop Monitoring button missing")
            return False
        
        # Check for Export Changes CSV button
        export_button_pattern = r'btn_estop_export.*=.*ttk\.Button.*text.*Export Changes CSV'
        if re.search(export_button_pattern, source_code):
            print("✅ Export Changes CSV button exists")
        else:
            print("❌ Export Changes CSV button missing")
            return False
        
        # Check for Session Report button
        session_report_button_pattern = r'btn_estop_session_report.*=.*ttk\.Button.*text.*Session Report'
        if re.search(session_report_button_pattern, source_code):
            print("✅ Session Report button exists")
        else:
            print("❌ Session Report button missing")
            return False
        
        # Check for Export Session CSV button
        session_export_button_pattern = r'btn_estop_session_export.*=.*ttk\.Button.*text.*Export Session CSV'
        if re.search(session_export_button_pattern, source_code):
            print("✅ Export Session CSV button exists")
        else:
            print("❌ Export Session CSV button missing")
            return False
        
        # Check that remaining event handlers exist
        print("\nChecking remaining event handlers...")
        
        # Check for Start Monitoring event handler
        start_handler_pattern = r'def _on_start_estop_monitoring\(self\):'
        if re.search(start_handler_pattern, source_code):
            print("✅ _on_start_estop_monitoring method exists")
        else:
            print("❌ _on_start_estop_monitoring method missing")
            return False
        
        # Check for Stop Monitoring event handler
        stop_handler_pattern = r'def _on_stop_estop_monitoring\(self\):'
        if re.search(stop_handler_pattern, source_code):
            print("✅ _on_stop_estop_monitoring method exists")
        else:
            print("❌ _on_stop_estop_monitoring method missing")
            return False
        
        # Check for Export Changes event handler
        export_handler_pattern = r'def _on_export_estop_changes\(self\):'
        if re.search(export_handler_pattern, source_code):
            print("✅ _on_export_estop_changes method exists")
        else:
            print("❌ _on_export_estop_changes method missing")
            return False
        
        # Check for Session Report event handler
        session_report_handler_pattern = r'def _on_generate_estop_session_report\(self\):'
        if re.search(session_report_handler_pattern, source_code):
            print("✅ _on_generate_estop_session_report method exists")
        else:
            print("❌ _on_generate_estop_session_report method missing")
            return False
        
        # Check for Export Session CSV event handler
        session_export_handler_pattern = r'def _on_export_estop_session_csv\(self\):'
        if re.search(session_export_handler_pattern, source_code):
            print("✅ _on_export_estop_session_csv method exists")
        else:
            print("❌ _on_export_estop_session_csv method missing")
            return False
        
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
        # Read the PLC verification source code
        with open('/workspace/plc_verification.py', 'r') as f:
            source_code = f.read()
        
        print("Analyzing PLC verification source code...")
        
        # Check that GetPLCType is no longer used
        getplctype_pattern = r'comm\.GetPLCType\(\)'
        if re.search(getplctype_pattern, source_code):
            print("❌ GetPLCType method call still exists in source code")
            return False
        else:
            print("✅ GetPLCType method call successfully removed")
        
        # Check that Controller.ProcessorType is used instead
        processor_type_pattern = r'comm\.Read\("Controller\.ProcessorType"\)'
        if re.search(processor_type_pattern, source_code):
            print("✅ Controller.ProcessorType read method added")
        else:
            print("❌ Controller.ProcessorType read method not found")
            return False
        
        # Test the actual PLC verification
        from plc_verification import PLCVerifier
        
        print("\nTesting PLC verification (expecting connection error, not GetPLCType error)...")
        verifier = PLCVerifier()
        test_ip = "11.200.0.10"
        
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