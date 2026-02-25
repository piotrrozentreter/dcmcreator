"""HL7 v2.x / FHIR R4 integration tab for DICOM Creator."""
import tkinter as tk
from tkinter import ttk, messagebox
import threading

try:
    from .hl7_handler import HL7Handler
except ImportError:
    from hl7_handler import HL7Handler

_SAMPLE_ADT = (
    "MSH|^~\\&|SENDING|FACILITY|RECEIVING|FACILITY|20240101120000||ADT^A01|MSG001|P|2.5\n"
    "PID|1||123456^^^MRN||Doe^John^A||19800115|M|||123 Main St^^Springfield^IL^62701\n"
)


class HL7Tab:
    """HL7 v2.x / FHIR R4 tab: parse messages and populate DICOM form fields."""

    def __init__(self, parent_frame, app, logger):
        self.frame = parent_frame
        self.app = app
        self.logger = logger
        self.handler = HL7Handler(logger=logger)
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        nb = ttk.Notebook(self.frame)
        nb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        hl7_frame = ttk.Frame(nb)
        fhir_frame = ttk.Frame(nb)
        nb.add(hl7_frame, text="HL7 v2.x")
        nb.add(fhir_frame, text="FHIR R4")
        self._build_hl7_panel(hl7_frame)
        self._build_fhir_panel(fhir_frame)

    def _build_hl7_panel(self, parent):
        msg_frame = ttk.LabelFrame(parent, text="HL7 Message", padding=5)
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        msg_frame.rowconfigure(0, weight=1)
        msg_frame.columnconfigure(0, weight=1)

        self.hl7_text = tk.Text(msg_frame, height=8, wrap="none", font=("Courier", 9))
        sb_v = ttk.Scrollbar(msg_frame, orient="vertical", command=self.hl7_text.yview)
        sb_h = ttk.Scrollbar(msg_frame, orient="horizontal", command=self.hl7_text.xview)
        self.hl7_text.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        self.hl7_text.grid(row=0, column=0, sticky="nsew")
        sb_v.grid(row=0, column=1, sticky="ns")
        sb_h.grid(row=1, column=0, sticky="ew")
        self.hl7_text.insert("1.0", _SAMPLE_ADT)

        parse_frame = ttk.Frame(parent)
        parse_frame.pack(fill=tk.X, padx=10, pady=4)
        ttk.Button(parse_frame, text="Parse ADT → Patient", command=self._parse_adt).pack(side=tk.LEFT, padx=2)
        ttk.Button(parse_frame, text="Parse ORM → Study", command=self._parse_orm).pack(side=tk.LEFT, padx=2)
        ttk.Button(parse_frame, text="Build ORU from Form", command=self._build_oru).pack(side=tk.LEFT, padx=2)
        ttk.Button(parse_frame, text="Clear", command=lambda: self.hl7_text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=2)

        send_frame = ttk.LabelFrame(parent, text="Send via MLLP", padding=5)
        send_frame.pack(fill=tk.X, padx=10, pady=5)
        send_frame.columnconfigure(1, weight=1)

        ttk.Label(send_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.mllp_host = tk.StringVar(value="127.0.0.1")
        ttk.Entry(send_frame, textvariable=self.mllp_host).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(send_frame, text="Port:").grid(row=0, column=2, sticky="w", padx=5)
        self.mllp_port = tk.StringVar(value="2575")
        ttk.Entry(send_frame, textvariable=self.mllp_port, width=8).grid(row=0, column=3, sticky="w", padx=5)
        ttk.Button(send_frame, text="Send via MLLP", command=self._send_mllp).grid(row=0, column=4, padx=5)

        self.hl7_status = ttk.Label(parent, text="", foreground="blue")
        self.hl7_status.pack(fill=tk.X, padx=10, pady=2)

    def _build_fhir_panel(self, parent):
        conn_frame = ttk.LabelFrame(parent, text="FHIR R4 Server", padding=5)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        conn_frame.columnconfigure(1, weight=1)

        ttk.Label(conn_frame, text="Base URL:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.fhir_url = tk.StringVar(value="http://hapi.fhir.org/baseR4")
        ttk.Entry(conn_frame, textvariable=self.fhir_url).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(conn_frame, text="Patient ID:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.fhir_patient_id = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.fhir_patient_id).grid(row=1, column=1, sticky="ew", padx=5)

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="GET Patient → Populate Form", command=self._fhir_get).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="POST Current Patient → FHIR", command=self._fhir_post).pack(side=tk.LEFT, padx=2)

        self.fhir_status = ttk.Label(parent, text="", foreground="blue")
        self.fhir_status.pack(fill=tk.X, padx=10, pady=2)

        resp_frame = ttk.LabelFrame(parent, text="Response", padding=5)
        resp_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.fhir_response = tk.Text(resp_frame, height=10, wrap="word", state=tk.DISABLED, font=("Courier", 9))
        sb = ttk.Scrollbar(resp_frame, orient="vertical", command=self.fhir_response.yview)
        self.fhir_response.configure(yscrollcommand=sb.set)
        self.fhir_response.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    # ── HL7 actions ───────────────────────────────────────────────────────────

    def _parse_adt(self):
        msg = self.hl7_text.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showerror("HL7", "Paste an HL7 message first")
            return
        parsed = self.handler.parse_adt(msg)
        if not parsed:
            messagebox.showerror("HL7", "No PID segment found in the message")
            return
        self._apply_patient(parsed)
        self.hl7_status.config(text=f"Patient populated: {parsed.get('PatientName', '')}")

    def _parse_orm(self):
        msg = self.hl7_text.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showerror("HL7", "Paste an HL7 message first")
            return
        parsed = self.handler.parse_orm(msg)
        if not parsed:
            messagebox.showerror("HL7", "No OBR segment found in the message")
            return
        self._apply_study(parsed)
        self.hl7_status.config(text="Study fields populated from ORM")

    def _build_oru(self):
        patient = {k: v.get() for k, v in self.app.patient_vars.items()}
        study = {k: v.get() for k, v in self.app.study_vars.items()}
        oru = self.handler.build_oru(patient, study)
        self.hl7_text.delete("1.0", tk.END)
        self.hl7_text.insert("1.0", oru.replace('\r', '\n'))
        self.hl7_status.config(text="ORU^R01 message built from current form data")

    def _send_mllp(self):
        msg = self.hl7_text.get("1.0", tk.END).strip()
        host = self.mllp_host.get().strip()
        try:
            port = int(self.mllp_port.get().strip())
        except ValueError:
            messagebox.showerror("HL7", "Port must be numeric")
            return
        if not msg or not host:
            messagebox.showerror("HL7", "Host and HL7 message are required")
            return
        self.hl7_status.config(text=f"Connecting to {host}:{port}...")

        def worker():
            success, result = self.handler.send_mllp(host, port, msg.replace('\n', '\r'))
            def update():
                if success:
                    self.hl7_status.config(text="Message sent - ACK received")
                    messagebox.showinfo("HL7 MLLP", f"Sent successfully.\n\nACK:\n{result}")
                else:
                    self.hl7_status.config(text=f"Send failed: {result}")
                    messagebox.showerror("HL7 MLLP", f"MLLP send failed:\n{result}")
            self.frame.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    # ── FHIR actions ──────────────────────────────────────────────────────────

    def _fhir_get(self):
        base_url = self.fhir_url.get().strip()
        patient_id = self.fhir_patient_id.get().strip()
        if not base_url or not patient_id:
            messagebox.showerror("FHIR", "Base URL and Patient ID are required")
            return
        self.fhir_status.config(text=f"Fetching Patient/{patient_id}...")

        def worker():
            success, result = self.handler.fhir_get_patient(base_url, patient_id)
            def update():
                if success:
                    self._apply_patient(result)
                    self._set_response(str(result))
                    self.fhir_status.config(text=f"Loaded: {result.get('PatientName', patient_id)}")
                else:
                    self.fhir_status.config(text="GET failed")
                    self._set_response(result)
                    messagebox.showerror("FHIR", f"GET Patient failed:\n{result}")
            self.frame.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    def _fhir_post(self):
        base_url = self.fhir_url.get().strip()
        if not base_url:
            messagebox.showerror("FHIR", "Base URL is required")
            return
        patient = {k: v.get() for k, v in self.app.patient_vars.items()}
        self.fhir_status.config(text="Posting patient to FHIR server...")

        def worker():
            success, result = self.handler.fhir_post_patient(base_url, patient)
            def update():
                if success:
                    self.fhir_status.config(text=f"Posted - Server ID: {result}")
                    self._set_response(f"Patient created. Server assigned ID: {result}")
                    messagebox.showinfo("FHIR", f"Patient posted successfully.\nServer ID: {result}")
                else:
                    self.fhir_status.config(text="POST failed")
                    self._set_response(result)
                    messagebox.showerror("FHIR", f"POST Patient failed:\n{result}")
            self.frame.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _apply_patient(self, data):
        for key, val in data.items():
            if key in self.app.patient_vars and val:
                self.app.patient_vars[key].set(val)

    def _apply_study(self, data):
        study_keys = {'AccessionNumber', 'StudyDescription', 'StudyDate'}
        series_keys = {'Modality', 'BodyPartExamined'}
        for key, val in data.items():
            if val:
                if key in study_keys and key in self.app.study_vars:
                    self.app.study_vars[key].set(val)
                elif key in series_keys and key in self.app.series_vars:
                    self.app.series_vars[key].set(val)

    def _set_response(self, text):
        self.fhir_response.configure(state=tk.NORMAL)
        self.fhir_response.delete("1.0", tk.END)
        self.fhir_response.insert("1.0", text)
        self.fhir_response.configure(state=tk.DISABLED)
