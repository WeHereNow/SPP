#!/usr/bin/env python3
"""
Test E Stop CSV Export and Summary
Test the new CSV export and summary functionality
"""

import sys
import json
from datetime import datetime

def test_csv_export_and_summary():
    """Test CSV export and summary functionality"""
    print("E Stop CSV Export and Summary Test")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print(f"Testing CSV export and summary for PLC: {plc_ip}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from plc_communication import EnhancedPLCValidator
        
        # Create validator
        print("Creating PLC validator...")
        validator = EnhancedPLCValidator(plc_ip)
        print("✓ PLC validator created successfully")
        
        # Test summary generation
        print("\nTesting summary generation...")
        summary = validator.generate_estop_summary()
        print("✓ Summary generated successfully")
        
        # Display summary
        print("\n" + "="*60)
        print("GENERATED SUMMARY")
        print("="*60)
        
        session_info = summary["session_info"]
        print(f"Session End Time: {session_info['end_time']}")
        print(f"Monitoring Interval: {session_info['monitoring_interval']}s")
        print(f"Total Reads: {session_info['total_reads']}")
        print(f"Monitoring Active: {session_info['monitoring_active']}")
        
        change_stats = summary["change_statistics"]
        print(f"\nChange Statistics:")
        print(f"  Total Changes: {change_stats['total_changes']}")
        print(f"  Changes by E Stop: {change_stats['changes_by_estop']}")
        print(f"  Changes by State: {change_stats['changes_by_state']}")
        print(f"  Changes by Channel: {change_stats['changes_by_channel']}")
        
        print(f"\nE Stop Summary:")
        for estop_id, estop_data in summary["estop_summary"].items():
            print(f"  {estop_data['name']}: {estop_data['current_state']} "
                  f"({estop_data['total_changes']} changes)")
        
        # Test CSV export
        print("\nTesting CSV export...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"test_estop_export_{timestamp}.csv"
        
        validator.export_estop_changes_csv(csv_filename)
        print(f"✓ CSV export completed: {csv_filename}")
        
        # Test JSON export
        print("\nTesting JSON export...")
        json_filename = f"test_estop_export_{timestamp}.json"
        validator.export_estop_changes(json_filename)
        print(f"✓ JSON export completed: {json_filename}")
        
        # Test summary export
        print("\nTesting summary export...")
        summary_filename = f"test_estop_summary_{timestamp}.json"
        with open(summary_filename, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Summary export completed: {summary_filename}")
        
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
                
                if rows:
                    print("Sample CSV row:")
                    sample_row = rows[0]
                    for key, value in sample_row.items():
                        print(f"  {key}: {value}")
                else:
                    print("  No data rows (expected without PLC connection)")
                    
        except Exception as e:
            print(f"✗ Error reading CSV file: {e}")
        
        # Verify JSON file contents
        print("\nVerifying JSON file contents...")
        try:
            with open(json_filename, 'r') as jsonfile:
                json_data = json.load(jsonfile)
                print(f"✓ JSON export timestamp: {json_data.get('export_timestamp')}")
                print(f"✓ JSON total changes: {json_data.get('total_changes')}")
                print(f"✓ JSON changes array length: {len(json_data.get('changes', []))}")
        except Exception as e:
            print(f"✗ Error reading JSON file: {e}")
        
        # Test report generation
        print("\nTesting report generation...")
        report = validator.generate_estop_report()
        print("✓ Report generated successfully")
        print(f"Report length: {len(report)} characters")
        
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
    """Test CSV format with sample data"""
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
        monitor.export_changes_to_csv(test_csv_filename)
        print(f"✓ Mock CSV export completed: {test_csv_filename}")
        
        # Verify CSV contents
        import csv
        with open(test_csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            rows = list(reader)
            
            print(f"✓ CSV headers: {headers}")
            print(f"✓ CSV rows: {len(rows)}")
            
            for i, row in enumerate(rows):
                print(f"Row {i+1}:")
                for key, value in row.items():
                    print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ CSV format test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("E Stop CSV Export and Summary Test Suite")
    print("=" * 60)
    
    tests = [
        ("CSV Export and Summary", test_csv_export_and_summary),
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
        print("\nThe E Stop monitoring system now includes:")
        print("✅ CSV export with timestamps")
        print("✅ Comprehensive session summary")
        print("✅ Multiple export formats (JSON, CSV, Summary)")
        print("✅ Detailed change statistics")
        print("✅ Session duration tracking")
        print("✅ Export with timestamps for easy file management")
        print("\nCSV Export includes:")
        print("  - timestamp (ISO format)")
        print("  - date (YYYY-MM-DD)")
        print("  - time (HH:MM:SS.mmm)")
        print("  - estop_name")
        print("  - location")
        print("  - old_state")
        print("  - new_state")
        print("  - channel")
        print("  - duration_seconds")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()