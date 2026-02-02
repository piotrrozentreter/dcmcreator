"""
Quick test script for hierarchical DICOM generation.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from random_dicom import RandomDicomGenerator
from dcmlogger import setup_logging

def test_hierarchical_generation():
    """Test the new hierarchical generation method."""
    
    logger = setup_logging()
    
    print("=" * 60)
    print("Testing Hierarchical DICOM Generation")
    print("=" * 60)
    
    try:
        generator = RandomDicomGenerator(logger=logger)
        
        # Test parameters
        studies = 2
        series = 3
        instances = 2
        size_mb = 0.5
        
        print(f"\nGenerating hierarchy:")
        print(f"  Studies: {studies}")
        print(f"  Series per study: {series}")
        print(f"  Instances per series: {instances}")
        print(f"  Total files: {studies * series * instances}")
        print(f"  Size per file: {size_mb}MB")
        
        # Generate in-memory (no output_dir)
        datasets = generator.generate_hierarchical(
            studies_per_patient=studies,
            series_per_study=series,
            instances_per_series=instances,
            size_mb=size_mb,
            output_dir=None
        )
        
        print(f"\n? Generated {len(datasets)} datasets")
        
        # Verify hierarchy
        print("\nVerifying hierarchy...")
        
        # Group by study
        studies_dict = {}
        for ds in datasets:
            study_uid = str(ds.StudyInstanceUID)
            if study_uid not in studies_dict:
                studies_dict[study_uid] = {
                    'patient_id': str(ds.PatientID),
                    'patient_name': str(ds.PatientName),
                    'series': {}
                }
            
            series_uid = str(ds.SeriesInstanceUID)
            if series_uid not in studies_dict[study_uid]['series']:
                studies_dict[study_uid]['series'][series_uid] = []
            
            studies_dict[study_uid]['series'][series_uid].append(ds)
        
        print(f"  Studies found: {len(studies_dict)}")
        
        # Check each study
        patient_ids = set()
        for study_uid, study_data in studies_dict.items():
            patient_ids.add(study_data['patient_id'])
            num_series = len(study_data['series'])
            print(f"  Study {study_uid[:20]}... has {num_series} series")
            
            for series_uid, instances_list in study_data['series'].items():
                num_instances = len(instances_list)
                print(f"    Series {series_uid[:20]}... has {num_instances} instances")
        
        # Verify all belong to same patient
        print(f"\n  Unique patients: {len(patient_ids)}")
        if len(patient_ids) == 1:
            print(f"  ? All files belong to same patient: {list(patient_ids)[0]}")
        else:
            print(f"  ? ERROR: Multiple patients found!")
            return False
        
        # Verify structure matches expectations
        if len(studies_dict) == studies:
            print(f"  ? Correct number of studies: {studies}")
        else:
            print(f"  ? ERROR: Expected {studies} studies, found {len(studies_dict)}")
            return False
        
        # Check series count in each study
        for study_uid, study_data in studies_dict.items():
            if len(study_data['series']) == series:
                print(f"  ? Study has correct number of series: {series}")
            else:
                print(f"  ? ERROR: Expected {series} series, found {len(study_data['series'])}")
                return False
            
            # Check instance count in each series
            for series_uid, instances_list in study_data['series'].items():
                if len(instances_list) == instances:
                    print(f"  ? Series has correct number of instances: {instances}")
                else:
                    print(f"  ? ERROR: Expected {instances} instances, found {len(instances_list)}")
                    return False
        
        print("\n" + "=" * 60)
        print("? All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n? Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hierarchical_generation()
    sys.exit(0 if success else 1)
