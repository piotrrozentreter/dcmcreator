"""Tkinter controls for the internal DICOM Storage SCP."""

from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from .dicom_receiver import DicomReceiver
except ImportError:
    from dicom_receiver import DicomReceiver


class DicomReceiverTab:
    """Configure a receiver and display bounded, main-thread-only updates."""

    def __init__(self, parent_frame, app, logger):
        self.frame = parent_frame
        self.app = app
        self.logger = logger
        self.receiver = DicomReceiver()
        self._closed = False
        self._busy = False
        self._worker = None
        self._results = queue.Queue()
        self._settings = []
        self._variables = {}
        self._build_ui()
        self.frame.bind("<Destroy>", self._destroyed, add="+")
        self._timer = self.frame.after(150, self._poll)

    def _entry(self, parent, row, label, name, default="", browse=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=3)
        variable = tk.StringVar(master=self.frame, value=default)
        self._variables[name] = variable
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        self._settings.append(entry)
        if browse:
            button = ttk.Button(parent, text="Browse...", command=lambda: self._browse(name, browse))
            button.grid(row=row, column=2, padx=5, pady=3)
            self._settings.append(button)

    def _build_ui(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(4, weight=1)
        notebook = ttk.Notebook(self.frame)
        notebook.grid(row=0, column=0, sticky="ew", padx=8, pady=5)
        connection = ttk.Frame(notebook, padding=4)
        security = ttk.Frame(notebook, padding=4)
        notebook.add(connection, text="Listener")
        notebook.add(security, text="TLS")
        connection.columnconfigure(1, weight=1)
        security.columnconfigure(1, weight=1)
        self._entry(connection, 0, "Bind IPv4 address:", "host", "127.0.0.1")
        self._entry(connection, 1, "Port:", "port", "11112")
        self._entry(connection, 2, "Called AE title:", "ae_title", "DCMCREATOR_SCP")
        self._entry(connection, 3, "Allowed calling AEs (comma-separated):", "callers")
        self._entry(connection, 4, "Allowed source IPv4s (comma-separated):", "ips")
        self.prefer_rle = tk.BooleanVar(master=self.frame, value=False)
        preference = ttk.Checkbutton(connection, text="Prefer RLE Lossless",
                         variable=self.prefer_rle)
        preference.grid(row=5, column=0, columnspan=3, sticky="w", padx=5, pady=3)
        self._settings.append(preference)
        self.use_tls = tk.BooleanVar(master=self.frame, value=False)
        toggle = ttk.Checkbutton(security, text="Enable TLS", variable=self.use_tls)
        toggle.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=3)
        self._settings.append(toggle)
        self._entry(security, 1, "Server certificate (PEM):", "cert", browse="file")
        self._entry(security, 2, "Private key (unencrypted PEM):", "key", browse="file")
        self._entry(security, 3, "Client CA (requires client certificate):", "ca", browse="file")

        output = ttk.Frame(self.frame)
        output.columnconfigure(1, weight=1)
        output.grid(row=1, column=0, sticky="ew", padx=8)
        self._entry(output, 0, "Output directory:", "output",
                    str(Path.cwd() / "received_dicoms"), browse="directory")

        toolbar = ttk.Frame(self.frame)
        toolbar.grid(row=2, column=0, sticky="ew", padx=8, pady=5)
        self.start_button = ttk.Button(toolbar, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=3)
        self.stop_button = ttk.Button(toolbar, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="Clear Log", command=self._clear).pack(side=tk.LEFT, padx=3)
        self.status = tk.StringVar(master=self.frame, value="Stopped")
        ttk.Label(toolbar, textvariable=self.status).pack(side=tk.LEFT, padx=10)
        self.summary = tk.StringVar(master=self.frame)
        ttk.Label(self.frame, textvariable=self.summary).grid(
            row=3, column=0, sticky="w", padx=12, pady=3)

        log = ttk.Frame(self.frame)
        log.grid(row=4, column=0, sticky="nsew", padx=8, pady=5)
        log.rowconfigure(0, weight=1)
        log.columnconfigure(0, weight=1)
        columns = ("time", "kind", "peer", "calling_ae", "status", "uid",
                   "transfer_syntax", "path", "detail")
        self.tree = ttk.Treeview(log, columns=columns, show="headings", height=7)
        labels = ("Time", "Event", "Source IP", "Calling AE", "Status", "SOP Instance UID",
                  "Transfer Syntax UID", "Saved File", "Detail")
        for column, label in zip(columns, labels):
            self.tree.heading(column, text=label)
            self.tree.column(column, width=110 if column not in ("uid", "path") else 260,
                             minwidth=70, stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(log, orient=tk.VERTICAL, command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(log, orient=tk.HORIZONTAL, command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self._update_summary()

    def _browse(self, name, mode):
        if mode == "directory":
            selected = filedialog.askdirectory(parent=self.frame)
        else:
            selected = filedialog.askopenfilename(parent=self.frame,
                                                  filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if selected:
            self._variables[name].set(selected)

    def _configuration(self):
        values = {name: variable.get().strip() for name, variable in self._variables.items()}
        port = int(values["port"])
        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        settings = dict(output_dir=values["output"], host=values["host"], port=port,
                        ae_title=values["ae_title"],
                        prefer_rle=self.prefer_rle.get(),
                        allowed_calling_aes=[item.strip() for item in values["callers"].split(",") if item.strip()],
                        allowed_ips=[item.strip() for item in values["ips"].split(",") if item.strip()])
        if self.use_tls.get():
            if not values["cert"] or not values["key"]:
                raise ValueError("TLS requires both a certificate and private key")
            settings.update(tls_cert=values["cert"], tls_key=values["key"],
                            tls_ca=values["ca"] or None)
        return settings

    def start(self):
        """Start the listener without doing network work on the Tk thread."""
        if self._busy or self.receiver.running or self._closed:
            return
        try:
            settings = self._configuration()
        except ValueError as error:
            messagebox.showerror("DICOM Receiver", str(error), parent=self.frame)
            return
        self._launch(lambda: self.receiver.start(**settings), "Starting...")

    def stop(self):
        """Stop the listener and active associations in a worker thread."""
        if not self._busy and not self._closed:
            self._launch(self.receiver.stop, "Stopping...")

    def _launch(self, operation, status):
        self._busy = True
        self.status.set(status)
        self._controls()

        def worker():
            try:
                operation()
                self._results.put(None)
            except Exception as error:
                self._results.put(str(error))

        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()

    def _controls(self):
        locked = self._busy or self.receiver.running
        for widget in self._settings:
            widget.configure(state=tk.DISABLED if locked else tk.NORMAL)
        self.start_button.configure(state=tk.DISABLED if locked else tk.NORMAL)
        self.stop_button.configure(state=tk.NORMAL if self.receiver.running and not self._busy else tk.DISABLED)

    def _refresh(self):
        while True:
            try:
                result = self._results.get_nowait()
            except queue.Empty:
                break
            self._busy = False
            address = self.receiver.address
            self.status.set(f"Listening on {address[0]}:{address[1]}" if address else "Stopped")
            self._controls()
            if result:
                self.status.set("Error" if not self.receiver.running else "Stop failed")
                messagebox.showerror("DICOM Receiver", result, parent=self.frame)
        columns = self.tree["columns"]
        for _ in range(200):
            try:
                event = self.receiver.events.get_nowait()
            except queue.Empty:
                break
            self.tree.insert("", tk.END, values=[event.get(column, "") for column in columns])
        children = self.tree.get_children()
        if len(children) > 500:
            self.tree.delete(*children[:-500])
        self._update_summary()

    def _update_summary(self):
        stats = self.receiver.stats
        self.summary.set(
            f"Received: {stats['received']}   Failed: {stats['failed']}   "
            f"MiB: {stats['bytes'] / (1024 * 1024):.2f}   "
            f"Associations: {stats['associations']}   Log events dropped: {stats['dropped_events']}")

    def _poll(self):
        if not self._closed:
            self._refresh()
            self._timer = self.frame.after(150, self._poll)

    def _clear(self):
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)

    def _destroyed(self, event):
        if event.widget is self.frame:
            self.close()

    def close(self):
        """Stop network activity before destroying the application."""
        if self._closed:
            return
        self._closed = True
        self.frame.after_cancel(self._timer)
        if self._worker:
            self._worker.join()
        self.receiver.stop()