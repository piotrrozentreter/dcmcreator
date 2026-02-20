import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading

try:
    import pydicom
except Exception:
    pydicom = None

try:
    from PIL import Image, ImageTk
    import numpy as np
except Exception:
    Image = None
    ImageTk = None
    np = None

try:
    from .sop_utils import get_sop_name_only
except ImportError:
    try:
        from sop_utils import get_sop_name_only
    except ImportError:
        def get_sop_name_only(sop_uid):
            return "Unknown SOP"

APP_TITLE = "DICOM Creator v0.8.0\n"

try:
    from .dcmlogger import setup_logging, LOGGER_NAME
except Exception:
    from dcmlogger import setup_logging, LOGGER_NAME

# ============================================================================
# RESOURCE PATH HELPER - For PyInstaller compatibility
# ============================================================================
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    import sys
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not running in PyInstaller bundle - use script directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# ============================================================================
# LAZY IMPORTS - Import modules only when actually needed
# ============================================================================
try:
    from .import_helper import LazyImport
except Exception:
    from import_helper import LazyImport

# Feature modules (optional)
ServerPresetsManager = LazyImport(".presets", "presets")
RandomDicomGenerator = LazyImport(".random_dicom", "random_dicom")
TestRunner = LazyImport(".test_runner", "test_runner")

# Test-related modules (optional)
ConnectionValidator = LazyImport(".connection_validator", "connection_validator")
StressTestRunner = LazyImport(".stress_tester", "stress_tester")
TransmissionHistory = LazyImport(".transmission_history", "transmission_history")
PerformanceBenchmark = LazyImport(".performance_benchmarking", "performance_benchmarking")
ParallelTransmissionManager = LazyImport(".parallel_transmission", "parallel_transmission")

# Query/Retrieve module (optional)
DicomQueryHandler = LazyImport(".query_retrieve", "query_retrieve")

# Validator
VRValidator = LazyImport(".vr_validator", "vr_validator")

# Import ValidationDialog directly from its own module
try:
    from .validation_dialog import ValidationDialog
except ImportError:
    try:
        from validation_dialog import ValidationDialog
    except ImportError:
        ValidationDialog = None

# Import TagViewerDialog for tag viewing
try:
    from .tag_dialog import TagViewerDialog
except ImportError:
    try:
        from tag_dialog import TagViewerDialog
    except ImportError:
        TagViewerDialog = None

# Logic handler
DicomLogicHandler = LazyImport(".app_logic", "app_logic")

