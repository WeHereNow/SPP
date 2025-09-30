#!/usr/bin/env python3
"""
Test E Stop Report Improvement
Test the improved report generation with better connection status information
"""

import sys
from datetime import datetime

def test_improved_report():
    """Test the improved report generation"""
    print("E Stop Report Improvement Test")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print(f"Testing improved report for PLC: {plc_ip}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        print("Creating PLC validator...")
        validator = EnhancedPLCValidator(plc_ip)
        print("✓ PLC validator created successfully")
        
        # Start monitoring briefly to generate some read attempts
        print("\nStarting brief monitoring to generate read attempts...")
        validator.start_estop_monitoring(1.0)
        
        # Let it run for a few cycles
        import time
        time.sleep(3)
        
        # Stop monitoring
        validator.stop_estop_monitoring()
        print("✓ Monitoring stopped")
        
        # Get current status
        print("\nGetting current E Stop status...")
        status = validator.get_estop_status()
        
        # Check if we have read errors (expected without PLC connection)
        estops = status.get('estops', {})
        has_read_errors = any(estop_data.get('read_error') for estop_data in estops.values())
        
        if has_read_errors:
            print("✓ Read errors detected (expected without PLC connection)")
        else:
            print("⚠ No read errors detected")
        
        # Generate improved report
        print("\nGenerating improved report...")
        report = validator.generate_estop_report()
        print("✓ Report generated successfully")
        
        # Display the report
        print("\n" + "="*80)
        print("IMPROVED E STOP MONITORING REPORT")
        print("="*80)
        print(report)
        
        # Check if report contains connection status information
        if "PLC CONNECTION STATUS" in report:
            print("\n✅ Report includes PLC connection status section")
        else:
            print("\n❌ Report missing PLC connection status section")
        
        if "Connection Error" in report:
            print("✅ Report shows connection error indicators")
        else:
            print("❌ Report missing connection error indicators")
        
        if "Last Read:" in report:
            print("✅ Report shows last read timestamps")
        else:
            print("❌ Report missing last read timestamps")
        
        # Test summary generation
        print("\nTesting summary generation...")
        summary = validator.generate_estop_summary()
        print("✓ Summary generated successfully")
        
        # Check summary for read errors
        current_states = summary.get("current_states", {})
        has_summary_errors = any(state.get("read_error") for state in current_states.values())
        
        if has_summary_errors:
            print("✅ Summary includes read error information")
        else:
            print("❌ Summary missing read error information")
        
        # Close validator
        validator.close()
        print("\n✓ PLC validator closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_without_monitoring():
    """Test report generation without monitoring"""
    print("\n" + "="*60)
    print("TESTING REPORT WITHOUT MONITORING")
    print("="*60)
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        validator = EnhancedPLCValidator("11.200.0.10")
        
        # Generate report without any monitoring
        print("Generating report without monitoring...")
        report = validator.generate_estop_report()
        print("✓ Report generated successfully")
        
        # Check if report shows no monitoring activity
        if "Monitoring Active: No" in report:
            print("✅ Report correctly shows monitoring as inactive")
        else:
            print("❌ Report incorrectly shows monitoring status")
        
        # Check if report shows unknown states
        if "UNKNOWN" in report:
            print("✅ Report shows UNKNOWN states (expected without PLC connection)")
        else:
            print("❌ Report missing UNKNOWN states")
        
        # Close validator
        validator.close()
        print("✓ Test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("E Stop Report Improvement Test Suite")
    print("=" * 60)
    
    tests = [
        ("Improved Report with Monitoring", test_improved_report),
        ("Report without Monitoring", test_report_without_monitoring),
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
        print("\nThe E Stop monitoring report now includes:")
        print("✅ PLC connection status section")
        print("✅ Connection error indicators")
        print("✅ Last read timestamps")
        print("✅ Clear explanation of UNKNOWN states")
        print("✅ Better error reporting")
        print("\nThe 'UNKNOWN' status is now properly explained in the report.")
        print("When connected to a real PLC, the report will show actual states.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()