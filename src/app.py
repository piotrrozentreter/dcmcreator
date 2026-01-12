"""
DICOM Creator Application Entry Point
Simple entry point that launches the GUI application.
"""

try:
    from .appgui import DicomCreatorApp
except Exception:
    from appgui import DicomCreatorApp


def main():
    """Entrypoint for the GUI application."""
    app = DicomCreatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
