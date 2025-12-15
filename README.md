# DICOM Creator GUI App

This project provides a simple GUI to create DICOM files (Secondary Capture).

Features:
- Enter patient fields: Patient Name, Patient ID, Patient Birth Date, Patient Sex
- Enter study fields: Study Instance UID, Study Date, Study Time, Study Description
- Enter series fields: Series Instance UID, Series Number
- Enter modality fields: Modality
- Load an image (PNG/JPG) and convert it to DICOM pixel data
- Save as `.dcm`

Requirements:
- Python 3.9+
- pydicom
- pillow (PIL)
- numpy

Setup:
1. Create a virtual environment (optional).
2. Install dependencies:
   pip install -r requirements.txt
3. Run the app:
   python src/app.py

Notes:
- If you do not load an image, you can still save a minimal DICOM without pixel data.
- UIDs default to newly generated ones if left empty.
