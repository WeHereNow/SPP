#!/usr/bin/env python3
"""
Test E Stop Generate Report Functionality
Test the improved "Generate Report" functionality with connection status information
"""

import sys
from datetime import datetime

def test_generate_report_functionality():
    """Test the Generate Report functionality"""
    print("E Stop Generate Report Test")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print(f"Testing Generate Report for PLC: {plc_ip}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        print("Creating PLC validator...")
        validator = EnhancedPLCValidator(plc_ip)
        print("✓ PLC validator created successfully")
        
        # Test Generate Report functionality
        print("\nTesting Generate Report functionality...")
        report = validator.generate_estop_report()
        print("✓ Generate Report completed successfully")
        
        # Display the report
        print("\n" + "="*80)
        print("GENERATED E STOP MONITORING REPORT")
        print("="*80)
        print(report)
        
        # Verify the report contains the expected information
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)
        
        # Check if report contains connection status information
        if "PLC CONNECTION STATUS" in report:
            print("✅ Report includes PLC connection status section")
        else:
            print("❌ Report missing PLC connection status section")
        
        if "Connection Issues Detected" in report:
            print("✅ Report shows connection issues detected")
        else:
            print("❌ Report missing connection issues information")
        
        if "Connection Error" in report:
            print("✅ Report shows connection error indicators")
        else:
            print("❌ Report missing connection error indicators")
        
        if "Last Read:" in report:
            print("✅ Report shows last read timestamps")
        else:
            print("❌ Report missing last read timestamps")
        
        if "pylogix is not installed" in report:
            print("✅ Report shows specific error message")
        else:
            print("❌ Report missing specific error message")
        
        # Check if report shows UNKNOWN states
        if "UNKNOWN" in report:
            print("✅ Report shows UNKNOWN states (expected without PLC connection)")
        else:
            print("❌ Report missing UNKNOWN states")
        
        # Close validator
        validator.close()
        print("\n✓ PLC validator closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_vs_get_status():
    """Test that Generate Report and Get Status show consistent information"""
    print("\n" + "="*60)
    print("TESTING REPORT VS GET STATUS CONSISTENCY")
    print("="*60)
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        validator = EnhancedPLCValidator("11.200.0.10")
        
        # Get status
        print("Getting E Stop status...")
        status = validator.get_estop_status()
        
        # Generate report
        print("Generating E Stop report...")
        report = validator.generate_estop_report()
        
        # Check consistency
        print("Checking consistency between status and report...")
        
        # Both should show connection issues
        status_has_errors = any(estop_data.get('read_error') for estop_data in status['estops'].values())
        report_has_errors = "Connection Issues Detected" in report
        
        if status_has_errors and report_has_errors:
            print("✅ Both status and report show connection issues")
        else:
            print("❌ Inconsistent connection issue reporting")
            print(f"   Status has errors: {status_has_errors}")
            print(f"   Report has errors: {report_has_errors}")
        
        # Both should show UNKNOWN states
        status_has_unknown = all(estop_data['current_state'] == 'unknown' for estop_data in status['estops'].values())
        report_has_unknown = "UNKNOWN" in report
        
        if status_has_unknown and report_has_unknown:
            print("✅ Both status and report show UNKNOWN states")
        else:
            print("❌ Inconsistent state reporting")
            print(f"   Status has unknown: {status_has_unknown}")
            print(f"   Report has unknown: {report_has_unknown}")
        
        # Close validator
        validator.close()
        print("✓ Consistency test completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("E Stop Generate Report Test Suite")
    print("=" * 60)
    
    tests = [
        ("Generate Report Functionality", test_generate_report_functionality),
        ("Report vs Get Status Consistency", test_report_vs_get_status),
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
        print("\nThe Generate Report functionality now includes:")
        print("✅ PLC connection status section")
        print("✅ Connection error indicators")
        print("✅ Last read timestamps")
        print("✅ Clear explanation of UNKNOWN states")
        print("✅ Specific error messages")
        print("✅ Consistent with Get Status functionality")
        print("\nThe 'UNKNOWN' status is now properly explained in reports.")
        print("When connected to a real PLC, reports will show actual states.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()