# DICOM Creator v0.9.0 - Release Notes

**Version**: 0.9.0  
**Release Date**: January 2025  
**Repository**: https://github.com/piotrrozentreter/dcmcreator

---

## Overview

DICOM Creator v0.9.0 introduces comprehensive **HL7 v2.x and FHIR R4 integration** for hospital system connectivity. This release enables bidirectional communication between electronic health record (EHR) systems and DICOM infrastructure through industry-standard protocols.

### Key Highlights

✓ Full HL7 v2.x message parsing (ADT, ORM messages)  
✓ FHIR R4 REST client for patient resource management  
✓ MLLP (Minimal Lower Layer Protocol) support  
✓ Automatic HL7 to DICOM metadata mapping  
✓ Enhanced documentation with proper formatting  
✓ All character encoding issues resolved  

---

## What's New

### ✨ HL7 Handler (NEW)

A new `HL7Handler` class provides comprehensive hospital integration:

#### Message Parsing
- **ADT (Admit/Discharge/Transfer)** - Extract patient demographics
  - Patient ID, name, birth date, sex
  - Address and contact information
  - Segment: PID (Patient Identification)

- **ORM (Order)** - Parse order/study information
  - Accession number
  - Study description and modality
  - Body part examined
  - Study date
  - Segments: OBR (Order), PV1 (Patient Visit)

#### Message Building
- **ORU (Observation Result)** - Build result messages from DICOM studies
  - Create standardized result messages
  - Include study and patient metadata
  - Ready for transmission to EHR systems

#### Protocol Support
- **MLLP Communication** - Minimal Lower Layer Protocol
  - TCP-based hospital standard protocol
  - Proper message framing (Start Block, End Block, CR)
  - Timeout and error handling
  - Connection management

#### Logging
- Optional logger integration
- Exception handling with detailed error reporting
- Transaction logging support

### 🔗 FHIR R4 Integration (NEW)

REST client for FHIR Patient resource management:

#### Operations
- `fhir_get_patient()` - Retrieve patient from FHIR server
- `fhir_post_patient()` - Create/update patient resource
- Automatic format conversion (FHIR ↔ DICOM)

#### Data Mapping
- FHIR Patient resource ↔ DICOM demographics
- Name, birth date, gender, contact information
- Support for multiple names and contact methods
- Address standardization

#### Features
- JSON-based communication
- Timeout support (default 10 seconds)
- Detailed error reporting
- Graceful handling of missing `requests` library

### 📖 Documentation Improvements

- ✓ Version updated from 0.7.0 to 0.9.0 throughout docs
- ✓ Fixed all placeholder characters: `??` → `•`
- ✓ Proper formatting in example scripts output
- ✓ Consistent status indicators (✓/✗ for validation)
- ✓ Enhanced examples/README.md with 7 ready-to-run scripts
- ✓ New VERSION_0.9.0_SUMMARY.md document

### 🔍 Code Quality Improvements

- Removed character encoding issues from output
- Consistent bullet point formatting in all status displays
- Better error message formatting
- Improved readability of example scripts

---

## Files Added

### New Core Module
- `src/hl7_handler.py` - HL7 v2.x parser and FHIR R4 client

### New Documentation
- `doc/VERSION_0.9.0_SUMMARY.md` - Quick release summary
- `doc/CHANGELOG_v0.9.0.md` - This file

### Updated Files (Version Numbers)
- `README.md` - v0.7.0 → v0.9.0
- `doc/README.md` - v0.6.0 → v0.9.0
- `doc/INDEX.md` - References updated to v0.9.0

### Updated Files (Character Fixes)
- `examples/README.md` - Fixed `??` and status indicators
- `examples/parallel_send.py` - Fixed `??` characters
- `examples/test_history_recording.py` - Fixed `??` characters
- `examples/test_vr_validator.py` - Fixed `??` characters
- `examples/transmission_history_examples.py` - Fixed `??` characters
- `examples/view_history.py` - Fixed `??` characters

---

## Backward Compatibility

✓ **100% Backward Compatible**

- All existing DICOM functionality preserved
- Existing server presets remain valid
- Transmission history preserved
- SSL/TLS certificates continue to work
- No database migrations needed
- No configuration file changes required

### Migration from v0.7.0

Simply upgrade - no action required:
1. Extract new version
2. Run `python src/app.py`
3. All existing data and settings preserved

---

## API Reference

### HL7 Message Parsing

