"""
DICOM Validation Dialog
Displays validation results in a GUI dialog
"""

import tkinter as tk
from tkinter import scrolledtext


class ValidationDialog:
    """Helper class to show validation dialogs in GUI."""
    
    @staticmethod
    def show_validation_report(parent, validation_result, validator, action="save"):
        """
        Show validation report dialog and ask for confirmation.
        
        Args:
            parent: Parent tkinter window
            validation_result: Result from VRValidator.validate_form_fields()
            validator: VRValidator instance
            action: Action being performed ("save", "send", "load", "validate")
            
        Returns:
            bool: True if user wants to continue, False otherwise
        """
        if validation_result['error_count'] == 0 and validation_result['warning_count'] == 0:
            return True
        
        # Create dialog
        dialog = tk.Toplevel(parent)
        dialog.title(f"Validation Report - {action.capitalize()}")
        dialog.geometry("700x500")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Title
        title_frame = tk.Frame(dialog, bg='#f0f0f0')
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if validation_result['error_count'] > 0:
            icon = "?"
            msg = f"Found {validation_result['error_count']} error(s)"
            color = "#d32f2f"
        else:
            icon = "?"
            msg = f"Found {validation_result['warning_count']} warning(s)"
            color = "#f57c00"
        
        tk.Label(
            title_frame,
            text=f"{icon} {msg}",
            font=("Arial", 12, "bold"),
            fg=color,
            bg='#f0f0f0'
        ).pack()
        
        # Report text
        report_frame = tk.Frame(dialog)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        report_text = scrolledtext.ScrolledText(
            report_frame,
            wrap=tk.WORD,
            font=("Courier New", 9),
            height=20
        )
        report_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert report
        report = validator.format_validation_report(validation_result)
        report_text.insert(1.0, report)
        report_text.configure(state=tk.DISABLED)
        
        # Button frame
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        result = {'continue': False}
        
        def on_continue():
            result['continue'] = True
            dialog.destroy()
        
        def on_cancel():
            result['continue'] = False
            dialog.destroy()
        
        # Special handling for "validate" action - just viewing, no action needed
        if action == "validate":
            tk.Button(
                btn_frame,
                text="Close",
                command=on_cancel,
                font=("Arial", 10),
                padx=20
            ).pack(side=tk.LEFT, padx=5)
        elif validation_result['error_count'] > 0:
            # Errors present - show warning
            msg_label = tk.Label(
                btn_frame,
                text=f"? Errors detected! {action.capitalize()}ing may result in invalid DICOM file.",
                fg="#d32f2f",
                font=("Arial", 9, "bold")
            )
            msg_label.pack(pady=5)
            
            tk.Button(
                btn_frame,
                text=f"Continue {action.capitalize()} Anyway",
                command=on_continue,
                bg="#f57c00",
                fg="white",
                font=("Arial", 10, "bold"),
                padx=20
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                btn_frame,
                text="Cancel",
                command=on_cancel,
                font=("Arial", 10),
                padx=20
            ).pack(side=tk.LEFT, padx=5)
        else:
            # Only warnings - less severe
            tk.Button(
                btn_frame,
                text=f"Continue {action.capitalize()}",
                command=on_continue,
                bg="#4caf50",
                fg="white",
                font=("Arial", 10, "bold"),
                padx=20
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                btn_frame,
                text="Cancel",
                command=on_cancel,
                font=("Arial", 10),
                padx=20
            ).pack(side=tk.LEFT, padx=5)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog
        dialog.wait_window()
        
        return result['continue']
