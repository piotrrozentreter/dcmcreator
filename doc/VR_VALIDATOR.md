# DICOM VR Validator

## Overview

The VR (Value Representation) Validator is a comprehensive validation system that checks DICOM field values against their specifications defined in the DICOM standard (PS3.6 Data Dictionary).

## Features

- **Automatic VR Detection**: Maps common DICOM fields to their correct Value Representation types
- **Format Validation**: Validates data formats according to DICOM VR specifications
- **Length Checking**: Ensures field values don't exceed maximum allowed lengths
- **Pattern Matching**: Validates values against VR-specific patterns
- **User Confirmation**: Shows validation reports and asks for user confirmation when issues are found
- **Integration Points**: Validates before saving, loading, and sending DICOM files

## Supported Value Representations

The validator supports all standard DICOM VR types including:

- **AE** (Application Entity) - max 16 chars
- **AS** (Age String) - format: `###D/W/M/Y` (e.g., `032Y`, `012M`)
- **CS** (Code String) - max 16 chars, uppercase alphanumeric
- **DA** (Date) - format: `YYYYMMDD`
- **DS** (Decimal String) - max 16 chars, numeric with optional decimal
- **DT** (DateTime) - format: `YYYYMMDDHHMMSS.FFFFFF±ZZZZ`
- **IS** (Integer String) - max 12 chars, signed integer
- **LO** (Long String) - max 64 chars
- **LT** (Long Text) - max 10240 chars
- **PN** (Person Name) - max 64 chars, format: `Family^Given^Middle^Prefix^Suffix`
- **SH** (Short String) - max 16 chars
- **ST** (Short Text) - max 1024 chars
- **TM** (Time) - format: `HHMMSS.FFFFFF`
- **UI** (Unique Identifier) - max 64 chars, numeric with dots
- **And many more...**

## Usage

### In GUI Application

The validator is automatically integrated into the DICOM Creator GUI:

1. **Saving**: Validates all form fields before saving DICOM file
2. **Loading**: Validates loaded DICOM fields and warns about issues
3. **Sending**: Validates before sending to remote DICOM server

When validation issues are found:
- A detailed report is shown listing all errors and warnings
- For errors: User must confirm to continue (not recommended)
- For warnings: User is informed but can proceed normally

### Programmatic Usage

```python
from vr_validator import VRValidator

# Create validator instance
validator = VRValidator(logger=your_logger)

# Validate a single field
result = validator.validate_field('PatientName', 'Smith^John')
if not result['valid']:
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")

# Validate multiple fields
fields = {
    'PatientName': 'Smith^John',
    'PatientID': 'PAT12345',
    'PatientBirthDate': '19800515',
    'StudyDate': '20240115',
}

validation_result = validator.validate_form_fields(fields)

if not validation_result['valid']:
    report = validator.format_validation_report(validation_result)
    print(report)
```

### With Tkinter Dialog

```python
from vr_validator import VRValidator, ValidationDialog

# Validate fields
validator = VRValidator()
validation_result = validator.validate_form_fields(fields)

# Show validation dialog
continue_action = ValidationDialog.show_validation_report(
    parent=tk_window,
    validation_result=validation_result,
    validator=validator,
    action="save"  # or "send", "load"
)

if continue_action:
    # User confirmed - proceed with action
    pass
```

## Validation Rules

### Date (DA) Validation

- Format: `YYYYMMDD`
- Example: `20240115` (January 15, 2024)
- Must be exactly 8 digits
- Year must be valid (1900-2099)
- Month must be 01-12
- Day must be valid for the month

### Time (TM) Validation

- Format: `HHMMSS` or `HHMMSS.FFFFFF`
- Example: `143045` (2:30:45 PM)
- Hours: 00-23
- Minutes: 00-59
- Seconds: 00-59
- Fractional seconds optional (max 6 digits)

### Person Name (PN) Validation

