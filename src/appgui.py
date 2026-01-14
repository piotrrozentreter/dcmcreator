import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading

try:
    import pydicom
except Exception as e:
    pydicom = None

try:
    from PIL import Image, ImageTk
    import numpy as np
except Exception:
    Image = None
    ImageTk = None
    np = None

APP_TITLE = "DICOM Creator v0.3.1\n"

try:
    from .dcmlogger import setup_logging, LOGGER_NAME
except Exception:
    from dcmlogger import setup_logging, LOGGER_NAME

try:
    from .presets import ServerPresetsManager
except Exception:
    try:
        from presets import ServerPresetsManager
    except Exception:
        ServerPresetsManager = None

try:
    from .random_dicom import RandomDicomGenerator
except Exception:
    try:
        from random_dicom import RandomDicomGenerator
    except Exception:
        RandomDicomGenerator = None

try:
    from .test_runner import TestRunner
except Exception:
    try:
        from test_runner import TestRunner
    except Exception:
        TestRunner = None

# New test modules imports
try:
    from .connection_validator import ConnectionValidator
except Exception:
    try:
        from connection_validator import ConnectionValidator
    except Exception:
        ConnectionValidator = None

try:
    from .stress_tester import StressTestRunner
except Exception:
    try:
        from stress_tester import StressTestRunner
    except Exception:
        StressTestRunner = None

try:
    from .transmission_history import TransmissionHistory
except Exception:
    try:
        from transmission_history import TransmissionHistory
    except Exception:
        TransmissionHistory = None

try:
    from .performance_benchmarking import PerformanceBenchmark
except Exception:
    try:
        from performance_benchmarking import PerformanceBenchmark
    except Exception:
        PerformanceBenchmark = None

try:
    from .parallel_transmission import ParallelTransmissionManager
