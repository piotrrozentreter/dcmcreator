# DICOM Creator v0.9.0 - Quick Summary

**Version**: 0.9.0  
**Release Date**: January 2025  
**Type**: Production Release

## What Changed

### HL7 Handler Integration (NEW)
- Full HL7 v2.x parser for ADT (Admission/Discharge/Transfer) messages
- ORM (Order) message parsing with study/order information extraction
- ORU (Observation Result) message builder for DICOM study results
- MLLP (Minimal Lower Layer Protocol) communication support
- Automatic HL7 to DICOM metadata mapping
- FHIR R4 REST client integration for patient resource management
- Patient demographic sync between HL7 and DICOM systems

### Documentation Updates
- Updated all documentation to v0.9.0
- Fixed all placeholder characters (??  → •) throughout docs
- Enhanced example scripts with proper formatting
- Added HL7 handler usage examples
- Improved transmission history documentation

### Code Quality
- Removed character encoding issues
- Proper bullet point formatting in all output
- Consistent status indicator symbols (✓/✗)
- Better error message formatting

---

## Upgrade Path

**v0.7.0 to v0.9.0**: Drop-in replacement
- 100% backward compatible
- All presets and settings preserved
- New HL7 handler available for hospital integration
- No action required for existing workflows

---

## Key Features

### DICOM Management
- DICOM creation and editing
- Metadata management with validation
- Remote transmission (C-STORE)
- Connection testing and stress testing

### Hospital Integration (NEW in v0.9.0)
- HL7 ADT message parsing
- Patient demographic extraction
- Order/study information from ORM messages
- FHIR R4 patient resource support
- Secure MLLP protocol handling

### Testing & Performance
- Server presets management
- Connection quality assessment
- Parallel transmission testing
- Stress testing with configurable load
- Performance benchmarking
- Transmission history tracking

### Security
- SSL/TLS support for secure transmission
- Certificate management
- Secure MLLP communication
- Password-protected presets

---

## HL7 Handler Features

### Supported Message Types
- **ADT^A01** - Admit/Visit Notification
- **ORM^O01** - Order Messages
- **ORU^R01** - Observation Result (Unsolicited)

### Functions
- `parse_adt()` - Extract patient demographics from ADT messages
- `parse_orm()` - Extract order/study information
- `build_oru()` - Build result messages from DICOM studies
- `send_mllp()` - Send via MLLP protocol
- `fhir_get_patient()` - Retrieve FHIR patient resources
- `fhir_post_patient()` - Create/update FHIR patient resources

### Data Mappings
- HL7 PID segment → Patient demographics
- HL7 OBR segment → Study/Order information
- HL7 PV1 segment → Visit information
- DICOM metadata ↔ FHIR Patient resource

---

## Breaking Changes

None - v0.9.0 is fully backward compatible.

---

## Documentation Updates

- ✓ README.md - Version updated to 0.9.0
- ✓ All example scripts - Fixed output formatting
- ✓ All changelog files - Consistent formatting
- ✓ Examples/README.md - Proper bullet characters

---

## Known Limitations

- HL7 parser supports v2.x format (v3.x not supported)
- FHIR support limited to Patient resource
- MLLP implementation follows basic specification

---

## Migration Notes

If upgrading from v0.7.0:
1. No configuration changes needed
2. Existing transmission history preserved
3. New HL7 handler available but optional
4. All certificates and presets remain valid

---

## Support

For issues or questions:
- Check documentation in `doc/` folder
- Review example scripts in `examples/` folder
- Check GitHub issues at https://github.com/piotrrozentreter/dcmcreator

---

**Documentation Version**: 0.9.0  
**Last Updated**: January 2025