- Format: `Family^Given^Middle^Prefix^Suffix`
- Example: `Smith^John^A^Dr^Jr`
- Maximum 5 components (separated by `^`)
- Each component max 64 characters
- No backslash (`\`) allowed

### Age String (AS) Validation

- Format: `###D`, `###W`, `###M`, or `###Y`
- Examples: `032Y` (32 years), `012M` (12 months), `003W` (3 weeks)
- First 3 characters must be digits
- Last character: `D` (days), `W` (weeks), `M` (months), `Y` (years)

### Code String (CS) Validation

- Maximum 16 characters
- Uppercase letters, digits, space, underscore only
- Recommended: Use uppercase consistently

### Unique Identifier (UI) Validation

- Maximum 64 characters
- Format: Numeric components separated by dots
- Example: `1.2.840.10008.5.1.4.1.1.2`
- Must start and end with digit
- No leading zeros in components (except `0` alone)
- No consecutive dots

## Validation Report Format

The validator generates detailed reports showing:

```
======================================================================
DICOM Field Validation Report
======================================================================

? ERRORS: 3

Field: StudyDate
  Tag: (0008,0020)
  VR: DA
  Value: '2024-01-15'
  ? Invalid format for DA (Date (YYYYMMDD)). Expected pattern: ^\d{8}$
  ? Invalid date format. Expected YYYYMMDD, got: 2024-01-15

Field: SeriesNumber
  Tag: (0020,0011)
  VR: IS
  Value: 'ABC'
  ? Invalid format for IS (Integer String). Expected pattern: ^[+-]?\d+$

? WARNINGS: 1

Field: Modality
  Tag: (0008,0060)
  VR: CS
  Value: 'ct'
  ? Code String should be uppercase. Got: ct

======================================================================
```

## Configuration

### Custom VR Rules

You can extend or modify VR rules by updating the `VR_RULES` dictionary:

```python
validator = VRValidator()
validator.VR_RULES['CS']['max_length'] = 32  # Increase CS max length
```

### Custom Tag-VR Mapping

Add custom field mappings:

```python
validator.TAG_VR_MAP['CustomField'] = ('LO', '(0029,1010)')
```

## Integration with VR.xml

The validator uses the VR.xml file (DICOM PS3.6 Data Dictionary) to:

1. Load all standardized DICOM data elements
2. Extract VR types for each tag
3. Identify retired elements
4. Provide comprehensive field information

The VR.xml parser is in `app_logic.py`:

```python
from app_logic import DicomLogicHandler

logic = DicomLogicHandler(logger)
success, vr_data = logic.parse_vr_xml("path/to/VR.xml")

if success:
    for item in vr_data:
        print(f"{item['tag']}: {item['name']} ({item['vr']})")
```

## Testing

Run the validation test script:

```bash
python examples/test_vr_validator.py
```

This will:
- Load VR data from VR.xml
- Test individual field validation
- Test batch validation
- Display formatted validation reports

## Error Handling

The validator gracefully handles:

- Missing VR.xml file (validation continues with built-in rules)
- Unknown field names (warns but doesn't fail)
- Unknown VR types (warns but doesn't fail)
- Empty or None values (considered valid)
- GUI dialog errors (falls back to simple yes/no confirmation)

## Best Practices

1. **Always validate before saving**: Ensures files meet DICOM standards
2. **Review warnings carefully**: They indicate potential compatibility issues
3. **Fix errors when possible**: Errors may cause rejection by PACS systems
4. **Use uppercase for CS fields**: Improves compatibility
5. **Follow date/time formats strictly**: Many systems are strict about formats
6. **Validate after loading**: Check if loaded files meet standards

## Limitations

- Does not validate against IOD (Information Object Definition) requirements
- Does not check conditional requirements (Type 1C, Type 2C)
- Does not validate sequence contents
- Does not check against specific SOP Class requirements
- Pattern matching is basic (not full DICOM regex)

## Future Enhancements

Potential improvements:

- [ ] IOD-specific validation
- [ ] Conditional requirement checking
- [ ] Sequence validation
- [ ] SOP Class validation
- [ ] Value multiplicity (VM) validation
- [ ] Configurable severity levels
- [ ] Validation profiles (strict, lenient, etc.)
- [ ] Export validation reports to file
- [ ] Batch file validation

## Related Files

- `vr_validator.py` - Main validator implementation
- `app_logic.py` - VR.xml parser
- `appgui.py` - GUI integration
- `VR.xml` - DICOM PS3.6 Data Dictionary

## References

- [DICOM Standard PS3.6](http://dicom.nema.org/medical/dicom/current/output/chtml/part06/PS3.6.html) - Data Dictionary
- [DICOM Standard PS3.5](http://dicom.nema.org/medical/dicom/current/output/chtml/part05/PS3.5.html) - Data Structures and Encoding
- [DICOM VR Definitions](http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html)
