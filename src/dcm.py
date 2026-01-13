import datetime
import logging
try:
    from .dcmlogger import LOGGER_NAME
except Exception:
    # Fallback if relative import not available (e.g., run as script)
    LOGGER_NAME = "dcmcreator"

# Initialize module-level logger
_logger = logging.getLogger(LOGGER_NAME)

try:
    import pydicom
    from pydicom.dataset import Dataset, FileDataset
    from pydicom.uid import generate_uid, ExplicitVRLittleEndian, SecondaryCaptureImageStorage, MediaStorageDirectoryStorage
    from pydicom.valuerep import PersonName
except Exception:
    pydicom = None
    Dataset = None
    FileDataset = None
    generate_uid = None
    ExplicitVRLittleEndian = None
    SecondaryCaptureImageStorage = None
    MediaStorageDirectoryStorage = None
    PersonName = None


def create_dicom(save_path, patient, study, series, pixel_array=None):
    """
    Create a minimal but valid DICOM `FileDataset` using provided metadata and optional pixel data.

    - Uses Secondary Capture as SOP Class (generic image container).
    - Fills required attributes and some optional ones.
    - If `pixel_array` is None, creates a 1x1 black image as placeholder.
    - Returns an in-memory dataset; caller is responsible for `save_as`.
    """
    if pydicom is None:
        _logger.warning("pydicom not available; cannot create DICOM")
        raise RuntimeError("pydicom is required to create DICOM files")

    # Create file meta
    # File Meta Information contains UIDs for the storage class and instance, plus transfer syntax.
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    # Create dataset
    # The `FileDataset` uses a 128-byte preamble and the file meta above.
    ds = FileDataset(save_path, {}, file_meta=file_meta, preamble=b"\0" * 128)

    now = datetime.datetime.now()
    # Explicit VR Little Endian to match the file meta transfer syntax
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Patient fields
    # Use `PersonName` for proper VR formatting; allow empty strings for optional values.
    pn = (patient.get("PatientName") or "").strip()
    fam = (patient.get("PatientFamilyNameComplex") or "").strip()
    giv = (patient.get("PatientGivenName") or "").strip()
    mid = (patient.get("PatientMiddleName") or "").strip()
    pref = (patient.get("PatientPrefix") or "").strip()
    suf = (patient.get("PatientSuffix") or "").strip()
    if pn:
        ds.PatientName = PersonName(pn)
    elif any([fam, giv, mid, pref, suf]):
        ds.PatientName = PersonName(f"{fam}^{giv}^{mid}^{pref}^{suf}")
    else:
        ds.PatientName = ""
    ds.PatientID = (patient.get("PatientID") or "").strip()
    ds.PatientBirthDate = (patient.get("PatientBirthDate") or "").strip()
    ds.PatientSex = (patient.get("PatientSex") or "").strip()
    # Optional patient attributes
    pa = (patient.get("PatientAge") or "").strip()
    if pa:
        ds.PatientAge = pa
    pw = (patient.get("PatientWeight") or "").strip()
    if pw:
        ds.PatientWeight = pw
    psz = (patient.get("PatientSize") or "").strip()
    if psz:
        ds.PatientSize = psz
    pcom = (patient.get("PatientComments") or "").strip()
    if pcom:
        ds.PatientComments = pcom
    pmn = (patient.get("PatientMotherBirthName") or "").strip()
    if pmn:
        ds.PatientMotherBirthName = pmn
    pddt = (patient.get("PatientDeathDateTime") or "").strip()
    if pddt:
        ds.PatientDeathDateTime = pddt

    # Study fields
    # Default to generated UID/date/time if missing.
    ds.StudyInstanceUID = (study.get("StudyInstanceUID") or generate_uid()).strip()
    ds.StudyDate = (study.get("StudyDate") or now.strftime("%Y%m%d")).strip()
    ds.StudyTime = (study.get("StudyTime") or now.strftime("%H%M%S")).strip()
    ds.StudyDescription = (study.get("StudyDescription") or "").strip()
    # Optional study attributes
    an = (study.get("AccessionNumber") or "").strip()
    if an:
        ds.AccessionNumber = an
    stid = (study.get("StudyID") or "").strip()
    if stid:
        ds.StudyID = stid
    rpn = (study.get("ReferringPhysicianName") or "").strip()
    if rpn:
        ds.ReferringPhysicianName = rpn
    rps = (study.get("ReadingPhysicianName") or "").strip()
    if rps:
        ds.NameOfPhysiciansReadingStudy = rps
    reason = (study.get("ReasonForStudy") or "").strip()
    if reason:
        ds.ReasonForStudy = reason
    admit = (study.get("AdmittingDiagnosesDescription") or "").strip()
    if admit:
        ds.AdmittingDiagnosesDescription = admit
    spl = (study.get("StudyPatientLocation") or "").strip()
    if spl:
        ds.StudyPatientLocation = spl

    # Series fields
    # Generate SeriesInstanceUID if not provided; coerce SeriesNumber to int with default of 1.
    ds.SeriesInstanceUID = (series.get("SeriesInstanceUID") or generate_uid()).strip()
    series_number = series.get("SeriesNumber")
    ds.SeriesNumber = int(series_number.strip() or 1) if isinstance(series_number, str) else int(series_number or 1)
    ds.Modality = (series.get("Modality") or "SC").strip()
    # Optional series attributes
    sdesc = (series.get("SeriesDescription") or "").strip()
    if sdesc:
        ds.SeriesDescription = sdesc
    bpe = (series.get("BodyPartExamined") or "").strip()
    if bpe:
        ds.BodyPartExamined = bpe
    proto = (series.get("ProtocolName") or "").strip()
    if proto:
        ds.ProtocolName = proto
    sdate = (series.get("SeriesDate") or "").strip()
    if sdate:
        ds.SeriesDate = sdate
    stime = (series.get("SeriesTime") or "").strip()
    if stime:
        ds.SeriesTime = stime
    perf = (series.get("PerformingPhysicianName") or "").strip()
    if perf:
        ds.PerformingPhysicianName = perf
    ops = (series.get("OperatorsName") or "").strip()
    if ops:
        ds.OperatorsName = ops
    lat = (series.get("Laterality") or "").strip()
    if lat:
        ds.Laterality = lat

    # SOP Instance UID
    # Each dataset must have a unique SOP Instance UID and the matching Class UID.
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = SecondaryCaptureImageStorage

    # Required general DICOM attributes
    # Populate minimal common attributes expected for image-like instances.
    ds.PatientOrientation = ""
    ds.ContentDate = now.strftime("%Y%m%d")
    ds.ContentTime = now.strftime("%H%M%S")
    ds.InstanceNumber = 1
    ds.Manufacturer = "DICOM Creator"

    # Pixel data
    # Preserve original pixel data characteristics when available
    if pixel_array is not None:
        import numpy as _np
        arr = pixel_array
        
        # Handle multi-dimensional arrays - flatten to 2D if needed
        if arr.ndim > 2:
            # For 3D arrays, take first slice; for higher dimensions, try to extract 2D
            if arr.ndim == 3 and arr.shape[2] == 1:
                arr = arr[:, :, 0]
            elif arr.ndim == 3:
                _logger.warning("Saving first slice of 3D array with shape %s", arr.shape)
                arr = arr[:, :, 0]
            else:
                _logger.warning("Flattening multi-dimensional array with shape %s to 2D", arr.shape)
                arr = arr.reshape(arr.shape[0], arr.shape[1])
        
        # Ensure we have a 2D array
        if arr.ndim != 2:
            _logger.error("Cannot save pixel array with shape %s", arr.shape)
            raise ValueError(f"Pixel array must be 2D, got shape {arr.shape}")
        
        ds.Rows, ds.Columns = arr.shape
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.SamplesPerPixel = 1
        
        # Determine appropriate bit depth based on data type
        if arr.dtype == _np.uint8:
            ds.BitsAllocated = 8
            ds.BitsStored = 8
            ds.HighBit = 7
            ds.PixelRepresentation = 0
            ds.PixelData = arr.tobytes()
        elif arr.dtype == _np.uint16:
            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.PixelRepresentation = 0
            ds.PixelData = arr.tobytes()
        elif arr.dtype == _np.int16:
            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.PixelRepresentation = 1  # Signed
            ds.PixelData = arr.tobytes()
        else:
            # Convert other types to uint16 to preserve data range
            _logger.warning("Converting pixel array from %s to uint16", arr.dtype)
            if _np.issubdtype(arr.dtype, _np.integer):
                # Integer type - preserve range
                arr_min = arr.min()
                arr_max = arr.max()
                if arr_max - arr_min > 0:
                    arr_normalized = ((arr.astype(_np.float64) - arr_min) / (arr_max - arr_min) * 65535).astype(_np.uint16)
                else:
                    arr_normalized = _np.zeros_like(arr, dtype=_np.uint16)
            else:
                # Float type - normalize to 0-65535
                arr_normalized = (arr.astype(_np.float64) * 65535).clip(0, 65535).astype(_np.uint16)
            
            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.PixelRepresentation = 0
            ds.PixelData = arr_normalized.tobytes()
    else:
        # Include minimal image
        import numpy as _np
        ds.Rows = 1
        ds.Columns = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.SamplesPerPixel = 1
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = _np.zeros((1, 1), dtype=_np.uint8).tobytes()

    return ds


