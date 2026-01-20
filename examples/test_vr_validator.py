"""
Example script to test the VR Validator
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vr_validator import VRValidator


def test_validator():
    """Test the VR validator with sample data."""
    print("=" * 70)
    print("VR Validator Test")
    print("=" * 70)
    print()
    
    # Create validator
    validator = VRValidator()
    
    if validator.vr_data:
        print(f"? Loaded {len(validator.vr_data)} VR entries from VR.xml")
    else:
        print("? VR data not loaded - validation will be limited")
    print()
    
    # Test cases
    test_fields = {
        # Valid fields
        'PatientName': 'Smith^John^A^Dr^Jr',
        'PatientID': 'PAT12345',
        'PatientBirthDate': '19800515',
        'PatientSex': 'M',
        'PatientAge': '043Y',
        
        # Some invalid fields
        'StudyDate': '2024-01-15',  # Wrong format (should be YYYYMMDD)
        'StudyTime': '14:30:00',     # Wrong format (should be HHMMSS)
        'Modality': 'ct',            # Should be uppercase (CS type)
        'SeriesNumber': 'ABC',       # Should be numeric (IS type)
        'StudyDescription': 'A' * 70,  # Too long (LO max 64)
    }
    
    print("Testing individual fields:")
    print("-" * 70)
    for field_name, value in test_fields.items():
        result = validator.validate_field(field_name, value)
        
        status = "?" if result['valid'] else "?"
        print(f"{status} {field_name} = '{value}'")
        print(f"   VR: {result['vr']}, Tag: {result['tag']}")
        
        if result['errors']:
            for error in result['errors']:
                print(f"   ERROR: {error}")
        
        if result['warnings']:
            for warning in result['warnings']:
                print(f"   WARNING: {warning}")
        print()
    
    # Test batch validation
    print("=" * 70)
    print("Batch Validation Test")
    print("=" * 70)
    print()
    
    validation_result = validator.validate_form_fields(test_fields)
    
    print(f"Valid: {validation_result['valid']}")
    print(f"Errors: {validation_result['error_count']}")
    print(f"Warnings: {validation_result['warning_count']}")
    print()
    
    # Print formatted report
    report = validator.format_validation_report(validation_result)
    print(report)


if __name__ == "__main__":
    test_validator()
