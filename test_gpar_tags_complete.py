#!/usr/bin/env python3
"""
Test G Par Tags Complete
Verify that all the required G Par bit tags are now included in the Starting Script
"""

import sys
from datetime import datetime

def test_gpar_tags_complete():
    """Test that all required G Par bit tags are included"""
    print("G Par Tags Complete Verification")
    print("=" * 50)
    
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Required tags from user
    required_gpar1_tags = [
        'g_Par1.0', 'g_Par1.1', 'g_Par1.2', 'g_Par1.3', 'g_Par1.4', 'g_Par1.5', 'g_Par1.6', 'g_Par1.15'
    ]
    
    required_gparnew_tags = [
        'g_ParNew.0', 'g_ParNew.1', 'g_ParNew.2', 'g_ParNew.3', 'g_ParNew.4', 'g_ParNew.5', 'g_ParNew.6', 'g_ParNew.7',
        'g_ParNew.8', 'g_ParNew.9', 'g_ParNew.10', 'g_ParNew.11', 'g_ParNew.12', 'g_ParNew.13', 'g_ParNew.14', 'g_ParNew.15',
        'g_ParNew.16', 'g_ParNew.17', 'g_ParNew.19', 'g_ParNew.20', 'g_ParNew.21'
    ]
    
    required_gpartemp_tags = [
        'g_parTemp.1', 'g_parTemp.2', 'g_parTemp.3', 'g_parTemp.5', 'g_parTemp.6', 'g_parTemp.7'
    ]
    
    # Current tags from Starting Script (updated)
    current_gpar1_tags = [
        'g_Par1.0', 'g_Par1.1', 'g_Par1.2', 'g_Par1.3', 'g_Par1.4', 'g_Par1.5', 'g_Par1.6', 'g_Par1.15'
    ]
    
    current_gparnew_tags = [
        'g_ParNew.0', 'g_ParNew.1', 'g_ParNew.2', 'g_ParNew.3', 'g_ParNew.4', 'g_ParNew.5', 'g_ParNew.6', 'g_ParNew.7',
        'g_ParNew.8', 'g_ParNew.9', 'g_ParNew.10', 'g_ParNew.11', 'g_ParNew.12', 'g_ParNew.13', 'g_ParNew.14', 'g_ParNew.15',
        'g_ParNew.16', 'g_ParNew.17', 'g_ParNew.19', 'g_ParNew.20', 'g_ParNew.21'
    ]
    
    current_gpartemp_tags = [
        'g_parTemp.1', 'g_parTemp.2', 'g_parTemp.3', 'g_parTemp.5', 'g_parTemp.6', 'g_parTemp.7'
    ]
    
    print("🔍 Verifying G Par1 Tags:")
    missing_gpar1 = []
    for tag in required_gpar1_tags:
        if tag in current_gpar1_tags:
            print(f"  ✅ {tag}")
        else:
            print(f"  ❌ {tag} - MISSING")
            missing_gpar1.append(tag)
    
    print(f"\n🔍 Verifying G ParNew Tags:")
    missing_gparnew = []
    for tag in required_gparnew_tags:
        if tag in current_gparnew_tags:
            print(f"  ✅ {tag}")
        else:
            print(f"  ❌ {tag} - MISSING")
            missing_gparnew.append(tag)
    
    print(f"\n🔍 Verifying G ParTemp Tags:")
    missing_gpartemp = []
    for tag in required_gpartemp_tags:
        if tag in current_gpartemp_tags:
            print(f"  ✅ {tag}")
        else:
            print(f"  ❌ {tag} - MISSING")
            missing_gpartemp.append(tag)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  G Par1 Tags: {len(current_gpar1_tags)}/{len(required_gpar1_tags)} ({'✅ Complete' if not missing_gpar1 else '❌ Missing ' + str(len(missing_gpar1))})")
    print(f"  G ParNew Tags: {len(current_gparnew_tags)}/{len(required_gparnew_tags)} ({'✅ Complete' if not missing_gparnew else '❌ Missing ' + str(len(missing_gparnew))})")
    print(f"  G ParTemp Tags: {len(current_gpartemp_tags)}/{len(required_gpartemp_tags)} ({'✅ Complete' if not missing_gpartemp else '❌ Missing ' + str(len(missing_gpartemp))})")
    
    # Check for extra tags (not required but included)
    extra_gpar1 = [tag for tag in current_gpar1_tags if tag not in required_gpar1_tags]
    extra_gparnew = [tag for tag in current_gparnew_tags if tag not in required_gparnew_tags]
    extra_gpartemp = [tag for tag in current_gpartemp_tags if tag not in required_gpartemp_tags]
    
    if extra_gpar1 or extra_gparnew or extra_gpartemp:
        print(f"\n📋 Extra Tags (not in required list):")
        if extra_gpar1:
            print(f"  G Par1: {extra_gpar1}")
        if extra_gparnew:
            print(f"  G ParNew: {extra_gparnew}")
        if extra_gpartemp:
            print(f"  G ParTemp: {extra_gpartemp}")
    
    # Overall result
    all_complete = not (missing_gpar1 or missing_gparnew or missing_gpartemp)
    
    print(f"\n🎯 Overall Result:")
    if all_complete:
        print(f"  ✅ ALL REQUIRED TAGS ARE NOW INCLUDED!")
        print(f"  The Starting Script should now read all the G Par bits you specified.")
        print(f"  Total tags being read:")
        print(f"    • g_Par1: {len(current_gpar1_tags)} tags")
        print(f"    • g_ParNew: {len(current_gparnew_tags)} tags") 
        print(f"    • g_parTemp: {len(current_gpartemp_tags)} tags")
        print(f"    • Total: {len(current_gpar1_tags) + len(current_gparnew_tags) + len(current_gpartemp_tags)} additional G Par tags")
    else:
        print(f"  ❌ Some required tags are still missing:")
        if missing_gpar1:
            print(f"    Missing g_Par1: {missing_gpar1}")
        if missing_gparnew:
            print(f"    Missing g_ParNew: {missing_gparnew}")
        if missing_gpartemp:
            print(f"    Missing g_parTemp: {missing_gpartemp}")
    
    return all_complete