def load_dicom(path):
    """
    Read a DICOM file and return the dataset plus a best-effort pixel array.

    - Prefers `dataset.pixel_array` (handles decompression and photometric interpretation).
    - Falls back to manual parsing of `PixelData` for simple monochrome 8/16-bit images.
    - Returns `(ds, pixel_array)` where pixel_array may be None if unavailable.
    """
    if pydicom is None:
        _logger.warning("pydicom not available; cannot load DICOM: %s", path)
        raise RuntimeError("pydicom is required to load DICOM files")

    # Try reading with standard DICOM header first
    try:
        ds = pydicom.dcmread(path)
    except Exception as e:
        # If it fails, try with force=True for files without proper preamble
        try:
            ds = pydicom.dcmread(path, force=True)
            _logger.debug("Loaded DICOM file without standard header: %s", path)
        except Exception:
            # Re-raise original exception if force=True also fails
            raise e

    pixel_array = None
    try:
        # Prefer pydicom's pixel_array which handles decompress and interpretation
        if hasattr(ds, "pixel_array"):
            pixel_array = ds.pixel_array
        elif hasattr(ds, "PixelData") and hasattr(ds, "Rows") and hasattr(ds, "Columns"):
            # Manual fallback for simple cases
            import numpy as _np
            dtype = _np.uint8 if getattr(ds, "BitsAllocated", 8) == 8 else _np.uint16
            pixel_array = _np.frombuffer(ds.PixelData, dtype=dtype)
            expected = int(ds.Rows) * int(ds.Columns) * int(getattr(ds, "SamplesPerPixel", 1))
            if pixel_array.size >= expected:
                pixel_array = pixel_array[:expected]
                pixel_array = pixel_array.reshape((int(ds.Rows), int(ds.Columns)))
            else:
                pixel_array = None
    except Exception:
        _logger.debug("Failed to extract pixel data from %s", path)
        pixel_array = None

    return ds, pixel_array


