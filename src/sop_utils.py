"""
SOP Class utilities for friendly name lookup and caching.

Provides centralized utilities for mapping DICOM SOP Class UIDs to human-readable names,
with caching for performance across multiple modules.
"""
from typing import Dict

_sop_class_cache: Dict[str, str] = {}


def load_sop_classes() -> Dict[str, str]:
    """Load registered SOP Class UIDs and cache them.
    Returns a dictionary mapping SOP UID -> friendly name.
    Tries multiple methods to support different pynetdicom versions.
    """
    global _sop_class_cache
    
    if _sop_class_cache:
        return _sop_class_cache
    
    # Method 1: Try UID_dictionary (pynetdicom <3.0)
    try:
        from pynetdicom.uid import UID_dictionary
        for uid, (name, keyword, is_retired) in UID_dictionary.items():
            _sop_class_cache[uid] = name
        if _sop_class_cache:
            return _sop_class_cache
    except Exception:
        pass
    
    # Method 2: Try UID class and STANDARD_UID_DICT (pynetdicom 3.0+)
    try:
        from pynetdicom._uid_dict import STANDARD_UID_DICT
        for uid, info in STANDARD_UID_DICT.items():
            # info can be a tuple: (name, is_retired, ...)
            if isinstance(info, (tuple, list)) and len(info) > 0:
                name = info[0]
            else:
                name = str(info)
            _sop_class_cache[uid] = name
        if _sop_class_cache:
            return _sop_class_cache
    except Exception:
        pass
    
    # Method 3: Use sop_class module (pynetdicom 3.x - SOP classes ARE UIDs)
    try:
        from pynetdicom import sop_class
        from pynetdicom.sop_class import SOPClass
        import inspect
        for attr in dir(sop_class):
            if not attr.startswith('_') and not inspect.isclass(getattr(sop_class, attr, None)):
                obj = getattr(sop_class, attr)
                # In pynetdicom 3.x, SOP class instances are UID objects
                if isinstance(obj, SOPClass):
                    try:
                        uid_str = str(obj)
                        # Use the attribute name as the friendly name, clean it up
                        sop_class_name = attr.replace('_', ' ')
                        _sop_class_cache[uid_str] = sop_class_name
                    except Exception:
                        pass
        if _sop_class_cache:
            return _sop_class_cache
    except Exception:
        pass
    
    # Method 4: Build minimal dictionary from well-known SOPs
    # (fallback when pynetdicom is unavailable or has issues)
    try:
        _sop_class_cache.update({
            '1.2.840.10008.5.1.4.1.1.2': 'CT Image Storage',
            '1.2.840.10008.5.1.4.1.1.7': 'Secondary Capture Image Storage',
            '1.2.840.10008.5.1.4.1.1.1': 'CR Image Storage',
            '1.2.840.10008.1.1': 'Verification SOP Class',
            '1.2.840.10008.5.1.4.1.1.4': 'MR Image Storage',
            '1.2.840.10008.5.1.4.1.1.3': 'Ultrasound Image Storage',
            '1.2.840.10008.5.1.4.1.1.3.1': 'Ultrasound Multiframe Image Storage',
            '1.2.840.10008.5.1.4.1.1.6': 'Ultrasound Image Storage',
            '1.2.840.10008.5.1.4.1.1.66.4': 'Segmentation Storage',
            '1.2.840.10008.5.1.1.1': 'CR Image Storage',
        })
    except Exception:
        pass
    
    return _sop_class_cache


def get_sop_name(sop_uid: str) -> str:
    """Get the friendly name for a SOP Class UID.
    Returns the name if registered, otherwise returns the UID with 'Unknown' marker.
    """
    if not _sop_class_cache:
        load_sop_classes()
    
    sop_uid_str = str(sop_uid)
    name = _sop_class_cache.get(sop_uid_str)
    
    if name:
        return f"{name} ({sop_uid_str})"
    else:
        return f"Unknown SOP ({sop_uid_str})"


def get_sop_name_only(sop_uid: str) -> str:
    """Get just the friendly name for a SOP Class UID without the UID in parentheses."""
    if not _sop_class_cache:
        load_sop_classes()
    
    sop_uid_str = str(sop_uid)
    name = _sop_class_cache.get(sop_uid_str)
    
    return name if name else "Unknown SOP"
