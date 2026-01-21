"""
Run all test scripts in the test directory.

This script executes all test_*.py files in the test directory
and reports the results.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_all_tests():
    """Run all test scripts and report results."""
    
    # Get test directory
    test_dir = Path(__file__).parent
    
    # Find all test files
    test_files = sorted(test_dir.glob("test_*.py"))
    
    if not test_files:
        print("No test files found in test directory")
        return False
    
    print("=" * 70)
    print(f"Running {len(test_files)} test script(s)")
    print("=" * 70)
    
    results = []
    
    for test_file in test_files:
        print(f"\n{'=' * 70}")
        print(f"Running: {test_file.name}")
        print(f"{'=' * 70}")
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=False,
                text=True,
                cwd=test_dir.parent  # Run from project root
            )
            
            success = result.returncode == 0
            results.append((test_file.name, success))
            
            if success:
                print(f"\n? {test_file.name} PASSED")
            else:
                print(f"\n? {test_file.name} FAILED (exit code: {result.returncode})")
                
        except Exception as e:
            print(f"\n? {test_file.name} ERROR: {e}")
            results.append((test_file.name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for test_name, success in results:
        status = "? PASSED" if success else "? FAILED"
        print(f"{status:12} {test_name}")
    
    print(f"\n{'=' * 70}")
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print(f"{'=' * 70}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
