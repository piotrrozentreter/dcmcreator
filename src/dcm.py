import datetime
import logging
try:
    from .dcmlogger import LOGGER_NAME
except Exception:
    # Fallback if relative import not available (e.g., run as script)
    LOGGER_NAME = "dcmcreator"

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
    ds.PatientName = PersonName(pn) if pn else ""
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
    # If a pixel array is given (assumed 2D uint8), set monochrome attributes and embed raw bytes.
    # Otherwise include a 1x1 zeroed image to keep the file valid.
    if pixel_array is not None:
        arr = pixel_array
        ds.Rows, ds.Columns = arr.shape
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.SamplesPerPixel = 1
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = arr.tobytes()
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

    ds = pydicom.dcmread(path)

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
        _logger.warning("Failed to extract pixel data from %s", path, exc_info=True)
        pixel_array = None

    return ds, pixel_array


def _iter_dicom_files(paths_or_dir):
    """
    Yield file paths from a list, tuple, directory, or single file path.

    - For directories, walks recursively and yields all files (heuristic: accepts any file, giving precedence to common DICOM extensions).
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
                    # Heuristic: accept all, but prefer common DICOM extensions
                    if f.lower().endswith((".dcm", ".dicom")) or True:
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
    for path in _iter_dicom_files(paths_or_dir):
        try:
            ds, arr = load_dicom(path)
        except Exception:
            # Skip unreadable files silently to keep batch import robust.
            _logger.warning("Skipping unreadable DICOM file: %s", path, exc_info=True)
            continue

        study_uid = getattr(ds, "StudyInstanceUID", None) or ""
        series_uid = getattr(ds, "SeriesInstanceUID", None) or ""

        # Append instance under its Study/Series buckets.
        study_bucket = grouped.setdefault(study_uid, {})
        series_bucket = study_bucket.setdefault(series_uid, [])
        series_bucket.append((ds, arr))

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
        _logger.warning("Failed to probe DICOMDIR file: %s", path, exc_info=True)
        pass
    import os as _os
    return _os.path.basename(path).upper() == 'DICOMDIR'


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
