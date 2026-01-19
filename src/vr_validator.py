"""
DICOM Value Representation (VR) Validator
Validates DICOM field values against VR specifications from VR.xml
"""

import re
import os
from datetime import datetime


class VRValidator:
    """Validates DICOM field values against VR specifications."""
    
    # VR validation patterns and rules
    VR_RULES = {
        'AE': {'max_length': 16, 'pattern': r'^[\x20-\x7E]*$', 'description': 'Application Entity'},
        'AS': {'max_length': 4, 'pattern': r'^\d{3}[DWMY]$', 'description': 'Age String (e.g., 032Y, 012M)'},
        'CS': {'max_length': 16, 'pattern': r'^[A-Z0-9_ ]*$', 'description': 'Code String (uppercase alphanumeric)'},
        'DA': {'max_length': 8, 'pattern': r'^\d{8}$', 'description': 'Date (YYYYMMDD)'},
        'DS': {'max_length': 16, 'pattern': r'^[+-]?\d*\.?\d*$', 'description': 'Decimal String'},
        'DT': {'max_length': 26, 'pattern': r'^\d{4,14}(\.\d{1,6})?([+-]\d{4})?$', 'description': 'DateTime (YYYYMMDDHHMMSS)'},
        'FD': {'max_length': 8, 'pattern': None, 'description': 'Floating Point Double'},
        'FL': {'max_length': 4, 'pattern': None, 'description': 'Floating Point Single'},
        'IS': {'max_length': 12, 'pattern': r'^[+-]?\d+$', 'description': 'Integer String'},
        'LO': {'max_length': 64, 'pattern': r'^[\x20-\x7E]*$', 'description': 'Long String'},
        'LT': {'max_length': 10240, 'pattern': None, 'description': 'Long Text'},
        'OB': {'max_length': None, 'pattern': None, 'description': 'Other Byte'},
        'OD': {'max_length': None, 'pattern': None, 'description': 'Other Double'},
        'OF': {'max_length': None, 'pattern': None, 'description': 'Other Float'},
        'OL': {'max_length': None, 'pattern': None, 'description': 'Other Long'},
        'OW': {'max_length': None, 'pattern': None, 'description': 'Other Word'},
        'PN': {'max_length': 64, 'pattern': r'^[^\\]*(\^[^\\]*){0,4}$', 'description': 'Person Name'},
        'SH': {'max_length': 16, 'pattern': r'^[\x20-\x7E]*$', 'description': 'Short String'},
        'SL': {'max_length': 4, 'pattern': None, 'description': 'Signed Long'},
        'SQ': {'max_length': None, 'pattern': None, 'description': 'Sequence of Items'},
        'SS': {'max_length': 2, 'pattern': None, 'description': 'Signed Short'},
        'ST': {'max_length': 1024, 'pattern': None, 'description': 'Short Text'},
        'TM': {'max_length': 16, 'pattern': r'^\d{2,6}(\.\d{1,6})?$', 'description': 'Time (HHMMSS)'},
        'UC': {'max_length': None, 'pattern': None, 'description': 'Unlimited Characters'},
        'UI': {'max_length': 64, 'pattern': r'^[0-9.]+$', 'description': 'Unique Identifier'},
        'UL': {'max_length': 4, 'pattern': None, 'description': 'Unsigned Long'},
        'UN': {'max_length': None, 'pattern': None, 'description': 'Unknown'},
        'UR': {'max_length': None, 'pattern': None, 'description': 'URI/URL'},
        'US': {'max_length': 2, 'pattern': None, 'description': 'Unsigned Short'},
        'UT': {'max_length': None, 'pattern': None, 'description': 'Unlimited Text'},
    }
    
    # Common DICOM tag to VR mapping
    TAG_VR_MAP = {
        'PatientName': ('PN', '(0010,0010)'),
        'PatientID': ('LO', '(0010,0020)'),
        'PatientBirthDate': ('DA', '(0010,0030)'),
        'PatientSex': ('CS', '(0010,0040)'),
        'PatientAge': ('AS', '(0010,1010)'),
        'PatientWeight': ('DS', '(0010,1030)'),
        'PatientSize': ('DS', '(0010,1020)'),
        'PatientComments': ('LT', '(0010,4000)'),
        'StudyInstanceUID': ('UI', '(0020,000D)'),
        'StudyDate': ('DA', '(0008,0020)'),
        'StudyTime': ('TM', '(0008,0030)'),
        'StudyDescription': ('LO', '(0008,1030)'),
        'AccessionNumber': ('SH', '(0008,0050)'),
        'StudyID': ('SH', '(0020,0010)'),
        'ReferringPhysicianName': ('PN', '(0008,0090)'),
        'SeriesInstanceUID': ('UI', '(0020,000E)'),
        'SeriesNumber': ('IS', '(0020,0011)'),
        'Modality': ('CS', '(0008,0060)'),
        'SeriesDescription': ('LO', '(0008,103E)'),
        'BodyPartExamined': ('CS', '(0018,0015)'),
        'ProtocolName': ('LO', '(0018,1030)'),
        'SeriesDate': ('DA', '(0008,0021)'),
        'SeriesTime': ('TM', '(0008,0031)'),
        'PerformingPhysicianName': ('PN', '(0008,1050)'),
        'OperatorsName': ('PN', '(0008,1070)'),
        'Laterality': ('CS', '(0020,0060)'),
        'InstitutionName': ('LO', '(0008,0080)'),
    }
    
    def __init__(self, logger=None):
        """Initialize validator."""
        self.logger = logger
        self.vr_data = None
        self._load_vr_data()
    
    def _load_vr_data(self):
        """Load VR data from VR.xml using app_logic parser."""
        try:
            try:
                from .app_logic import DicomLogicHandler
            except ImportError:
                from app_logic import DicomLogicHandler
            
            # Look for VR.xml in src directory
            vr_file = os.path.join(os.path.dirname(__file__), "VR.xml")
            
            if not os.path.exists(vr_file):
                if self.logger:
                    self.logger.warning(f"VR.xml not found at: {vr_file}")
                return
            
            logic = DicomLogicHandler(self.logger)
            success, result = logic.parse_vr_xml(vr_file)
            
            if success:
                self.vr_data = result
                if self.logger:
                    self.logger.info(f"Loaded {len(result)} VR entries for validation")
            else:
                if self.logger:
                    self.logger.error(f"Failed to load VR data: {result}")
        except Exception as e:
            if self.logger:
                self.logger.exception("Error loading VR data")
    
    def validate_field(self, field_name, value, vr=None):
        """
        Validate a single field value against its VR specification.
        
        Args:
            field_name: Name of the field (e.g., 'PatientName')
            value: Value to validate
            vr: Optional VR type override
            
        Returns:
            dict: {
                'valid': bool,
                'field': str,
                'value': str,
                'vr': str,
                'tag': str,
                'errors': list of str,
                'warnings': list of str
            }
        """
        if not value or value.strip() == "":
            return {
                'valid': True,
                'field': field_name,
                'value': value,
                'vr': vr,
                'tag': '',
                'errors': [],
                'warnings': []
            }
        
        # Get VR and tag for this field
        if vr is None:
            if field_name in self.TAG_VR_MAP:
                vr, tag = self.TAG_VR_MAP[field_name]
            else:
                return {
                    'valid': True,
                    'field': field_name,
                    'value': value,
                    'vr': 'Unknown',
                    'tag': '',
                    'errors': [],
                    'warnings': [f"Unknown field '{field_name}' - cannot validate"]
                }
        else:
            tag = self.TAG_VR_MAP.get(field_name, ('', ''))[1]
        
        errors = []
        warnings = []
        
        # Get VR rules
        if vr not in self.VR_RULES:
            warnings.append(f"Unknown VR type '{vr}' for field '{field_name}'")
            return {
                'valid': True,
                'field': field_name,
                'value': value,
                'vr': vr,
                'tag': tag,
                'errors': [],
                'warnings': warnings
            }
        
        rules = self.VR_RULES[vr]
        value_str = str(value).strip()
        
        # Check length
        if rules['max_length'] is not None:
            if len(value_str) > rules['max_length']:
                errors.append(
                    f"Value too long: {len(value_str)} characters "
                    f"(max {rules['max_length']} for {vr})"
                )
        
        # Check pattern
        if rules['pattern'] is not None:
            if not re.match(rules['pattern'], value_str):
                errors.append(
                    f"Invalid format for {vr} ({rules['description']}). "
                    f"Expected pattern: {rules['pattern']}"
                )
        
        # Additional specific validations
        if vr == 'DA':  # Date validation
            try:
                datetime.strptime(value_str, '%Y%m%d')
            except ValueError:
                errors.append(f"Invalid date format. Expected YYYYMMDD, got: {value_str}")
        
        elif vr == 'TM':  # Time validation
            if not self._validate_time(value_str):
                errors.append(f"Invalid time format. Expected HHMMSS or HHMMSS.FFFFFF, got: {value_str}")
        
        elif vr == 'AS':  # Age String validation
            if len(value_str) == 4:
                try:
                    age_val = int(value_str[:3])
                    age_unit = value_str[3]
                    if age_unit not in ['D', 'W', 'M', 'Y']:
                        errors.append(f"Invalid age unit '{age_unit}'. Must be D, W, M, or Y")
                    if age_val < 0:
                        errors.append(f"Age value cannot be negative: {age_val}")
                except ValueError:
                    errors.append(f"Invalid age format: {value_str}")
        
        elif vr == 'CS':  # Code String - uppercase check
            if value_str != value_str.upper():
                warnings.append(f"Code String should be uppercase. Got: {value_str}")
        
        elif vr == 'UI':  # UID validation
            if not self._validate_uid(value_str):
                errors.append(f"Invalid UID format: {value_str}")
        
        elif vr == 'PN':  # Person Name validation
            if not self._validate_person_name(value_str):
                warnings.append(f"Person Name may have invalid format: {value_str}")
        
        return {
            'valid': len(errors) == 0,
            'field': field_name,
            'value': value_str,
            'vr': vr,
            'tag': tag,
            'errors': errors,
            'warnings': warnings
        }
    
    def validate_form_fields(self, fields_dict):
        """
        Validate multiple form fields.
        
        Args:
            fields_dict: Dictionary of {field_name: value}
            
        Returns:
            dict: {
                'valid': bool (True if no errors),
                'has_warnings': bool,
                'results': list of validation results,
                'error_count': int,
                'warning_count': int
            }
        """
        results = []
        error_count = 0
        warning_count = 0
        
        for field_name, value in fields_dict.items():
            if value is None:
                continue
                
            # Handle StringVar objects
            if hasattr(value, 'get'):
                value = value.get()
            
            result = self.validate_field(field_name, value)
            
            if result['errors']:
                error_count += len(result['errors'])
                results.append(result)
            elif result['warnings']:
                warning_count += len(result['warnings'])
                results.append(result)
        
        return {
            'valid': error_count == 0,
            'has_warnings': warning_count > 0,
            'results': results,
            'error_count': error_count,
            'warning_count': warning_count
        }
    
    def format_validation_report(self, validation_result):
        """
        Format validation results into a readable report.
        
        Args:
            validation_result: Result from validate_form_fields()
            
        Returns:
            str: Formatted report
        """
        if validation_result['error_count'] == 0 and validation_result['warning_count'] == 0:
            return "? All fields are valid"
        
        report = []
        report.append("=" * 70)
        report.append("DICOM Field Validation Report")
        report.append("=" * 70)
        report.append("")
        
        if validation_result['error_count'] > 0:
            report.append(f"? ERRORS: {validation_result['error_count']}")
            report.append("")
            
            for result in validation_result['results']:
                if result['errors']:
                    report.append(f"Field: {result['field']}")
                    report.append(f"  Tag: {result['tag']}")
                    report.append(f"  VR: {result['vr']}")
                    report.append(f"  Value: '{result['value']}'")
                    for error in result['errors']:
                        report.append(f"  ? {error}")
                    report.append("")
        
        if validation_result['warning_count'] > 0:
            report.append(f"? WARNINGS: {validation_result['warning_count']}")
            report.append("")
            
            for result in validation_result['results']:
                if result['warnings'] and not result['errors']:
                    report.append(f"Field: {result['field']}")
                    report.append(f"  Tag: {result['tag']}")
                    report.append(f"  VR: {result['vr']}")
                    report.append(f"  Value: '{result['value']}'")
                    for warning in result['warnings']:
                        report.append(f"  ? {warning}")
                    report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def _validate_time(self, time_str):
        """Validate DICOM time format (HHMMSS or HHMMSS.FFFFFF)."""
        if not time_str:
            return True
        
        # Remove fractional seconds if present
        if '.' in time_str:
            parts = time_str.split('.')
            time_str = parts[0]
            frac = parts[1]
            if not frac.isdigit() or len(frac) > 6:
                return False
        
        # Must be 2, 4, or 6 digits
        if len(time_str) not in [2, 4, 6]:
            return False
        
        if not time_str.isdigit():
            return False
        
        try:
            if len(time_str) >= 2:
                hour = int(time_str[0:2])
                if hour > 23:
                    return False
            if len(time_str) >= 4:
                minute = int(time_str[2:4])
                if minute > 59:
                    return False
            if len(time_str) >= 6:
                second = int(time_str[4:6])
                if second > 59:
                    return False
            return True
        except ValueError:
            return False
    
    def _validate_uid(self, uid_str):
        """Validate DICOM UID format."""
        if not uid_str:
            return True
        
        # Must start and end with digit
        if not uid_str[0].isdigit() or not uid_str[-1].isdigit():
            return False
        
        # Can only contain digits and dots
        if not re.match(r'^[0-9.]+$', uid_str):
            return False
        
        # No consecutive dots
        if '..' in uid_str:
            return False
        
        # Each component must be valid
        parts = uid_str.split('.')
        for part in parts:
            if not part or not part.isdigit():
                return False
            # No leading zeros except for '0'
            if len(part) > 1 and part[0] == '0':
                return False
        
        return True
    
    def _validate_person_name(self, name_str):
        """Validate DICOM person name format."""
        if not name_str:
            return True
        
        # Person name can have up to 5 components separated by ^
        # Format: FamilyName^GivenName^MiddleName^Prefix^Suffix
        components = name_str.split('^')
        if len(components) > 5:
            return False
        
        # Each component should not contain backslash
        for comp in components:
            if '\\' in comp:
                return False
        
        return True
