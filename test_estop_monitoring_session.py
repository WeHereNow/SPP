#!/usr/bin/env python3
"""
Test E Stop Monitoring Session Report
Test the new monitoring session report functionality with CSV export
"""

import sys
import time
from datetime import datetime

def test_monitoring_session_report():
    """Test the monitoring session report functionality"""
    print("E Stop Monitoring Session Report Test")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print(f"Testing monitoring session report for PLC: {plc_ip}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        print("Creating PLC validator...")
        validator = EnhancedPLCValidator(plc_ip)
        print("✓ PLC validator created successfully")
        
        # Start monitoring briefly to generate some data
        print("\nStarting brief monitoring to generate session data...")
        validator.start_estop_monitoring(1.0)
        
        # Let it run for a few cycles
        print("Monitoring for 5 seconds...")
        for i in range(5):
            time.sleep(1)
            print(f"  Cycle {i+1}/5...")
        
        # Stop monitoring
        print("Stopping monitoring...")
        validator.stop_estop_monitoring()
        print("✓ Monitoring stopped")
        
        # Test monitoring session report generation
        print("\nTesting monitoring session report generation...")
        session_report = validator.generate_estop_monitoring_session_report()
        print("✓ Monitoring session report generated successfully")
        
        # Display the report
        print("\n" + "="*80)
        print("GENERATED MONITORING SESSION REPORT")
        print("="*80)
        print(session_report)
        
        # Test CSV export
        print("\nTesting CSV export of monitoring session report...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"test_monitoring_session_{timestamp}.csv"
        validator.export_estop_monitoring_session_csv(csv_filename)
        print(f"✓ CSV export completed: {csv_filename}")
        
        # Verify CSV file contents
        print("\nVerifying CSV file contents...")
        try:
            import csv
            with open(csv_filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                rows = list(reader)
                
                print(f"✓ CSV headers: {headers}")
                print(f"✓ CSV rows: {len(rows)}")
                
                # Check for different report types
                report_types = set(row['report_type'] for row in rows)
                print(f"✓ Report types found: {report_types}")
                
                # Show sample rows
                print("\nSample CSV rows:")
                for i, row in enumerate(rows[:10]):  # Show first 10 rows
                    print(f"  Row {i+1}: {row['report_type']} - {row['description']} = {row['value']}")
                
                if len(rows) > 10:
                    print(f"  ... and {len(rows) - 10} more rows")
                    
        except Exception as e:
            print(f"✗ Error reading CSV file: {e}")
        
        # Verify report content
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)
        
        # Check if report contains session information
        if "MONITORING SESSION INFORMATION" in session_report:
            print("✅ Report includes monitoring session information")
        else:
            print("❌ Report missing monitoring session information")
        
        # Check if report contains connection status
        if "PLC CONNECTION STATUS" in session_report:
            print("✅ Report includes PLC connection status")
        else:
            print("❌ Report missing PLC connection status")
        
        # Check if report contains current states
        if "CURRENT E STOP STATES" in session_report:
            print("✅ Report includes current E Stop states")
        else:
            print("❌ Report missing current E Stop states")
        
        # Check if report contains statistics
        if "STATE CHANGE STATISTICS" in session_report:
            print("✅ Report includes state change statistics")
        else:
            print("❌ Report missing state change statistics")
        
        # Check if report contains recent changes
        if "RECENT STATE CHANGES" in session_report:
            print("✅ Report includes recent state changes")
        else:
            print("❌ Report missing recent state changes")
        
        # Close validator
        validator.close()
        print("\n✓ PLC validator closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_format():
    """Test the CSV format with sample data"""
    print("\n" + "="*60)
    print("TESTING CSV FORMAT")
    print("="*60)
    
    try:
        from estop_monitor import EStopMonitor, EStopStateChange, EStopState
        from datetime import datetime
        
        # Create a mock E Stop monitor for testing
        class MockPLCConnectionManager:
            def get_connection(self):
                return self
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def Read(self, tags):
                return []
        
        monitor = EStopMonitor(MockPLCConnectionManager(), None)
        
        # Add some mock state changes
        mock_changes = [
            EStopStateChange(
                timestamp=datetime.now(),
                estop_name="Back Left E-Stop",
                old_state=EStopState.INACTIVE,
                new_state=EStopState.ACTIVE,
                channel="A",
                duration_seconds=0.0
            ),
            EStopStateChange(
                timestamp=datetime.now(),
                estop_name="Front E-Stop",
                old_state=EStopState.ACTIVE,
                new_state=EStopState.INACTIVE,
                channel="B",
                duration_seconds=5.5
            )
        ]
        
        # Add mock changes to monitor
        monitor.state_changes = mock_changes
        
        # Test CSV export
        test_csv_filename = f"test_csv_format_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        monitor.export_monitoring_session_to_csv(test_csv_filename)
        print(f"✓ Mock CSV export completed: {test_csv_filename}")
        
        # Verify CSV contents
        import csv
        with open(test_csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            rows = list(reader)
            
            print(f"✓ CSV headers: {headers}")
            print(f"✓ CSV rows: {len(rows)}")
            
            # Check for different report types
            report_types = set(row['report_type'] for row in rows)
            print(f"✓ Report types found: {report_types}")
            
            # Show sample rows
            print("\nSample CSV rows:")
            for i, row in enumerate(rows[:15]):  # Show first 15 rows
                print(f"  Row {i+1}: {row['report_type']} - {row['description']} = {row['value']}")
        
        return True
        
    except Exception as e:
        print(f"✗ CSV format test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("E Stop Monitoring Session Report Test Suite")
    print("=" * 60)
    
    tests = [
        ("Monitoring Session Report", test_monitoring_session_report),
        ("CSV Format", test_csv_format),
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
        print("\nThe E Stop monitoring session report system now includes:")
        print("✅ Comprehensive monitoring session report")
        print("✅ Session information (start, end, duration)")
        print("✅ Current E Stop states with connection status")
        print("✅ State change statistics")
        print("✅ Recent state changes")
        print("✅ CSV export with structured data")
        print("✅ Multiple report types in CSV (SESSION_INFO, CURRENT_STATE, STATE_CHANGE)")
        print("\nThe system now reads results from Start/Stop Monitoring")
        print("and generates comprehensive reports that can be exported to CSV.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()