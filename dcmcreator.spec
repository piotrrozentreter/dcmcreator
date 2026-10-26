# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

block_cipher = None
src_dir = Path(SPECPATH) / 'src'

# Collect data files - use simple tuple pairs
# Note: VR.xml is included via ('src', 'src') which copies entire src directory
# The second line is kept for explicitness and documentation
datas = [
    ('src', 'src'),                # Include all source files (includes VR.xml)
    ('src/VR.xml', 'src'),        # CRITICAL: DICOM data dictionary (7MB) - explicitly ensure it's included
]

# Comprehensive hidden imports
hiddenimports = [
    # Core application modules (new optional features)
    'app_logic',
    'dcm',
    'dcmlogger',
    'import_helper',
    'presets',
    'random_dicom',
    'test_runner',
    'connection_validator',
    'stress_tester',
    'transmission_history',
    'performance_benchmarking',
    'parallel_transmission',
    'remote',
    'vr_validator',
    'validation_dialog',
    'tag',
    'tag_dialog',
    
    # PyDICOM - core and all submodules
    'pydicom',
    'pydicom.uid',
    'pydicom.dataset',
    'pydicom.sequence',
    'pydicom.filereader',
    'pydicom.filewriter',
    'pydicom.dataelem',
    'pydicom.valuerep',
    'pydicom.multival',
    'pydicom.datadict',
    'pydicom.charset',
    'pydicom.config',
    'pydicom.misc',
    'pydicom.errors',
    'pydicom.compat',
    'pydicom.pixel_data_handlers',
    'pydicom.pixel_data_handlers.numpy_handler',
    'pydicom.uid_dict',
    'pydicom._dicom_dict',
    'pydicom.charset.encodings',
    'pydicom.charset.encodings_compat',
    'pydicom.json_handler',
    'pydicom.jsonwriter',
    'pydicom.jsonreader',
    'pydicom.dataset',
    'pydicom.multival',
    'pydicom.valuerep',
    
    # PyNetDICOM - core and all submodules (for networking features)
    'pynetdicom',
    'pynetdicom.compat',
    'pynetdicom.pdu',
    'pynetdicom.pdu_primitives',
    'pynetdicom.service_class',
    'pynetdicom._uid_dict',
    'pynetdicom.events',
    'pynetdicom.sop_class',
    'pynetdicom.dataset',
    'pynetdicom.association',
    'pynetdicom.dimse',
    'pynetdicom.dimse_primitives',
    'pynetdicom.dimse_messages',
    'pynetdicom.timer',
    
    # NumPy
    'numpy',
    'numpy.random',
    'numpy.core',
    'numpy.ma',
    'numpy.lib',
    'numpy.linalg',
    'numpy.polynomial',
    'numpy.testing',
    
    # PIL/Pillow - COMPLETE SET including all image format handlers
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageFilter',
    'PIL.ImageOps',
    'PIL.ImageChops',
    'PIL.ImageMath',
    'PIL.ImageSequence',
    'PIL.ImageStat',
    'PIL.ImageTransform',
    # Image format plugins
    'PIL.PngImagePlugin',
    'PIL.JpegImagePlugin',
    'PIL.BmpImagePlugin',
    'PIL.GifImagePlugin',
    'PIL.TiffImagePlugin',
    # Resampling filters
    'PIL.ImageResampling',
    
    # TKinter
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.simpledialog',
    
    # Logging and utilities
    'logging',
    'logging.handlers',
    'threading',
    'socket',
    'ssl',
    'json',
    'pathlib',
]

# LazyImport module names are invisible to PyInstaller's static analysis.
hiddenimports = sorted(set(hiddenimports) | {
    module.stem for module in src_dir.glob('*.py')
    if module.stem != '__init__'
})

a = Analysis(
    ['src/app.py'],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DICOM Creator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico' if os.path.exists('app.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DICOM Creator'
)