except Exception:
    try:
        from parallel_transmission import ParallelTransmissionManager
    except Exception:
        ParallelTransmissionManager = None


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
        if ServerPresetsManager:
            self.presets_manager = ServerPresetsManager()
        else:
            self.presets_manager = None

        # Tab visibility state
        self.tab_visibility = {
            "Patient": tk.BooleanVar(value=True),
            "Study": tk.BooleanVar(value=True),
            "Series/Modality": tk.BooleanVar(value=True),
            "Image": tk.BooleanVar(value=True),
            "Load DICOM": tk.BooleanVar(value=True),
            "Save": tk.BooleanVar(value=True),
            "Remote": tk.BooleanVar(value=True),
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
        file_menu.add_command(label="Exit", command=self.on_quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Remote menu
        remote_menu = tk.Menu(menubar, tearoff=False)
        remote_menu.add_command(label="Send to Remote", command=lambda: self.send_remote(), accelerator="Ctrl+R")
        menubar.add_cascade(label="Remote", menu=remote_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_label("Core Tabs", state=tk.DISABLED)
        view_menu.add_checkbutton(label="Patient", variable=self.tab_visibility["Patient"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Study", variable=self.tab_visibility["Study"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Series/Modality", variable=self.tab_visibility["Series/Modality"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Image", variable=self.tab_visibility["Image"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Load DICOM", variable=self.tab_visibility["Load DICOM"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Save", variable=self.tab_visibility["Save"], command=self._update_tab_visibility)
        view_menu.add_checkbutton(label="Remote", variable=self.tab_visibility["Remote"], command=self._update_tab_visibility)
        view_menu.add_separator()
        view_menu.add_label("Test Tabs", state=tk.DISABLED)
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
        self.bind_all("<Control-Shift-o>", lambda e: self.load_dicom_folder())
        self.bind_all("<Control-s>", lambda e: self.save_dicom())
        self.bind_all("<Control-r>", lambda e: self.send_remote())

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
        self.test_frame = ttk.Frame(container)
        
        # New test tabs
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
        
        # Test/Generate tab
        self._build_test_tab()
        
        # Build new test tabs
        self._build_connection_test_tab()
        self._build_stress_test_tab()
        self._build_history_tab()
        self._build_benchmark_tab()
        self._build_parallel_tab()
        
    def _build_patient_fields(self):
        """Build patient metadata form fields."""
        self.patient_vars = {
            "PatientName": tk.StringVar(),
            "PatientFamilyNameComplex": tk.StringVar(),
            "PatientPrefix": tk.StringVar(),
            "PatientGivenName": tk.StringVar(),
            "PatientMiddleName": tk.StringVar(),
            "PatientSuffix": tk.StringVar(),
            "PatientID": tk.StringVar(),
            "PatientBirthDate": tk.StringVar(),
            "PatientSex": tk.StringVar(),
            "PatientAge": tk.StringVar(),
            "PatientWeight": tk.StringVar(),
            "PatientSize": tk.StringVar(),
            "PatientComments": tk.StringVar(),
            "PatientMothersBirthName": tk.StringVar(),
            "PatientDeathDateTime": tk.StringVar(),
        }
        self._add_labeled_entry(self.patient_frame, "Patient Name", self.patient_vars["PatientName"], 0)
        self._add_labeled_entry(self.patient_frame, "Family Name Complex", self.patient_vars["PatientFamilyNameComplex"], 1)
        self._add_labeled_entry(self.patient_frame, "Prefix", self.patient_vars["PatientPrefix"], 2)
        self._add_labeled_entry(self.patient_frame, "Given Name", self.patient_vars["PatientGivenName"], 3)
        self._add_labeled_entry(self.patient_frame, "Middle Name", self.patient_vars["PatientMiddleName"], 4)
        self._add_labeled_entry(self.patient_frame, "Suffix", self.patient_vars["PatientSuffix"], 5)
        self._add_labeled_entry(self.patient_frame, "Patient ID", self.patient_vars["PatientID"], 6)
        self._add_labeled_entry(self.patient_frame, "Birth Date (YYYYMMDD)", self.patient_vars["PatientBirthDate"], 7)
        self._add_labeled_entry(self.patient_frame, "Sex (M/F/O)", self.patient_vars["PatientSex"], 8)
        self._add_labeled_entry(self.patient_frame, "Patient Age (e.g., 032Y)", self.patient_vars["PatientAge"], 9)
        self._add_labeled_entry(self.patient_frame, "Patient Weight (kg)", self.patient_vars["PatientWeight"], 10)
        self._add_labeled_entry(self.patient_frame, "Patient Size/Height (m)", self.patient_vars["PatientSize"], 11)
        self._add_labeled_entry(self.patient_frame, "Patient Comments", self.patient_vars["PatientComments"], 12)
        self._add_labeled_entry(self.patient_frame, "Mother's Birth Name", self.patient_vars["PatientMothersBirthName"], 13)
        self._add_labeled_entry(self.patient_frame, "Datetime of death\n(YYYYMMDDHHMMSS)", self.patient_vars["PatientDeathDateTime"], 14)

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
        with_patient_id = ["ReferringPhysicianName", "ReadingPhysicianName"]
        for i, (label, var) in enumerate(self.study_vars.items()):
            if label in with_patient_id:
                continue
            self._add_labeled_entry(self.study_frame, label.replace("Name", " Physician Name"), var, i+7)

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
        }
        
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

    def _build_test_tab(self):
        """Build Test/Generator tab for creating and testing bulk DICOM transmission."""
        # Generator section
        gen_frame = ttk.LabelFrame(self.test_frame, text="DICOM Generator", padding=10)
        gen_frame.pack(fill=tk.X, padx=10, pady=5)
        
        gen_inner = ttk.Frame(gen_frame)
        gen_inner.pack(fill=tk.X)
        gen_inner.columnconfigure(1, weight=1)
        
        ttk.Label(gen_inner, text="Count:").grid(row=0, column=0, sticky="w", padx=5)
        self.test_vars = {}
        self.test_vars["count"] = tk.StringVar(value="10")
        ttk.Entry(gen_inner, textvariable=self.test_vars["count"], width=10).grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(gen_inner, text="Size/File (MB):").grid(row=0, column=2, sticky="w", padx=5)
        self.test_vars["size_mb"] = tk.StringVar(value="1.0")
        ttk.Entry(gen_inner, textvariable=self.test_vars["size_mb"], width=10).grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(gen_inner, text="Output Dir:").grid(row=1, column=0, sticky="w", padx=5)
        self.test_vars["output_dir"] = tk.StringVar()
        ttk.Entry(gen_inner, textvariable=self.test_vars["output_dir"]).grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)
        ttk.Button(gen_inner, text="Browse", command=self._select_test_output_dir, width=8).grid(row=1, column=3, padx=5)
        
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

    def _generate_test_dicoms(self):
        """Generate test DICOM files."""
        if RandomDicomGenerator is None:
            messagebox.showerror(APP_TITLE, "RandomDicomGenerator not available")
            return

        try:
            count = int(self.test_vars["count"].get())
            size_mb = float(self.test_vars["size_mb"].get())
            output_dir = self.test_vars["output_dir"].get()

            if not output_dir:
                messagebox.showerror(APP_TITLE, "Please select an output directory")
                return

            self._append_test_status(f"Generating {count} test DICOMs ({size_mb}MB each)...")

            generator = RandomDicomGenerator(logger=self.logger)
            files = generator.generate_with_sizes(count=count, size_mb=size_mb, output_dir=output_dir)

            self._append_test_status(f"? Generated {len(files)} test DICOM files")
            self._append_test_status(f"  Location: {output_dir}")

            messagebox.showinfo(APP_TITLE, f"Generated {len(files)} test DICOM files")
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
            self.send_remote()
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
            f"{APP_TITLE}(c) 2025-2026 by Hyland\nWritten by Piotr Rozentreter\n\n"
            "Simple tool to create and edit DICOM metadata and images."
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
            # Normalize to 8-bit if needed
            if arr.ndim == 2:
                img = Image.fromarray(self._to_uint8(arr), mode="L")
            elif arr.ndim == 3 and arr.shape[2] in (3, 4):
                if arr.dtype != np.uint8:
                    arr = self._to_uint8(arr)
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
                        
                    img = Image.fromarray(self._to_uint8(arr2), mode="L")
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

    def _to_uint8(self, arr):
        """Normalize arbitrary numeric array to uint8 [0,255] range for display."""
        if arr.dtype == np.uint8:
            return arr
        a = arr.astype(np.float32)
        mn = np.min(a)
        mx = np.max(a)
        if mx - mn > 1e-5:
            a = (a - mn) / (mx - mn) * 255.0
        else:
            a = np.zeros_like(a) if not np.any(a) else np.full_like(a, 255)
        return a.astype(np.uint8)

    def save_dicom(self):
        """Save the current metadata and pixel data into a DICOM file."""
        if pydicom is None:
            self.logger.warning("pydicom not available; cannot save DICOM")
            messagebox.showerror(APP_TITLE, "pydicom is required to save DICOM files.")
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

        try:
            ds = create_dicom(
                save_path=save_path,
                patient={
                    "PatientName": self.patient_vars["PatientName"].get().strip(),
                    "PatientFamilyNameComplex": self.patient_vars["PatientFamilyNameComplex"].get().strip(),
                    "PatientPrefix": self.patient_vars["PatientPrefix"].get().strip(),
                    "PatientGivenName": self.patient_vars["PatientGivenName"].get().strip(),
                    "PatientMiddleName": self.patient_vars["PatientMiddleName"].get().strip(),
                    "PatientSuffix": self.patient_vars["PatientSuffix"].get().strip(),
                    "PatientID": self.patient_vars["PatientID"].get().strip(),
                    "PatientBirthDate": self.patient_vars["PatientBirthDate"].get().strip(),
                    "PatientSex": self.patient_vars["PatientSex"].get().strip(),
                    "PatientAge": self.patient_vars["PatientAge"].get().strip(),
                    "PatientWeight": self.patient_vars["PatientWeight"].get().strip(),
                    "PatientSize": self.patient_vars["PatientSize"].get().strip(),
                    "PatientComments": self.patient_vars["PatientComments"].get().strip(),
                    "PatientMotherBirthName": self.patient_vars["PatientMothersBirthName"].get().strip(),
                    "PatientDeathDateTime": self.patient_vars["PatientDeathDateTime"].get().strip(),
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
        except Exception as e:
            self.logger.exception("Failed to create DICOM dataset")
            messagebox.showerror(APP_TITLE, f"Failed to create DICOM: {e}")
            return

        try:
            ds.save_as(save_path)
            messagebox.showinfo(APP_TITLE, f"DICOM saved to: {save_path}")
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
                    self.series_tree.insert(series_node, "end", text=inst_text)
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
        
        # Update image info
        rows = getattr(ds, 'Rows', None)
        cols = getattr(ds, 'Columns', None)
        if rows and cols:
            self.image_label.config(text=f"Selected Series: {series_uid} | {cols}x{rows}")
            
        # Only update preview if no user-loaded image is active
        if self.image_source != "file" and arr is not None:
            self.image_source = "dicom"
            self._update_image_preview(arr)

    def _populate_patient_fields(self, ds):
        """Populate patient form fields from DICOM dataset."""
        self.patient_vars["PatientName"].set(str(getattr(ds, 'PatientName', '') or ''))
        
        try:
            pn = getattr(ds, 'PatientName', '')
            fam = getattr(pn, 'family_name', '') if pn else ''
            giv = getattr(pn, 'given_name', '') if pn else ''
            mid = getattr(pn, 'middle_name', '') if pn else ''
            pref = getattr(pn, 'name_prefix', '') if pn else ''
            suf = getattr(pn, 'name_suffix', '') if pn else ''
            self.patient_vars["PatientFamilyNameComplex"].set(str(fam or ''))
            self.patient_vars["PatientGivenName"].set(str(giv or ''))
            self.patient_vars["PatientMiddleName"].set(str(mid or ''))
            self.patient_vars["PatientPrefix"].set(str(pref or ''))
            self.patient_vars["PatientSuffix"].set(str(suf or ''))
        except Exception:
            pass
            
        self.patient_vars["PatientID"].set(str(getattr(ds, 'PatientID', '') or ''))
        self.patient_vars["PatientBirthDate"].set(str(getattr(ds, 'PatientBirthDate', '') or ''))
        self.patient_vars["PatientSex"].set(str(getattr(ds, 'PatientSex', '') or ''))
        self.patient_vars["PatientAge"].set(str(getattr(ds, 'PatientAge', '') or ''))
        self.patient_vars["PatientWeight"].set(str(getattr(ds, 'PatientWeight', '') or ''))
        self.patient_vars["PatientSize"].set(str(getattr(ds, 'PatientSize', '') or ''))
        self.patient_vars["PatientComments"].set(str(getattr(ds, 'PatientComments', '') or ''))
        self.patient_vars["PatientMothersBirthName"].set(str(getattr(ds, 'PatientMotherBirthName', '') or ''))
        self.patient_vars["PatientDeathDateTime"].set(str(getattr(ds, 'PatientDeathDateTime', '') or ''))

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
        self.series_vars["SeriesNumber"].set(str(getattr(ds, 'InstanceNumber', getattr(ds, 'SeriesNumber', '')) or ''))
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
            self.remote_messages.configure(state=tk.DISABLED)
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
        
        # Always create dataset from current form values to ensure modifications are sent
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
                    "PatientFamilyNameComplex": self.patient_vars["PatientFamilyNameComplex"].get().strip(),
                    "PatientPrefix": self.patient_vars["PatientPrefix"].get().strip(),
                    "PatientGivenName": self.patient_vars["PatientGivenName"].get().strip(),
                    "PatientMiddleName": self.patient_vars["PatientMiddleName"].get().strip(),
                    "PatientSuffix": self.patient_vars["PatientSuffix"].get().strip(),
                    "PatientID": patient_id,
                    "PatientBirthDate": self.patient_vars["PatientBirthDate"].get().strip(),
                    "PatientSex": self.patient_vars["PatientSex"].get().strip(),
                    "PatientAge": self.patient_vars["PatientAge"].get().strip(),
                    "PatientWeight": self.patient_vars["PatientWeight"].get().strip(),
                    "PatientSize": self.patient_vars["PatientSize"].get().strip(),
                    "PatientComments": self.patient_vars["PatientComments"].get().strip(),
                    "PatientMotherBirthName": self.patient_vars["PatientMothersBirthName"].get().strip(),
                    "PatientDeathDateTime": self.patient_vars["PatientDeathDateTime"].get().strip(),
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
            
            self._append_remote_message(f"Loaded preset: {name}")
            messagebox.showinfo(APP_TITLE, f"Preset '{name}' loaded successfully")
        except Exception as e:
            self.logger.exception("Failed to load preset")
            messagebox.showerror(APP_TITLE, f"Failed to load preset: {e}")

    def _save_current_preset(self):
        """Save the current remote settings to a preset.
        
        If preset name is provided, uses that. Otherwise uses Server IP/name.
        If preset already exists, it will be replaced.
        """
        try:
            # Get preset name from input
            preset_name = self.remote_vars["preset_name"].get().strip()
            
            # If no name provided, use server IP/hostname as preset name
            if not preset_name:
                preset_name = self.remote_vars["server"].get().strip()
                
                if not preset_name:
                    messagebox.showerror(APP_TITLE, "Please enter a server address or preset name")
                    return
                
                # Confirm using server as preset name
                if not messagebox.askyesno(
                    APP_TITLE, 
                    f"No preset name provided.\nUse server '{preset_name}' as preset name?"
                ):
                    return
            
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
            
            # Check if preset already exists
            if self.presets_manager.preset_exists(preset_name):
                # Update existing preset
                success, message = self.presets_manager.update_preset(
                    preset_name,
                    server=server,
                    port=port,
                    calling_ae=calling_ae,
                    called_ae=callsed_ae
                )
                
                if success:
                    self._refresh_presets_list()
                    self._append_remote_message(f"? Updated preset: {preset_name}")
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
                    called_ae=callsed_ae
                )
                
                if success:
                    self._refresh_presets_list()
                    self._append_remote_message(f"? Created preset: {preset_name}")
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
                self._append_remote_message(f"? Deleted preset: {name}")
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
        
        config_frame.columnconfigure(1, weight=1)
        
        # Buttons
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
        
        self.connection_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
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
        
        self.stress_results = tk.Text(results_frame, height=15, width=70, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.stress_results.yview)
        self.stress_results.config(yscrollcommand=scrollbar.set)
        
        self.stress_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
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
        
        test = self.stress_runner.start_stress_test(self.stress_runner.current_test['plan'] if hasattr(self.stress_runner, 'current_test') else self.stress_runner.create_test_plan("Test", 50, 60))
        
        self.stress_results.configure(state=tk.NORMAL)
        self.stress_results.insert(tk.END, "\nTest running...\n")
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
        
        self.history_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history = TransmissionHistory(logger=self.logger) if TransmissionHistory else None
    
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
            msg += "=" * 50 + "\n"
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
        ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.parallel_workers, width=10).grid(row=0, column=1, sticky="w", padx=5)
        
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
        ttk.Button(btn_frame, text="Example Code", command=self._show_parallel_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Documentation", command=self._show_parallel_docs).pack(side=tk.LEFT, padx=2)
    
    def _show_parallel_example(self):
        """Show parallel transmission example."""
        example = """Parallel Transmission Example:

from src.parallel_transmission import ParallelTransmissionManager

# Create manager with 5 workers
mgr = ParallelTransmissionManager(max_workers=5)

# Start session
session = mgr.start_session("Bulk Send")

# Queue files for transmission
for file_path in file_list:
    mgr.queue_transmission(file_path, send_function)

# Or queue batch
mgr.queue_batch(file_list, send_function)

# Wait for completion
mgr.wait_for_completion(timeout=3600)

# Get report
print(mgr.get_session_report())

# Benefits:
# - 5 workers = ~5x faster than sequential
# - Automatic load balancing
# - Real-time progress tracking
# - Detailed performance report
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

    def _build_view_menu(self, menubar):
        """Build the View menu for controlling tab visibility."""
        for tab_name, var in self.tab_visibility.items():
            # Skip built-in tabs
            if tab_name in ("Patient", "Study", "Series/Modality", "Image", "Load DICOM", "Save", "Remote"):
                continue
            
            # Add checkbox menu item for each tab
            menubar.add_checkbutton(
                label=f"Show {tab_name} Tab",
                variable=var,
                command=self._update_tab_visibility
            )

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
                "Load DICOM", "Save", "Remote", "Test/Generate",
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
