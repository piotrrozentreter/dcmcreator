import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime
import logging
import sys
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

APP_TITLE = "DICOM Creator v0.2.2\n"
try:
    from .dcmlogger import setup_logging, LOGGER_NAME
except Exception:
    # Fallback when running as a script (no package context)
    from dcmlogger import setup_logging, LOGGER_NAME

class DicomCreatorApp(tk.Tk):
    # Main application window for DICOM creation and editing.
    # Provides tabs for Patient/Study/Series metadata, image loading, DICOM loading, and saving.
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

        # DICOM loading state
        self.grouped_dicom = {}
        self.selected_study_uid = None
        self.selected_series_uid = None

        self._build_ui()

    def _build_ui(self):
        # Build the overall UI: menu bar and a tabbed notebook with multiple sections.
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

        self.patient_frame = ttk.Frame(container)
        self.study_frame = ttk.Frame(container)
        self.series_frame = ttk.Frame(container)
        self.image_frame = ttk.Frame(container)
        self.load_dcm_frame = ttk.Frame(container)
        self.save_frame = ttk.Frame(container)
        self.remote_frame = ttk.Frame(container)

        container.add(self.patient_frame, text="Patient")
        container.add(self.study_frame, text="Study")
        container.add(self.series_frame, text="Series/Modality")
        container.add(self.image_frame, text="Image")
        container.add(self.load_dcm_frame, text="Load DICOM")
        container.add(self.save_frame, text="Save")
        container.add(self.remote_frame, text="Remote")

        # Patient fields
        # Metadata variables are bound to form entries for easy retrieval and population.
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

        # Study fields
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
        self._add_labeled_entry(self.study_frame, "Reason for Study", self.study_vars["ReasonForStudy"], 8)
        self._add_labeled_entry(self.study_frame, "Admit Diagnosis", self.study_vars["AdmittingDiagnosesDescription"], 9)
        self._add_labeled_entry(self.study_frame, "Study Patient Location", self.study_vars["StudyPatientLocation"], 10)

        # Series fields
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

        # Image tab
        # Controls to load an external image and preview it.
        img_controls = ttk.Frame(self.image_frame)
        img_controls.pack(fill=tk.X, pady=10)
        ttk.Button(img_controls, text="Load Image", command=self.load_image).pack(side=tk.LEFT)
        self.image_label = ttk.Label(self.image_frame, text="No image loaded")
        self.image_label.pack(fill=tk.X, pady=10)
        # Image preview area
        self.preview_label = ttk.Label(self.image_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Save tab
        # Save the currently entered metadata and image as a DICOM file.
        ttk.Button(self.save_frame, text="Save DICOM", command=self.save_dicom).pack(pady=20)

        # Load DICOM tab
        # Load DICOM files or folders, then visualize Study/Series/Instances in a tree.
        dcm_controls = ttk.Frame(self.load_dcm_frame)
        dcm_controls.pack(fill=tk.X, pady=10)
        ttk.Button(dcm_controls, text="Load DICOM File(s)", command=self.load_dicom_file).pack(side=tk.LEFT)
        ttk.Button(dcm_controls, text="Load DICOM Folder", command=self.load_dicom_folder).pack(side=tk.LEFT, padx=8)
        self.dcm_info_label = ttk.Label(self.load_dcm_frame, text="No DICOM loaded")
        self.dcm_info_label.pack(fill=tk.X, pady=10)

        # Studies/Series tree with scrollbars
        # Tree hierarchy: Study -> Series -> Instance (text only for instances).
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

        # Remote tab UI
        self._build_remote_ui()

    def _build_remote_ui(self):
        # Controls for remote DICOM transmission (C-STORE)
        self.remote_vars = {
            "server": tk.StringVar(),
            "port": tk.StringVar(value="4321"),
            "calling_ae": tk.StringVar(value="DCMCREATOR"),
            "called_ae": tk.StringVar(value="AcuoMed1"),
        }
        self._add_labeled_entry(self.remote_frame, "Server (IP/Name)", self.remote_vars["server"], 0)
        self._add_labeled_entry(self.remote_frame, "Port", self.remote_vars["port"], 1)
        self._add_labeled_entry(self.remote_frame, "Calling AE Title", self.remote_vars["calling_ae"], 2)
        self._add_labeled_entry(self.remote_frame, "Called AE Title", self.remote_vars["called_ae"], 3)

        # Send button
        btn_row = ttk.Frame(self.remote_frame)
        btn_row.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        self.remote_send_button = ttk.Button(btn_row, text="Send All Loaded DICOM", command=self.send_remote)
        self.remote_send_button.pack(side=tk.LEFT)

        # Message area for errors
        msg_row = ttk.Frame(self.remote_frame)
        msg_row.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)
        self.remote_frame.rowconfigure(5, weight=1)
        self.remote_frame.columnconfigure(0, weight=1)
        ttk.Label(msg_row, text="Messages / Errors:").pack(anchor=tk.W)
        self.remote_messages = tk.Text(msg_row, height=8, wrap="word")
        self.remote_messages.pack(fill=tk.BOTH, expand=True)
        self.remote_messages.configure(state=tk.DISABLED)

    def new_file(self):
        # Confirm with user before clearing everything
        if not messagebox.askyesno(APP_TITLE, "This will clear all metadata, loaded images, and loaded DICOM. Continue?"):
            return
        # Clear all controls and internal state (forms, images, DICOM lists).
        # Clear form fields (Patient, Study, Series)
        for d in (self.patient_vars, self.study_vars, self.series_vars):
            for v in d.values():
                v.set("")

        # Reset image-related state and preview
        self.image_path = None
        self.pixel_array = None
        self._tk_img = None
        self.image_label.config(text="No image loaded")
        try:
            self.preview_label.configure(image="")
        except Exception:
            pass

        # Reset DICOM-loaded structures and tree view
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
        # Basic About dialog
        messagebox.showinfo(APP_TITLE, f"{APP_TITLE}(c) 2025-2026 by Hyland\nWritten by Piotr Rozentreter\n\nSimple tool to create and edit DICOM metadata and images.")

    def on_quit(self):
        # Ask for confirmation before quitting the application
        try:
            if messagebox.askyesno(APP_TITLE, "Are you sure you want to quit? Any unsaved changes will be lost."):
                self.destroy()
        except Exception:
            # Fallback to direct quit
            try:
                self.destroy()
            except Exception:
                pass

    def _add_labeled_entry(self, parent, label, var, row):
        # Helper: create a label + entry bound to a StringVar, aligned in a grid row.
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        parent.columnconfigure(0, weight=1)
        ttk.Label(frame, text=label, width=30).pack(side=tk.LEFT)
        ttk.Entry(frame, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def load_image(self):
        # Load an image from disk and convert to grayscale pixel array for preview and DICOM.
        path = filedialog.askopenfilename(title="Select image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")])
        if not path:
            return
        if Image is None or np is None:
            if hasattr(self, 'logger'):
                self.logger.warning("Pillow/numpy not available; cannot load image")
            messagebox.showerror(APP_TITLE, "Pillow and numpy are required to load images.")
            return
        try:
            img = Image.open(path).convert("L")  # convert to 8-bit grayscale
            self.pixel_array = np.array(img)
            self.image_path = path
            self.image_label.config(text=f"Loaded: {os.path.basename(path)} | {img.size[0]}x{img.size[1]}")
            self._update_image_preview(self.pixel_array)
        except Exception as e:
            self.logger.exception("Failed to load image '%s'", path)
            messagebox.showerror(APP_TITLE, f"Failed to load image: {e}")

    def _update_image_preview(self, arr):
        # Convert the array to a displayable image and update the Tkinter label.
        if arr is None or Image is None:
            return
        try:
            # Normalize to 8-bit if needed
            if arr.ndim == 2:
                img = Image.fromarray(self._to_uint8(arr), mode="L")
            elif arr.ndim == 3 and arr.shape[2] in (3, 4):
                # Assume already uint8 RGB/RGBA
                if arr.dtype != np.uint8:
                    arr = self._to_uint8(arr)
                mode = "RGBA" if arr.shape[2] == 4 else "RGB"
                img = Image.fromarray(arr, mode=mode)
            else:
                # Unsupported shape; try squeeze to 2D
                arr2 = np.squeeze(arr)
                img = Image.fromarray(self._to_uint8(arr2), mode="L")

            # Optionally scale down to fit preview area
            try:
                max_w = max(200, self.preview_label.winfo_width())
                max_h = max(200, self.preview_label.winfo_height())
                if max_w > 0 and max_h > 0:
                    img.thumbnail((max_w, max_h))
            except Exception:
                pass

            if ImageTk is None:
                return
            self._tk_img = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=self._tk_img)
        except Exception:
            # Ignore preview errors
            self.logger.warning("Failed to update image preview", exc_info=True)

    def _to_uint8(self, arr):
        # Normalize arbitrary numeric array to uint8 [0,255] range for display.
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
        # Save the current metadata and pixel data into a DICOM file using helper function.
        if pydicom is None:
            if hasattr(self, 'logger'):
                self.logger.warning("pydicom not available; cannot save DICOM")
            messagebox.showerror(APP_TITLE, "pydicom is required to save DICOM files.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".dcm", filetypes=[("DICOM", "*.dcm"), ("All Files", "*.*")])
        if not save_path:
            return
        try:
            from .dcm import create_dicom
        except Exception:
            try:
                from dcm import create_dicom
            except Exception as e:
                if hasattr(self, 'logger'):
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
        # Load one or more DICOM files. Supports picking a DICOMDIR file to expand dataset references.
        if pydicom is None:
            if hasattr(self, 'logger'):
                self.logger.warning("pydicom not available; cannot load DICOM files")
            messagebox.showerror(APP_TITLE, "pydicom is required to load DICOM files.")
            return
        # Allow multi-select files to load many instances
        paths = filedialog.askopenfilenames(title="Select DICOM file(s)", filetypes=[("DICOM Files", "*.dcm;*.dicom;*"), ("All Files", "*.*")])
        if not paths:
            return
        try:
            try:
                from .dcm import load_dicom_grouped, is_dicomdir, load_dicomdir_grouped
            except Exception:
                from dcm import load_dicom_grouped, is_dicomdir, load_dicomdir_grouped

            grouped = {}

            def merge_grouped(target, source):
                # Merge source grouped dict (study->series->instances) into target.
                for study_uid, series_map in source.items():
                    t_series_map = target.setdefault(study_uid, {})
                    for series_uid, instances in series_map.items():
                        t_instances = t_series_map.setdefault(series_uid, [])
                        t_instances.extend(instances)

            # If single selection and it's a DICOMDIR, load via DICOMDIR
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
            self.grouped_dicom = grouped
            self.series_tree.delete(*self.series_tree.get_children())
            # Populate tree: Study -> Series -> Instances
            total_instances = 0
            first_series_id = None
            for study_uid, series_map in grouped.items():
                study_node = self.series_tree.insert("", "end", iid=f"study:{study_uid}", text=f"Study: {study_uid}")
                for series_uid, instances in series_map.items():
                    series_node = self.series_tree.insert(study_node, "end", iid=f"series:{study_uid}:{series_uid}", text=f"Series: {series_uid} ({len(instances)} images)")
                    if first_series_id is None:
                        first_series_id = f"series:{study_uid}:{series_uid}"
                    for idx, (ds, arr) in enumerate(instances):
                        inst_text = f"Instance {idx+1}: {getattr(ds, 'SOPInstanceUID', '')}"
                        self.series_tree.insert(series_node, "end", text=inst_text)
                        total_instances += 1

            self.dcm_info_label.config(text=f"Loaded {len(grouped)} studies, {sum(len(v) for v in grouped.values())} series, {total_instances} instances")
            # Auto-select first series to show preview
            if first_series_id:
                self.series_tree.selection_set(first_series_id)
                self.on_tree_select(None)
        except Exception as e:
            self.logger.exception("Failed to load DICOM selections: %s", paths)
            messagebox.showerror(APP_TITLE, f"Failed to load DICOM: {e}")

    def load_dicom_folder(self):
        # Load all DICOM files under a selected folder and group them for display.
        if pydicom is None:
            if hasattr(self, 'logger'):
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
            self.grouped_dicom = grouped
            self.series_tree.delete(*self.series_tree.get_children())
            total_instances = 0
            first_series_id = None
            for study_uid, series_map in grouped.items():
                study_node = self.series_tree.insert("", "end", iid=f"study:{study_uid}", text=f"Study: {study_uid}")
                for series_uid, instances in series_map.items():
                    series_node = self.series_tree.insert(study_node, "end", iid=f"series:{study_uid}:{series_uid}", text=f"Series: {series_uid} ({len(instances)} images)")
                    if first_series_id is None:
                        first_series_id = f"series:{study_uid}:{series_uid}"
                    for idx, (ds, arr) in enumerate(instances):
                        inst_text = f"Instance {idx+1}: {getattr(ds, 'SOPInstanceUID', '')}"
                        self.series_tree.insert(series_node, "end", text=inst_text)
                        total_instances += 1
            self.dcm_info_label.config(text=f"Loaded {len(grouped)} studies, {sum(len(v) for v in grouped.values())} series, {total_instances} instances")
            if first_series_id:
                self.series_tree.selection_set(first_series_id)
                self.on_tree_select(None)
        except Exception as e:
            self.logger.exception("Failed to load DICOM folder: %s", folder)
            messagebox.showerror(APP_TITLE, f"Failed to load DICOM folder: {e}")

    def on_tree_select(self, event):
        # Handle selection in the series tree. When a series is selected, populate forms and preview first image.
        sel = self.series_tree.selection()
        if not sel:
            return
        node_id = sel[0]
        if node_id.startswith("series:"):
            _, study_uid, series_uid = node_id.split(":", 2)
            self.selected_study_uid = study_uid
            self.selected_series_uid = series_uid
            instances = self.grouped_dicom.get(study_uid, {}).get(series_uid, [])
            if not instances:
                return
            ds, arr = instances[0]
            self.pixel_array = arr if arr is not None else self.pixel_array
            # Populate forms
            self.patient_vars["PatientName"].set(str(getattr(ds, 'PatientName', '') or ''))
            # Person name components
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
            self.patient_vars["PatientMothersBirthName"].set(str(getattr(ds, 'PatientMotherBirthName', getattr(ds, 'PatientMotherBirthName', '')) or ''))
            self.patient_vars["PatientDeathDateTime"].set(str(getattr(ds, 'PatientDeathDateTime', '') or ''))

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

            rows = getattr(ds, 'Rows', None)
            cols = getattr(ds, 'Columns', None)
            if rows and cols:
                self.image_label.config(text=f"Selected Series: {series_uid} | {cols}x{rows}")
            # Show image if pixel data
            if arr is not None:
                self._update_image_preview(arr)

    def _append_remote_message(self, text):
        try:
            self.remote_messages.configure(state=tk.NORMAL)
            self.remote_messages.insert(tk.END, text + "\n")
            self.remote_messages.see(tk.END)
            self.remote_messages.configure(state=tk.DISABLED)
            # Ensure UI refresh even during long operations
            self.remote_messages.update_idletasks()
        except Exception:
            pass

    def send_remote(self):
        # Send all loaded DICOM instances to a remote DICOM SCP using C-STORE (all-or-nothing).
        # Check dependencies first for better UX
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
        
        grouped_to_send = self.grouped_dicom
        if not grouped_to_send:
            # Build a single in-memory dataset from current form + image
            try:
                try:
                    from .dcm import create_dicom
                except Exception:
                    from dcm import create_dicom
            except Exception as ie:
                self.logger.exception("Failed to import DICOM module for in-memory send")
                messagebox.showerror(APP_TITLE, f"No DICOM loaded and cannot create one from current form: {ie}")
                return
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
                grouped_to_send = {suid: {seruid: [(ds, self.pixel_array)]}}
                # Inform user we're sending the current dataset
                self._append_remote_message("No DICOM loaded; sending current in-memory dataset")
            except Exception as ce:
                self.logger.exception("Failed to build in-memory dataset for sending")
                messagebox.showerror(APP_TITLE, f"Failed to build dataset from current form: {ce}")
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
                # Notify success on UI thread
                self.after(0, lambda: messagebox.showinfo(APP_TITLE, "All DICOM instances sent successfully"))
            except Exception as e:
                # First error aborts sending; show and log
                try:
                    self.logger.exception("Remote send failed")
                except Exception:
                    pass
                self.after(0, post_message, f"Error: {e}")
                self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Remote send failed: {e}"))
            finally:
                # Re-enable button
                try:
                    self.after(0, lambda: self.remote_send_button.configure(state=tk.NORMAL))
                except Exception:
                    pass

        t = threading.Thread(target=worker, daemon=True)
        t.start()


def main():
    # Entrypoint for the GUI application.
    app = DicomCreatorApp()
    app.mainloop()

if __name__ == "__main__":
    main()
