"""
TLS Settings Dialog

Provides a dialog for configuring TLS/SSL settings for secure DICOM transmission.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json


class TLSSettingsDialog(tk.Toplevel):
    """Dialog for configuring TLS/SSL settings."""
    
    def __init__(self, parent, logger, tls_config=None):
        """
        Initialize TLS settings dialog.
        
        Args:
            parent: Parent window
            logger: Logger instance
            tls_config: Optional dict with existing TLS configuration
        """
        super().__init__(parent)
        self.logger = logger
        self.tls_config = tls_config or {}
        self.result = None
        
        self.title("TLS/SSL Settings")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
        self._load_existing_config()
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _build_ui(self):
        """Build the dialog UI."""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(title_frame, text="TLS/SSL Configuration", 
                 font=("Arial", 12, "bold")).pack()
        ttk.Label(title_frame, text="Configure certificates and TLS settings for secure DICOM transmission",
                 font=("Arial", 9), foreground="gray").pack()
        
        # Main content frame with scrollbar
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Certificate files section
        cert_frame = ttk.LabelFrame(scrollable_frame, text="Certificate Files", padding=10)
        cert_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cert_vars = {}
        
        # Client Certificate (PEM format)
        ttk.Label(cert_frame, text="Client Certificate (PEM):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cert_vars["cert_file"] = tk.StringVar()
        cert_entry = ttk.Entry(cert_frame, textvariable=self.cert_vars["cert_file"], width=40)
        cert_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(cert_frame, text="Browse", command=lambda: self._browse_file("cert_file", "certificate")).grid(row=0, column=2, padx=5, pady=5)
        
        # Private Key (PEM format)
        ttk.Label(cert_frame, text="Private Key (PEM):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.cert_vars["key_file"] = tk.StringVar()
        key_entry = ttk.Entry(cert_frame, textvariable=self.cert_vars["key_file"], width=40)
        key_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(cert_frame, text="Browse", command=lambda: self._browse_file("key_file", "key")).grid(row=1, column=2, padx=5, pady=5)
        
        # Key Password (optional)
        ttk.Label(cert_frame, text="Key Password (optional):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.cert_vars["key_password"] = tk.StringVar()
        key_pass_entry = ttk.Entry(cert_frame, textvariable=self.cert_vars["key_password"], width=40, show="*")
        key_pass_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # CA Certificate (for server verification)
        ttk.Label(cert_frame, text="CA Certificate (PEM):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.cert_vars["ca_file"] = tk.StringVar()
        ca_entry = ttk.Entry(cert_frame, textvariable=self.cert_vars["ca_file"], width=40)
        ca_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(cert_frame, text="Browse", command=lambda: self._browse_file("ca_file", "CA certificate")).grid(row=3, column=2, padx=5, pady=5)
        
        cert_frame.columnconfigure(1, weight=1)
        
        # TLS Options section
        options_frame = ttk.LabelFrame(scrollable_frame, text="TLS Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Verify Server Certificate
        self.cert_vars["verify_server"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Verify Server Certificate", 
                       variable=self.cert_vars["verify_server"]).pack(anchor="w", pady=2)
        
        # Verify Hostname
        self.cert_vars["verify_hostname"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Verify Server Hostname", 
                       variable=self.cert_vars["verify_hostname"]).pack(anchor="w", pady=2)
        
        # Allow self-signed certificates
        self.cert_vars["allow_self_signed"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Allow Self-Signed Certificates", 
                       variable=self.cert_vars["allow_self_signed"]).pack(anchor="w", pady=2)
        
        # TLS Version
        version_frame = ttk.Frame(options_frame)
        version_frame.pack(fill=tk.X, pady=5)
        ttk.Label(version_frame, text="Minimum TLS Version:").pack(side=tk.LEFT, padx=5)
        self.cert_vars["tls_version"] = tk.StringVar(value="TLSv1.2")
        tls_combo = ttk.Combobox(version_frame, textvariable=self.cert_vars["tls_version"], 
                                 values=["TLSv1.1", "TLSv1.2", "TLSv1.3"], state="readonly", width=15)
        tls_combo.pack(side=tk.LEFT, padx=5)
        
        # Cipher Suite (optional)
        cipher_frame = ttk.Frame(options_frame)
        cipher_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cipher_frame, text="Cipher Suite (optional):").pack(side=tk.LEFT, padx=5)
        self.cert_vars["cipher_suite"] = tk.StringVar()
        cipher_entry = ttk.Entry(cipher_frame, textvariable=self.cert_vars["cipher_suite"], width=30)
        cipher_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Help section
        help_frame = ttk.LabelFrame(scrollable_frame, text="Help", padding=10)
        help_frame.pack(fill=tk.X, padx=5, pady=5)
        
        help_text = (
            "- Client Certificate: Your certificate file (PEM format)\n"
            "- Private Key: Private key for your certificate (PEM format)\n"
            "- CA Certificate: Certificate Authority file to verify server\n"
            "- Leave fields empty if TLS authentication is not required by server\n"
            "- Verify options are recommended for security but may need to be\n"
            "  disabled for testing with self-signed certificates"
        )
        help_label = ttk.Label(help_frame, text=help_text, font=("Arial", 8), foreground="gray")
        help_label.pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self._on_ok, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Load Config", command=self._load_config_file, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Config", command=self._save_config_file, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self._clear_all, width=15).pack(side=tk.LEFT, padx=5)
    
    def _browse_file(self, var_name, file_type):
        """Browse for a certificate or key file."""
        filetypes = [
            ("PEM files", "*.pem"),
            ("CRT files", "*.crt"),
            ("KEY files", "*.key"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title=f"Select {file_type} file",
            filetypes=filetypes,
            parent=self
        )
        if filename:
            self.cert_vars[var_name].set(filename)
    
    def _load_existing_config(self):
        """Load existing TLS configuration into the dialog."""
        if not self.tls_config:
            return
        
        for key, var in self.cert_vars.items():
            if key in self.tls_config:
                value = self.tls_config[key]
                if isinstance(var, tk.BooleanVar):
                    var.set(bool(value))
                else:
                    var.set(str(value) if value else "")
    
    def _load_config_file(self):
        """Load TLS configuration from a JSON file."""
        filename = filedialog.askopenfilename(
            title="Load TLS Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self
        )
        if not filename:
            return
        
        try:
            with open(filename, "r") as f:
                config = json.load(f)
            
            for key, var in self.cert_vars.items():
                if key in config:
                    value = config[key]
                    if isinstance(var, tk.BooleanVar):
                        var.set(bool(value))
                    else:
                        var.set(str(value) if value else "")
            
            messagebox.showinfo("TLS Settings", f"Configuration loaded from {filename}", parent=self)
        except Exception as e:
            self.logger.exception(f"Failed to load TLS config from {filename}")
            messagebox.showerror("Error", f"Failed to load configuration: {e}", parent=self)
    
    def _save_config_file(self):
        """Save current TLS configuration to a JSON file."""
        filename = filedialog.asksaveasfilename(
            title="Save TLS Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self
        )
        if not filename:
            return
        
        try:
            config = self._get_config()
            with open(filename, "w") as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("TLS Settings", f"Configuration saved to {filename}", parent=self)
        except Exception as e:
            self.logger.exception(f"Failed to save TLS config to {filename}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}", parent=self)
    
    def _clear_all(self):
        """Clear all configuration fields."""
        if messagebox.askyesno("Clear All", "Clear all TLS settings?", parent=self):
            for key, var in self.cert_vars.items():
                if isinstance(var, tk.BooleanVar):
                    if key == "verify_server" or key == "verify_hostname":
                        var.set(True)
                    else:
                        var.set(False)
                elif key == "tls_version":
                    var.set("TLSv1.2")
                else:
                    var.set("")
    
    def _get_config(self):
        """Get the current configuration as a dictionary."""
        config = {}
        for key, var in self.cert_vars.items():
            if isinstance(var, tk.BooleanVar):
                config[key] = var.get()
            else:
                value = var.get().strip()
                config[key] = value if value else None
        return config
    
    def _validate_config(self):
        """Validate the TLS configuration."""
        config = self._get_config()
        
        # Check if certificate and key are both provided or both empty
        cert_file = config.get("cert_file")
        key_file = config.get("key_file")
        
        if cert_file and not key_file:
            messagebox.showerror("Validation Error", 
                               "Private key is required when client certificate is provided", 
                               parent=self)
            return False
        
        if key_file and not cert_file:
            messagebox.showerror("Validation Error", 
                               "Client certificate is required when private key is provided", 
                               parent=self)
            return False
        
        # Verify files exist
        for file_key in ["cert_file", "key_file", "ca_file"]:
            file_path = config.get(file_key)
            if file_path and not os.path.exists(file_path):
                messagebox.showerror("Validation Error", 
                                   f"File not found: {file_path}", 
                                   parent=self)
                return False
        
        return True
    
    def _on_ok(self):
        """Handle OK button click."""
        if self._validate_config():
            self.result = self._get_config()
            self.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.destroy()
    
    def get_result(self):
        """Get the dialog result after it's closed."""
        return self.result
