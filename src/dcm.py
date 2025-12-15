import datetime

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
    if pydicom is None:
        raise RuntimeError("pydicom is required to create DICOM files")

    # Create file meta
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    # Create dataset
    ds = FileDataset(save_path, {}, file_meta=file_meta, preamble=b"\0" * 128)

    now = datetime.datetime.now()
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Patient fields
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
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = SecondaryCaptureImageStorage

    # Required general DICOM attributes
    ds.PatientOrientation = ""
    ds.ContentDate = now.strftime("%Y%m%d")
    ds.ContentTime = now.strftime("%H%M%S")
    ds.InstanceNumber = 1
    ds.Manufacturer = "DICOM Creator"

    # Pixel data
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
    if pydicom is None:
        raise RuntimeError("pydicom is required to load DICOM files")

    ds = pydicom.dcmread(path)

    pixel_array = None
    try:
        # Prefer pydicom's pixel_array which handles decompress and interpretation
        if hasattr(ds, "pixel_array"):
            pixel_array = ds.pixel_array
        elif hasattr(ds, "PixelData") and hasattr(ds, "Rows") and hasattr(ds, "Columns"):
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
        pixel_array = None

    return ds, pixel_array


def _iter_dicom_files(paths_or_dir):
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
        raise RuntimeError("pydicom is required to load DICOM files")

    grouped = {}
    for path in _iter_dicom_files(paths_or_dir):
        try:
            ds, arr = load_dicom(path)
        except Exception:
            continue

        study_uid = getattr(ds, "StudyInstanceUID", None) or ""
        series_uid = getattr(ds, "SeriesInstanceUID", None) or ""

        study_bucket = grouped.setdefault(study_uid, {})
        series_bucket = study_bucket.setdefault(series_uid, [])
        series_bucket.append((ds, arr))

    return grouped


def is_dicomdir(path):
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
        pass
    import os as _os
    return _os.path.basename(path).upper() == 'DICOMDIR'


def load_dicomdir_grouped(dicomdir_path):
    """
    Load a DICOMDIR file and group referenced instances by Study and Series UIDs.
    """
    if pydicom is None:
        raise RuntimeError("pydicom is required to load DICOMDIR files")

    import os as _os
    base = _os.path.dirname(dicomdir_path)
    try:
        ddir = pydicom.dcmread(dicomdir_path)
    except Exception as e:
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
