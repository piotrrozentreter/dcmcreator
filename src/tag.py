"""
DICOM Tag Reader Module

Provides functionality to read and extract all DICOM tags from a dataset,
including private tags.
"""

try:
    import pydicom
    from pydicom.dataelem import DataElement
except ImportError:
    pydicom = None
    DataElement = None


def get_all_tags_from_file(filepath, logger=None):
    """
    Read all DICOM tags from a file.
    
    Args:
        filepath: Path to DICOM file
        logger: Optional logger instance
        
    Returns:
        tuple: (success: bool, result: list or error_msg: str)
               If success, result is list of tag dictionaries
               If failure, result is error message string
    """
    if pydicom is None:
        return False, "pydicom is not available"
    
    try:
        # Read DICOM file
        ds = pydicom.dcmread(filepath, force=True)
        
        # Extract all tags
        tags = extract_tags_from_dataset(ds, logger=logger)
        
        return True, tags
    
    except Exception as e:
        error_msg = f"Failed to read DICOM file: {e}"
        if logger:
            logger.exception(f"Error reading DICOM file: {filepath}")
        return False, error_msg


def get_all_tags_from_dataset(ds, logger=None):
    """
    Extract all tags from a DICOM dataset.
    
    Args:
        ds: pydicom.Dataset instance
        logger: Optional logger instance
        
    Returns:
        tuple: (success: bool, result: list or error_msg: str)
    """
    if ds is None:
        return False, "No dataset provided"
    
    try:
        tags = extract_tags_from_dataset(ds, logger=logger)
        return True, tags
    
    except Exception as e:
        error_msg = f"Failed to extract tags: {e}"
        if logger:
            logger.exception("Error extracting tags from dataset")
        return False, error_msg


def extract_tags_from_dataset(ds, logger=None, prefix=""):
    """
    Recursively extract all tags from a dataset, including sequences.
    
    Args:
        ds: pydicom.Dataset instance
        logger: Optional logger instance
        prefix: String prefix for nested sequences (for display hierarchy)
        
    Returns:
        list: List of dictionaries with tag information
    """
    tags = []
    
    for elem in ds:
        try:
            tag_dict = extract_tag_info(elem, prefix=prefix)
            tags.append(tag_dict)
            
            # If this is a sequence, recursively extract tags from items
            if elem.VR == "SQ":
                for i, item in enumerate(elem.value):
                    nested_prefix = f"{prefix}  [{i}] "
                    nested_tags = extract_tags_from_dataset(item, logger=logger, prefix=nested_prefix)
                    tags.extend(nested_tags)
        
        except Exception as e:
            if logger:
                logger.warning(f"Error extracting tag {elem.tag}: {e}")
            # Add error entry
            tags.append({
                'tag': str(elem.tag),
                'name': 'Error',
                'vr': '??',
                'vm': '?',
                'value': f'<Error: {e}>',
                'is_private': elem.tag.is_private,
                'prefix': prefix
            })
    
    return tags


def extract_tag_info(elem, prefix=""):
    """
    Extract information from a single data element.
    
    Args:
        elem: pydicom.DataElement instance
        prefix: String prefix for display hierarchy
        
    Returns:
        dict: Dictionary with tag information
    """
    # Get tag number
    tag_str = f"({elem.tag.group:04X},{elem.tag.element:04X})"
    
    # Get tag name
    try:
        name = elem.name if hasattr(elem, 'name') else elem.description()
    except Exception:
        name = "Unknown"
    
    # Get VR
    vr = elem.VR if elem.VR else "??"
    
    # Get VM (Value Multiplicity)
    try:
        if hasattr(elem, 'VM'):
            vm = str(elem.VM)
        else:
            vm = "1"
    except Exception:
        vm = "?"
    
    # Get value
    try:
        if vr == "SQ":
            # For sequences, show number of items
            value = f"[Sequence with {len(elem.value)} item(s)]"
        elif elem.value is None or elem.value == '':
            value = "<empty>"
        else:
            # Convert value to string, truncate if too long
            value_str = str(elem.value)
            if len(value_str) > 200:
                value_str = value_str[:200] + "..."
            value = value_str
    except Exception as e:
        value = f"<Error reading value: {e}>"
    
    # Check if private tag
    is_private = elem.tag.is_private
    
    return {
        'tag': tag_str,
        'name': name,
        'vr': vr,
        'vm': vm,
        'value': value,
        'is_private': is_private,
        'prefix': prefix
    }


def format_tag_list(tags, include_private=True):
    """
    Format tag list as readable text.
    
    Args:
        tags: List of tag dictionaries
        include_private: Whether to include private tags
        
    Returns:
        str: Formatted tag list
    """
    lines = []
    lines.append("DICOM Tags")
    lines.append("=" * 80)
    lines.append("")
    
    for tag_dict in tags:
        if not include_private and tag_dict['is_private']:
            continue
        
        prefix = tag_dict.get('prefix', '')
        tag = tag_dict['tag']
        name = tag_dict['name']
        vr = tag_dict['vr']
        vm = tag_dict['vm']
        value = tag_dict['value']
        is_private = tag_dict['is_private']
        
        private_marker = "[PRIVATE] " if is_private else ""
        
        lines.append(f"{prefix}{private_marker}{tag} {name} ({vr}, VM={vm})")
        lines.append(f"{prefix}  Value: {value}")
        lines.append("")
    
    return "\n".join(lines)


def get_tag_statistics(tags):
    """
    Get statistics about tags.
    
    Args:
        tags: List of tag dictionaries
        
    Returns:
        dict: Statistics dictionary
    """
    total = len(tags)
    private = sum(1 for t in tags if t['is_private'])
    public = total - private
    
    # Count by VR
    vr_counts = {}
    for tag in tags:
        vr = tag['vr']
        vr_counts[vr] = vr_counts.get(vr, 0) + 1
    
    return {
        'total': total,
        'public': public,
        'private': private,
        'vr_counts': vr_counts
    }
