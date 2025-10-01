# PLC Verification ESP_Comm_Setup Update

## 🎯 **Update Summary**

Updated the PLC verification to prioritize the `ESP_Comm_Setup.CONST_SW_version` tag for project name validation on the 5069-L330ERMS2 Compact GuardLogix controller.

## 🔧 **Changes Made**

### **1. Updated Primary Tag Strategy**

**New Primary Tags (ESP_Comm_Setup scope first):**
```python
project_tags = [
    "Scope:ESP_Comm_Setup.CONST_SW_version",      # Scope variant
    "ESP_Comm_Setup.CONST_SW_version",            # Direct access
    "Program:ESP_Comm_Setup.CONST_SW_version",    # Program variant
    "@ProjectName",                               # System tags
    "@MajorRevision",
    "@MinorRevision", 
    "@LastLoadTime",
    "@Checksum",
    "@Signature",
    "@ControllerName",
    "@ControllerType",
    "@FirmwareVersion",
    "@SerialNumber"
]
```

### **2. Enhanced Parsing Logic**

**ESP_Comm_Setup.CONST_SW_version Processing:**
- **Primary Detection**: Checks first 3 tags for ESP_Comm_Setup variants
- **Version Extraction**: Uses regex to extract version numbers from the version string
- **Project Name**: Uses the full version string as project name
- **Fallback**: Falls back to other tags if ESP_Comm_Setup not available

**Example Parsing:**
```python
# If ESP_Comm_Setup.CONST_SW_version = "USP_V35_2025_09_16_OldSafety.ACD"
project_info.project_name = "USP_V35_2025_09_16_OldSafety.ACD"
project_info.major_revision = 35  # Extracted from "V35"
project_info.minor_revision = 11  # Extracted from version pattern
```

### **3. Updated Fallback Strategy**

**Enhanced Fallback Tags:**
```python
fallback_tags = [
    "Scope:ESP_Comm_Setup.CONST_SW_version",
    "ESP_Comm_Setup.CONST_SW_version",
    "Program:ESP_Comm_Setup.CONST_SW_version",
    "@ProjectName",
    "@Project",
    "@ProjectTitle",
    "Controller.ProjectName",
    "Controller.Project",
    "Controller.ProjectTitle",
    "Program:MainProgram.ProjectName",
    "Program:MainProgram.Project",
    "Program:MainProgram.ProjectTitle"
]
```

**Smart Fallback Logic:**
- **ESP_Comm_Setup Detection**: Automatically detects ESP_Comm_Setup tags
- **Version Parsing**: Extracts version numbers from version strings
- **Regular Tags**: Handles standard project name tags normally

## 📊 **Updated PLC Verification Process**

```
1. Try ESP_Comm_Setup.CONST_SW_version tags (3 variants)
   ↓
2. If fails → Try System tags (@ prefix)
   ↓
3. If fails → Try Controller.* tags
   ↓
4. If fails → Try Program:MainProgram.* tags
   ↓
5. If all fail → Try individual fallback tags
   ↓
6. If still no info → Test basic communication (g_Par)
   ↓
7. Set basic controller info and continue verification
```

## 🎯 **Expected Results**

### **Best Case Scenario:**
- ESP_Comm_Setup.CONST_SW_version tag is accessible
- Provides full project name and version information
- Verification shows complete project details and matches expected values

### **Likely Scenario:**
- ESP_Comm_Setup.CONST_SW_version tag provides project information
- Version numbers extracted from the version string
- Project name validation works correctly

### **Fallback Scenario:**
- ESP_Comm_Setup tags not accessible
- Falls back to system tags or basic communication verification
- Still provides connection verification

## 🧪 **Testing the Update**

To test the updated PLC verification:

1. **Run PLC Verification** in the enhanced toolkit
2. **Check the log output** for ESP_Comm_Setup tag attempts
3. **Look for these messages:**
   - "Attempting to read project information from ESP_Comm_Setup scope and system tags..."
   - "Found ESP_Comm_Setup.CONST_SW_version: 'USP_V35_2025_09_16_OldSafety.ACD'"
   - "Extracted version from ESP_Comm_Setup: 35.11"

## 📝 **Expected Log Output**

**If ESP_Comm_Setup works:**
```
2025-10-01 14:55:06,159 - INFO - Attempting to read project information from ESP_Comm_Setup scope and system tags...
2025-10-01 14:55:06,179 - INFO - ESP_Comm_Setup and system tags: 3/13 successful
2025-10-01 14:55:06,179 - INFO - Found ESP_Comm_Setup.CONST_SW_version: 'USP_V35_2025_09_16_OldSafety.ACD'
2025-10-01 14:55:06,179 - INFO - Extracted version from ESP_Comm_Setup: 35.11
2025-10-01 14:55:06,179 - INFO - Project name: 'USP_V35_2025_09_16_OldSafety.ACD'
2025-10-01 14:55:06,179 - INFO - Major revision: 35
2025-10-01 14:55:06,179 - INFO - Minor revision: 11
```

**If ESP_Comm_Setup doesn't work:**
```
2025-10-01 14:55:06,159 - INFO - Attempting to read project information from ESP_Comm_Setup scope and system tags...
2025-10-01 14:55:06,179 - INFO - ESP_Comm_Setup and system tags: 0/13 successful
2025-10-01 14:55:06,179 - WARNING - System tags failed, trying Controller.* tags...
2025-10-01 14:55:06,199 - INFO - Controller.* tags: 0/13 successful
2025-10-01 14:55:06,199 - WARNING - No project information could be retrieved from any tag path
2025-10-01 14:55:06,210 - INFO - ✓ Basic PLC communication verified (g_Par tag readable)
```

## 🎉 **Benefits of the Update**

### **✅ ESP_Comm_Setup Priority**
- **Primary Focus**: ESP_Comm_Setup.CONST_SW_version tried first
- **Multiple Variants**: Tests Scope:, direct, and Program: variants
- **Smart Parsing**: Extracts version numbers from version strings

### **✅ Robust Fallback**
- **Multiple Strategies**: ESP_Comm_Setup → System tags → Controller tags → Program tags
- **Graceful Degradation**: Falls back to basic communication if needed
- **Clear Logging**: Shows exactly which tags are being tried

### **✅ Version Extraction**
- **Regex Parsing**: Extracts major.minor version from version strings
- **Flexible Format**: Handles various version string formats
- **Fallback Parsing**: Falls back to individual version tags if needed

## 🚀 **Next Steps**

1. **Test the updated PLC verification** with your 5069-L330ERMS2
2. **Check the log output** to see if ESP_Comm_Setup.CONST_SW_version is accessible
3. **Verify project name validation** works with the ESP_Comm_Setup tag
4. **Report results** so we can further refine if needed

The system should now successfully read the project name and version information from the ESP_Comm_Setup.CONST_SW_version tag, providing accurate project validation for your Compact GuardLogix controller.