def _iter_dicom_files(paths_or_dir):
    """
    Yield file paths from a list, tuple, directory, or single file path.

    - For directories, walks recursively and yields files with DICOM-like characteristics.
    - For lists/tuples, yields existing files only.
    """
    import os
    if isinstance(paths_or_dir, (list, tuple)):
        for p in paths_or_dir:
            if p and os.path.isfile(p):
                yield p
    elif isinstance(paths_or_dir, str):
        if os.path.isdir(paths_or_dir):
            for root, _, files in os.walk(paths_or_dir):
                for f in files:
                    # Skip obvious non-DICOM files
                    lower_f = f.lower()
                    
                    # Skip common non-DICOM extensions
                    skip_extensions = ('.txt', '.xml', '.html', '.json', '.ini', '.log', 
                                      '.bat', '.sh', '.exe', '.dll', '.so', '.py', '.pyc',
                                      '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', 
                                      '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar', '.gz')
                    if any(lower_f.endswith(ext) for ext in skip_extensions):
                        continue
                    
                    # Prefer files with DICOM extensions or no extension
                    yield os.path.join(root, f)
        elif os.path.isfile(paths_or_dir):
            yield paths_or_dir


def load_dicom_grouped(paths_or_dir):
    """
    Load multiple DICOM files and group them by Study and Series.

    Returns a nested dict: {StudyInstanceUID: {SeriesInstanceUID: [ (dataset, pixel_array) ] }}
    """
    if pydicom is None:
        _logger.warning("pydicom not available; cannot load DICOM group")
        raise RuntimeError("pydicom is required to load DICOM files")

    grouped = {}
    skipped_count = 0
    for path in _iter_dicom_files(paths_or_dir):
        try:
            ds, arr = load_dicom(path)
        except Exception:
            # Skip unreadable files silently to keep batch import robust.
            skipped_count += 1
            _logger.debug("Skipping unreadable file: %s", path)
            continue

        study_uid = getattr(ds, "StudyInstanceUID", None) or ""
        series_uid = getattr(ds, "SeriesInstanceUID", None) or ""

        # Append instance under its Study/Series buckets.
        study_bucket = grouped.setdefault(study_uid, {})
        series_bucket = study_bucket.setdefault(series_uid, [])
        series_bucket.append((ds, arr))

    if skipped_count > 0:
        _logger.info("Skipped %d non-DICOM or unreadable files", skipped_count)

    return grouped


