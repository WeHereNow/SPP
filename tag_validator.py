#!/usr/bin/env python3
"""
Tag Validator - Test individual PLC tags to identify which ones are causing issues
"""

import sys
import time
from typing import List, Dict, Any

# Try to import pylogix
try:
    from pylogix import PLC
    PYLOGIX_AVAILABLE = True
except ImportError:
    PYLOGIX_AVAILABLE = False
    print("ERROR: pylogix is not installed. Please run: pip install pylogix")
    sys.exit(1)

# Tag definitions from the original script
G_PAR_TAGS = ['g_Par', 'g_Par1', 'g_ParNew', 'g_parTemp']

SAFETY_TAGS = [
    'Program:SafetyProgram.SafetyIO.In.ESTOP_Relay1Feedback',
    'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelA',
    'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelB',
    'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelA',
    'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelB',
    'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelA',
    'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelB',
    'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelA',
    'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelB',
]

INTERLOCK_TAG = 'IO.PLC.In.DownstreamConveyorEnabled'

VERIFICATION_TAGS = [
    'H1_PACK_WMS_Connected',
    'H2_SLAM1_WMS_Connected',
    'NTP_Connected'
]

def test_single_tag(comm: PLC, tag: str) -> Dict[str, Any]:
    """Test a single tag and return detailed results"""
    result = {
        'tag': tag,
        'status': 'Unknown',
        'value': None,
        'error': None,
        'success': False
    }
    
    try:
        print(f"Testing tag: {tag}")
        response = comm.Read(tag)
        
        if response.Status == "Success":
            result['status'] = 'Success'
            result['value'] = response.Value
            result['success'] = True
            print(f"  ✓ SUCCESS: {response.Value}")
        else:
            result['status'] = 'Failed'
            result['error'] = response.Status
            if hasattr(response, 'StatusExtended'):
                result['error'] += f" ({response.StatusExtended})"
            print(f"  ✗ FAILED: {result['error']}")
            
    except Exception as e:
        result['status'] = 'Exception'
        result['error'] = str(e)
        print(f"  ✗ EXCEPTION: {e}")
    
    return result

def test_tag_group(comm: PLC, tags: List[str], group_name: str) -> List[Dict[str, Any]]:
    """Test a group of tags and return results"""
    print(f"\n{'='*60}")
    print(f"TESTING {group_name.upper()}")
    print(f"{'='*60}")
    
    results = []
    for tag in tags:
        result = test_single_tag(comm, tag)
        results.append(result)
        time.sleep(0.1)  # Small delay between reads
    
    return results

def test_multiple_tags(comm: PLC, tags: List[str], group_name: str) -> Dict[str, Any]:
    """Test reading multiple tags at once"""
    print(f"\n{'='*60}")
    print(f"TESTING {group_name.upper()} - MULTIPLE READ")
    print(f"{'='*60}")
    
    try:
        print(f"Reading {len(tags)} tags at once...")
        responses = comm.Read(tags)
        
        if isinstance(responses, list):
            print(f"  ✓ SUCCESS: Read {len(responses)} tags")
            for i, (tag, response) in enumerate(zip(tags, responses)):
                if response.Status == "Success":
                    print(f"    {i+1}. {tag}: {response.Value}")
                else:
                    print(f"    {i+1}. {tag}: FAILED - {response.Status}")
        else:
            print(f"  ✗ FAILED: Expected list, got {type(responses)}")
            
    except Exception as e:
        print(f"  ✗ EXCEPTION: {e}")
        return {'success': False, 'error': str(e)}
    
    return {'success': True, 'responses': responses}

def main():
    """Main validation function"""
    if len(sys.argv) != 2:
        print("Usage: python tag_validator.py <PLC_IP>")
        print("Example: python tag_validator.py 11.200.0.10")
        sys.exit(1)
    
    plc_ip = sys.argv[1]
    print(f"PLC Tag Validator")
    print(f"Target PLC: {plc_ip}")
    print(f"pylogix available: {PYLOGIX_AVAILABLE}")
    
    # Test connection first
    print(f"\n{'='*60}")
    print("TESTING PLC CONNECTION")
    print(f"{'='*60}")
    
    try:
        with PLC() as comm:
            comm.IPAddress = plc_ip
            comm.SocketTimeout = 5
            
            # Test basic connection with a simple tag
            print("Testing basic connection...")
            test_result = comm.Read("g_Par")
            if test_result.Status == "Success":
                print(f"  ✓ Connection successful! g_Par = {test_result.Value}")
            else:
                print(f"  ✗ Connection failed: {test_result.Status}")
                if hasattr(test_result, 'StatusExtended'):
                    print(f"    Extended status: {test_result.StatusExtended}")
                return
            
            # Test individual tags
            gpar_results = test_tag_group(comm, G_PAR_TAGS, "Parameter Tags")
            safety_results = test_tag_group(comm, SAFETY_TAGS, "Safety Tags")
            interlock_results = test_tag_group(comm, [INTERLOCK_TAG], "Interlock Tag")
            verification_results = test_tag_group(comm, VERIFICATION_TAGS, "Verification Tags")
            
            # Test multiple reads
            test_multiple_tags(comm, G_PAR_TAGS, "Parameter Tags")
            test_multiple_tags(comm, SAFETY_TAGS, "Safety Tags")
            test_multiple_tags(comm, VERIFICATION_TAGS, "Verification Tags")
            
            # Summary
            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}")
            
            all_results = gpar_results + safety_results + interlock_results + verification_results
            successful = [r for r in all_results if r['success']]
            failed = [r for r in all_results if not r['success']]
            
            print(f"Total tags tested: {len(all_results)}")
            print(f"Successful: {len(successful)}")
            print(f"Failed: {len(failed)}")
            
            if failed:
                print(f"\nFAILED TAGS:")
                for result in failed:
                    print(f"  - {result['tag']}: {result['error']}")
            
            if successful:
                print(f"\nSUCCESSFUL TAGS:")
                for result in successful:
                    print(f"  - {result['tag']}: {result['value']}")
                    
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        return

if __name__ == "__main__":
    main()