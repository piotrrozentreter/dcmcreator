"""
Random DICOM Generator for testing and bulk transmission.

This module provides utilities to generate random test DICOM files
with configurable parameters for testing and stress testing.
"""

import os
import uuid
from datetime import datetime, timedelta
import random

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pydicom
    from pydicom.dataset import Dataset, FileDataset
    from pydicom.uid import generate_uid
except Exception:
    pydicom = None


class RandomDicomGenerator:
    """Generate random test DICOM files for testing purposes."""
    
    def __init__(self, logger=None):
        """Initialize the generator.
        
        Args:
            logger: Optional logger instance
        
        Raises:
            ImportError: If required dependencies (numpy, pydicom) are not available
        """
        if np is None or pydicom is None:
            raise ImportError("RandomDicomGenerator requires numpy and pydicom. Install with: pip install numpy pydicom")
        
        self.logger = logger
        self.generated_dicoms = []
    
    def generate_single(self, 
                       filename=None,
                       patient_name=None,
                       patient_id=None,
                       width=256,
                       height=256,
                       seed=None):
        """Generate a single random DICOM file.
        
        Args:
            filename: Output filename (generates random if None)
            patient_name: Patient name (generates random if None)
            patient_id: Patient ID (generates random if None)
            width: Image width in pixels
            height: Image height in pixels
            seed: Random seed for reproducibility
            
        Returns:
            FileDataset or None on error
        """
        if pydicom is None:
            if self.logger:
                self.logger.error("pydicom not available")
            return None
        
        try:
            if seed is not None:
                np.random.seed(seed)
                random.seed(seed)
            
            # Generate metadata
            if patient_name is None:
                first_names = ['John', 'Jane', 'Robert', 'Mary', 'Michael', 'Patricia']
                last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']
                patient_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            if patient_id is None:
                patient_id = f"TEST{random.randint(100000, 999999)}"
            
            if filename is None:
                filename = f"test_dicom_{uuid.uuid4().hex[:8]}.dcm"
            
            # Create file metadata
            file_meta = Dataset()
            file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.7'  # Secondary Capture
            file_meta.MediaStorageSOPInstanceUID = generate_uid()
            file_meta.ImplementationClassUID = generate_uid()
            file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
            
            # Create main dataset
            ds = FileDataset(
                filename,
                {},
                file_meta=file_meta,
                preamble=b"\0" * 128
            )
            
            # Set timestamps
            now = datetime.now()
            ds.ContentDate = now.strftime('%Y%m%d')
            ds.ContentTime = now.strftime('%H%M%S.%f')
            ds.StudyDate = (now - timedelta(days=random.randint(1, 30))).strftime('%Y%m%d')
            ds.StudyTime = f"{random.randint(0, 23):02d}{random.randint(0, 59):02d}{random.randint(0, 59):02d}"
            ds.SeriesDate = ds.StudyDate
            ds.SeriesTime = ds.StudyTime
            
            # Patient info
            ds.PatientName = patient_name
            ds.PatientID = patient_id
            ds.PatientBirthDate = (now - timedelta(days=random.randint(365*18, 365*80))).strftime('%Y%m%d')
            ds.PatientSex = random.choice(['M', 'F', 'O'])
            ds.PatientAge = f"{random.randint(18, 90):03d}Y"
            ds.PatientWeight = str(random.randint(50, 120))
            ds.PatientSize = f"{random.uniform(1.5, 2.0):.2f}"
            
            # Study info
            ds.StudyInstanceUID = generate_uid()
            ds.StudyID = f"STUDY{random.randint(1000, 9999)}"
            ds.StudyDescription = random.choice([
                'Test Study - Chest X-Ray',
                'Test Study - Abdomen',
                'Test Study - Head CT',
                'Test Study - Extremity',
                'Test Study - Cardiac',
                'Test Study - General'
            ])
            ds.AccessionNumber = f"ACC{random.randint(100000, 999999)}"
            
            # Series info
            ds.SeriesInstanceUID = generate_uid()
            ds.SeriesNumber = random.randint(1, 10)
            ds.Modality = random.choice(['CR', 'DX', 'CT', 'MR', 'XC', 'SC'])
            ds.SeriesDescription = f"Test Series {random.randint(1, 100)}"
            ds.BodyPartExamined = random.choice(['CHEST', 'ABDOMEN', 'HEAD', 'EXTREMITY', 'UNKNOWN'])
            ds.ProtocolName = f"Test Protocol {random.randint(1, 50)}"
            
            # Operator/Physician info
            ds.OperatorsName = f"Test^Operator{random.randint(1, 10)}"
            ds.PerformingPhysicianName = f"Test^Physician{random.randint(1, 10)}"
            ds.ReferringPhysicianName = f"Test^Referring{random.randint(1, 10)}"
            
            # Image info
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"
            ds.Rows = height
            ds.Columns = width
            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.PixelRepresentation = 0
            
            # Generate random pixel data
            pixel_array = np.random.randint(0, 65535, size=(height, width), dtype=np.uint16)
            ds.PixelData = pixel_array.tobytes()
            
            # DICOM metadata
            ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.7'
            ds.SOPInstanceUID = generate_uid()
            ds.InstanceNumber = 1
            
            if self.logger:
                self.logger.warning(f"Generated test DICOM: {patient_name} ({patient_id})")
            
            return ds
            
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to generate DICOM: {e}")
            return None
    
    def generate_batch(self,
                      count=10,
                      output_dir=None,
                      width=256,
                      height=256,
                      randomize_patient=True):
        """Generate multiple random DICOM files.
        
        Args:
            count: Number of DICOMs to generate
            output_dir: Directory to save files (if None, returns in-memory)
            width: Image width
            height: Image height
            randomize_patient: If True, generate different patients for each
            
        Returns:
            List of FileDataset objects or saved file paths
        """
        if pydicom is None:
            if self.logger:
                self.logger.error("pydicom not available")
            return []
        
        dicoms = []
        patients = []
        
        # Generate unique patients if requested
        if randomize_patient:
            first_names = ['John', 'Jane', 'Robert', 'Mary', 'Michael', 'Patricia',
                          'David', 'Linda', 'Richard', 'Barbara', 'Joseph', 'Susan', 'Piotr', 'Adam']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Brzeszczyszczykiewicz',
                         'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Rozen', 'Rozsoft']
            
            for i in range(count):
                first = random.choice(first_names)
                last = random.choice(last_names)
                patients.append((f"{first} {last}", f"TEST{1000+i}"))
        else:
            patients = [(f"Test Patient {i}", f"TESTID{i}") for i in range(count)]
        
        try:
            # Create output directory if needed
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            for i, (patient_name, patient_id) in enumerate(patients):
                filename = None
                if output_dir:
                    filename = os.path.join(output_dir, f"test_dicom_{i+1:04d}.dcm")
                
                ds = self.generate_single(
                    filename=filename,
                    patient_name=patient_name,
                    patient_id=patient_id,
                    width=width,
                    height=height
                )
                
                if ds:
                    if output_dir:
                        try:
                            ds.save_as(filename, write_like_original=False)
                            dicoms.append(filename)
                            if self.logger:
                                self.logger.warning(f"Saved: {filename}")
                        except Exception as e:
                            if self.logger:
                                self.logger.exception(f"Failed to save {filename}: {e}")
                    else:
                        dicoms.append(ds)
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Batch generation failed: {e}")
        
        self.generated_dicoms = dicoms
        return dicoms
    
    def generate_with_sizes(self,
                           count=10,
                           size_mb=None,
                           output_dir=None):
        """Generate DICOMs with specific sizes.
        
        Args:
            count: Number of files
            size_mb: Target size per file in MB (None for default ~1MB)
            output_dir: Output directory
            
        Returns:
            List of file paths or datasets
        """
        if size_mb is None:
            size_mb = 1.0
        
        # Estimate dimensions for target size
        # Each pixel is 2 bytes (uint16)
        # Need: size_mb * 1024 * 1024 / 2 = pixels
        target_pixels = int(size_mb * 1024 * 1024 / 2)
        dim = int(np.sqrt(target_pixels))
        dim = (dim // 16) * 16  # Round to nearest 16
        dim = max(256, min(4096, dim))  # Clamp between 256 and 4096
        
        if self.logger:
            self.logger.warning(f"Generating {count} DICOMs of ~{size_mb}MB each ({dim}x{dim})")
        
        return self.generate_batch(
            count=count,
            output_dir=output_dir,
            width=dim,
            height=dim,
            randomize_patient=True
        )
    
    def get_generated_files(self):
        """Get list of generated DICOM files or datasets."""
        return self.generated_dicoms