def is_dicomdir(path):
    """
    Heuristically detect if a path points to a DICOMDIR file.

    - Checks SOP Class UID and File Meta for Media Storage Directory.
    - Also checks for presence of `DirectoryRecordSequence`.
    - Finally, falls back to filename equality to 'DICOMDIR'.
    """
    if pydicom is None:
        return False
    
    # Quick check: if filename is DICOMDIR, likely a DICOMDIR
    import os as _os
    if _os.path.basename(path).upper() == 'DICOMDIR':
        return True
    
    try:
        ds = pydicom.dcmread(path, stop_before_pixels=True)
        if getattr(ds, 'SOPClassUID', None) == MediaStorageDirectoryStorage:
            return True
        fm = getattr(ds, 'file_meta', None)
        if fm is not None and getattr(fm, 'MediaStorageSOPClassUID', None) == MediaStorageDirectoryStorage:
            return True
        if hasattr(ds, 'DirectoryRecordSequence'):
            return True
    except Exception:
        # Try with force=True for files without proper preamble
        try:
            ds = pydicom.dcmread(path, stop_before_pixels=True, force=True)
            if getattr(ds, 'SOPClassUID', None) == MediaStorageDirectoryStorage:
                return True
            if hasattr(ds, 'DirectoryRecordSequence'):
                return True
        except Exception:
            # Not a DICOMDIR or not readable
            pass
    
    return False


def load_dicomdir_grouped(dicomdir_path):
    """
    Load a DICOMDIR file and group referenced instances by Study and Series UIDs.
    Follows references in `DirectoryRecordSequence`; if none found, scans the directory.
    """
    if pydicom is None:
        _logger.warning("pydicom not available; cannot load DICOMDIR: %s", dicomdir_path)
        raise RuntimeError("pydicom is required to load DICOMDIR files")

    import os as _os
    base = _os.path.dirname(dicomdir_path)
    try:
        ddir = pydicom.dcmread(dicomdir_path)
    except Exception as e:
        # Propagate the error to the caller for user-friendly messaging upstream.
        _logger.warning("Failed to read DICOMDIR: %s", dicomdir_path, exc_info=True)
        raise

    referenced_files = []
    seq = getattr(ddir, 'DirectoryRecordSequence', None)
    if seq is not None:
        for record in seq:
            rtype = getattr(record, 'DirectoryRecordType', '')
            if rtype == 'IMAGE':
                ref = getattr(record, 'ReferencedFileID', None)
                if ref:
                    if isinstance(ref, (list, tuple)):
                        rel = _os.path.join(*ref)
                    else:
                        rel = str(ref)
                    referenced_files.append(_os.path.join(base, rel))
    # Fallback: if no image records, scan folder
    if not referenced_files:
        referenced_files = list(_iter_dicom_files(base))

    return load_dicom_grouped(referenced_files)
