@echo off
REM Build script for DICOM Creator
REM This script installs PyInstaller, creates an icon, builds the executable, and creates a ZIP distribution

setlocal enabledelayedexpansion

echo.
echo ================================
echo DICOM Creator - Build Script
echo ================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

echo Step 1: Installing build dependencies...
echo Installing PyInstaller and Pillow...
pip install -r build-requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install build dependencies
    pause
    exit /b 1
)
echo ? Dependencies installed

echo.
echo Step 2: Creating application icon...
python create_icon.py
if errorlevel 1 (
    echo WARNING: Icon creation failed, continuing without custom icon
) else (
    echo ? Icon created successfully
)

echo.
echo Step 3: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
echo ? Previous builds cleaned

echo.
echo Step 4: Building executable...
echo This may take a few minutes...
echo.

REM Run PyInstaller
pyinstaller dcmcreator.spec

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo ================================
echo Creating ZIP distribution...
echo ================================
echo.

REM Create ZIP using PowerShell (available on all modern Windows)
powershell -Command "Add-Type -AssemblyName 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('dist\DICOM Creator', 'DICOM Creator.zip')"

if errorlevel 1 (
    echo WARNING: ZIP creation failed, but executable was built successfully
    echo You can manually create the ZIP:
    echo   Right-click dist\DICOM Creator ^-^> Send to ^-^> Compressed (zipped) folder
) else (
    echo ? ZIP distribution created: DICOM Creator.zip
    
    REM Get file sizes
    for /F "usebackq" %%A in ('powershell -Command "[math]::Round((Get-Item 'DICOM Creator.zip').Length / 1MB, 1)"') do set ZIP_SIZE=%%A
    echo   ZIP file size: !ZIP_SIZE! MB
)

echo.
echo ================================
echo Build completed successfully!
echo ================================
echo.
echo Your application is ready for distribution:
echo.
echo Options:
echo   1. ZIP file (for email, GitHub, websites):
echo      ? DICOM Creator.zip
echo      ? Users extract and run DICOM Creator.exe
echo.
echo   2. Folder (for USB drives, network shares):
echo      ? dist\DICOM Creator\
echo      ? Users run DICOM Creator.exe
echo.
echo System Requirements:
echo   - Windows 7 or newer (64-bit)
echo   - ~100 MB disk space
echo   - No Python required!
echo.
pause
