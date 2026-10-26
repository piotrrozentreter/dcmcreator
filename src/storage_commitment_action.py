"""Remote-tab action for requesting Storage Commitment."""

import threading
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from pydicom.uid import generate_uid
except ImportError:
    generate_uid = None


class StorageCommitmentAction:
    """Add and handle the Storage Commitment action in the Remote tab."""

    def __init__(self, app, config_frame, button_frame):
        self.app = app
        self.transaction_uid = tk.StringVar(
            master=app,
            value=generate_uid() if generate_uid else "",
        )
        app.remote_vars["transaction_uid"] = self.transaction_uid
        app._add_labeled_entry(
            config_frame,
            "Storage Commitment Transaction UID",
            self.transaction_uid,
            7,
        )
        self.button = ttk.Button(
            button_frame,
            text="Request Storage Commitment for Loaded Instances",
            command=self.request,
        )
        self.button.pack(side=tk.LEFT, padx=8)

    def request(self):
        """Request commitment for loaded instances already stored by the peer."""
        try:
            from .storage_commitment import send_storage_commitment
        except Exception:
            try:
                from storage_commitment import send_storage_commitment
            except Exception as error:
                self.app.logger.exception("Failed to import Storage Commitment client")
                messagebox.showerror("DICOM Creator", f"Storage Commitment is not available: {error}")
                return

        remote_vars = self.app.remote_vars
        server = remote_vars["server"].get().strip()
        port_text = remote_vars["port"].get().strip()
        calling_ae = remote_vars["calling_ae"].get().strip() or "DCMCREATOR"
        called_ae = remote_vars["called_ae"].get().strip() or "ANY-SCP"
        transaction_uid = self.transaction_uid.get().strip()

        if not server:
            messagebox.showerror("DICOM Creator", "Server address is required")
            return
        try:
            port = int(port_text)
            if not 1 <= port <= 65535:
                raise ValueError
        except (TypeError, ValueError):
            messagebox.showerror("DICOM Creator", "Port must be an integer between 1 and 65535")
            return

        references = []
        for series_map in self.app.grouped_dicom.values():
            for instances in series_map.values():
                for dataset, _ in instances:
                    references.append((
                        str(getattr(dataset, "SOPClassUID", "")),
                        str(getattr(dataset, "SOPInstanceUID", "")),
                    ))
        if not references:
            messagebox.showerror(
                "DICOM Creator",
                "Load DICOM instances first. Storage Commitment references instances already stored by the peer; this action does not send them.",
            )
            return
        if not transaction_uid:
            messagebox.showerror("DICOM Creator", "Storage Commitment Transaction UID is required")
            return

        config = {
            "server": server,
            "port": port,
            "calling_ae": calling_ae,
            "called_ae": called_ae,
            "use_tls": bool(remote_vars["use_tls"].get()),
            "tls_config": self.app.tls_config if remote_vars["use_tls"].get() else None,
        }
        self.button.configure(state=tk.DISABLED)

        def post_message(message):
            try:
                self.app.after(0, self.app._append_remote_message, message)
            except Exception:
                pass

        def worker():
            try:
                status_code = send_storage_commitment(
                    references=references,
                    transaction_uid=transaction_uid,
                    config=config,
                    logger=self.app.logger,
                    on_message=post_message,
                )
                self.app.after(
                    0,
                    lambda: messagebox.showinfo(
                        "DICOM Creator",
                        f"Storage Commitment N-ACTION response: 0x{status_code:04X}.\n\n"
                        "The peer accepted the request; this is not the final commitment result. "
                        "This app does not receive the later N-EVENT-REPORT.",
                    ),
                )
                if generate_uid:
                    self.app.after(0, lambda: self.transaction_uid.set(generate_uid()))
            except Exception as error:
                error_message = str(error)
                try:
                    self.app.logger.exception("Storage Commitment request failed")
                except Exception:
                    pass
                self.app.after(
                    0,
                    lambda: messagebox.showerror(
                        "DICOM Creator",
                        f"Storage Commitment request failed: {error_message}",
                    ),
                )
            finally:
                try:
                    self.app.after(0, lambda: self.button.configure(state=tk.NORMAL))
                except Exception:
                    pass

        threading.Thread(target=worker, daemon=True).start()