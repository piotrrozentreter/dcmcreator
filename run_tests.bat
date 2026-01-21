@echo off
REM Run all test scripts in the test directory
REM Usage: run_tests.bat

echo ======================================================================
echo Running All Tests
echo ======================================================================
echo.

python test\run_all_tests.py

echo.
echo ======================================================================
echo Test run complete. Check output above for results.
echo ======================================================================
pause
