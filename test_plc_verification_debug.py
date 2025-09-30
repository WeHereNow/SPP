#!/usr/bin/env python3
"""
Test PLC Verification Debug
Debug the PLC verification issue to understand why project information is not being read
"""

import sys
from datetime import datetime

def test_plc_verification_debug():
    """Debug PLC verification to understand the issue"""
    print("PLC Verification Debug Test")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print(f"Testing PLC verification for: {plc_ip}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from plc_verification import PLCVerifier
        
        # Create verifier
        print("Creating PLC Verifier...")
        verifier = PLCVerifier()
        print("✓ PLC Verifier created successfully")
        
        # Test getting project info
        print(f"\nTesting project info retrieval for {plc_ip}...")
        try:
            project_info = verifier.get_plc_project_info(plc_ip)
            print("✓ Project info retrieval completed")
            
            print(f"\nProject Information:")
            print(f"  IP Address: {project_info.ip_address}")
            print(f"  Project Name: '{project_info.project_name}'")
            print(f"  Major Revision: {project_info.major_revision}")
            print(f"  Minor Revision: {project_info.minor_revision}")
            print(f"  Last Load Time: '{project_info.last_load_time}'")
            print(f"  Controller Name: '{project_info.controller_name}'")
            print(f"  Controller Type: '{project_info.controller_type}'")
            print(f"  Firmware Version: '{project_info.firmware_version}'")
            print(f"  Serial Number: '{project_info.serial_number}'")
            print(f"  Checksum: '{project_info.checksum}'")
            print(f"  Signature: '{project_info.signature}'")
            
        except Exception as e:
            print(f"✗ Error getting project info: {e}")
            import traceback
            traceback.print_exc()
        
        # Test verification with expected values
        print(f"\nTesting PLC verification with expected values...")
        try:
            result = verifier.verify_plc(
                ip_address=plc_ip,
                expected_project_name="USP_V35_2025_09_16_OldSafety.ACD",
                expected_major_revision=35,
                expected_minor_revision=11
            )
            
            print("✓ PLC verification completed")
            print(f"\nVerification Result:")
            print(f"  IP Address: {result.ip_address}")
            print(f"  Connection Successful: {result.connection_successful}")
            print(f"  Expected Project: '{result.expected_project_name}'")
            print(f"  Expected Version: {result.expected_major_revision}.{result.expected_minor_revision}")
            print(f"  Project Match: {result.project_matches}")
            print(f"  Version Match: {result.version_matches}")
            print(f"  Error Message: '{result.error_message}'")
            
        except Exception as e:
            print(f"✗ Error during verification: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plc_tag_reading():
    """Test reading individual PLC tags to see what's available"""
    print("\n" + "="*60)
    print("TESTING PLC TAG READING")
    print("="*60)
    
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    try:
        from pylogix import PLC
        
        print(f"Testing direct PLC tag reading for {plc_ip}...")
        
        with PLC() as comm:
            comm.IPAddress = plc_ip
            comm.SocketTimeout = 5.0
            
            # Test basic connection
            print("\nTesting basic connection...")
            try:
                result = comm.Read("g_Par")
                print(f"  g_Par read result: {result.Status}")
                if result.Status == "Success":
                    print(f"  g_Par value: {result.Value}")
                else:
                    print(f"  g_Par error: {result.Status}")
            except Exception as e:
                print(f"  g_Par error: {e}")
            
            # Test project tags
            print("\nTesting project information tags...")
            project_tags = [
                "Program:MainProgram.ProjectName",
                "Program:MainProgram.MajorRevision", 
                "Program:MainProgram.MinorRevision",
                "Program:MainProgram.LastLoadTime",
                "Program:MainProgram.ControllerName",
                "Program:MainProgram.ControllerType",
                "Program:MainProgram.FirmwareVersion",
                "Program:MainProgram.SerialNumber"
            ]
            
            for tag in project_tags:
                try:
                    result = comm.Read(tag)
                    print(f"  {tag}: {result.Status}")
                    if result.Status == "Success":
                        print(f"    Value: '{result.Value}'")
                    else:
                        print(f"    Error: {result.Status}")
                except Exception as e:
                    print(f"  {tag}: Exception - {e}")
            
            # Test alternative controller tags
            print("\nTesting alternative controller tags...")
            controller_tags = [
                "Controller.ProjectName",
                "Controller.MajorRevision",
                "Controller.MinorRevision", 
                "Controller.LastLoadTime",
                "Controller.Name",
                "Controller.Type",
                "Controller.FirmwareVersion",
                "Controller.SerialNumber"
            ]
            
            for tag in controller_tags:
                try:
                    result = comm.Read(tag)
                    print(f"  {tag}: {result.Status}")
                    if result.Status == "Success":
                        print(f"    Value: '{result.Value}'")
                    else:
                        print(f"    Error: {result.Status}")
                except Exception as e:
                    print(f"  {tag}: Exception - {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("PLC Verification Debug Test Suite")
    print("=" * 60)
    
    tests = [
        ("PLC Verification Debug", test_plc_verification_debug),
        ("PLC Tag Reading", test_plc_tag_reading),
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
        print("🎉 ALL TESTS COMPLETED!")
        print("\nThe PLC verification debug test has been completed.")
        print("Check the output above to understand why project information")
        print("is not being read from the PLC.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()