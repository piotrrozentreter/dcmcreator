#!/bin/bash
# Run all test scripts in the test directory
# Usage: ./run_tests.sh

echo "======================================================================"
echo "Running All Tests"
echo "======================================================================"
echo ""

python3 test/run_all_tests.py

echo ""
echo "======================================================================"
echo "Test run complete. Check output above for results."
echo "======================================================================"