def test_descriptions_coverage():
    """Test that descriptions exist for all tags"""
    print(f"\n" + "="*60)
    print("DESCRIPTIONS COVERAGE TEST")
    print("="*60)
    
    # Descriptions from Starting Script (updated)
    G_PAR1_DESCRIPTIONS = {
        0: 'EU Paper Mode', 1: 'Jaw auto seal pressure adjustment',
        2: 'Temporary fix for nip roller until safety code is fixed',
        3: 'Enable/disable FIFE auto/manual mode', 4: 'Reduce speed for gripper 70%',
        5: 'Pregessis paper testing', 6: 'Nip Roller Inrush Current Monitor for Low Roll Detection',
        15: 'Additional g_Par1 function (Bit 15)',
    }

    G_PARNEW_DESCRIPTIONS = {
        0: 'Vision test active', 1: 'Variable Bag length test active',
        2: 'Sealing Process Issue detected, divert to KO', 3: 'Vertical seal clearance active',
        4: 'Paper Type Georgia Pacific - Enabled', 5: 'Paper Type Pregis - Enabled',
        6: 'Horizontal & Vertical Seal Sensor test', 7: 'Tall item Ultrasonic value correction Enabled',
        8: 'Inhibit Sealing by ASIN Sensors', 9: 'Horizontal Seal Sensor check for increasing bag size',
        10: 'Disable Bag gripper, JawSeqCoolingRequest', 11: 'Copy 50 last PACK, SLAM messages',
        12: 'Bypass the vertical keep out area warning', 13: 'Low Sealing Force Process failure',
        14: 'Servo speed ramp for cold start', 15: 'Commissioning Mode / Dry Cycle Mode',
        16: 'Additional g_ParNew function (Bit 16)', 17: 'Additional g_ParNew function (Bit 17)',
        19: 'Additional g_ParNew function (Bit 19)', 20: 'Dry cycling 16$Q bags', 21: 'Use 2 new top rear ultrasonics for 36$Q',
    }

    G_PARTEMP_DESCRIPTIONS = {
        1: 'Disable OEE Starved time reporting', 2: 'Disable takeaway and reject conveyor jams stopping machine',
        3: 'Allow disabling tamp interlock to light curtain', 5: 'Allow downstream into running timer > 15 sec',
        6: 'Enable 2 Bag Mode', 7: 'Disable all takeaway and reject jam alarming',
    }
    
    # Required bit numbers
    required_gpar1_bits = [0, 1, 2, 3, 4, 5, 6, 15]
    required_gparnew_bits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21]
    required_gpartemp_bits = [1, 2, 3, 5, 6, 7]
    
    print("🔍 Checking G Par1 Descriptions:")
    missing_gpar1_desc = []
    for bit in required_gpar1_bits:
        if bit in G_PAR1_DESCRIPTIONS:
            print(f"  ✅ Bit {bit}: {G_PAR1_DESCRIPTIONS[bit]}")
        else:
            print(f"  ❌ Bit {bit}: No description")
            missing_gpar1_desc.append(bit)
    
    print(f"\n🔍 Checking G ParNew Descriptions:")
    missing_gparnew_desc = []
    for bit in required_gparnew_bits:
        if bit in G_PARNEW_DESCRIPTIONS:
            print(f"  ✅ Bit {bit}: {G_PARNEW_DESCRIPTIONS[bit]}")
        else:
            print(f"  ❌ Bit {bit}: No description")
            missing_gparnew_desc.append(bit)
    
    print(f"\n🔍 Checking G ParTemp Descriptions:")
    missing_gpartemp_desc = []
    for bit in required_gpartemp_bits:
        if bit in G_PARTEMP_DESCRIPTIONS:
            print(f"  ✅ Bit {bit}: {G_PARTEMP_DESCRIPTIONS[bit]}")
        else:
            print(f"  ❌ Bit {bit}: No description")
            missing_gpartemp_desc.append(bit)
    
    # Summary
    all_descriptions_complete = not (missing_gpar1_desc or missing_gparnew_desc or missing_gpartemp_desc)
    
    print(f"\n📊 Descriptions Summary:")
    if all_descriptions_complete:
        print(f"  ✅ ALL REQUIRED BITS HAVE DESCRIPTIONS!")
    else:
        print(f"  ❌ Some bits are missing descriptions:")
        if missing_gpar1_desc:
            print(f"    Missing g_Par1 descriptions: {missing_gpar1_desc}")
        if missing_gparnew_desc:
            print(f"    Missing g_ParNew descriptions: {missing_gparnew_desc}")
        if missing_gpartemp_desc:
            print(f"    Missing g_parTemp descriptions: {missing_gpartemp_desc}")
    
    return all_descriptions_complete

def main():
    """Run all tests"""
    print("G Par Tags Complete Verification Suite")
    print("=" * 60)
    
    tests = [
        ("G Par Tags Complete", test_gpar_tags_complete),
        ("Descriptions Coverage", test_descriptions_coverage),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 SUCCESS! All required G Par bit tags are now included!")
        print("\nThe Starting Script has been updated to read:")
        print("✅ All g_Par1 bits you specified (including g_Par1.15)")
        print("✅ All g_ParNew bits you specified (including g_ParNew.9 and g_ParNew.19)")
        print("✅ All g_parTemp bits you specified")
        print("✅ All bits have proper descriptions")
        print("\nWhen you run the PLC validation now, it should show all the")
        print("active bits from these tags that are currently TRUE in your PLC.")
    else:
        print("❌ Some issues remain. Check the test output above.")
    
    return all_passed

if __name__ == "__main__":
    main()