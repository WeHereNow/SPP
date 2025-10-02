#!/usr/bin/env python3
"""
PLC Tags Diagnostic Test
Test what tags are actually available on the 5069-L330ERMS2 Compact GuardLogix
"""

import sys
from datetime import datetime

def test_plc_tags_diagnostic():
    """Test what tags are actually available on the PLC"""
    print("PLC Tags Diagnostic Test")
    print("=" * 50)
    
    # Get PLC IP from command line or use default
    plc_ip = sys.argv[1] if len(sys.argv) > 1 else "11.200.0.10"
    
    print(f"Testing PLC tags for: {plc_ip}")
    print(f"Controller: 5069-L330ERMS2 Compact GuardLogix")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from pylogix import PLC
        
        print("Connecting to PLC...")
        
        with PLC() as comm:
            comm.IPAddress = plc_ip
            comm.SocketTimeout = 5.0
            
            # Test basic connection first
            print("\n1. Testing basic connection...")
            try:
                result = comm.Read("g_Par")
                print(f"   g_Par: {result.Status}")
                if result.Status == "Success":
                    print(f"   ✓ Connection successful! g_Par = {result.Value}")
                else:
                    print(f"   ✗ Connection failed: {result.Status}")
                    return False
            except Exception as e:
                print(f"   ✗ Connection error: {e}")
                return False
            
            # Test various tag paths systematically
            print("\n2. Testing Controller.* tags...")
            controller_tags = [
                "Controller.ProjectName",
                "Controller.Project",
                "Controller.ProjectTitle",
                "Controller.Name",
                "Controller.HostName",
                "Controller.Type",
                "Controller.ProcessorType",
                "Controller.Model",
                "Controller.MajorRevision",
                "Controller.MinorRevision",
                "Controller.Version",
                "Controller.FirmwareVersion",
                "Controller.SerialNumber",
                "Controller.LastLoadTime",
                "Controller.Checksum",
                "Controller.Signature"
            ]
            
            successful_controller_tags = []
            for tag in controller_tags:
                try:
                    result = comm.Read(tag)
                    print(f"   {tag}: {result.Status}")
                    if result.Status == "Success":
                        print(f"      Value: '{result.Value}'")
                        successful_controller_tags.append(tag)
                    else:
                        print(f"      Error: {result.Status}")
                except Exception as e:
                    print(f"   {tag}: Exception - {e}")
            
            print(f"\n   Successful Controller.* tags: {len(successful_controller_tags)}/{len(controller_tags)}")
            
            # Test Program:MainProgram.* tags
            print("\n3. Testing Program:MainProgram.* tags...")
            program_tags = [
                "Program:MainProgram.ProjectName",
                "Program:MainProgram.Project",
                "Program:MainProgram.ProjectTitle",
                "Program:MainProgram.ControllerName",
                "Program:MainProgram.ControllerType",
                "Program:MainProgram.MajorRevision",
                "Program:MainProgram.MinorRevision",
                "Program:MainProgram.FirmwareVersion",
                "Program:MainProgram.SerialNumber",
                "Program:MainProgram.LastLoadTime",
                "Program:MainProgram.Checksum",
                "Program:MainProgram.Signature"
            ]
            
            successful_program_tags = []
            for tag in program_tags:
                try:
                    result = comm.Read(tag)
                    print(f"   {tag}: {result.Status}")
                    if result.Status == "Success":
                        print(f"      Value: '{result.Value}'")
                        successful_program_tags.append(tag)
                    else:
                        print(f"      Error: {result.Status}")
                except Exception as e:
                    print(f"   {tag}: Exception - {e}")
            
            print(f"\n   Successful Program:MainProgram.* tags: {len(successful_program_tags)}/{len(program_tags)}")
            
            # Test other possible tag paths
            print("\n4. Testing other possible tag paths...")
            other_tags = [
                "System.ProjectName",
                "System.ControllerName",
                "System.ControllerType",
                "System.FirmwareVersion",
                "System.SerialNumber",
                "Project.ProjectName",
                "Project.ControllerName",
                "Project.Version",
                "MainProgram.ProjectName",
                "MainProgram.ControllerName",
                "MainProgram.Version",
                "g_Par",  # We know this works
                "g_Par.0",  # Test individual bit
                "g_Par1",
                "g_ParNew"
            ]
            
            successful_other_tags = []
            for tag in other_tags:
                try:
                    result = comm.Read(tag)
                    print(f"   {tag}: {result.Status}")
                    if result.Status == "Success":
                        print(f"      Value: '{result.Value}'")
                        successful_other_tags.append(tag)
                    else:
                        print(f"      Error: {result.Status}")
                except Exception as e:
                    print(f"   {tag}: Exception - {e}")
            
            print(f"\n   Successful other tags: {len(successful_other_tags)}/{len(other_tags)}")
            
            # Test if we can get controller properties through other means
            print("\n5. Testing controller properties...")
            try:
                # Try to get controller properties
                result = comm.GetPLCTime()
                print(f"   GetPLCTime: {result.Status}")
                if result.Status == "Success":
                    print(f"      PLC Time: {result.Value}")
            except Exception as e:
                print(f"   GetPLCTime: Exception - {e}")
            
            # Summary
            print("\n" + "="*60)
            print("DIAGNOSTIC SUMMARY")
            print("="*60)
            print(f"Total successful Controller.* tags: {len(successful_controller_tags)}")
            print(f"Total successful Program:MainProgram.* tags: {len(successful_program_tags)}")
            print(f"Total successful other tags: {len(successful_other_tags)}")
            
            if successful_controller_tags:
                print(f"\nWorking Controller.* tags:")
                for tag in successful_controller_tags:
                    print(f"  ✓ {tag}")
            
            if successful_program_tags:
                print(f"\nWorking Program:MainProgram.* tags:")
                for tag in successful_program_tags:
                    print(f"  ✓ {tag}")
            
            if successful_other_tags:
                print(f"\nWorking other tags:")
                for tag in successful_other_tags:
                    print(f"  ✓ {tag}")
            
            if not successful_controller_tags and not successful_program_tags:
                print("\n⚠️  No project information tags are accessible!")
                print("This suggests that either:")
                print("1. The PLC doesn't expose project information through these tag paths")
                print("2. The tags are protected or not accessible via pylogix")
                print("3. The PLC firmware version doesn't support these tags")
                print("4. The tags exist but with different names/paths")
            
            return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the diagnostic test"""
    print("PLC Tags Diagnostic Test Suite")
    print("=" * 60)
    
    result = test_plc_tags_diagnostic()
    
    print("\n" + "=" * 60)
    if result:
        print("🎉 DIAGNOSTIC COMPLETED!")
        print("\nThe diagnostic test has been completed.")
        print("Check the output above to see which tags are actually")
        print("available on your 5069-L330ERMS2 Compact GuardLogix.")
        print("\nThis information will help us fix the PLC verification")
        print("to use the correct tag paths for your controller.")
    else:
        print("❌ Diagnostic test failed.")
        print("Please check the connection and try again.")
    
    return result

if __name__ == "__main__":
    main()