class DicomCreatorApp(tk.Tk):
    """Main application window for DICOM creation and editing.
    Provides tabs for Patient/Study/Series metadata, image loading, DICOM loading, and saving.
    """
    
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("800x600")
        self.resizable(True, True)

        # Logger
        self.logger = setup_logging()

        # Image-related state
        self.image_path = None
        self.pixel_array = None
        self._tk_img = None
        self.image_source = None  # Track if image is from file ("file") or DICOM ("dicom")

        # DICOM loading state
        self.grouped_dicom = {}
        self.selected_study_uid = None
        self.selected_series_uid = None
        
        # Server presets
        try:
            presets_cls = ServerPresetsManager._load_class()
            self.presets_manager = presets_cls() if presets_cls else None
        except Exception:
            self.presets_manager = None

        # Transmission history
        try:
            history_cls = TransmissionHistory._load_class()
            self.transmission_history = history_cls(logger=self.logger) if history_cls else None
            self.history = self.transmission_history  # Also set as self.history for convenience
        except Exception:
            self.transmission_history = None
            self.history = None

        # VR Validator
        self.vr_validator = None
        self.vr_validator_error = None
        try:
            validator_cls = VRValidator._load_class()
            if validator_cls is None:
                # LazyImport returned None - try to get more details
                try:
                    # Try to import directly to get the actual error
                    from .vr_validator import VRValidator as DirectImport
                    self.vr_validator = DirectImport(logger=self.logger)
                except Exception as direct_error:
                    self.vr_validator_error = f"VRValidator class could not be loaded: {direct_error}"
                    self.logger.exception("Direct import of VRValidator failed")
            else:
                self.vr_validator = validator_cls(logger=self.logger)
        except Exception as e:
            self.vr_validator_error = str(e)
            self.logger.exception("VR Validator not available")
            self.vr_validator = None

        # Tab visibility state
        self.tab_visibility = {
            "Patient": tk.BooleanVar(value=True),
            "Study": tk.BooleanVar(value=True),
            "Series/Modality": tk.BooleanVar(value=True),
            "Image": tk.BooleanVar(value=True),
            "Load DICOM": tk.BooleanVar(value=True),
            "Save": tk.BooleanVar(value=True),
            "Remote": tk.BooleanVar(value=True),
            "Query PACS": tk.BooleanVar(value=True),
            "Test/Generate": tk.BooleanVar(value=False),
            "Connection Test": tk.BooleanVar(value=False),
            "Stress Test": tk.BooleanVar(value=False),
            "Transmission History": tk.BooleanVar(value=False),
            "Benchmarking": tk.BooleanVar(value=False),
            "Parallel Send": tk.BooleanVar(value=False),
        }
        
        self.tab_frames = {}
        self.container = None

        self._build_ui()

    def _build_ui(self):
        """Build the overall UI: menu bar and a tabbed notebook with multiple sections."""
        # Menu bar
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Load", command=self.load_dicom_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Load Folder", command=self.load_dicom_folder, accelerator="Ctrl+Shift+O")
        file_menu.add_command(label="Save", command=self.save_dicom, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Validate", command=self.validate_current_data, accelerator="Ctrl+Shift+V")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Remote menu
        remote_menu = tk.Menu(menubar, tearoff=False)
        remote_menu.add_command(label="Send to Remote", command=lambda: self.send_remote(), accelerator="Ctrl+R")
        remote_menu.add_separator()
        remote_menu.add_command(label="Query PACS (C-FIND)...", command=self._switch_to_query_tab, accelerator="Ctrl+Q")
        remote_menu.add_separator()
        remote_menu.add_command(label="TLS Settings...", command=self.show_tls_settings)
        menubar.add_cascade(label="Remote", menu=remote_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_command(label="Core Tabs", state=tk.DISABLED)
        view_menu.add_checkbutton(label="Patient", variable=self.tab_visibility["Patient"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Study", variable=self.tab_visibility["Study"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Series/Modality", variable=self.tab_visibility["Series/Modality"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Image", variable=self.tab_visibility["Image"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Load DICOM", variable=self.tab_visibility["Load DICOM"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Save", variable=self.tab_visibility["Save"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Remote", variable=self.tab_visibility["Remote"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Query PACS", variable=self.tab_visibility["Query PACS"], command=self._update_tab_visibility)
        view_menu.add_separator()
        view_menu.add_command(label="Test Tabs", state=tk.DISABLED)
        view_menu.add_checkbutton(label="Test/Generate", variable=self.tab_visibility["Test/Generate"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Connection Test", variable=self.tab_visibility["Connection Test"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Stress Test", variable=self.tab_visibility["Stress Test"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Transmission History", variable=self.tab_visibility["Transmission History"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Benchmarking", variable=self.tab_visibility["Benchmarking"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Parallel Send", variable=self.tab_visibility["Parallel Send"], command=self._update_tab_visibility)
        view_menu.add_separator()
        view_menu.add_command(label="Show All", command=self._show_all_tabs)
        view_menu.add_command(label="Hide Test Tabs", command=self._hide_test_tabs)
        menubar.add_cascade(label="View", menu=view_menu)

        # VR menu
        vr_menu = tk.Menu(menubar, tearoff=False)
        vr_menu.add_command(label="View VRs", command=self.show_vr_viewer)
        vr_menu.add_command(label="View All Tags", command=self.show_tag_viewer)
        menubar.add_cascade(label="DICOM", menu=vr_menu)

        # About menu
        about_menu = tk.Menu(menubar, tearoff=False)
        about_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="About", menu=about_menu)

        self.config(menu=menubar)
        
        # Confirm on window close
        try:
            self.protocol("WM_DELETE_WINDOW", self.on_quit)
        except Exception:
            pass
            
        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-o>", lambda e: self.load_dicom_file())
        self.bind_all("<Control-O>", lambda e: self.load_dicom_folder())
        self.bind_all("<Control-s>", lambda e: self.save_dicom())
        self.bind_all("<Control-V>", lambda e: self.validate_current_data())
        self.bind_all("<Control-r>", lambda e: self.send_remote())
        self.bind_all("<Control-q>", lambda e: self._switch_to_query_tab())

        # Tabbed container for different sections
        container = ttk.Notebook(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.container = container

        self.patient_frame = ttk.Frame(container)
        self.study_frame = ttk.Frame(container)
        self.series_frame = ttk.Frame(container)
        self.image_frame = ttk.Frame(container)
        self.load_dcm_frame = ttk.Frame(container)
        self.save_frame = ttk.Frame(container)
        self.remote_frame = ttk.Frame(container)
        self.query_frame = ttk.Frame(container)
        self.test_frame = ttk.Frame(container)

        # Test tabs
        self.connection_test_frame = ttk.Frame(container)
        self.stress_test_frame = ttk.Frame(container)
        self.history_frame = ttk.Frame(container)
        self.benchmark_frame = ttk.Frame(container)
        self.parallel_frame = ttk.Frame(container)

        # Store tab references for visibility control
        self.tab_frames["Patient"] = (self.patient_frame, "Patient")
        self.tab_frames["Study"] = (self.study_frame, "Study")
        self.tab_frames["Series/Modality"] = (self.series_frame, "Series/Modality")
        self.tab_frames["Image"] = (self.image_frame, "Image")
        self.tab_frames["Load DICOM"] = (self.load_dcm_frame, "Load DICOM")
        self.tab_frames["Save"] = (self.save_frame, "Save")
        self.tab_frames["Remote"] = (self.remote_frame, "Remote")
        self.tab_frames["Query PACS"] = (self.query_frame, "Query PACS")
        self.tab_frames["Test/Generate"] = (self.test_frame, "Test/Generate")
        self.tab_frames["Connection Test"] = (self.connection_test_frame, "Connection Test")
        self.tab_frames["Stress Test"] = (self.stress_test_frame, "Stress Test")
        self.tab_frames["Transmission History"] = (self.history_frame, "Transmission History")
        self.tab_frames["Benchmarking"] = (self.benchmark_frame, "Benchmarking")
        self.tab_frames["Parallel Send"] = (self.parallel_frame, "Parallel Send")

        container.add(self.patient_frame, text="Patient")
        container.add(self.study_frame, text="Study")
        container.add(self.series_frame, text="Series/Modality")
        container.add(self.image_frame, text="Image")
        container.add(self.load_dcm_frame, text="Load DICOM")
        container.add(self.save_frame, text="Save")
        container.add(self.remote_frame, text="Remote")
        container.add(self.query_frame, text="Query PACS")
        container.add(self.test_frame, text="Test/Generate")
        container.add(self.connection_test_frame, text="Connection Test")
        container.add(self.stress_test_frame, text="Stress Test")
        container.add(self.history_frame, text="Transmission History")
        container.add(self.benchmark_frame, text="Benchmarking")
        container.add(self.parallel_frame, text="Parallel Send")

        # Patient fields
        self._build_patient_fields()
        
        # Study fields
        self._build_study_fields()
        
        # Series fields
        self._build_series_fields()
        
        # Image tab
        self._build_image_tab()
        
        # Load DICOM tab
        self._build_load_dicom_tab()
        
        # Save tab
        self._build_save_tab()
        
        # Remote tab
        self._build_remote_ui()

        # Query PACS tab
        self._build_query_pacs_tab()

        # Test/Generate tab
        self._build_test_tab()
        
        # Build new test tabs
        self._build_connection_test_tab()
        self._build_stress_test_tab()
        self._build_history_tab()
        self._build_benchmark_tab()
        self._build_parallel_tab()
        
        # Apply initial tab visibility (hide test tabs by default)
        self._update_tab_visibility()

    def _build_patient_fields(self):
        """Build patient metadata form fields."""
        self.patient_vars = {
            "PatientName": tk.StringVar(),
            "PatientID": tk.StringVar(),
            "PatientBirthDate": tk.StringVar(),
            "PatientSex": tk.StringVar(),
            "PatientAge": tk.StringVar(),
            "PatientWeight": tk.StringVar(),
            "PatientSize": tk.StringVar(),
            "PatientComments": tk.StringVar(),
            "PatientMothersBirthName": tk.StringVar(),
            "PatientDeathDateTime": tk.StringVar(),
            "PatientBirthTime": tk.StringVar(),
            "PatientAddress": tk.StringVar(),
            "PatientTelephoneNumbers": tk.StringVar(),
        }
        self._add_labeled_entry(self.patient_frame, "Patient Name", self.patient_vars["PatientName"], 0)
        self._add_labeled_entry(self.patient_frame, "Patient ID", self.patient_vars["PatientID"], 1)
        self._add_labeled_entry(self.patient_frame, "Birth Date (YYYYMMDD)", self.patient_vars["PatientBirthDate"], 2)
        self._add_labeled_entry(self.patient_frame, "Sex (M/F)", self.patient_vars["PatientSex"], 3)
        self._add_labeled_entry(self.patient_frame, "Patient Age (e.g., 032Y)", self.patient_vars["PatientAge"], 4)
        self._add_labeled_entry(self.patient_frame, "Patient Weight (kg)", self.patient_vars["PatientWeight"], 5)
        self._add_labeled_entry(self.patient_frame, "Patient Size/Height (m)", self.patient_vars["PatientSize"], 6)
        self._add_labeled_entry(self.patient_frame, "Patient Comments", self.patient_vars["PatientComments"], 7)
        self._add_labeled_entry(self.patient_frame, "Mother's Birth Name", self.patient_vars["PatientMothersBirthName"], 8)
        self._add_labeled_entry(self.patient_frame, "Datetime of death\n(YYYYMMDDHHMMSS)", self.patient_vars["PatientDeathDateTime"], 9)
        self._add_labeled_entry(self.patient_frame, "Birth Time (HHMMSS)", self.patient_vars["PatientBirthTime"], 10)
        self._add_labeled_entry(self.patient_frame, "Address", self.patient_vars["PatientAddress"], 11)
        self._add_labeled_entry(self.patient_frame, "Telephone Numbers", self.patient_vars["PatientTelephoneNumbers"], 12)

    def _build_study_fields(self):
        """Build study metadata form fields."""
        self.study_vars = {
            "StudyInstanceUID": tk.StringVar(),
            "StudyDate": tk.StringVar(),
            "StudyTime": tk.StringVar(),
            "StudyDescription": tk.StringVar(),
            "AccessionNumber": tk.StringVar(),
            "StudyID": tk.StringVar(),
            "ReferringPhysicianName": tk.StringVar(),
            "ReadingPhysicianName": tk.StringVar(),
            "ReasonForStudy": tk.StringVar(),
            "AdmittingDiagnosesDescription": tk.StringVar(),
            "StudyPatientLocation": tk.StringVar(),
        }
        self._add_labeled_entry(self.study_frame, "Study Instance UID (optional)", self.study_vars["StudyInstanceUID"], 0)
        self._add_labeled_entry(self.study_frame, "Study Date (YYYYMMDD)", self.study_vars["StudyDate"], 1)
        self._add_labeled_entry(self.study_frame, "Study Time (HHMMSS)", self.study_vars["StudyTime"], 2)
        self._add_labeled_entry(self.study_frame, "Study Description", self.study_vars["StudyDescription"], 3)
        self._add_labeled_entry(self.study_frame, "Accession Number", self.study_vars["AccessionNumber"], 4)
        self._add_labeled_entry(self.study_frame, "Study ID", self.study_vars["StudyID"], 5)
        self._add_labeled_entry(self.study_frame, "Referring Physician Name", self.study_vars["ReferringPhysicianName"], 6)
        self._add_labeled_entry(self.study_frame, "Reading Physician Name", self.study_vars["ReadingPhysicianName"], 7)
        self._add_labeled_entry(self.study_frame, "Reason For Study", self.study_vars["ReasonForStudy"], 8)
        self._add_labeled_entry(self.study_frame, "Admitting Diagnoses Description", self.study_vars["AdmittingDiagnosesDescription"], 9)
        self._add_labeled_entry(self.study_frame, "Study Patient Location", self.study_vars["StudyPatientLocation"], 10)

    def _build_series_fields(self):
        """Build series metadata form fields."""
        self.series_vars = {
            "SeriesInstanceUID": tk.StringVar(),
            "SeriesNumber": tk.StringVar(),
            "Modality": tk.StringVar(value="SC"),
            "SeriesDescription": tk.StringVar(),
            "BodyPartExamined": tk.StringVar(),
            "ProtocolName": tk.StringVar(),
            "SeriesDate": tk.StringVar(),
            "SeriesTime": tk.StringVar(),
            "PerformingPhysicianName": tk.StringVar(),
            "OperatorsName": tk.StringVar(),
            "Laterality": tk.StringVar(),
        }
        self._add_labeled_entry(self.series_frame, "Series Instance UID (optional)", self.series_vars["SeriesInstanceUID"], 0)
        self._add_labeled_entry(self.series_frame, "Series Number", self.series_vars["SeriesNumber"], 1)
        self._add_labeled_entry(self.series_frame, "Modality", self.series_vars["Modality"], 2)
        self._add_labeled_entry(self.series_frame, "Series Description", self.series_vars["SeriesDescription"], 3)
        self._add_labeled_entry(self.series_frame, "Body Part Examined", self.series_vars["BodyPartExamined"], 4)
        self._add_labeled_entry(self.series_frame, "Protocol Name", self.series_vars["ProtocolName"], 5)
        self._add_labeled_entry(self.series_frame, "Series Date (YYYYMMDD)", self.series_vars["SeriesDate"], 6)
        self._add_labeled_entry(self.series_frame, "Series Time (HHMMSS)", self.series_vars["SeriesTime"], 7)
        self._add_labeled_entry(self.series_frame, "Performing Physician Name", self.series_vars["PerformingPhysicianName"], 8)
        self._add_labeled_entry(self.series_frame, "Operator's Name", self.series_vars["OperatorsName"], 9)
        self._add_labeled_entry(self.series_frame, "Laterality (L/R)", self.series_vars["Laterality"], 10)

    def _build_image_tab(self):
        """Build image loading and preview tab."""
        img_controls = ttk.Frame(self.image_frame)
        img_controls.pack(fill=tk.X, pady=10)
        ttk.Button(img_controls, text="Load Image", command=self.load_image).pack(side=tk.LEFT)
        self.image_label = ttk.Label(self.image_frame, text="No image loaded")
        self.image_label.pack(fill=tk.X, pady=10)
        self.preview_label = ttk.Label(self.image_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

    def _build_save_tab(self):
        """Build DICOM save tab."""
        ttk.Button(self.save_frame, text="Save DICOM", command=self.save_dicom).pack(pady=20)

    def _build_load_dicom_tab(self):
        """Build DICOM loading and tree view tab."""
        dcm_controls = ttk.Frame(self.load_dcm_frame)
        dcm_controls.pack(fill=tk.X, pady=10)
        ttk.Button(dcm_controls, text="Load DICOM File(s)", command=self.load_dicom_file).pack(side=tk.LEFT)
        ttk.Button(dcm_controls, text="Load DICOM Folder", command=self.load_dicom_folder).pack(side=tk.LEFT, padx=8)
        self.dcm_info_label = ttk.Label(self.load_dcm_frame, text="No DICOM loaded")
        self.dcm_info_label.pack(fill=tk.X, pady=10)

        # Studies/Series tree with scrollbars
        tree_container = ttk.Frame(self.load_dcm_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.series_tree = ttk.Treeview(tree_container, columns=("desc"), show="tree", height=24)
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.series_tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.series_tree.xview)
        self.series_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.series_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.series_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.series_tree.bind("<Button-3>", self._show_instance_context_menu)
    
        # CREATE CONTEXT MENU:
        self.instance_context_menu = tk.Menu(self, tearoff=0)
        self.instance_context_menu.add_command(label="Show Image", command=self._show_instance_image)

    def _add_labeled_entry(self, parent, label, var, row):
        """Helper: create a label + entry bound to a StringVar, aligned in a grid row."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        parent.columnconfigure(0, weight=1)
        ttk.Label(frame, text=label, width=30).pack(side=tk.LEFT)
        ttk.Entry(frame, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _build_remote_ui(self):
        """Build remote DICOM transmission tab."""
        self.remote_vars = {
            "server": tk.StringVar(),
            "port": tk.StringVar(value="4321"),
            "calling_ae": tk.StringVar(value="DCMCREATOR"),
            "called_ae": tk.StringVar(value="AcuoMed1"),
            "preset_name": tk.StringVar(),
            "skip_c_echo": tk.BooleanVar(value=False),
            "use_tls": tk.BooleanVar(value=False),
        }
        
        # TLS configuration storage
        self.tls_config = {}
        
        # Preset management section
        preset_frame = ttk.LabelFrame(self.remote_frame, text="Server Presets", padding=10)
        preset_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.remote_frame.columnconfigure(0, weight=1)
        
        preset_inner = ttk.Frame(preset_frame)
        preset_inner.pack(fill=tk.X)
        preset_inner.columnconfigure(1, weight=1)
        
        ttk.Label(preset_inner, text="Preset:").grid(row=0, column=0, sticky="w", padx=5)
        self.preset_combo = ttk.Combobox(preset_inner, textvariable=self.remote_vars["preset_name"], state="readonly")
        self.preset_combo.grid(row=0, column=1, sticky="ew", padx=5)
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)
        
        preset_btn_frame = ttk.Frame(preset_frame)
        preset_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(preset_btn_frame, text="Load", command=self._load_preset).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_btn_frame, text="Save Current", command=self._save_current_preset).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_btn_frame, text="Delete", command=self._delete_preset).pack(side=tk.LEFT, padx=2)
        
        # Refresh presets list on startup
        self._refresh_presets_list()
        
        # Server configuration section
        config_frame = ttk.LabelFrame(self.remote_frame, text="Server Configuration", padding=10)
        config_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.remote_frame.columnconfigure(0, weight=1)
        
        self._add_labeled_entry(config_frame, "Server (IP/Name)", self.remote_vars["server"], 0)
        self._add_labeled_entry(config_frame, "Port", self.remote_vars["port"], 1)
        self._add_labeled_entry(config_frame, "Calling AE Title", self.remote_vars["calling_ae"], 2)
        self._add_labeled_entry(config_frame, "Called AE Title", self.remote_vars["called_ae"], 3)
        ttk.Checkbutton(config_frame, text="Skip C-ECHO", variable=self.remote_vars["skip_c_echo"]).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(config_frame, text="Use TLS/SSL", variable=self.remote_vars["use_tls"]).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Send button
        btn_row = ttk.Frame(self.remote_frame)
        btn_row.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.remote_send_button = ttk.Button(btn_row, text="Send All Loaded DICOM", command=self.send_remote)
        self.remote_send_button.pack(side=tk.LEFT)

        # Message area
        msg_row = ttk.Frame(self.remote_frame)
        msg_row.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        self.remote_frame.rowconfigure(3, weight=1)
        self.remote_frame.columnconfigure(0, weight=1)
        ttk.Label(msg_row, text="Messages / Errors:").pack(anchor=tk.W)
        self.remote_messages = tk.Text(msg_row, height=8, wrap="word")
        self.remote_messages.pack(fill=tk.BOTH, expand=True)
        self.remote_messages.configure(state=tk.DISABLED)

    def _build_query_pacs_tab(self):
        """Build Query PACS tab for C-FIND queries."""
        if DicomQueryHandler is None:
            label = ttk.Label(self.query_frame, text="Query/Retrieve module not available")
            label.pack(padx=10, pady=10)
            return

        # Title
        title_frame = ttk.Frame(self.query_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="DICOM Query (C-FIND)", font=("Arial", 12, "bold")).pack()

        # Server Configuration Section (can use presets from Remote tab)
        server_frame = ttk.LabelFrame(self.query_frame, text="PACS Server Configuration", padding=10)
        server_frame.pack(fill=tk.X, padx=10, pady=5)

        server_inner = ttk.Frame(server_frame)
        server_inner.pack(fill=tk.X)
        server_inner.columnconfigure(1, weight=1)

        ttk.Label(server_inner, text="Server:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.query_server = tk.StringVar()
        ttk.Entry(server_inner, textvariable=self.query_server).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(server_inner, text="Port:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.query_port = tk.StringVar(value="104")
        ttk.Entry(server_inner, textvariable=self.query_port, width=10).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(server_inner, text="Calling AE:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.query_calling_ae = tk.StringVar(value="DCMCREATOR")
        ttk.Entry(server_inner, textvariable=self.query_calling_ae).grid(row=2, column=1, sticky="ew", padx=5)

        ttk.Label(server_inner, text="Called AE:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.query_called_ae = tk.StringVar(value="ANY-SCP")
        ttk.Entry(server_inner, textvariable=self.query_called_ae).grid(row=3, column=1, sticky="ew", padx=5)

        # Copy from Remote button
        ttk.Button(server_inner, text="Copy from Remote Tab", 
                  command=self._copy_remote_to_query).grid(row=4, column=1, sticky="e", padx=5, pady=5)

        # Search Criteria Section
        search_frame = ttk.LabelFrame(self.query_frame, text="Search Criteria", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        search_inner = ttk.Frame(search_frame)
        search_inner.pack(fill=tk.X)
        search_inner.columnconfigure(1, weight=1)
        search_inner.columnconfigure(3, weight=1)

        # Query Level
        ttk.Label(search_inner, text="Query Level:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.query_level = tk.StringVar(value="STUDY")
        query_level_combo = ttk.Combobox(search_inner, textvariable=self.query_level, 
                                        values=["PATIENT", "STUDY", "SERIES", "IMAGE"],
                                        state="readonly", width=15)
        query_level_combo.grid(row=0, column=1, sticky="w", padx=5)

        # Patient Name
        ttk.Label(search_inner, text="Patient Name:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.query_patient_name = tk.StringVar()
        ttk.Entry(search_inner, textvariable=self.query_patient_name).grid(row=1, column=1, sticky="ew", padx=5)

        # Patient ID
        ttk.Label(search_inner, text="Patient ID:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.query_patient_id = tk.StringVar()
        ttk.Entry(search_inner, textvariable=self.query_patient_id).grid(row=1, column=3, sticky="ew", padx=5)

        # Study Date Range
        ttk.Label(search_inner, text="Study Date From:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.query_study_date_from = tk.StringVar()
        ttk.Entry(search_inner, textvariable=self.query_study_date_from, 
                 width=12).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(search_inner, text="To:").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        self.query_study_date_to = tk.StringVar()
        ttk.Entry(search_inner, textvariable=self.query_study_date_to, 
                 width=12).grid(row=2, column=3, sticky="w", padx=5)

        # Study Description
        ttk.Label(search_inner, text="Study Description:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.query_study_desc = tk.StringVar()
        ttk.Entry(search_inner, textvariable=self.query_study_desc).grid(row=3, column=1, sticky="ew", padx=5)

        # Accession Number
        ttk.Label(search_inner, text="Accession #:").grid(row=3, column=2, sticky="w", padx=5, pady=2)
        self.query_accession = tk.StringVar()
        ttk.Entry(search_inner, textvariable=self.query_accession).grid(row=3, column=3, sticky="ew", padx=5)

        # Modality
        ttk.Label(search_inner, text="Modality:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.query_modality = tk.StringVar()
        modality_combo = ttk.Combobox(search_inner, textvariable=self.query_modality,
                                      values=["", "CT", "MR", "US", "CR", "DX", "MG", "NM", "PT", "XA"],
                                      width=10)
        modality_combo.grid(row=4, column=1, sticky="w", padx=5)

        # Action Buttons
        btn_frame = ttk.Frame(self.query_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="Query PACS", command=self._execute_query,
                  style="Accent.TButton" if hasattr(ttk, "Accent") else "").pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear Results", command=self._clear_query_results).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear Form", command=self._clear_query_form).pack(side=tk.LEFT, padx=2)

        # Results Section
        results_frame = ttk.LabelFrame(self.query_frame, text="Query Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Results tree with scrollbars
        tree_container = ttk.Frame(results_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        # Define columns based on query level
        columns = ("patient_id", "patient_name", "study_date", "study_desc", "modality", "accession")
        self.query_results_tree = ttk.Treeview(tree_container, columns=columns, show="tree headings", height=12)

        # Configure columns
        self.query_results_tree.heading("#0", text="Level")
        self.query_results_tree.heading("patient_id", text="Patient ID")
        self.query_results_tree.heading("patient_name", text="Patient Name")
        self.query_results_tree.heading("study_date", text="Study Date")
        self.query_results_tree.heading("study_desc", text="Study Description")
        self.query_results_tree.heading("modality", text="Modality")
        self.query_results_tree.heading("accession", text="Accession #")

        self.query_results_tree.column("#0", width=80, anchor="center")
        self.query_results_tree.column("patient_id", width=100, anchor="w")
        self.query_results_tree.column("patient_name", width=150, anchor="w")
        self.query_results_tree.column("study_date", width=100, anchor="center")
        self.query_results_tree.column("study_desc", width=200, anchor="w")
        self.query_results_tree.column("modality", width=60, anchor="center")
        self.query_results_tree.column("accession", width=100, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.query_results_tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.query_results_tree.xview)
        self.query_results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.query_results_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Status label
        self.query_status_label = ttk.Label(results_frame, text="No query executed yet")
        self.query_status_label.pack(fill=tk.X, pady=5)

        # Double-click to load study (future C-GET integration)
        self.query_results_tree.bind("<Double-Button-1>", self._on_query_result_double_click)

    def _copy_remote_to_query(self):
        """Copy server settings from Remote tab to Query PACS tab."""
        try:
            self.query_server.set(self.remote_vars["server"].get())
            self.query_port.set(self.remote_vars["port"].get())
            self.query_calling_ae.set(self.remote_vars["calling_ae"].get())
            self.query_called_ae.set(self.remote_vars["called_ae"].get())
            messagebox.showinfo(APP_TITLE, "Server settings copied from Remote tab")
        except Exception as e:
            self.logger.exception("Failed to copy remote settings")
            messagebox.showerror(APP_TITLE, f"Failed to copy settings: {e}")

    def _execute_query(self):
        """Execute C-FIND query against PACS."""
        if DicomQueryHandler is None:
            messagebox.showerror(APP_TITLE, "Query module not available")
            return

        # Validate inputs
        server = self.query_server.get().strip()
        port_str = self.query_port.get().strip()
        calling_ae = self.query_calling_ae.get().strip()
        called_ae = self.query_called_ae.get().strip()
        query_level = self.query_level.get()

        if not server or not port_str:
            messagebox.showerror(APP_TITLE, "Server and port are required")
            return

        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror(APP_TITLE, "Port must be a number")
            return

        # Build search criteria
        search_criteria = {}

        if self.query_patient_name.get().strip():
            search_criteria['PatientName'] = self.query_patient_name.get().strip()
        if self.query_patient_id.get().strip():
            search_criteria['PatientID'] = self.query_patient_id.get().strip()
        if self.query_study_desc.get().strip():
            search_criteria['StudyDescription'] = self.query_study_desc.get().strip()
        if self.query_accession.get().strip():
            search_criteria['AccessionNumber'] = self.query_accession.get().strip()
        if self.query_modality.get().strip():
            search_criteria['Modality'] = self.query_modality.get().strip()

        # Handle date range
        date_from = self.query_study_date_from.get().strip()
        date_to = self.query_study_date_to.get().strip()
        if date_from or date_to:
            if date_from and date_to:
                search_criteria['StudyDate'] = f"{date_from}-{date_to}"
            elif date_from:
                search_criteria['StudyDate'] = f"{date_from}-"
            elif date_to:
                search_criteria['StudyDate'] = f"-{date_to}"

        # Update status
        self.query_status_label.config(text=f"Querying {server}:{port}...")
        self.update_idletasks()

        # Execute query in background thread
        def query_worker():
            try:
                handler_cls = DicomQueryHandler._load_class()
                if handler_cls is None:
                    self.after(0, lambda: messagebox.showerror(APP_TITLE, "Failed to load query handler"))
                    return

                handler = handler_cls(logger=self.logger)

                success, results, message = handler.query_pacs(
                    server=server,
                    port=port,
                    calling_ae=calling_ae,
                    called_ae=called_ae,
                    query_level=query_level,
                    search_criteria=search_criteria,
                    query_model="StudyRoot"
                )

                # Update UI in main thread
                self.after(0, lambda: self._display_query_results(success, results, message))

            except Exception as e:
                self.logger.exception("Query execution failed")
                self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Query failed: {e}"))
                self.after(0, lambda: self.query_status_label.config(text="Query failed"))

        thread = threading.Thread(target=query_worker, daemon=True)
        thread.start()

    def _display_query_results(self, success: bool, results: list, message: str):
        """Display query results in the tree view."""
        # Clear existing results
        for item in self.query_results_tree.get_children():
            self.query_results_tree.delete(item)

        if not success:
            self.query_status_label.config(text=f"Query failed: {message}")
            messagebox.showerror(APP_TITLE, f"Query failed: {message}")
            return

        if not results:
            self.query_status_label.config(text="Query completed - No results found")
            messagebox.showinfo(APP_TITLE, "No results found matching search criteria")
            return

        # Display results
        for i, result in enumerate(results):
            values = (
                result.patient_id,
                result.patient_name,
                result.study_date,
                result.study_description,
                result.modality,
                result.accession_number
            )

            # Insert with level as tree text
            self.query_results_tree.insert(
                "", "end", 
                text=result.level,
                values=values,
                tags=(f"result_{i}",)
            )

        self.query_status_label.config(text=f"Found {len(results)} results")
        self.logger.info(f"Query completed: {len(results)} results")

    def _clear_query_results(self):
        """Clear query results tree."""
        for item in self.query_results_tree.get_children():
            self.query_results_tree.delete(item)
        self.query_status_label.config(text="Results cleared")

    def _clear_query_form(self):
        """Clear all search criteria fields."""
        self.query_patient_name.set("")
        self.query_patient_id.set("")
        self.query_study_date_from.set("")
        self.query_study_date_to.set("")
        self.query_study_desc.set("")
        self.query_accession.set("")
        self.query_modality.set("")
        self.query_level.set("STUDY")

    def _on_query_result_double_click(self, event):
        """Handle double-click on query result (placeholder for future C-GET)."""
        selection = self.query_results_tree.selection()
        if not selection:
            return

        item = self.query_results_tree.item(selection[0])
        values = item['values']

        messagebox.showinfo(
            APP_TITLE,
            f"C-GET (Download) Feature\n\n"
            f"This will download the selected study/series.\n\n"
            f"Patient: {values[1]}\n"
            f"Study: {values[3]}\n\n"
            f"C-GET functionality coming in next phase!"
        )

    def _build_test_tab(self):
        """Build Test/Generator tab for creating and testing bulk DICOM transmission."""
        # Generator section
        gen_frame = ttk.LabelFrame(self.test_frame, text="DICOM Generator", padding=10)
        gen_frame.pack(fill=tk.X, padx=10, pady=5)
        
        gen_inner = ttk.Frame(gen_frame)
        gen_inner.pack(fill=tk.X)
        gen_inner.columnconfigure(1, weight=1)
        gen_inner.columnconfigure(3, weight=1)
        
        # Hierarchy controls
        ttk.Label(gen_inner, text="Studies/Patient:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.test_vars = {}
        self.test_vars["studies_per_patient"] = tk.StringVar(value="1")
        ttk.Entry(gen_inner, textvariable=self.test_vars["studies_per_patient"], width=10).grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(gen_inner, text="Series/Study:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.test_vars["series_per_study"] = tk.StringVar(value="1")
        ttk.Entry(gen_inner, textvariable=self.test_vars["series_per_study"], width=10).grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(gen_inner, text="Instances/Series:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.test_vars["instances_per_series"] = tk.StringVar(value="1")
        ttk.Entry(gen_inner, textvariable=self.test_vars["instances_per_series"], width=10).grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(gen_inner, text="Size/File (MB):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.test_vars["size_mb"] = tk.StringVar(value="1.0")
        ttk.Entry(gen_inner, textvariable=self.test_vars["size_mb"], width=10).grid(row=1, column=3, sticky="w", padx=5)
        
        # Total count display (calculated)
        ttk.Label(gen_inner, text="Total Files:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.test_vars["total_count_label"] = tk.StringVar(value="1")
        total_label = ttk.Label(gen_inner, textvariable=self.test_vars["total_count_label"], 
                               font=("Arial", 10, "bold"), foreground="blue")
        total_label.grid(row=2, column=1, sticky="w", padx=5)
        
        # Bind calculation to input changes
        self.test_vars["studies_per_patient"].trace('w', self._update_total_count)
        self.test_vars["series_per_study"].trace('w', self._update_total_count)
        self.test_vars["instances_per_series"].trace('w', self._update_total_count)
        
        # Output directory
        ttk.Label(gen_inner, text="Output Dir:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.test_vars["output_dir"] = tk.StringVar()
        ttk.Entry(gen_inner, textvariable=self.test_vars["output_dir"]).grid(row=3, column=1, columnspan=2, sticky="ew", padx=5)
        ttk.Button(gen_inner, text="Browse", command=self._select_test_output_dir, width=8).grid(row=3, column=3, padx=5)
        
        gen_buttons = ttk.Frame(gen_frame)
        gen_buttons.pack(fill=tk.X, pady=10)
        ttk.Button(gen_buttons, text="Generate DICOMs", command=self._generate_test_dicoms).pack(side=tk.LEFT, padx=2)
        ttk.Button(gen_buttons, text="Generate & Send", command=self._generate_and_send).pack(side=tk.LEFT, padx=2)
        
        # Test section
        test_frame = ttk.LabelFrame(self.test_frame, text="Test Transmission", padding=10)
        test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        test_inner = ttk.Frame(test_frame)
        test_inner.pack(fill=tk.X)
        
        ttk.Button(test_inner, text="Test Connection", command=self._test_connection).pack(side=tk.LEFT, padx=2)
        ttk.Button(test_inner, text="Send All Generated", command=self._send_generated_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(test_inner, text="View Results", command=self._view_test_results).pack(side=tk.LEFT, padx=2)
        
        # Status section
        status_frame = ttk.LabelFrame(self.test_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.test_status = tk.Text(status_frame, height=15, wrap="word")
        self.test_status.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.test_status.yview)
        self.test_status.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _select_test_output_dir(self):
        """Select output directory for generated DICOMs."""
        folder = filedialog.askdirectory(title="Select output directory for test DICOMs")
        if folder:
            self.test_vars["output_dir"].set(folder)
    
    def _update_total_count(self, *args):
        """Calculate and update the total file count based on hierarchy."""
        try:
            studies = int(self.test_vars["studies_per_patient"].get() or 1)
            series = int(self.test_vars["series_per_study"].get() or 1)
            instances = int(self.test_vars["instances_per_series"].get() or 1)
            total = studies * series * instances
            self.test_vars["total_count_label"].set(str(total))
        except (ValueError, KeyError):
            self.test_vars["total_count_label"].set("?")

    def _generate_test_dicoms(self):
        """Generate test DICOM files using hierarchical structure."""
        if RandomDicomGenerator is None:
            messagebox.showerror(APP_TITLE, "RandomDicomGenerator not available")
            return

        try:
            # Get hierarchy parameters
            studies_per_patient = int(self.test_vars["studies_per_patient"].get())
            series_per_study = int(self.test_vars["series_per_study"].get())
            instances_per_series = int(self.test_vars["instances_per_series"].get())
            size_mb = float(self.test_vars["size_mb"].get())
            output_dir = self.test_vars["output_dir"].get()
            
            # Calculate total count
            total_count = studies_per_patient * series_per_study * instances_per_series

            if not output_dir:
                messagebox.showerror(APP_TITLE, "Please select an output directory")
                return
            
            if total_count <= 0:
                messagebox.showerror(APP_TITLE, "Invalid counts: all values must be positive")
                return

            self._append_test_status(f"Generating {total_count} test DICOMs ({size_mb}MB each)...")
            self._append_test_status(f"  Hierarchy: {studies_per_patient} study(ies) x {series_per_study} series x {instances_per_series} instance(s)")

            generator = RandomDicomGenerator(logger=self.logger)
            
            # Use hierarchical generation method
            files = generator.generate_hierarchical(
                studies_per_patient=studies_per_patient,
                series_per_study=series_per_study,
                instances_per_series=instances_per_series,
                size_mb=size_mb,
                output_dir=output_dir
            )

            self._append_test_status(f"  Generated {len(files)} hierarchical DICOM files")
            self._append_test_status(f"  Location: {output_dir}")
            self._append_test_status(f"  Structure: Patient: {studies_per_patient} Studies -> {series_per_study} Series -> {instances_per_series} Instances")

            messagebox.showinfo(APP_TITLE, f"Generated {len(files)} hierarchical DICOM files")
        except ValueError as ve:
            messagebox.showerror(APP_TITLE, f"Invalid input: {ve}")
        except Exception as e:
            self.logger.exception("Failed to generate test DICOMs")
            messagebox.showerror(APP_TITLE, f"Generation failed: {e}")

    def _generate_and_send(self):
        """Generate test DICOMs and send them to the remote server."""
        self._generate_test_dicoms()
        self._send_generated_files()

    def _send_generated_files(self):
        """Send all generated files to remote server."""
        output_dir = self.test_vars["output_dir"].get()
        if not output_dir or not os.path.exists(output_dir):
            messagebox.showerror(APP_TITLE, "No valid output directory")
            return

        # Load all DICOMs from directory
        self._append_test_status("\nLoading generated DICOMs...")
        try:
            from .dcm import load_dicom_grouped
        except:
            try:
                from dcm import load_dicom_grouped
            except:
                messagebox.showerror(APP_TITLE, "Failed to import DICOM loader")
                return

        try:
            grouped = load_dicom_grouped(output_dir)
            self._append_test_status(f"? Loaded {sum(len(v) for v in grouped.values())} instances")

            # Store grouped DICOM for sending
            self.grouped_dicom = grouped
            
            # Extract patient info from first DICOM and populate form fields
            if grouped:
                first_study_uid = list(grouped.keys())[0]
                first_series_uid = list(grouped[first_study_uid].keys())[0]
                instances = grouped[first_study_uid][first_series_uid]
                if instances:
                    ds, arr = instances[0]
                    # Populate form fields from the generated DICOM
                    self._populate_patient_fields(ds)
                    self._populate_study_fields(ds)
                    self._populate_series_fields(ds)
                    
                    # Update pixel array if available
                    if arr is not None:
                        self.pixel_array = arr
                        self.image_source = "dicom"
                        self._update_image_preview(arr)
                    
                    self._append_test_status(f"? Populated form fields from generated DICOM")

            # Send to remote
            self.send_remote();
        except Exception as e:
            self.logger.exception("Failed to load generated DICOMs")
            messagebox.showerror(APP_TITLE, f"Failed to load DICOMs: {e}")

    def _test_connection(self):
        """Test connection to remote DICOM server."""
        server = self.remote_vars["server"].get().strip()
        port_s = self.remote_vars["port"].get().strip()
        calling_ae = self.remote_vars["calling_ae"].get().strip() or "DCMCREATOR"
        called_ae = self.remote_vars["called_ae"].get().strip() or "ANY-SCP"

        if not server or not port_s:
            messagebox.showerror(APP_TITLE, "Server and port are required")
            return

        try:
            port = int(port_s)
        except:
            messagebox.showerror(APP_TITLE, "Port must be numeric")
            return

        self._append_test_status("\nTesting connection...")

        def test_worker():
            try:
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)

                self._append_test_status(f"  Connecting to {server}:{port}...")
                result = sock.connect_ex((server, port))
                sock.close()

                if result == 0:
                    self._append_test_status(f"  ? Connection successful")
                    self.after(0, lambda: messagebox.showinfo(APP_TITLE, "Connection test PASSED"))
                else:
                    self._append_test_status(f"  ? Connection failed (errno {result})")
                    self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Connection FAILED (errno {result})"))
            except Exception as e:
                self._append_test_status(f"  ? Error: {e}")
                self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Test failed: {e}"))

        t = threading.Thread(target=test_worker, daemon=True)
        t.start()

    def _view_test_results(self):
        """View test results (placeholder)."""
        if TestRunner is None:
            messagebox.showinfo(APP_TITLE, "TestRunner not available yet")
            return

        results = "Test Results\n" + "=" * 50 + "\n\nNo tests run yet"
        messagebox.showinfo(APP_TITLE, results)

    def _append_test_status(self, text):
        """Append text to test status area."""
        try:
            self.test_status.configure(state=tk.NORMAL)
            self.test_status.insert(tk.END, text + "\n")
            self.test_status.see(tk.END)
            self.test_status.configure(state=tk.DISABLED)
            self.test_status.update_idletasks()
        except Exception:
            pass

    def _switch_to_query_tab(self):
        """Switch to the Query PACS tab."""
        try:
            for i, tab_id in enumerate(self.container.tabs()):
                if self.container.tab(tab_id, "text") == "Query PACS":
                    self.container.select(i)
                    return
            # If tab not visible, show it first
            self.tab_visibility["Query PACS"].set(True)
            self._update_tab_visibility()
            # Now switch to it
            for i, tab_id in enumerate(self.container.tabs()):
                if self.container.tab(tab_id, "text") == "Query PACS":
                    self.container.select(i)
                    return
        except Exception as e:
            self.logger.exception("Failed to switch to Query PACS tab")

    def new_file(self):
        """Clear all metadata, loaded images, and loaded DICOM."""
        if not messagebox.askyesno(APP_TITLE, "This will clear all metadata, loaded images, and loaded DICOM. Continue?"):
            return
            
        # Clear form fields
        for d in (self.patient_vars, self.study_vars, self.series_vars):
            for v in d.values():
                v.set("")

        # Reset image-related state
        self.image_path = None
        self.pixel_array = None
        self._tk_img = None
        self.image_source = None
        self.image_label.config(text="No image loaded")
        try:
            self.preview_label.configure(image="")
        except Exception:
            pass

        # Reset DICOM-loaded structures
        self.grouped_dicom = {}
        try:
            self.series_tree.delete(*self.series_tree.get_children())
        except Exception:
            pass
        self.dcm_info_label.config(text="No DICOM loaded")

        # Reset selected identifiers
        self.selected_study_uid = None
        self.selected_series_uid = None

        # Clear remote messages
        try:
            self.remote_messages.configure(state=tk.NORMAL)
            self.remote_messages.delete("1.0", tk.END)
            self.remote_messages.configure(state=tk.DISABLED)
        except Exception:
            pass

    def show_about(self):
        """Show About dialog."""
        messagebox.showinfo(
            APP_TITLE,
            f"{APP_TITLE}(c) 2025-2026 by Piotr Rozentreter\n\n"
            "A tool to create, edit, test and send DICOM metadata and images.\n\n"
            "Features:\n"
            "- DICOM creation and editing\n"
            "- C-STORE transmission to PACS\n"
            "- C-FIND query/retrieve (NEW)\n"
            "- Stress testing and benchmarking\n"
            "- VR validation\n"
            "- TLS/SSL support"
        )

    def show_tls_settings(self):
        """Show TLS/SSL settings dialog."""
        try:
            from .tls_dialog import TLSSettingsDialog
        except ImportError:
            try:
                from tls_dialog import TLSSettingsDialog
            except ImportError as e:
                self.logger.exception("Failed to import TLS dialog")
                messagebox.showerror(
                    APP_TITLE,
                    f"TLS Settings dialog is not available: {e}"
                )
                return
        
        dialog = TLSSettingsDialog(self, self.logger, self.tls_config)
        self.wait_window(dialog)
        
        result = dialog.get_result()
        if result is not None:
            self.tls_config = result
            self.logger.info("TLS configuration updated")
            messagebox.showinfo(
                APP_TITLE,
                "TLS settings have been saved.\n\n"
                "Enable 'Use TLS/SSL' checkbox on Remote tab to use these settings."
            )

    def show_vr_viewer(self):
        """Show DICOM Value Representation viewer dialog."""
        VRViewerDialog(self, self.logger)

    def show_tag_viewer(self):
        """Show DICOM Tag viewer dialog for viewing all tags from loaded file or dataset."""
        if TagViewerDialog is None:
            messagebox.showerror(
                APP_TITLE,
                "Tag Viewer is not available.\n\n"
                "The tag_dialog module could not be loaded."
            )
            return
        
        # Determine what to show
        # Priority: 1. Selected series, 2. First series in grouped_dicom, 3. Ask user to select file
        dataset = None
        filepath = None
        
        # Try to get dataset from selected series
        if self.selected_study_uid and self.selected_series_uid:
            instances = self.grouped_dicom.get(self.selected_study_uid, {}).get(self.selected_series_uid, [])
            if instances:
                dataset, _ = instances[0]
        # Try to get first available dataset
        elif self.grouped_dicom:
            for study_uid, series_map in self.grouped_dicom.items():
                for series_uid, instances in series_map.items():
                    if instances:
                        dataset, _ = instances[0]
                        break
                if dataset:
                    break
        
        # If we have a dataset, show it
        if dataset:
            TagViewerDialog(self, self.logger, dataset=dataset)
        else:
            # No dataset loaded, ask user to select a file
            if messagebox.askyesno(
                APP_TITLE,
                "No DICOM loaded. Would you like to select a DICOM file to view tags?"
            ):
                filepath = filedialog.askopenfilename(
                    title="Select DICOM file to view tags",
                    filetypes=[("DICOM Files", "*.dcm;*.dicom;*"), ("All Files", "*.*")]
                )
                if filepath:
                    TagViewerDialog(self, self.logger, filepath=filepath)

    def validate_current_data(self):
        """Validate current form data and show validation report."""
        if self.vr_validator is None:
            error_details = ""
            if self.vr_validator_error:
                error_details = f"\n\nError details:\n{self.vr_validator_error}"
            
            messagebox.showerror(
                APP_TITLE,
                f"VR Validator is not available.{error_details}\n\n"
                "The validator module could not be loaded.\n"
                "Check the log for more details."
            )
            return
        
        try:
            # Collect all form fields
            all_fields = {}
            
            # Patient fields
            for field_name, var in self.patient_vars.items():
                all_fields[field_name] = var
            
            # Study fields
            for field_name, var in self.study_vars.items():
                all_fields[field_name] = var
            
            # Series fields
            for field_name, var in self.series_vars.items():
                all_fields[field_name] = var
            
            # Validate
            validation_result = self.vr_validator.validate_form_fields(all_fields)
            
            # Check if all valid
            if validation_result['valid'] and not validation_result['has_warnings']:
                field_count = validation_result.get('field_count', len(all_fields))
                messagebox.showinfo(
                    APP_TITLE,
                    "? Validation Passed\n\n"
                    f"All {field_count} fields are valid.\n"
                    "No errors or warnings found."
                )
                self.logger.info("Manual validation passed - all fields valid")
                return
            
            # Show validation report dialog
            try:
                if ValidationDialog is None:
                    # Fallback: show simple text report
                    report = self.vr_validator.format_validation_report(validation_result)
                    messagebox.showwarning(
                        APP_TITLE,
                        f"Validation Report:\n\n{report}\n\n"
                        "(ValidationDialog not available for detailed view)"
                    )
                    return
                
                # Show full dialog without action buttons (just for viewing)
                ValidationDialog.show_validation_report(
                    self,
                    validation_result,
                    self.vr_validator,
                    "validate"  # Special action to indicate this is manual validation
                )
            except Exception as e:
                self.logger.exception("Error showing validation dialog")
                # Fallback: show simple text report
                report = self.vr_validator.format_validation_report(validation_result)
                messagebox.showwarning(
                    APP_TITLE,
                    f"Validation Report:\n\n{report}\n\n"
                    f"(Error displaying full dialog: {e})"
                )
        
        except Exception as e:
            self.logger.exception("Error during validation")
            messagebox.showerror(
                APP_TITLE,
                f"Validation error occurred:\n\n{e}\n\n"
                "Check the log for details."
            )

    def on_quit(self):
        """Ask for confirmation before quitting the application."""
        try:
            if messagebox.askyesno(APP_TITLE, "Are you sure you want to quit? Any unsaved changes will be lost."):
                self.destroy()
        except Exception:
            try:
                self.destroy()
            except Exception:
                pass

    def load_image(self):
        """Load an image from disk and convert to grayscale pixel array for preview and DICOM."""
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
        )
        if not path:
            return
            
        if Image is None or np is None:
            self.logger.warning("Pillow/numpy not available; cannot load image")
            messagebox.showerror(APP_TITLE, "Pillar and numpy are required to load images.")
            return
            
        try:
            img = Image.open(path).convert("L")
            self.pixel_array = np.array(img)
            self.image_path = path
            self.image_source = "file"  # Mark image as from file
            self.image_label.config(text=f"Loaded: {os.path.basename(path)} | {img.size[0]}x{img.size[1]}")
            self._update_image_preview(self.pixel_array)
        except Exception as e:
            self.logger.exception("Failed to load image '%s'", path)
            messagebox.showerror(APP_TITLE, f"Failed to load image: {e}")

    def _update_image_preview(self, arr):
        """Convert the array to a displayable image and update the Tkinter label."""
        if arr is None:
            return
        
        if Image is None or ImageTk is None:
            self.logger.warning("PIL or ImageTk not available; cannot display image preview")
            return
            
        try:
            if DicomLogicHandler:
                logic = DicomLogicHandler(self.logger)

            # Normalize to 8-bit if needed
            if arr.ndim == 2:
                img = Image.fromarray(logic.process_image_to_uint8(arr), mode="L")
            elif arr.ndim == 3 and arr.shape[2] in (3, 4):
                if arr.dtype != np.uint8:
                    arr = logic.process_image_to_uint8(arr)
                mode = "RGBA" if arr.shape[2] == 4 else "RGB"
                img = Image.fromarray(arr, mode=mode)
            else:
                # Unsupported shape; try to extract first 2D slice if possible
                if arr.size > 0:
                    # Handle unusual multi-dimensional data
                    if arr.ndim > 2:
                        # Try to get the first valid 2D slice
                        arr2 = arr[:, :, 0] if arr.shape[2] > 0 else arr.reshape(arr.shape[0], arr.shape[1])
                    else:
                        arr2 = np.squeeze(arr)
                    
                    # Ensure we have a 2D array
                    if arr2.ndim != 2:
                        self.logger.warning(f"Cannot preview image with shape {arr.shape}")
                        return
                        
                    img = Image.fromarray(logic.process_image_to_uint8(arr2), mode="L")
                else:
                    self.logger.warning("Empty pixel array, cannot preview")
                    return

            # Scale down to fit preview area - improved logic
            try:
                # Get the actual preview label size
                self.preview_label.update_idletasks()  # Force layout update
                max_w = self.preview_label.winfo_width()
                max_h = self.preview_label.winfo_height()
                
                # Use reasonable defaults if sizes are not yet available
                if max_w <= 1:
                    max_w = 400
                if max_h <= 1:
                    max_h = 300
                
                # Ensure minimum reasonable size
                max_w = max(200, max_w)
                max_h = max(200, max_h)
                
                # Thumbnail with aspect ratio preservation
                img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            except Exception as e:
                self.logger.debug(f"Thumbnail sizing failed: {e}, using original image")
                # Continue with original size if thumbnail fails

            # Create PhotoImage - with explicit error handling
            try:
                self._tk_img = ImageTk.PhotoImage(img)
                self.preview_label.configure(image=self._tk_img)
                self.preview_label.image = self._tk_img  # Keep a reference!
            except Exception as e:
                self.logger.error(f"Failed to create PhotoImage: {e}")
                self.preview_label.config(text="Image display error")
                
        except Exception as e:
            self.logger.warning(f"Failed to update image preview: {e}", exc_info=True)
            self.preview_label.config(text="Failed to load image")

    def _validate_form_fields(self, action="save"):
        """
        Validate all form fields against VR specifications.
        
        Args:
            action: Action being performed ("save", "send", "load")
            
        Returns:
            bool: True if validation passed or user wants to continue anyway
        """
        if self.vr_validator is None:
            return True  # Skip validation if validator not available
        
        # Collect all form fields
        all_fields = {}
        
        # Patient fields
        for field_name, var in self.patient_vars.items():
            all_fields[field_name] = var
        
        # Study fields
        for field_name, var in self.study_vars.items():
            all_fields[field_name] = var
        
        # Series fields
        for field_name, var in self.series_vars.items():
            all_fields[field_name] = var
        
        # Validate
        validation_result = self.vr_validator.validate_form_fields(all_fields)
        
        # If all valid, return True
        if validation_result['valid'] and not validation_result['has_warnings']:
            return True
        
        # Show validation report and ask for confirmation
        try:
            if ValidationDialog is None:
                return True
            
            return ValidationDialog.show_validation_report(
                self,
                validation_result,
                self.vr_validator,
                action
            )
        except Exception as e:
            self.logger.exception("Error showing validation dialog")
            # On error, ask user if they want to continue
            return messagebox.askyesno(
                APP_TITLE,
                f"Validation error occurred: {e}\n\nContinue anyway?"
            )
    
    def save_dicom(self):
        """Save the current metadata and pixel data into a DICOM file."""
        if pydicom is None:
            self.logger.warning("pydicom not available; cannot save DICOM")
            messagebox.showerror(APP_TITLE, "pydicom is required to save DICOM files.")
            return
        
        # Validate fields before saving
        if not self._validate_form_fields(action="save"):
            self.logger.info("Save cancelled due to validation")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".dcm",
            filetypes=[("DICOM", "*.dcm"), ("All Files", "*.*")]
        )
        if not save_path:
            return
            
        try:
            from .dcm import create_dicom
        except Exception:
            try:
                from dcm import create_dicom
            except Exception as e:
                self.logger.exception("Failed to import DICOM module")
                messagebox.showerror(APP_TITLE, f"Failed to import DICOM module: {e}")
                return

        # Get base dataset if available (to preserve private tags and other non-form tags)
        base_dataset = None
        if self.selected_study_uid and self.selected_series_uid:
            # Get the first instance from the selected series
            instances = self.grouped_dicom.get(self.selected_study_uid, {}).get(self.selected_series_uid, [])
            if instances:
                base_dataset, _ = instances[0]
                self.logger.info("Using loaded dataset as base to preserve private tags")

        try:
            ds = create_dicom(
                save_path=save_path,
                patient={
                    "PatientName": self.patient_vars["PatientName"].get().strip(),
                    "PatientID": self.patient_vars["PatientID"].get().strip(),
                    "PatientBirthDate": self.patient_vars["PatientBirthDate"].get().strip(),
                    "PatientSex": self.patient_vars["PatientSex"].get().strip(),
                    "PatientAge": self.patient_vars["PatientAge"].get().strip(),
                    "PatientWeight": self.patient_vars["PatientWeight"].get().strip(),
                    "PatientSize": self.patient_vars["PatientSize"].get().strip(),
                    "PatientComments": self.patient_vars["PatientComments"].get().strip(),
                    "PatientMotherBirthName": self.patient_vars["PatientMothersBirthName"].get().strip(),
                    "PatientDeathDateTime": self.patient_vars["PatientDeathDateTime"].get().strip(),
                    "PatientBirthTime": self.patient_vars["PatientBirthTime"].get().strip(),
                    "PatientAddress": self.patient_vars["PatientAddress"].get().strip(),
                    "PatientTelephoneNumbers": self.patient_vars["PatientTelephoneNumbers"].get().strip(),
                },
                study={
                    "StudyInstanceUID": self.study_vars["StudyInstanceUID"].get().strip(),
                    "StudyDate": self.study_vars["StudyDate"].get().strip(),
                    "StudyTime": self.study_vars["StudyTime"].get().strip(),
                    "StudyDescription": self.study_vars["StudyDescription"].get().strip(),
                    "AccessionNumber": self.study_vars["AccessionNumber"].get().strip(),
                    "StudyID": self.study_vars["StudyID"].get().strip(),
                    "ReferringPhysicianName": self.study_vars["ReferringPhysicianName"].get().strip(),
                    "ReadingPhysicianName": self.study_vars["ReadingPhysicianName"].get().strip(),
                    "ReasonForStudy": self.study_vars["ReasonForStudy"].get().strip(),
                    "AdmittingDiagnosesDescription": self.study_vars["AdmittingDiagnosesDescription"].get().strip(),
                    "StudyPatientLocation": self.study_vars["StudyPatientLocation"].get().strip(),
                },
                series={
                    "SeriesInstanceUID": self.series_vars["SeriesInstanceUID"].get().strip(),
                    "SeriesNumber": self.series_vars["SeriesNumber"].get().strip(),
                    "Modality": self.series_vars["Modality"].get().strip(),
                    "SeriesDescription": self.series_vars["SeriesDescription"].get().strip(),
                    "BodyPartExamined": self.series_vars["BodyPartExamined"].get().strip(),
                    "ProtocolName": self.series_vars["ProtocolName"].get().strip(),
                    "SeriesDate": self.series_vars["SeriesDate"].get().strip(),
                    "SeriesTime": self.series_vars["SeriesTime"].get().strip(),
                    "PerformingPhysicianName": self.series_vars["PerformingPhysicianName"].get().strip(),
                    "OperatorsName": self.series_vars["OperatorsName"].get().strip(),
                    "Laterality": self.series_vars["Laterality"].get().strip(),
                },
                pixel_array=self.pixel_array,
                base_dataset=base_dataset,
            )
        except Exception as e:
            self.logger.exception("Failed to create DICOM dataset")
            messagebox.showerror(APP_TITLE, f"Failed to create DICOM: {e}")
            return

        # Count total tags before save to detect removals
        tags_before = len(ds)
        original_tag_count = tags_before
        
        # Warn user about potential tag removal if using base_dataset
        if base_dataset is not None:
            warning_msg = (
                "DICOM Tag Cleanup Notice\n\n"
                f"Original file: {original_tag_count} tags\n\n"
                "During save, pydicom will remove:\n"
                "- Group Length tags (element 0000) - deprecated since DICOM 2008\n"
                "- Obsolete/retired tags - for DICOM 2008+ compliance\n\n"
                "All data-bearing private tags will be preserved.\n\n"
                "Do you want to continue saving?"
            )
            
            result = messagebox.askyesno(APP_TITLE, warning_msg)
            if not result:
                self.logger.info("Save cancelled by user due to tag removal warning")
                messagebox.showinfo(APP_TITLE, "Save cancelled.")
                return

        try:
            # Save with write_like_original=False to ensure proper DICOM format
            ds.save_as(save_path, write_like_original=False)
            
            # Verify private tags were saved correctly
            try:
                import pydicom as pydicom_verify
                saved_ds = pydicom_verify.dcmread(save_path)
                tags_after = len(saved_ds)
                removed_tags_count = original_tag_count - tags_after
                
                saved_private_tags = [(elem.tag, elem.tag.group, elem.tag.element) 
                                      for elem in saved_ds if elem.tag.group % 2 == 1]
                
                # Check if any Group Length tags were removed
                original_private_tags = [(elem.tag, elem.tag.group, elem.tag.element) 
                                        for elem in ds if elem.tag.group % 2 == 1]
                
                removed_group_length = False
                for tag, group, elem in original_private_tags:
                    if elem == 0 and (group, elem) not in [(t[1], t[2]) for t in saved_private_tags]:
                        removed_group_length = True
                        print(f"[INFO] Group Length tag ({group:04x},0000) was removed (deprecated in modern DICOM)")
                
                print(f"[VERIFY] Saved file contains {len(saved_private_tags)} private tag(s)")
                if len(saved_private_tags) > 0:
                    for tag, group, element in saved_private_tags:
                        print(f"  [VERIFY TAG] {tag} (group={group:04x}, elem={element:04x})")
                        
                if removed_group_length:
                    self.logger.info("Group Length tags removed during save (standard DICOM behavior)")
                
                # Show confirmation with tag counts
                if removed_tags_count > 0:
                    info_msg = (
                        "DICOM file saved successfully!\n\n"
                        f"Tags before: {original_tag_count}\n"
                        f"Tags after: {tags_after}\n"
                        f"Removed: {removed_tags_count} (obsolete/retired tags)\n"
                        f"Private tags preserved: {len(saved_private_tags)}"
                    )
                else:
                    info_msg = f"DICOM file saved successfully!\n\nTotal tags: {tags_after}"
                
                messagebox.showinfo(APP_TITLE, info_msg)
            except Exception as verify_error:
                self.logger.warning("Verification of saved DICOM failed", exc_info=True)
                messagebox.showwarning(APP_TITLE, "DICOM saved but verification failed")
        except Exception as e:
            self.logger.exception("Failed to save DICOM to '%s'", save_path)
            messagebox.showerror(APP_TITLE, f"Failed to save DICOM: {e}")

    def load_dicom_file(self):
        """Load one or more DICOM files. Supports picking a DICOMDIR file to expand dataset references."""
        if pydicom is None:
            self.logger.warning("pydicom not available; cannot load DICOM files")
            messagebox.showerror(APP_TITLE, "pydicom is required to load DICOM files.")
            return
            
        paths = filedialog.askopenfilenames(
            title="Select DICOM file(s)",
            filetypes=[("DICOM Files", "*.dcm;*.dicom;*"), ("All Files", "*.*")]
        )
        if not paths:
            return
            
        try:
            try:
                from .dcm import load_dicom_grouped, is_dicomdir, load_dicomdir_grouped
            except Exception:
                from dcm import load_dicom_grouped, is_dicomdir, load_dicomdir_grouped

            grouped = {}

            def merge_grouped(target, source):
                for study_uid, series_map in source.items():
                    t_series_map = target.setdefault(study_uid, {})
                    for series_uid, instances in series_map.items():
                        t_instances = t_series_map.setdefault(series_uid, [])
                        t_instances.extend(instances)

            if len(paths) == 1 and is_dicomdir(paths[0]):
                grouped = load_dicomdir_grouped(paths[0])
            else:
                non_dir_files = []
                for p in paths:
                    if is_dicomdir(p):
                        part = load_dicomdir_grouped(p)
                        merge_grouped(grouped, part)
                    else:
                        non_dir_files.append(p)
                if non_dir_files:
                    part = load_dicom_grouped(list(non_dir_files))
                    merge_grouped(grouped, part)
                    
            self._populate_dicom_tree(grouped)
        except Exception as e:
            self.logger.exception("Failed to load DICOM selections: %s", paths)
            messagebox.showerror(APP_TITLE, f"Failed to load DICOM: {e}")

    def load_dicom_folder(self):
        """Load all DICOM files under a selected folder and group them for display."""
        if pydicom is None:
            self.logger.warning("pydicom not available; cannot load DICOM folder")
            messagebox.showerror(APP_TITLE, "pydicom is required to load DICOM files.")
            return
            
        folder = filedialog.askdirectory(title="Select DICOM folder")
        if not folder:
            return
            
        try:
            try:
                from .dcm import load_dicom_grouped
            except Exception:
                from dcm import load_dicom_grouped
                
            grouped = load_dicom_grouped(folder)
            self._populate_dicom_tree(grouped)
        except Exception as e:
            self.logger.exception("Failed to load DICOM folder: %s", folder)
            messagebox.showerror(APP_TITLE, f"Failed to load DICOM folder: {e}")

    def _show_instance_context_menu(self, event):
        """Show context menu for instance nodes on right-click."""
        try:
            item_id = self.series_tree.identify_row(event.y)
        
            if not item_id or not item_id.startswith("instance:"):
                return
        
            self.series_tree.selection_set(item_id)
            self.selected_instance_id = item_id
            self.instance_context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            self.logger.exception("Failed to show instance context menu")

    def _show_instance_image(self):
        """Show the image for the selected instance in the Image tab."""
        try:
            if not hasattr(self, 'selected_instance_id') or not self.selected_instance_id:
                return
        
            parts = self.selected_instance_id.split(":", 3)
            if len(parts) != 4 or parts[0] != "instance":
                return
        
            _, study_uid, series_uid, idx_str = parts
            idx = int(idx_str)
        
            instances = self.grouped_dicom.get(study_uid, {}).get(series_uid, [])
        
            if idx < 0 or idx >= len(instances):
                messagebox.showerror(APP_TITLE, "Instance not found")
                return
        
            ds, arr = instances[idx]
        
            if arr is None:
                messagebox.showwarning(APP_TITLE, "No pixel data available for this instance")
                return
        
            self.pixel_array = arr
            self.image_source = "dicom"
        
            rows = getattr(ds, 'Rows', None)
            cols = getattr(ds, 'Columns', None)
            sop_uid = getattr(ds, 'SOPInstanceUID', 'N/A')
        
            if rows and cols:
                self.image_label.config(text=f"Instance: {sop_uid} | {cols}x{rows}")
            else:
                self.image_label.config(text=f"Instance: {sop_uid}")
        
            self._update_image_preview(arr)
        
            # Switch to Image tab
            for i, tab_id in enumerate(self.container.tabs()):
                if self.container.tab(tab_id, "text") == "Image":
                    self.container.select(i)
                    break
        
            self.logger.info(f"Displayed image for instance: {sop_uid}")
        
        except Exception as e:
            self.logger.exception("Failed to show instance image")
            messagebox.showerror(APP_TITLE, f"Failed to show image: {e}")
        
    def _populate_dicom_tree(self, grouped):
        """Populate the tree view with loaded DICOM data."""
        self.grouped_dicom = grouped
        self.series_tree.delete(*self.series_tree.get_children())
        
        total_instances = 0
        first_series_id = None
        
        for study_uid, series_map in grouped.items():
            study_node = self.series_tree.insert("", "end", iid=f"study:{study_uid}", text=f"Study: {study_uid}")
            for series_uid, instances in series_map.items():
                series_node = self.series_tree.insert(
                    study_node, "end",
                    iid=f"series:{study_uid}:{series_uid}",
                    text=f"Series: {series_uid} ({len(instances)} images)"
                )
                if first_series_id is None:
                    first_series_id = f"series:{study_uid}:{series_uid}"
                    
                for idx, (ds, arr) in enumerate(instances):
                    inst_text = f"Instance {idx+1}: {getattr(ds, 'SOPInstanceUID', '')}"
                    inst_id = f"instance:{study_uid}:{series_uid}:{idx}"
                    self.series_tree.insert(series_node, "end", iid=inst_id, text=inst_text)
                    total_instances += 1

        self.dcm_info_label.config(
            text=f"Loaded {len(grouped)} studies, {sum(len(v) for v in grouped.values())} series, {total_instances} instances"
        )
        
        if first_series_id:
            self.series_tree.selection_set(first_series_id)
            self.on_tree_select(None)

    def on_tree_select(self, event):
        """Handle selection in the series tree."""
        sel = self.series_tree.selection()
        if not sel:
            return
            
        node_id = sel[0]
        
        # Handle STUDY node selection
        if node_id.startswith("study:"):
            _, study_uid = node_id.split(":", 1)
            self.selected_study_uid = study_uid
            self.selected_series_uid = None
            
            # Get first series from this study
            series_map = self.grouped_dicom.get(study_uid, {})
            if not series_map:
                return
            
            first_series_uid = list(series_map.keys())[0]
            instances = series_map.get(first_series_uid, [])
            
            if not instances:
                return
            
            ds, arr = instances[0]
            
            # Populate fields from first series in this study
            self._populate_patient_fields(ds)
            self._populate_study_fields(ds)
            self._populate_series_fields(ds)
            
            # Update pixel array if available
            if self.image_source != "file":
                self.pixel_array = arr if arr is not None else self.pixel_array
            
            # Update image info
            rows = getattr(ds, 'Rows', None)
            cols = getattr(ds, 'Columns', None)
            if rows and cols:
                self.image_label.config(text=f"Selected Study: {study_uid} | {cols}x{rows}")
            else:
                self.image_label.config(text=f"Selected Study: {study_uid}")
            
            # Update preview if no user-loaded image is active
            if self.image_source != "file" and arr is not None:
                self.image_source = "dicom"
                self._update_image_preview(arr)
            
            return
        
        # Handle SERIES node selection
        if not node_id.startswith("series:"):
            return
            
        _, study_uid, series_uid = node_id.split(":", 2)
        self.selected_study_uid = study_uid
        self.selected_series_uid = series_uid
        instances = self.grouped_dicom.get(study_uid, {}).get(series_uid, [])
        
        if not instances:
            return
            
        ds, arr = instances[0]
        # Only update pixel_array if no image is currently loaded from a file
        if self.image_source != "file":
            self.pixel_array = arr if arr is not None else self.pixel_array
        
            # Populate patient fields
            self._populate_patient_fields(ds)
            
            # Populate study fields
            self._populate_study_fields(ds)
            
            # Populate series fields
            self._populate_series_fields(ds)
            
            # Validate loaded fields
            if self.vr_validator is not None:
                try:
                    # Collect all fields
                    all_fields = {}
                    all_fields.update(self.patient_vars)
                    all_fields.update(self.study_vars)
                    all_fields.update(self.series_vars)
                    
                    # Validate
                    validation_result = self.vr_validator.validate_form_fields(all_fields)
                    
                    # Show warnings if any
                    if validation_result['error_count'] > 0 or validation_result['warning_count'] > 0:
                        report = self.vr_validator.format_validation_report(validation_result)
                        self.logger.warning(f"Validation issues in loaded DICOM:\n{report}")
                        
                        # Only show dialog if there are errors (not just warnings)
                        if validation_result['error_count'] > 0:
                            if messagebox.askyesno(
                                APP_TITLE,
                                f"Loaded DICOM has {validation_result['error_count']} validation error(s).\n\n"
                                "View validation report?",
                                icon=messagebox.WARNING
                            ):
                                try:
                                    if ValidationDialog:
                                        ValidationDialog.show_validation_report(
                                            self,
                                            validation_result,
                                            self.vr_validator,
                                            "load"
                                        )
                                except Exception as e:
                                    self.logger.exception("Error showing validation dialog")
                except Exception as e:
                    self.logger.exception("Error validating loaded DICOM fields")
            
            # Update image info
        rows = getattr(ds, 'Rows', None)
        cols = getattr(ds, 'Columns', None)
        if rows and cols:
            self.image_label.config(text=f"Selected Series: {series_uid} | {cols}x{rows}")
        else:
            self.image_label.config(text=f"Selected Series: {series_uid}")
            
        # Only update preview if no user-loaded image is active
        if self.image_source != "file" and arr is not None:
            self.image_source = "dicom"
            self._update_image_preview(arr)

    def _populate_patient_fields(self, ds):
        """Populate patient form fields from DICOM dataset."""
        self.patient_vars["PatientName"].set(str(getattr(ds, 'PatientName', '') or ''))
        self.patient_vars["PatientID"].set(str(getattr(ds, 'PatientID', '') or ''))
        self.patient_vars["PatientBirthDate"].set(str(getattr(ds, 'PatientBirthDate', '') or ''))
        self.patient_vars["PatientSex"].set(str(getattr(ds, 'PatientSex', '') or ''))
        self.patient_vars["PatientAge"].set(str(getattr(ds, 'PatientAge', '') or ''))
        self.patient_vars["PatientWeight"].set(str(getattr(ds, 'PatientWeight', '') or ''))
        self.patient_vars["PatientSize"].set(str(getattr(ds, 'PatientSize', '') or ''))
        self.patient_vars["PatientComments"].set(str(getattr(ds, 'PatientComments', '') or ''))
        self.patient_vars["PatientMothersBirthName"].set(str(getattr(ds, 'PatientMotherBirthName', '') or ''))
        self.patient_vars["PatientDeathDateTime"].set(str(getattr(ds, 'PatientDeathDateTime', '') or ''))
        self.patient_vars["PatientBirthTime"].set(str(getattr(ds, 'PatientBirthTime', '') or ''))
        self.patient_vars["PatientAddress"].set(str(getattr(ds, 'PatientAddress', '') or ''))
        self.patient_vars["PatientTelephoneNumbers"].set(str(getattr(ds, 'PatientTelephoneNumbers', '') or ''))

    def _populate_study_fields(self, ds):
        """Populate study form fields from DICOM dataset."""
        self.study_vars["StudyInstanceUID"].set(str(getattr(ds, 'StudyInstanceUID', '') or ''))
        self.study_vars["StudyDate"].set(str(getattr(ds, 'StudyDate', '') or ''))
        self.study_vars["StudyTime"].set(str(getattr(ds, 'StudyTime', '') or ''))
        self.study_vars["StudyDescription"].set(str(getattr(ds, 'StudyDescription', '') or ''))
        self.study_vars["AccessionNumber"].set(str(getattr(ds, 'AccessionNumber', '') or ''))
        self.study_vars["StudyID"].set(str(getattr(ds, 'StudyID', '') or ''))
        self.study_vars["ReferringPhysicianName"].set(str(getattr(ds, 'ReferringPhysicianName', '') or ''))
        self.study_vars["ReadingPhysicianName"].set(str(getattr(ds, 'NameOfPhysiciansReadingStudy', '') or ''))
        self.study_vars["ReasonForStudy"].set(str(getattr(ds, 'ReasonForStudy', '') or ''))
        self.study_vars["AdmittingDiagnosesDescription"].set(str(getattr(ds, 'AdmittingDiagnosesDescription', '') or ''))
        self.study_vars["StudyPatientLocation"].set(str(getattr(ds, 'StudyPatientLocation', '') or ''))

    def _populate_series_fields(self, ds):
        """Populate series form fields from DICOM dataset."""
        self.series_vars["SeriesInstanceUID"].set(str(getattr(ds, 'SeriesInstanceUID', '') or ''))
        self.series_vars["SeriesNumber"].set(str(getattr(ds, 'SeriesNumber', '') or ''))
        self.series_vars["Modality"].set(str(getattr(ds, 'Modality', '') or ''))
        self.series_vars["SeriesDescription"].set(str(getattr(ds, 'SeriesDescription', '') or ''))
        self.series_vars["BodyPartExamined"].set(str(getattr(ds, 'BodyPartExamined', '') or ''))
        self.series_vars["ProtocolName"].set(str(getattr(ds, 'ProtocolName', '') or ''))
        self.series_vars["SeriesDate"].set(str(getattr(ds, 'SeriesDate', '') or ''))
        self.series_vars["SeriesTime"].set(str(getattr(ds, 'SeriesTime', '') or ''))
        self.series_vars["PerformingPhysicianName"].set(str(getattr(ds, 'PerformingPhysicianName', '') or ''))
        self.series_vars["OperatorsName"].set(str(getattr(ds, 'OperatorsName', '') or ''))
        self.series_vars["Laterality"].set(str(getattr(ds, 'Laterality', '') or ''))

    def _append_remote_message(self, text):
        """Append a message to the remote messages text area."""
        try:
            self.remote_messages.configure(state=tk.NORMAL)
            self.remote_messages.insert(tk.END, text + "\n")
            self.remote_messages.see(tk.END)
            self.remote_messages.configure(state=tk.DISabled)
        except Exception:
            pass

    def send_remote(self):
        """Send all loaded DICOM instances to a remote DICOM SCP using C-STORE."""
        try:
            from .remote import send_grouped_dicom, is_remote_available, remote_unavailable_reason
        except Exception:
            try:
                from remote import send_grouped_dicom, is_remote_available, remote_unavailable_reason
            except Exception as e:
                self.logger.exception("Failed to import remote sender")
                messagebox.showerror(APP_TITLE, f"Failed to import remote sender: {e}")
                return
                
        if not is_remote_available():
            reason = remote_unavailable_reason()
            self.logger.error("Remote send unavailable: %s", reason)
            self._append_remote_message(f"Remote unavailable: {reason}")
            messagebox.showerror(APP_TITLE, f"Remote unavailable: {reason}")
            return

        server = self.remote_vars["server"].get().strip()
        port_s = self.remote_vars["port"].get().strip()
        calling_ae = self.remote_vars["calling_ae"].get().strip() or "DCMCREATOR"
        called_ae = self.remote_vars["called_ae"].get().strip() or "ANY-SCP"

        # Validate inputs
        if not server:
            messagebox.showerror(APP_TITLE, "Server address is required")
            return
        try:
            port = int(port_s)
        except Exception:
            messagebox.showerror(APP_TITLE, "Port must be an integer")
            return
        
        # Check if Patient ID is empty and confirm with user
        patient_id = self.patient_vars["PatientID"].get().strip()
        if not patient_id:
            if not messagebox.askyesno(
                APP_TITLE,
                "Patient ID is empty. While technically allowed, this is not recommended "
                "and may cause issues with some DICOM systems.\n\n"
                "Do you want to continue sending anyway?"
            ):
                return
        
        # Validate fields before sending
        if not self._validate_form_fields(action="send"):
            self.logger.info("Send cancelled due to validation")
            return
        
        # Use loaded studies if available, otherwise create from form values
        if self.grouped_dicom:
            # Update loaded datasets with current form field values
            grouped_to_send = self._update_datasets_with_form_values(self.grouped_dicom)
            self._append_remote_message(f"Sending {len(grouped_to_send)} loaded studies with updated form values")
        else:
            # No studies loaded, create dataset from current form values
            grouped_to_send = self._create_in_memory_dataset(patient_id)
        
        if not grouped_to_send:
            return

        # Clear previous messages
        self.remote_messages.configure(state=tk.NORMAL)
        self.remote_messages.delete("1.0", tk.END)
        self.remote_messages.configure(state=tk.DISABLED)

        # Disable button during send
        try:
            self.remote_send_button.configure(state=tk.DISABLED)
        except Exception:
            pass

        config = {
            "server": server,
            "port": port,
            "calling_ae": calling_ae,
            "called_ae": called_ae,
            "skip_c_echo": bool(self.remote_vars["skip_c_echo"].get()),
            "use_tls": bool(self.remote_vars["use_tls"].get()),
            "tls_config": self.tls_config if self.remote_vars["use_tls"].get() else None,
        }

        def post_message(msg: str):
            try:
                self.after(0, self._append_remote_message, msg)
            except Exception:
                pass

        def worker():
            try:
                post_message(f"Starting send to {server}:{port} as {calling_ae}->{called_ae}")
                send_grouped_dicom(
                    grouped=grouped_to_send,
                    config=config,
                    logger=self.logger,
                    on_message=post_message,
                    transmission_history=self.transmission_history,
                )
                self.after(0, lambda: messagebox.showinfo(APP_TITLE, "All DICOM instances sent successfully"))
            except Exception as e:
                error_msg = str(e)
                try:
                    self.logger.exception("Remote send failed")
                except Exception:
                    pass
                self.after(0, post_message, f"Error: {error_msg}")
                self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Remote send failed: {error_msg}"))
            finally:
                try:
                    self.after(0, lambda: self.remote_send_button.configure(state=tk.NORMAL))
                except Exception:
                    pass

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _create_in_memory_dataset(self, patient_id):
        """Create a DICOM dataset from current form values."""
        try:
            try:
                from .dcm import create_dicom
            except Exception:
                from dcm import create_dicom
        except Exception as ie:
            self.logger.exception("Failed to import DICOM module for in-memory send")
            messagebox.showerror(APP_TITLE, f"No DICOM loaded and cannot create one from current form: {ie}")
            return None
            
        try:
            ds = create_dicom(
                save_path="in-memory",
                patient={
                    "PatientName": self.patient_vars["PatientName"].get().strip(),
                    "PatientID": patient_id,
                    "PatientBirthDate": self.patient_vars["PatientBirthDate"].get().strip(),
                    "PatientSex": self.patient_vars["PatientSex"].get().strip(),
                    "PatientAge": self.patient_vars["PatientAge"].get().strip(),
                    "PatientWeight": self.patient_vars["PatientWeight"].get().strip(),
                    "PatientSize": self.patient_vars["PatientSize"].get().strip(),
                    "PatientComments": self.patient_vars["PatientComments"].get().strip(),
                    "PatientMotherBirthName": self.patient_vars["PatientMothersBirthName"].get().strip(),
                    "PatientDeathDateTime": self.patient_vars["PatientDeathDateTime"].get().strip(),
                    "PatientBirthTime": self.patient_vars["PatientBirthTime"].get().strip(),
                    "PatientAddress": self.patient_vars["PatientAddress"].get().strip(),
                    "PatientTelephoneNumbers": self.patient_vars["PatientTelephoneNumbers"].get().strip(),
                },
                study={
                    "StudyInstanceUID": self.study_vars["StudyInstanceUID"].get().strip(),
                    "StudyDate": self.study_vars["StudyDate"].get().strip(),
                    "StudyTime": self.study_vars["StudyTime"].get().strip(),
                    "StudyDescription": self.study_vars["StudyDescription"].get().strip(),
                    "AccessionNumber": self.study_vars["AccessionNumber"].get().strip(),
                    "StudyID": self.study_vars["StudyID"].get().strip(),
                    "ReferringPhysicianName": self.study_vars["ReferringPhysicianName"].get().strip(),
                    "ReadingPhysicianName": self.study_vars["ReadingPhysicianName"].get().strip(),
                    "ReasonForStudy": self.study_vars["ReasonForStudy"].get().strip(),
                    "AdmittingDiagnosesDescription": self.study_vars["AdmittingDiagnosesDescription"].get().strip(),
                    "StudyPatientLocation": self.study_vars["StudyPatientLocation"].get().strip(),
                },
                series={
                    "SeriesInstanceUID": self.series_vars["SeriesInstanceUID"].get().strip(),
                    "SeriesNumber": self.series_vars["SeriesNumber"].get().strip(),
                    "Modality": self.series_vars["Modality"].get().strip(),
                    "SeriesDescription": self.series_vars["SeriesDescription"].get().strip(),
                    "BodyPartExamined": self.series_vars["BodyPartExamined"].get().strip(),
                    "ProtocolName": self.series_vars["ProtocolName"].get().strip(),
                    "SeriesDate": self.series_vars["SeriesDate"].get().strip(),
                    "SeriesTime": self.series_vars["SeriesTime"].get().strip(),
                    "PerformingPhysicianName": self.series_vars["PerformingPhysicianName"].get().strip(),
                    "OperatorsName": self.series_vars["OperatorsName"].get().strip(),
                    "Laterality": self.series_vars["Laterality"].get().strip(),
                },
                pixel_array=self.pixel_array,
            )
            suid = str(getattr(ds, 'StudyInstanceUID', ''))
            seruid = str(getattr(ds, 'SeriesInstanceUID', ''))
            self._append_remote_message("Sending DICOM dataset from current form values")
            return {suid: {seruid: [(ds, self.pixel_array)]}}
        except Exception as ce:
            self.logger.exception("Failed to build in-memory dataset for sending")
            messagebox.showerror(APP_TITLE, f"Failed to build dataset from current form: {ce}")
            return None

    def _update_datasets_with_form_values(self, grouped):
        """Update loaded DICOM datasets with current form field values.

        Args:
            grouped: Dictionary of {study_uid: {series_uid: [(ds, pixel_array)]}}

        Returns:
            Updated grouped dictionary with form values applied to datasets
        """
        try:
            # Create a copy to avoid modifying the original
            import copy
            updated_grouped = {}
            uids_changed = False

            for study_uid, series_map in grouped.items():
                updated_series_map = {}

                for series_uid, instances in series_map.items():
                    updated_instances = []

                    for ds, pixel_array in instances:
                        # Create a shallow copy of the dataset
                        updated_ds = copy.copy(ds)

                        # Update ALL patient fields (including empty values to allow clearing)
                        updated_ds.PatientName = self.patient_vars["PatientName"].get().strip()
                        updated_ds.PatientID = self.patient_vars["PatientID"].get().strip()

                        val = self.patient_vars["PatientBirthDate"].get().strip()
                        if val:
                            updated_ds.PatientBirthDate = val

                        val = self.patient_vars["PatientSex"].get().strip()
                        if val:
                            updated_ds.PatientSex = val

                        val = self.patient_vars["PatientAge"].get().strip()
                        if val:
                            updated_ds.PatientAge = val

                        val = self.patient_vars["PatientWeight"].get().strip()
                        if val:
                            updated_ds.PatientWeight = val

                        val = self.patient_vars["PatientSize"].get().strip()
                        if val:
                            updated_ds.PatientSize = val

                        val = self.patient_vars["PatientComments"].get().strip()
                        if val:
                            updated_ds.PatientComments = val

                        val = self.patient_vars["PatientMothersBirthName"].get().strip()
                        if val:
                            updated_ds.PatientMotherBirthName = val

                        val = self.patient_vars["PatientDeathDateTime"].get().strip()
                        if val:
                            updated_ds.PatientDeathDateTime = val

                        val = self.patient_vars["PatientBirthTime"].get().strip()
                        if val:
                            updated_ds.PatientBirthTime = val

                        val = self.patient_vars["PatientAddress"].get().strip()
                        if val:
                            updated_ds.PatientAddress = val

                        val = self.patient_vars["PatientTelephoneNumbers"].get().strip()
                        if val:
                            updated_ds.PatientTelephoneNumbers = val

                        # Update ALL study fields (including UIDs!)
                        new_study_uid = self.study_vars["StudyInstanceUID"].get().strip()
                        if new_study_uid and new_study_uid != study_uid:
                            updated_ds.StudyInstanceUID = new_study_uid
                            uids_changed = True

                        val = self.study_vars["StudyDate"].get().strip()
                        if val:
                            updated_ds.StudyDate = val

                        val = self.study_vars["StudyTime"].get().strip()
                        if val:
                            updated_ds.StudyTime = val

                        val = self.study_vars["StudyDescription"].get().strip()
                        if val:
                            updated_ds.StudyDescription = val

                        val = self.study_vars["AccessionNumber"].get().strip()
                        if val:
                            updated_ds.AccessionNumber = val

                        val = self.study_vars["StudyID"].get().strip()
                        if val:
                            updated_ds.StudyID = val

                        val = self.study_vars["ReferringPhysicianName"].get().strip()
                        if val:
                            updated_ds.ReferringPhysicianName = val

                        val = self.study_vars["ReadingPhysicianName"].get().strip()
                        if val:
                            updated_ds.NameOfPhysiciansReadingStudy = val

                        val = self.study_vars["ReasonForStudy"].get().strip()
                        if val:
                            updated_ds.ReasonForStudy = val

                        val = self.study_vars["AdmittingDiagnosesDescription"].get().strip()
                        if val:
                            updated_ds.AdmittingDiagnosesDescription = val

                        val = self.study_vars["StudyPatientLocation"].get().strip()
                        if val:
                            updated_ds.StudyPatientLocation = val

                        # Update ALL series fields (including UIDs!)
                        new_series_uid = self.series_vars["SeriesInstanceUID"].get().strip()
                        if new_series_uid and new_series_uid != series_uid:
                            updated_ds.SeriesInstanceUID = new_series_uid
                            uids_changed = True

                        val = self.series_vars["SeriesNumber"].get().strip()
                        if val:
                            updated_ds.SeriesNumber = val

                        val = self.series_vars["Modality"].get().strip()
                        if val:
                            updated_ds.Modality = val

                        val = self.series_vars["SeriesDescription"].get().strip()
                        if val:
                            updated_ds.SeriesDescription = val

                        val = self.series_vars["BodyPartExamined"].get().strip()
                        if val:
                            updated_ds.BodyPartExamined = val

                        val = self.series_vars["ProtocolName"].get().strip()
                        if val:
                            updated_ds.ProtocolName = val

                        val = self.series_vars["SeriesDate"].get().strip()
                        if val:
                            updated_ds.SeriesDate = val

                        val = self.series_vars["SeriesTime"].get().strip()
                        if val:
                            updated_ds.SeriesTime = val

                        val = self.series_vars["PerformingPhysicianName"].get().strip()
                        if val:
                            updated_ds.PerformingPhysicianName = val

                        val = self.series_vars["OperatorsName"].get().strip()
                        if val:
                            updated_ds.OperatorsName = val

                        val = self.series_vars["Laterality"].get().strip()
                        if val:
                            updated_ds.Laterality = val

                        updated_instances.append((updated_ds, pixel_array))

                    # Use new series UID if it was changed, otherwise use original
                    final_series_uid = series_uid
                    if updated_instances:
                        first_ds, _ = updated_instances[0]
                        final_series_uid = str(getattr(first_ds, 'SeriesInstanceUID', series_uid))

                    updated_series_map[final_series_uid] = updated_instances

                # Use new study UID if it was changed, otherwise use original
                final_study_uid = study_uid
                if updated_series_map:
                    first_series_uid = list(updated_series_map.keys())[0]
                    first_instances = updated_series_map[first_series_uid]
                    if first_instances:
                        first_ds, _ = first_instances[0]
                        final_study_uid = str(getattr(first_ds, 'StudyInstanceUID', study_uid))

                updated_grouped[final_study_uid] = updated_series_map

            # Update internal state if UIDs changed
            if uids_changed:
                self.logger.info("Study/Series UIDs were changed - updating internal state")
                # Update the main grouped_dicom structure
                self.grouped_dicom = updated_grouped
                # Rebuild the tree view with new UIDs
                self.after(100, lambda: self._populate_dicom_tree(updated_grouped))

            self.logger.info("Updated loaded DICOM datasets with current form values")
            return updated_grouped

        except Exception as e:
            self.logger.exception("Failed to update datasets with form values")
            # On error, return original grouped data
            messagebox.showwarning(
                APP_TITLE,
                f"Warning: Could not apply form changes to loaded DICOM: {e}\n\n"
                "Sending original data instead."
            )
            return grouped

    def _on_preset_selected(self, event=None):
        """Handle preset selection from the combobox."""
        try:
            if not self.presets_manager:
                return
            
            name = self.preset_combo.get().strip()
            if name:
                preset = self.presets_manager.load_preset(name)
                if preset:
                    # Apply preset values to remote vars
                    self.remote_vars["server"].set(preset.get('server', ''))
                    self.remote_vars["port"].set(str(preset.get('port', '4321')))
                    self.remote_vars["calling_ae"].set(preset.get('calling_ae', 'DCMCREATOR'))
                    self.remote_vars["called_ae"].set(preset.get('called_ae', 'ANY-SCP'))
                    self.remote_vars["use_tls"].set(preset.get('use_tls', False))
                    # Load TLS config if present
                    if 'tls_config' in preset and preset['tls_config']:
                        self.tls_config = preset['tls_config']
        except Exception as e:
            self.logger.exception("Failed to load preset")

    def _refresh_presets_list(self):
        """Refresh the list of presets in the combobox."""
        try:
            if not self.presets_manager:
                self.preset_combo['values'] = []
                return
            
            presets = self.presets_manager.list_presets()
            self.preset_combo['values'] = presets
            
            # Clear current selection
            self.preset_combo.set("")
            self.remote_vars["preset_name"].set("")
        except Exception as e:
            self.logger.exception("Failed to refresh presets list")
            self.preset_combo['values'] = []

    def _load_preset(self):
        """Load the selected preset into the remote settings fields."""
        try:
            if not self.presets_manager:
                messagebox.showerror(APP_TITLE, "Presets manager not available")
                return
            
            name = self.preset_combo.get().strip()
            if not name:
                messagebox.showerror(APP_TITLE, "No preset selected")
                return
            
            preset = self.presets_manager.load_preset(name)
            if not preset:
                messagebox.showerror(APP_TITLE, f"Preset '{name}' not found")
                return
            
            # Apply preset values to remote vars
            self.remote_vars["server"].set(preset.get('server', ''))
            self.remote_vars["port"].set(str(preset.get('port', '4321')))
            self.remote_vars["calling_ae"].set(preset.get('calling_ae', 'DCMCREATOR'))
            self.remote_vars["called_ae"].set(preset.get('called_ae', 'ANY-SCP'))
            self.remote_vars["use_tls"].set(preset.get('use_tls', False))
            # Load TLS config if present
            if 'tls_config' in preset and preset['tls_config']:
                self.tls_config = preset['tls_config']
            
            self._append_remote_message(f"Loaded preset: {name}")
            messagebox.showinfo(APP_TITLE, f"Preset '{name}' loaded successfully")
        except Exception as e:
            self.logger.exception("Failed to load preset")
            messagebox.showerror(APP_TITLE, f"Failed to load preset: {e}")

    def _save_current_preset(self):
        """Save the current remote settings to a preset.
        
        If preset name is provided and server matches, updates that preset.
        If preset name is provided but server differs, asks to create new or update.
        If no preset name, uses server IP as preset name.
        """
        try:
            # Get preset name from input
            preset_name = self.remote_vars["preset_name"].get().strip()
            
            # Collect current remote settings
            server = self.remote_vars["server"].get().strip()
            port = self.remote_vars["port"].get().strip()
            calling_ae = self.remote_vars["calling_ae"].get().strip()
            called_ae = self.remote_vars["called_ae"].get().strip()
            
            # Validate required fields
            if not server:
                messagebox.showerror(APP_TITLE, "Server address is required")
                return
            
            if not port:
                messagebox.showerror(APP_TITLE, "Port is required")
                return
            
            # Try to convert port to int
            try:
                port = int(port)
            except ValueError:
                messagebox.showerror(APP_TITLE, "Port must be a valid number")
                return
            
            # If preset name is provided, check if it exists and if server matches
            if preset_name:
                if self.presets_manager.preset_exists(preset_name):
                    # Load existing preset to check server IP
                    existing_preset = self.presets_manager.load_preset(preset_name)
                    existing_server = existing_preset.get('server', '') if existing_preset else ''
                    
                    # If server IP differs, ask user what to do
                    if existing_server != server:
                        choice = messagebox.askyesnocancel(
                            APP_TITLE,
                            f"Preset '{preset_name}' has different server ({existing_server}).\n\n"
                            f"Current server: {server}\n\n"
                            f"Yes: Create new preset with name '{server}'\n"
                            f"No: Update existing preset '{preset_name}'\n"
                            f"Cancel: Abort"
                        )
                        
                        if choice is None:  # Cancel
                            return
                        elif choice:  # Yes - create new preset with server name
                            preset_name = server
                            # Check if this new name already exists
                            if self.presets_manager.preset_exists(preset_name):
                                if not messagebox.askyesno(
                                    APP_TITLE,
                                    f"Preset '{preset_name}' already exists. Update it?"
                                ):
                                    return
                        # else: No - continue with updating existing preset
            else:
                # No preset name provided, use server IP as preset name
                preset_name = server
                
                if not preset_name:
                    messagebox.showerror(APP_TITLE, "Please enter a server address or preset name")
                    return
                
                # Confirm using server as preset name if it's a new preset
                if not self.presets_manager.preset_exists(preset_name):
                    if not messagebox.askyesno(
                        APP_TITLE, 
                        f"Create new preset with name '{preset_name}'?"
                    ):
                        return
            
            # Save or update preset
            if self.presets_manager.preset_exists(preset_name):
                # Update existing preset
                success, message = self.presets_manager.update_preset(
                    preset_name,
                    server=server,
                    port=port,
                    calling_ae=calling_ae,
                    called_ae=called_ae,
                    use_tls=self.remote_vars["use_tls"].get(),
                    tls_config=self.tls_config if self.remote_vars["use_tls"].get() else None
                )
                
                if success:
                    self._refresh_presets_list()
                    self._append_remote_message(f"Updated preset: {preset_name}")
                    messagebox.showinfo(APP_TITLE, message)
                    self.remote_vars["preset_name"].set("")  # Clear the input field
                else:
                    messagebox.showerror(APP_TITLE, message)
            else:
                # Create new preset
                success, message = self.presets_manager.create_preset(
                    preset_name,
                    server=server,
                    port=port,
                    calling_ae=calling_ae,
                    called_ae=called_ae,
                    use_tls=self.remote_vars["use_tls"].get(),
                    tls_config=self.tls_config if self.remote_vars["use_tls"].get() else None
                )
                
                if success:
                    self._refresh_presets_list()
                    self._append_remote_message(f"Created preset: {preset_name}")
                    messagebox.showinfo(APP_TITLE, message)
                    self.remote_vars["preset_name"].set("")  # Clear the input field
                else:
                    messagebox.showerror(APP_TITLE, message)
        
        except Exception as e:
            self.logger.exception("Failed to save preset")
            messagebox.showerror(APP_TITLE, f"Failed to save preset: {e}")

    def _delete_preset(self):
        """Delete the selected preset."""
        try:
            if not self.presets_manager:
                messagebox.showerror(APP_TITLE, "Presets manager not available")
                return
            
            name = self.preset_combo.get().strip()
            if not name:
                messagebox.showerror(APP_TITLE, "No preset selected")
                return
            
            if not messagebox.askyesno(APP_TITLE, f"Delete preset '{name}'?"):
                return
            
            # Delete preset using enhanced method
            success, message = self.presets_manager.delete_preset(name)
            
            if success:
                self._refresh_presets_list()
                self._append_remote_message(f"Deleted preset: {name}")
                messagebox.showinfo(APP_TITLE, message)
            else:
                messagebox.showerror(APP_TITLE, message)
            
            # Clear preset name field
            self.remote_vars["preset_name"].set("")
        except Exception as e:
            self.logger.exception("Failed to delete preset")
            messagebox.showerror(APP_TITLE, f"Failed to delete preset: {e}")

    def _build_connection_test_tab(self):
        """Build Connection Testing tab."""
        if ConnectionValidator is None:
            label = ttk.Label(self.connection_test_frame, text="Connection Validator not available")
            label.pack(padx=10, pady=10)
            return
        
        # Title
        title_frame = ttk.Frame(self.connection_test_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="Connection Testing", font=("Arial", 12, "bold")).pack()
        
        # Configuration section
        config_frame = ttk.LabelFrame(self.connection_test_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Server:").grid(row=0, column=0, sticky="w", padx=5)
        self.conn_server = tk.StringVar(value="192.168.1.100")
        ttk.Entry(config_frame, textvariable=self.conn_server, width=30).grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(config_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5)
        self.conn_port = tk.StringVar(value="4321")
        ttk.Entry(config_frame, textvariable=self.conn_port, width=30).grid(row=1, column=1, sticky="ew", padx=5)
        
        ttk.Label(config_frame, text="Attempts:").grid(row=2, column=0, sticky="w", padx=5)
        self.conn_attempts = tk.StringVar(value="5")
        ttk.Entry(config_frame, textvariable=self.conn_attempts, width=30).grid(row=2, column=1, sticky="ew", padx=5)
        
        # Send button
        btn_frame = ttk.Frame(self.connection_test_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Test TCP", command=self._test_tcp).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Connection Quality", command=self._test_quality).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Latency Variations", command=self._test_latency).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self._clear_connection_results).pack(side=tk.LEFT, padx=2)
        
        # Results
        results_frame = ttk.LabelFrame(self.connection_test_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.connection_results = tk.Text(results_frame, height=15, width=70, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.connection_results.yview)
        self.connection_results.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.connection_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _test_tcp(self):
        """Test TCP connection."""
        if ConnectionValidator is None:
            messagebox.showerror(APP_TITLE, "Connection Validator not available")
            return
        
        try:
            server = self.conn_server.get().strip()
            port = int(self.conn_port.get().strip())
            
            if not server:
                messagebox.showerror(APP_TITLE, "Server address required")
                return
            
            validator = ConnectionValidator(logger=self.logger)
            
            def test_worker():
                result = validator.test_tcp_connection(server, port)
                self.connection_results.configure(state=tk.NORMAL)
                self.connection_results.insert(tk.END, f"\nTCP Connection Test: {server}:{port}\n")
                self.connection_results.insert(tk.END, f"=" * 60 + "\n")
                self.connection_results.insert(tk.END, f"Success: {result['success']}\n")
                if result['success']:
                    self.connection_results.insert(tk.END, f"Latency: {result['latency_ms']:.2f} ms\n")
                else:
                    self.connection_results.insert(tk.END, f"Error: {result['error']}\n")
                self.connection_results.insert(tk.END, "\n")
                self.connection_results.see(tk.END)
                self.connection_results.configure(state=tk.DISABLED)
            
            t = threading.Thread(target=test_worker, daemon=True)
            t.start()
        
        except ValueError:
            messagebox.showerror(APP_TITLE, "Port must be numeric")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Error: {e}")
    
    def _test_quality(self):
        """Test connection quality."""
        if ConnectionValidator is None:
            messagebox.showerror(APP_TITLE, "Connection Validator not available")
            return
        
        try:
            server = self.conn_server.get().strip()
            port = int(self.conn_port.get().strip())
            
            if not server:
                messagebox.showerror(APP_TITLE, "Server address required")
                return
            
            validator = ConnectionValidator(logger=self.logger)
            
            def test_worker():
                quality = validator.get_connection_quality(server, port)
                self.connection_results.configure(state=tk.NORMAL)
                self.connection_results.insert(tk.END, f"\nConnection Quality Assessment: {server}:{port}\n")
                self.connection_results.insert(tk.END, f"=" * 60 + "\n")
                self.connection_results.insert(tk.END, f"Status: {quality['status']}\n")
                self.connection_results.insert(tk.END, f"Level: {quality['level']}\n")
                self.connection_results.insert(tk.END, f"Description: {quality['description']}\n")
                self.connection_results.insert(tk.END, f"Recommendation: {quality['recommendation']}\n")
                if quality.get('latency_ms'):
                    self.connection_results.insert(tk.END, f"Latency: {quality['latency_ms']:.2f} ms\n")
                self.connection_results.insert(tk.END, "\n")
                self.connection_results.see(tk.END)
                self.connection_results.configure(state=tk.DISABLED)
            
            t = threading.Thread(target=test_worker, daemon=True)
            t.start()
        
        except ValueError:
            messagebox.showerror(APP_TITLE, "Port must be numeric")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Error: {e}")
    
    def _test_latency(self):
        """Test latency variations."""
        if ConnectionValidator is None:
            messagebox.showerror(APP_TITLE, "Connection Validator not available")
            return
        
        try:
            server = self.conn_server.get().strip()
            port = int(self.conn_port.get().strip())
            attempts = int(self.conn_attempts.get().strip())
            
            if not server:
                messagebox.showerror(APP_TITLE, "Server address required")
                return
            
            validator = ConnectionValidator(logger=self.logger)
            
            def test_worker():
                self.connection_results.configure(state=tk.NORMAL)
                self.connection_results.insert(tk.END, f"\nLatency Variations Test: {server}:{port} ({attempts} attempts)\n")
                self.connection_results.insert(tk.END, f"=" * 60 + "\n")
                self.connection_results.insert(tk.END, "Testing...\n")
                self.connection_results.see(tk.END)
                self.connection_results.configure(state=tk.DISABLED)
                
                variations = validator.test_latency_variations(server, port, attempts)
                
                self.connection_results.configure(state=tk.NORMAL)
                self.connection_results.delete("end-6c", tk.END)
                self.connection_results.insert(tk.END, f"Min Latency: {variations['min']} ms\n")
                self.connection_results.insert(tk.END, f"Max Latency: {variations['max']} ms\n")
                self.connection_results.insert(tk.END, f"Avg Latency: {variations['avg']} ms\n")
                self.connection_results.insert(tk.END, f"Std Dev: {variations['std_dev']} ms\n")
                self.connection_results.insert(tk.END, f"Successful: {variations['successful']}/{variations['attempts']}\n")
                self.connection_results.insert(tk.END, "\n")
                self.connection_results.see(tk.END)
                self.connection_results.configure(state=tk.DISABLED)
            
            t = threading.Thread(target=test_worker, daemon=True)
            t.start()
        
        except ValueError:
            messagebox.showerror(APP_TITLE, "Port and Attempts must be numeric")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Error: {e}")
    
    def _clear_connection_results(self):
        """Clear connection test results."""
        self.connection_results.configure(state=tk.NORMAL)
        self.connection_results.delete(1.0, tk.END)
        self.connection_results.configure(state=tk.DISABLED)
    
    def _build_stress_test_tab(self):
        """Build Stress Testing tab."""
        if StressTestRunner is None:
            label = ttk.Label(self.stress_test_frame, text="Stress Tester not available")
            label.pack(padx=10, pady=10)
            return
        
        # Title
        title_frame = ttk.Frame(self.stress_test_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="Stress Testing", font=("Arial", 12, "bold")).pack()
        
        # Configuration section
        config_frame = ttk.LabelFrame(self.stress_test_frame, text="Test Plan Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Test Name:").grid(row=0, column=0, sticky="w", padx=5)
        self.stress_name = tk.StringVar(value="Load Test")
        ttk.Entry(config_frame, textvariable=self.stress_name, width=30).grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(config_frame, text="Files/Second:").grid(row=1, column=0, sticky="w", padx=5)
        self.stress_fps = tk.StringVar(value="50")
        ttk.Entry(config_frame, textvariable=self.stress_fps, width=30).grid(row=1, column=1, sticky="ew", padx=5)
        
        ttk.Label(config_frame, text="Duration (sec):").grid(row=2, column=0, sticky="w", padx=5)
        self.stress_duration = tk.StringVar(value="60")
        ttk.Entry(config_frame, textvariable=self.stress_duration, width=30).grid(row=2, column=1, sticky="ew", padx=5)
        
        ttk.Label(config_frame, text="File Size (MB):").grid(row=3, column=0, sticky="w", padx=5)
        self.stress_filesize = tk.StringVar(value="1.0")
        ttk.Entry(config_frame, textvariable=self.stress_filesize, width=30).grid(row=3, column=1, sticky="ew", padx=5)
        
        ttk.Label(config_frame, text="Workers:").grid(row=4, column=0, sticky="w", padx=5)
        self.stress_workers = tk.StringVar(value="5")
        ttk.Entry(config_frame, textvariable=self.stress_workers, width=30).grid(row=4, column=1, sticky="ew", padx=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(self.stress_test_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Create Plan", command=self._create_stress_plan).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Start Test", command=self._start_stress_test).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self._clear_stress_results).pack(side=tk.LEFT, padx=2)
        
        # Results
        results_frame = ttk.LabelFrame(self.stress_test_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.stress_results = tk.Text(results_frame, height=15, wrap="word")
        self.stress_results.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.stress_results.yview)
        self.stress_results.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stress_runner = None
    
    def _create_stress_plan(self):
        """Create stress test plan."""
        if StressTestRunner is None:
            messagebox.showerror(APP_TITLE, "Stress Tester not available")
            return
        
        try:
            name = self.stress_name.get().strip()
            fps = int(self.stress_fps.get().strip())
            duration = int(self.stress_duration.get().strip())
            filesize = float(self.stress_filesize.get().strip())
            workers = int(self.stress_workers.get().strip())
            
            if not name:
                messagebox.showerror(APP_TITLE, "Test name required")
                return
            
            self.stress_runner = StressTestRunner(logger=self.logger)
            plan = self.stress_runner.create_test_plan(name, fps, duration, filesize, workers)
            
            self.stress_results.configure(state=tk.NORMAL)
            self.stress_results.delete(1.0, tk.END)
            self.stress_results.insert(tk.END, f"Stress Test Plan: {name}\n")
            self.stress_results.insert(tk.END, f"=" * 60 + "\n")
            for key, value in plan.items():
                self.stress_results.insert(tk.END, f"{key}: {value}\n")
            self.stress_results.insert(tk.END, "\n")
            self.stress_results.configure(state=tk.DISABLED)
            
            messagebox.showinfo(APP_TITLE, "Plan created. Click 'Start Test' to run simulation.")
        
        except ValueError:
            messagebox.showerror(APP_TITLE, "All fields must be numeric")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Error: {e}")
    
    def _start_stress_test(self):
        """Start stress test."""
        if self.stress_runner is None:
            messagebox.showerror(APP_TITLE, "Create a plan first")
            return
        
        # Get the test plan
        if self.stress_runner.current_test and 'plan' in self.stress_runner.current_test:
            plan = self.stress_runner.current_test['plan']
        else:
            plan = self.stress_runner.create_test_plan("Test", 50, 60, 1.0, 1)
        
        test = self.stress_runner.start_stress_test(plan)
        
        self.stress_results.configure(state=tk.NORMAL)
        self.stress_results.insert(tk.END, f"\nStarting test: {plan['name']}\n")
        self.stress_results.insert(tk.END, f"Target: {plan['files_per_second']} files/sec for {plan['duration_seconds']}s\n")
        self.stress_results.insert(tk.END, "Running...\n\n")
        self.stress_results.configure(state=tk.DISABLED)
        
        # Use logic handler to run simulation
        if DicomLogicHandler:
            logic = DicomLogicHandler(self.logger)
            logic.run_stress_test_simulation(
                self.stress_runner,
                on_complete_callback=self._display_stress_report,
                on_error_callback=lambda err: messagebox.showerror(APP_TITLE, f"Test error: {err}")
            )
        else:
            # Fallback: run directly
            def run_test():
                try:
                    self.stress_runner.run_simulation()
                    report = self.stress_runner.get_stress_test_report()
                    self.after(0, lambda: self._display_stress_report(report))
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Test error: {e}"))
            
            t = threading.Thread(target=run_test, daemon=True)
            t.start()
    
    def _display_stress_report(self, report):
        """Display stress test report in results area."""
        self.stress_results.configure(state=tk.NORMAL)
        self.stress_results.insert(tk.END, report)
        self.stress_results.see(tk.END)
        self.stress_results.configure(state=tk.DISABLED)
    
    def _clear_stress_results(self):
        """Clear stress test results."""
        self.stress_results.configure(state=tk.NORMAL)
        self.stress_results.delete(1.0, tk.END)
        self.stress_results.configure(state=tk.DISABLED)
    
    def _build_history_tab(self):
        """Build Transmission History tab."""
        if TransmissionHistory is None:
            label = ttk.Label(self.history_frame, text="Transmission History not available")
            label.pack(padx=10, pady=10)
            return
        
        # Title
        title_frame = ttk.Frame(self.history_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="Transmission History", font=("Arial", 12, "bold")).pack()
        
        # Buttons
        btn_frame = ttk.Frame(self.history_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Statistics", command=self._show_history_stats).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Export JSON", command=self._export_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self._clear_history_view).pack(side=tk.LEFT, padx=2)
        
        # Results
        results_frame = ttk.LabelFrame(self.history_frame, text="History Viewer", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.history_view = tk.Text(results_frame, height=20, width=80, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.history_view.yview)
        self.history_view.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _refresh_history(self):
        """Refresh transmission history."""
        if self.history is None:
            messagebox.showerror(APP_TITLE, "Transmission History not available")
            return
        
        try:
            recent = self.history.get_recent_transmissions(limit=50)
            
            self.history_view.configure(state=tk.NORMAL)
            self.history_view.delete(1.0, tk.END)
            self.history_view.insert(tk.END, "Recent Transmissions (Last 50)\n")
            self.history_view.insert(tk.END, "=" * 80 + "\n\n")
            
            if recent:
                for i, trans in enumerate(recent, 1):
                    self.history_view.insert(tk.END, f"{i}. {trans.get('filename', 'N/A')} ? {trans.get('server_ip', 'N/A')}:{trans.get('server_port', 'N/A')}\n")
                    self.history_view.insert(tk.END, f"   Status: {'? SUCCESS' if trans.get('success') else '? FAILED'} | ")
                    self.history_view.insert(tk.END, f"Bytes: {trans.get('bytes_sent', 0)} | ")
                    self.history_view.insert(tk.END, f"Time: {trans.get('timestamp', 'N/A')}\n\n")
            else:
                self.history_view.insert(tk.END, "No transmissions recorded yet.\n")
            
            self.history_view.configure(state=tk.DISABLED)
        
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Error: {e}")
    
    def _show_history_stats(self):
        """Show history statistics."""
        if self.history is None:
            messagebox.showerror(APP_TITLE, "Transmission History not available")
            return
        
        try:
            stats = self.history.get_statistics()
            
            msg = "Transmission Statistics\n"
            msg += "=" * 16 + "\n"
            msg += f"Total Transmissions: {stats.get('total_transmissions', 0)}\n"
            msg += f"Successful: {stats.get('successful', 0)}\n"
            msg += f"Failed: {stats.get('failed', 0)}\n"
            msg += f"Success Rate: {stats.get('success_rate', 0):.1f}%\n"
            msg += f"Total Data: {stats.get('total_mb_transferred', 0):.2f} MB\n"
            msg += f"Avg Throughput: {stats.get('avg_throughput_mbps', 0):.2f} MB/s\n"
            
            messagebox.showinfo(APP_TITLE, msg)
        
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Error: {e}")
    
    def _export_history(self):
        """Export history to JSON."""
        if self.history is None:
            messagebox.showerror(APP_TITLE, "Transmission History not available")
            return
        
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filepath:
                if self.history.export_to_json(filepath):
                    messagebox.showinfo(APP_TITLE, f"History exported to {filepath}")
                else:
                    messagebox.showerror(APP_TITLE, "Failed to export history")
        
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Error: {e}")
    
    def _clear_history_view(self):
        """Clear history view."""
        self.history_view.configure(state=tk.NORMAL)
        self.history_view.delete(1.0, tk.END)
        self.history_view.configure(state=tk.DISABLED)
    
    def _build_benchmark_tab(self):
        """Build Performance Benchmarking tab."""
        if PerformanceBenchmark is None:
            label = ttk.Label(self.benchmark_frame, text="Performance Benchmarking not available")
            label.pack(padx=10, pady=10)
            return
        
        # Title
        title_frame = ttk.Frame(self.benchmark_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="Performance Benchmarking", font=("Arial", 12, "bold")).pack()
        
        # Info
        info_frame = ttk.LabelFrame(self.benchmark_frame, text="Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text="Benchmarking module provides:\n" +
                  "- File Size Performance (0.5MB - 10MB)\n" +
                  "- Latency Analysis (min/max/avg)\n" +
                  "- Throughput Measurements\n" +
                  "- Performance Trend Analysis", justify=tk.LEFT).pack()
        
        # Buttons
        btn_frame = ttk.Frame(self.benchmark_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Open Python Console", command=self._open_benchmark_console).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Example Code", command=self._show_benchmark_example).pack(side=tk.LEFT, padx=2)
        
        # Notes
        notes_frame = ttk.LabelFrame(self.benchmark_frame, text="Usage Instructions", padding=10)
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        notes_text = tk.Text(notes_frame, height=15, width=80, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(notes_frame, orient=tk.VERTICAL, command=notes_text.yview)
        notes_text.config(yscrollcommand=scrollbar.set)
        
        notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        notes_text.configure(state=tk.NORMAL)
        notes_text.insert(tk.END, """PERFORMANCE BENCHMARKING
=====================================

To run benchmarks, use Python API:

1. File Size Benchmark:
   from src.performance_benchmarking import PerformanceBenchmark
   bench = PerformanceBenchmark()
   result = bench.run_file_size_benchmark(send_func, sizes_mb=[1,5,10])

2. Latency Benchmark:
   result = bench.run_latency_benchmark(ping_func, iterations=10)

3. Throughput Benchmark:
   result = bench.run_throughput_benchmark(send_batch_func, 100, 1.0)

4. Get Reports:
   print(bench.get_benchmark_report(0))
   print(bench.get_all_benchmarks_summary())

See: doc/COMPLETE_TEST_EXECUTION_REFERENCE.md for examples
""")
        notes_text.configure(state=tk.DISABLED)
    
    def _open_benchmark_console(self):
        """Open Python console for benchmarking."""
        messagebox.showinfo(APP_TITLE, "Run Python console:\n\npython\n>>> from src.performance_benchmarking import PerformanceBenchmark\n>>> bench = PerformanceBenchmark()")
    
    def _show_benchmark_example(self):
        """Show benchmark example code."""
        example = """Example Benchmark Code:

from src.performance_benchmarking import PerformanceBenchmark

bench = PerformanceBenchmark()

# Define send function
def mock_send(size_mb):
    import time
    time.sleep(0.1)
    return size_mb * 1024 * 1024, 0.1

# Run file size benchmark
result = bench.run_file_size_benchmark(
    send_function=mock_send,
    sizes_mb=[1, 5, 10],
    iterations=3
)

# Get report
print(bench.get_benchmark_report(0))
print(bench.get_all_benchmarks_summary())

BENEFITS:
- 5 workers = ~5x faster than sequential
- Automatic load balancing
- Real-time progress tracking
- Detailed performance report

Tips:
- For large files, increase memory limits
- Monitor CPU/memory usage during tests
- Adjust worker count based on system capability
"""
        messagebox.showinfo(APP_TITLE, example)
    
    def _build_parallel_tab(self):
        """Build Parallel Transmission tab."""
        if ParallelTransmissionManager is None:
            label = ttk.Label(self.parallel_frame, text="Parallel Transmission not available")
            label.pack(padx=10, pady=10)
            return
        
        # Title
        title_frame = ttk.Frame(self.parallel_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="Parallel Transmission Manager", font=("Arial", 12, "bold")).pack()
        
        # Configuration
        config_frame = ttk.LabelFrame(self.parallel_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Worker Threads:").grid(row=0, column=0, sticky="w", padx=5)
        self.parallel_workers = tk.StringVar(value="5")
        ttk.Entry(config_frame, textvariable=self.parallel_workers, width=30).grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(config_frame, text="Session Name:").grid(row=1, column=0, sticky="w", padx=5)
        self.parallel_session_name = tk.StringVar(value="Bulk Transmission")
        ttk.Entry(config_frame, textvariable=self.parallel_session_name, width=30).grid(row=1, column=1, sticky="ew", padx=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Info
        info_frame = ttk.LabelFrame(self.parallel_frame, text="Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text="Parallel Transmission features:\n" +
                  "- Multi-threaded file transmission (1-10 workers)\n" +
                  "- 3-5x speed improvement over sequential\n" +
                  "- Session management and progress tracking\n" +
                  "- Real-time performance metrics\n\n" +
                  "Note: Configure workers and use Python API for active transmission",
                  justify=tk.LEFT).pack()
        
        # Buttons
        btn_frame = ttk.Frame(self.parallel_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Save Config", command=self.save_parallel_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Example Code", command=self._show_parallel_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Documentation", command=self._show_parallel_docs).pack(side=tk.LEFT, padx=2)
    
    def _show_parallel_example(self):
        """Show parallel transmission example code."""
        example = """Parallel Transmission Example:

from src.parallel_transmission import ParallelTransmissionManager

# Create manager with 5 workers
mgr = ParallelTransmissionManager(max_workers=5)

# Start session
session = mgr.start_session("Bulk Send")

# Define send function
def send_dicom(file_path):
    # Your transmission logic
    return True

# Queue files
for file_path in file_list:
    mgr.queue_transmission(file_path, send_dicom)

# Or queue batch
mgr.queue_batch(file_list, send_dicom)

# Wait for completion
mgr.wait_for_completion(timeout=3600)

# Get session report
report = mgr.get_session_report()
print(f"Files sent: {report['files_sent']}")
print(f"Success rate: {report['success_rate']}%")
print(f"Duration: {report['duration_seconds']}s")
print(f"Throughput: {report['throughput_mbps']} MB/s")

Benefits:
- 5 workers = ~5x faster than sequential
- Automatic load balancing
- Real-time progress tracking
- Detailed performance report
"""
        messagebox.showinfo(APP_TITLE, example)

    def _show_parallel_docs(self):
        """Show parallel transmission documentation."""
        docs = """Parallel Transmission Manager
=====================================

CONFIGURATION:
- Worker Threads: 1-10 (more = faster but higher CPU)
- Session Name: Name for this transmission session

FEATURES:
1. Queue-based distribution
2. Multi-threaded execution
3. Session management
4. Progress tracking
5. Performance metrics

PERFORMANCE:
- 5 workers: ~5MB/s per worker
- 10 workers: up to 10x improvement
- CPU usage: Moderate (mostly network I/O)

RECOMMENDED SETTINGS:
- Light load: 2-3 workers
- Medium load: 5 workers
- Heavy load: 8-10 workers

See: doc/WHERE_TO_RUN_TESTS.md
"""
        messagebox.showinfo(APP_TITLE, docs)

    def save_parallel_config(self):
        """Save parallel transmission configuration to JSON file."""
        try:
            import json
            config = {
                "workers": int(self.parallel_workers.get()),
                "session_name": self.parallel_session_name.get()
            }
            with open("parallel_config.json", "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo(APP_TITLE, "Configuration saved to: parallel_config.json\n\n"
                                          "You can now run: python examples/parallel_send.py")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to save config: {e}")
            self.logger.exception("Failed to save parallel config")

    def _update_tab_visibility(self):
        """Update the visibility of tabs based on the menu selections."""
        try:
            if not self.container:
                return
            
            # Remove all tabs first
            for tab in self.container.tabs():
                self.container.forget(tab)

            # Re-add visible tabs in order
            tab_order = [
                "Patient", "Study", "Series/Modality", "Image", 
                "Load DICOM", "Save", "Remote", "Query PACS", "Test/Generate",
                "Connection Test", "Stress Test", "Transmission History",
                "Benchmarking", "Parallel Send"
            ]
            
            for tab_name in tab_order:
                if self.tab_visibility[tab_name].get():
                    frame, text = self.tab_frames[tab_name]
                    self.container.add(frame, text=text)

            self.container.update_idletasks()
        except Exception as e:
            self.logger.exception("Failed to update tab visibility")
            messagebox.showerror(APP_TITLE, f"Error updating tab visibility: {e}")

    def _show_all_tabs(self):
        """Show all tabs."""
        for var in self.tab_visibility.values():
            var.set(True)
        self._update_tab_visibility()
    
    def _hide_test_tabs(self):
        """Hide test-related tabs and show only core tabs."""
        test_tabs = [
            "Test/Generate", "Connection Test", "Stress Test",
            "Transmission History", "Benchmarking", "Parallel Send"
        ]
        for tab_name, var in self.tab_visibility.items():
            if tab_name in test_tabs:
                var.set(False)
            else:
                var.set(True)
        self._update_tab_visibility()


class VRViewerDialog(tk.Toplevel):
    """Dialog for viewing DICOM Value Representations from VR.xml."""
    
    def __init__(self, parent, logger):
        super().__init__(parent)
        self.logger = logger
        self.title("DICOM Value Representations (VR) Viewer")
        self.geometry("1000x600")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
        self._load_vr_data()
    
    def _build_ui(self):
        """Build the dialog UI."""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="DICOM Data Dictionary - Value Representations", 
                 font=("Arial", 12, "bold")).pack()
        
        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self._clear_search).pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = ttk.Label(self, text="Loading VR data...")
        self.info_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Tree frame with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Create treeview with columns
        columns = ("Tag", "Name", "Keyword", "VR", "VM", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Configure column headings and widths
        self.tree.heading("Tag", text="Tag", command=lambda: self._sort_by_column("Tag", False))
        self.tree.heading("Name", text="Name", command=lambda: self._sort_by_column("Name", False))
        self.tree.heading("Keyword", text="Keyword", command=lambda: self._sort_by_column("Keyword", False))
        self.tree.heading("VR", text="VR", command=lambda: self._sort_by_column("VR", False))
        self.tree.heading("VM", text="VM", command=lambda: self._sort_by_column("VM", False))
        self.tree.heading("Status", text="Status", command=lambda: self._sort_by_column("Status", False))
        
        self.tree.column("Tag", width=120, anchor="center")
        self.tree.column("Name", width=300, anchor="w")
        self.tree.column("Keyword", width=250, anchor="w")
        self.tree.column("VR", width=60, anchor="center")
        self.tree.column("VM", width=60, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self._load_vr_data).pack(side=tk.RIGHT, padx=5)
        
        # Store all items for search filtering
        self.all_items = []
    
    def _load_vr_data(self):
        """Load and parse VR data from VR.xml file."""
        try:
            # Use resource path helper for PyInstaller compatibility
            vr_file = get_resource_path("VR.xml")
            
            # Fallback: try in src subdirectory
            if not os.path.exists(vr_file):
                vr_file = get_resource_path(os.path.join("src", "VR.xml"))
            
            if not os.path.exists(vr_file):
                self.info_label.config(text="Error: VR.xml not found")
                self.logger.error(f"VR.xml not found. Tried paths:")
                self.logger.error(f"  1. {get_resource_path('VR.xml')}")
                self.logger.error(f"  2. {get_resource_path(os.path.join('src', 'VR.xml'))}")
                return
            
            self.info_label.config(text="Parsing VR.xml...")
            self.update_idletasks()
            
            # Use logic handler to parse XML
            if DicomLogicHandler is not None:
                logic = DicomLogicHandler(self.logger)
                success, result = logic.parse_vr_xml(vr_file)
                
                if not success:
                    # result is error message
                    self.info_label.config(text=result)
                    messagebox.showerror("VR Viewer Error", result)
                    return
                
                # result is list of VR data dicts
                vr_data = result
            else:
                # Fallback if logic handler not available
                self.info_label.config(text="Error: Logic handler not available")
                return
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.all_items.clear()
            
            # Populate tree with parsed data
            count = 0
            for vr_item in vr_data:
                # Add to tree
                item_id = self.tree.insert("", "end", values=(
                    vr_item['tag'],
                    vr_item['name'],
                    vr_item['keyword'],
                    vr_item['vr'],
                    vr_item['vm'],
                    vr_item['status']
                ))
                
                # Style retired items differently
                if vr_item['is_retired']:
                    self.tree.item(item_id, tags=("retired",))
                
                # Store for search
                self.all_items.append({
                    "id": item_id,
                    "tag": vr_item['tag'],
                    "name": vr_item['name'],
                    "keyword": vr_item['keyword'],
                    "vr": vr_item['vr'],
                    "vm": vr_item['vm'],
                    "status": vr_item['status']
                })
                
                count += 1
            
            # Configure retired item styling
            self.tree.tag_configure("retired", foreground="gray")
            
            self.info_label.config(text=f"Loaded {count} DICOM data elements from PS3.6 Data Dictionary")
            self.logger.info(f"Loaded {count} VR entries from VR.xml")
            
        except Exception as e:
            error_msg = f"Failed to load VR data: {e}"
            self.info_label.config(text=error_msg)
            self.logger.exception("Failed to load VR.xml")
            messagebox.showerror("VR Viewer Error", error_msg)

    
    def _on_search_changed(self, *args):
        """Handle search text changes."""
        search_text = self.search_var.get().lower()
        
        # Clear current view
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # If empty search, show all items
        if not search_text:
            for item_data in self.all_items:
                item_id = self.tree.insert("", "end", values=(
                    item_data["tag"], item_data["name"], item_data["keyword"],
                    item_data["vr"], item_data["vm"], item_data["status"]
                ))
                if "RET" in item_data["status"]:
                    self.tree.item(item_id, tags=("retired",))
            self.info_label.config(text=f"Showing all {len(self.all_items)} data elements")
            return
        
        # Filter items
        matches = 0
        for item_data in self.all_items:
            # Search in tag, name, and keyword
            if (search_text in item_data["tag"].lower() or
                search_text in item_data["name"].lower() or
                search_text in item_data["keyword"].lower()):
                
                item_id = self.tree.insert("", "end", values=(
                    item_data["tag"], item_data["name"], item_data["keyword"],
                    item_data["vr"], item_data["vm"], item_data["status"]
                ))
                if "RET" in item_data["status"]:
                    self.tree.item(item_id, tags=("retired",))
                matches += 1
        
        self.info_label.config(text=f"Found {matches} matching data elements")
    
    def _clear_search(self):
        """Clear search text."""
        self.search_var.set("")
    
    def _sort_by_column(self, col, reverse):
        """Sort treeview by column."""
        try:
            # Get all items
            items = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
            
            # Sort items
            items.sort(reverse=reverse)
            
            # Rearrange items in sorted positions
            for index, (val, item) in enumerate(items):
                self.tree.move(item, "", index)
            
            # Reverse sort next time
            self.tree.heading(col, command=lambda: self._sort_by_column(col, not reverse))
        except Exception as e:
            self.logger.debug(f"Sort error: {e}")