```python
from src.hl7_handler import HL7Handler

handler = HL7Handler()

# Parse ADT message
patient_data = handler.parse_adt(hl7_message)
# Returns: {
#   'PatientID': '12345',
#   'PatientName': 'Smith^John',
#   'PatientBirthDate': '19800515',
#   'PatientSex': 'M',
#   'PatientAddress': '123 Main St',
#   'PatientTelephoneNumbers': '555-1234'
# }

# Parse ORM message
order_data = handler.parse_orm(hl7_message)
# Returns: {
#   'AccessionNumber': 'ACC-001',
#   'StudyDescription': 'CT CHEST',
#   'Modality': 'CT',
#   'BodyPartExamined': 'CHEST',
#   'StudyDate': '20250114'
# }
```

### ORU Message Building

```python
# Build ORU message
oru_message = handler.build_oru(patient_data, order_data)
```

### MLLP Transmission

```python
success, ack = handler.send_mllp('192.168.1.100', 4321, message)
if success:
    print(f"ACK: {ack}")
else:
    print(f"Error: {ack}")
```

### FHIR Operations

```python
# Get patient from FHIR server
success, patient = handler.fhir_get_patient('https://fhir.server/api', 'patient-id')

# Create/update patient
success, created_id = handler.fhir_post_patient(
    'https://fhir.server/api',
    patient_data
)
```

---

## Known Limitations

- HL7 parsing supports v2.x format only (v3.x not supported)
- FHIR support limited to Patient resource type
- MLLP implementation follows basic specification (no enhanced protocol)
- `requests` library required for FHIR operations (optional dependency)

---

## Installation & Setup

### Requirements

For HL7/FHIR features (optional):
```bash
pip install requests
```

All other features work without additional dependencies.

### Using HL7 Handler

```python
from src.hl7_handler import HL7Handler
from src.dcmlogger import setup_logging

logger = setup_logging()
handler = HL7Handler(logger=logger)

# Parse messages
adt = handler.parse_adt(message)
orm = handler.parse_orm(message)

# Send via MLLP
success, ack = handler.send_mllp(host, port, message)

# FHIR operations
success, patient = handler.fhir_get_patient(url, patient_id)
success, id = handler.fhir_post_patient(url, patient_data)
```

---

## Testing

All examples remain functional and enhanced:

```bash
python examples/test_connection.py
python examples/generate_test_dicoms.py
python examples/parallel_send.py
python examples/stress_test.py
python examples/view_history.py
python examples/test_history_recording.py
python examples/transmission_history_examples.py
```

---

## Fixes & Improvements

### Documentation
- ✓ Fixed malformed bullet characters in all examples
- ✓ Consistent status icons throughout
- ✓ Better error message formatting
- ✓ Proper character encoding in output

### Code Quality
- ✓ Removed placeholder characters
- ✓ Improved error handling
- ✓ Better logging integration
- ✓ Type hints for new functions

---

## Upgrade Instructions

### From v0.7.0

1. **Backup current installation** (optional but recommended)
2. **Extract v0.9.0** to the same location
3. **Run the application**:
   ```bash
   python src/app.py
   ```
4. **Verify**: All settings should be preserved

### Using New Features

1. **Import the HL7Handler**:
   ```python
   from src.hl7_handler import HL7Handler
   ```

2. **For FHIR support**, install requests:
   ```bash
   pip install requests
   ```

3. **Check examples** in `examples/` for usage patterns

---

## Breaking Changes

**None** - v0.9.0 is fully backward compatible with v0.7.0

---

## Dependencies

### Core
- Python 3.9+
- pydicom (for DICOM file handling)

### Optional
- `requests` (for FHIR operations)

---

## Troubleshooting

### HL7 Message Not Parsing
- Verify message format is HL7 v2.x
- Check segment identifiers (PID, OBR, PV1)
- Review logging output for details

### FHIR Operations Fail
- Install `requests`: `pip install requests`
- Verify FHIR server URL is correct
- Check network connectivity
- Review error message for details

### MLLP Connection Issues
- Verify host and port are correct
- Check firewall settings
- Ensure server is running
- Review timeout setting

---

## Support & Resources

- **GitHub**: https://github.com/piotrrozentreter/dcmcreator
- **Issues**: Report bugs on GitHub Issues
- **Documentation**: See `doc/` folder for comprehensive guides
- **Examples**: Check `examples/` folder for working code

---

## Contributors

Thanks to all contributors and testers who helped improve v0.9.0!

---

**DICOM Creator v0.9.0**  
**Professional DICOM Management with Hospital Integration**

Last Updated: January 2025
