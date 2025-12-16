# DICOM Creator GUI App

This project provides a simple GUI to create DICOM files (Secondary Capture).

Features:
- Enter patient fields: Patient Name, Patient ID, Patient Birth Date, Patient Sex
- Enter study fields: Study Instance UID, Study Date, Study Time, Study Description
- Enter series fields: Series Instance UID, Series Number
- Enter modality fields: Modality
- Load an image (PNG/JPG) and convert it to DICOM pixel data
- Save as `.dcm`
- Remote tab: send grouped or in-memory DICOM instances to a remote DICOM server (SCP) using C-STORE
- Live progress during remote send: connection, association, C-ECHO, per-instance status, bytes estimate, and release
- In-memory send: if no DICOMs are loaded, a dataset is created from current form fields and sent
- Extended Patient fields: Family Name Complex, Prefix, Given Name, Middle Name, Suffix, Mother’s Birth Name, Death DateTime
- Extended Study fields: Referring Physician, Reading Physician, Accession Number, Reason for Study, Admitting Diagnoses Description, Study Patient Location
- Extended Series fields: Series Date/Time, Performing Physician, Operator’s Name, Laterality
- Quit confirmation when exiting the app
- Centralized logging via `src/dcmlogger.py` (logs to console and `dcmcreator.log`)

Requirements:
- Python 3.9+
- pydicom
- pillow (PIL)
- numpy
- `pynetdicom` >= 2.0.0 (required for Remote tab C-STORE)

Setup:
1. Create a virtual environment (optional).
2. Install dependencies:
   pip install -r requirements.txt
3. Run the app:
   python src/app.py

Notes:
- If you do not load an image, you can still save a minimal DICOM without pixel data.
- UIDs default to newly generated ones if left empty.
