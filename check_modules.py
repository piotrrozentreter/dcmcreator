#!/usr/bin/env python
"""Diagnostic script to check which modules can be imported."""

from src.import_helper import LazyImport

modules = {
    "ServerPresetsManager": (".presets", "presets"),
    "RandomDicomGenerator": (".random_dicom", "random_dicom"),
    "TestRunner": (".test_runner", "test_runner"),
    "ConnectionValidator": (".connection_validator", "connection_validator"),
    "StressTestRunner": (".stress_tester", "stress_tester"),
    "TransmissionHistory": (".transmission_history", "transmission_history"),
    "PerformanceBenchmark": (".performance_benchmarking", "performance_benchmarking"),
    "ParallelTransmissionManager": (".parallel_transmission", "parallel_transmission"),
    "DicomLogicHandler": (".app_logic", "app_logic"),
}

print("=" * 70)
print("MODULE IMPORT DIAGNOSTIC")
print("=" * 70)
print()

loaded = []
failed = []

for name, (rel, abs_) in modules.items():
    lazy = LazyImport(rel, abs_, debug=False)
    result = lazy._load()
    error = lazy.get_error()
    
    if result is not None:
        loaded.append(name)
        print(f"? {name:35} LOADED")
    else:
        failed.append((name, error))
        print(f"? {name:35} FAILED")
        if error:
            print(f"  ?? Error: {error}")

print()
print("=" * 70)
print(f"SUMMARY: {len(loaded)} loaded, {len(failed)} failed")
print("=" * 70)

if failed:
    print("\nFAILED MODULES:")
    for name, error in failed:
        print(f"\n{name}:")
        print(f"  {error}")
    
    print("\n" + "=" * 70)
    print("TO FIX MISSING DEPENDENCIES:")
    print("=" * 70)
    print("\nInstall missing packages:")
    print("  pip install numpy")
    print("  pip install pydicom")
    print("  pip install pillow")
    print("\nOr install all at once:")
    print("  pip install numpy pydicom pillow")
