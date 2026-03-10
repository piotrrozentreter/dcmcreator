# GitHub Copilot Instructions - DICOM Creator Project

## Project Overview
**DICOM Creator v0.9.0** - Professional DICOM file creation, editing, and transmission tool with comprehensive testing, validation, and performance analysis capabilities.

**Tech Stack:** Python 3.9+, Tkinter GUI, pydicom, pynetdicom, Pillow, numpy, requests  
**Architecture:** Modular, LazyImport-based, event-driven GUI  
**Platform:** Cross-platform (Windows, macOS, Linux)

---

## 🏗️ Architectural Principles

### 1. Modular Design (CRITICAL)
**ALL new features MUST be implemented as separate modules:**
- ✅ **One class per file** (preferred)
- ✅ **Small, focused modules** (<500 lines ideal, <1000 max)
- ✅ **Clear separation of concerns**
- ❌ **Never add to existing 1000+ line files**
- ❌ **No monolithic classes**

**Examples of good modularity:**
```python
# Good: Separate files
src/hl7_handler.py       # HL7 parsing logic (~130 lines)
src/hl7_tab.py           # HL7 GUI tab (~190 lines)
src/presets.py           # Server presets logic
src/tls_dialog.py        # TLS configuration UI

# Bad: Everything in one file
src/appgui.py            # 2500+ lines (legacy, do NOT add to it)
```

### 2. Lazy Import Pattern
Use `LazyImport` for optional features to avoid circular dependencies:
```python
from import_helper import LazyImport

# Lazy load optional modules
HL7Handler = LazyImport(".hl7_handler", "hl7_handler")
ServerPresets = LazyImport(".presets", "presets")

# Check availability before use
if HL7Handler is None:
    show_error("HL7 module not available")
    return
```

**LazyImport Rules:**
- Prioritize the main/public class during class extraction
- For modules with multiple classes, ensure the main class is recognized
- Check `import_helper.py` for implementation details

### 3. UI Tab Structure
New UI features should follow the tab pattern:
```python
# Logic handler (no GUI)
class FeatureHandler:
    def __init__(self, logger=None):
        self.logger = logger
    
    def do_work(self):
        # Pure logic here
        pass

# UI tab (separate file)
class FeatureTab:
    def __init__(self, parent_frame, app, logger):
        self.frame = parent_frame
        self.app = app
        self.handler = FeatureHandler(logger=logger)
        self._build_ui()
    
    def _build_ui(self):
        # Tkinter UI here
        pass
```

---

## 📦 Dependency Management

### Prefer External Packages
**ALWAYS prefer well-maintained external packages over custom implementations:**

✅ **Use these packages:**
- `requests` → HTTP/REST API calls (FHIR)
- `pydicom` → DICOM file operations
- `pynetdicom` → DICOM networking (C-STORE, C-FIND, C-GET)
- `Pillow` → Image processing
- `numpy` → Array operations
- `cryptography` → TLS/SSL (if needed beyond stdlib)

❌ **Avoid reinventing:**
- HTTP clients (use `requests`)
- Image codecs (use `Pillow`)
- Parsing libraries (use stdlib or existing packages)
- Compression (use stdlib `gzip`, `zlib`, etc.)

**When adding dependencies:**
1. Check if package is actively maintained (GitHub stars, last update)
2. Verify Python 3.9+ compatibility
3. Add to `requirements.txt` immediately
4. Document in code why this package was chosen

---

## 🌐 Unicode & Character Encoding

### NO Double Question Marks (✓✓)
**CRITICAL: Avoid ✓✓ characters in documentation and code:**

✅ **Correct Unicode characters:**
```markdown
✓ Success (U+2713 CHECK MARK)
✗ Error (U+2717 BALLOT X)
→ Arrow (U+2192 RIGHTWARDS ARROW)
• Bullet (U+2022 BULLET)
─ Line (U+2500 BOX DRAWINGS LIGHT HORIZONTAL)
```

❌ **Incorrect (causes ✓✓):**
```python
# Bad: Using emoji or wrong encoding
print("✓✓ Success")  # Will render as ✓✓
```

✅ **Safe alternatives:**
```python
# Good: Use ASCII or proper Unicode
print("✓ Success")   # U+2713
print("[OK] Success")  # ASCII safe
print("SUCCESS")       # Uppercase ASCII
```

**File encoding:**
- All Python files: UTF-8 with BOM (Windows) or UTF-8 no BOM (Unix)
- Markdown files: UTF-8 no BOM
- Use `# -*- coding: utf-8 -*-` if needed for Python 2 compatibility

---

## 📝 GitHub Project Standards

### Repository Structure
```
dcmcreator/
├── .github/
│   ├── copilot-instructions.md    # This file
│   └── workflows/                 # CI/CD (future)
├── src/                           # All Python source code
│   ├── appgui.py                 # Main GUI (legacy, minimize changes)
│   ├── app_logic.py              # Business logic coordinator
│   ├── hl7_handler.py            # HL7 logic (NEW)
│   ├── hl7_tab.py                # HL7 UI (NEW)
│   └── ...                       # Other modules
├── doc/                          # All documentation
│   ├── INDEX.md                  # Documentation hub
│   ├── CHANGELOG_v{X}.md         # Version changelogs
│   └── ...                       # Feature guides
├── examples/                     # Usage examples
├── test/                         # Test suite
├── README.md                     # Project overview
├── requirements.txt              # Python dependencies
├── build-requirements.txt        # Build tool dependencies
└── LICENSE                       # MIT License
```

### Commit Message Standards
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add HL7 v2.x parsing and FHIR R4 support
fix: resolve LazyImport class detection issue
docs: update ORGANIZATION.md for v0.9.0
refactor: split appgui.py into separate tab modules
test: add unit tests for HL7Handler
chore: update requirements.txt with requests
```

**Prefixes:**
- `feat:` → New feature
- `fix:` → Bug fix
- `docs:` → Documentation only
- `style:` → Code style (formatting, no logic change)
- `refactor:` → Code restructuring (no feature change)
- `test:` → Test changes
- `chore:` → Build, dependencies, tooling

### Branch Strategy
```
main          → Production-ready code
develop       → Integration branch
feature/NAME  → New features
fix/NAME      → Bug fixes
docs/NAME     → Documentation updates
```

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Checklist
- [ ] Code follows project style
- [ ] Module is < 500 lines
- [ ] Dependencies added to requirements.txt
- [ ] Documentation updated
- [ ] No ✓✓ characters introduced
- [ ] Tested on Windows/Linux/macOS (if applicable)

## Testing
Describe testing performed
```

---

## 🎨 Code Style

### Python Style (PEP 8 + Project Extensions)
```python
# Class names: PascalCase
class HL7Handler:
    pass

# Function/method names: snake_case
def parse_adt(self, message):
    pass

# Constants: UPPER_SNAKE_CASE
MLLP_SB = b'\x0b'

# Private methods: _leading_underscore
def _internal_helper(self):
    pass

# Module-level "private" vars: _leading_underscore
_SAMPLE_ADT = "MSH|..."
```

**Docstrings:**
```python
def parse_adt(self, message):
    """Parse HL7 ADT message → patient demographics dict.
    
    Args:
        message: HL7 v2.x message string with \r or \n separators
    
    Returns:
        dict: Patient data {PatientID, PatientName, ...} or {} if no PID
    
    Example:
        >>> handler.parse_adt(hl7_msg)
        {'PatientID': '123456', 'PatientName': 'Doe^John'}
    """
```

**Import Order:**
```python
# 1. Standard library
import os
import socket
from datetime import datetime

# 2. Third-party packages
import pydicom
import numpy as np

# 3. Local application imports (relative)
try:
    from .hl7_handler import HL7Handler
except ImportError:
    from hl7_handler import HL7Handler
```

### GUI Code Style
```python
# Use ttk widgets (themed)
from tkinter import ttk
ttk.Button(frame, text="Click")  # Good
tk.Button(frame, text="Click")   # Avoid

# Grid layout for forms
ttk.Label(frame, text="Host:").grid(row=0, column=0, sticky="w")
ttk.Entry(frame, textvariable=var).grid(row=0, column=1, sticky="ew")

# Pack for simple layouts
btn_frame.pack(fill=tk.X, padx=10, pady=5)

# Threading for I/O operations
def long_operation():
    result = blocking_call()
    self.frame.after(0, lambda: update_ui(result))

threading.Thread(target=long_operation, daemon=True).start()
```

---

## 🧪 Testing Guidelines

### Test File Organization
```python
# test/test_hl7_handler.py
import unittest
from src.hl7_handler import HL7Handler

class TestHL7Handler(unittest.TestCase):
    def setUp(self):
        self.handler = HL7Handler()
    
    def test_parse_adt_valid(self):
        msg = "MSH|...\nPID|1||123456||Doe^John||19800115|M"
        result = self.handler.parse_adt(msg)
        self.assertEqual(result['PatientID'], '123456')
        self.assertEqual(result['PatientName'], 'Doe^John')
    
    def test_parse_adt_no_pid(self):
        msg = "MSH|..."
        result = self.handler.parse_adt(msg)
        self.assertEqual(result, {})
```

**Test naming:**
- `test_FUNCTION_SCENARIO`
- `test_parse_adt_valid`
- `test_fhir_get_patient_not_found`
- `test_send_mllp_connection_refused`

---

## 📚 Documentation Standards

### Markdown Structure
```markdown
# Feature Name

Brief one-line description.

## Overview
What is this feature and why does it exist?

## Quick Start
Minimal example to get started:
```python
# Code example
```

## API Reference
### ClassName
#### method_name(args)
Description, parameters, returns, examples.

## Examples
Full working examples with explanations.

## Troubleshooting
Common issues and solutions.

## See Also
Links to related documentation.
```

### Code Comments
```python
# Good: Explains WHY, not WHAT
# Parse ADT to populate patient form fields (requirement #42)
parsed = self.handler.parse_adt(msg)

# Bad: States the obvious
# Call parse_adt function
parsed = self.handler.parse_adt(msg)

# Section separators (80 chars)
# ── HL7 v2.x ─────────────────────────────────────────────────────────────

# Inline for complex logic
result = data.get('name', [{}])[0].get('family', '')  # FHIR nested structure
```

---

## 🔧 Development Workflow

### Adding a New Feature

1. **Plan the module structure:**
   ```
   src/feature_logic.py     # Business logic (~150 lines)
   src/feature_tab.py       # GUI tab (~200 lines)
   doc/FEATURE_GUIDE.md     # Documentation
   test/test_feature.py     # Unit tests
   ```

2. **Create stub files:**
   ```python
   # feature_logic.py
   class FeatureHandler:
       def __init__(self, logger=None):
           self.logger = logger
       
       def do_work(self):
           raise NotImplementedError("TODO")
   ```

3. **Wire into appgui.py:**
   ```python
   # Import (top of file)
   FeatureTab = LazyImport(".feature_tab", "feature_tab")
   
   # Add tab visibility (in __init__)
   "Feature": tk.BooleanVar(value=True),
   
   # Create frame and wire up
   self.feature_frame = ttk.Frame(container)
   self.tab_frames["Feature"] = (self.feature_frame, "Feature")
   container.add(self.feature_frame, text="Feature")
   
   # Build UI
   def _build_feature_tab(self):
       if FeatureTab is None:
           ttk.Label(self.feature_frame, text="Feature not available").pack()
           return
       self._feature_tab = FeatureTab(self.feature_frame, self, self.logger)
   ```

4. **Add dependencies:**
   ```bash
   pip install new-package
   echo "new-package>=1.0.0" >> requirements.txt
   ```

5. **Document:**
   - Update `doc/INDEX.md`
   - Create `doc/FEATURE_GUIDE.md`
   - Add changelog entry `doc/CHANGELOG_v{VERSION}.md`

6. **Test:**
   ```bash
   python -m pytest test/test_feature.py
   python src/app.py  # Manual GUI test
   ```

### Code Review Checklist
- [ ] Module is < 500 lines (or < 1000 with good reason)
- [ ] No new code added to `appgui.py` body (only wiring)
- [ ] External packages used where appropriate
- [ ] No ✓✓ or encoding issues
- [ ] Dependencies in `requirements.txt`
- [ ] Docstrings on public methods
- [ ] Unit tests for logic classes
- [ ] Documentation updated
- [ ] Follows PEP 8
- [ ] Git commit message follows conventions

---

## 🚨 Anti-Patterns to Avoid

### ❌ DON'T: Add features to appgui.py
```python
# BAD: Adding 200 lines of HL7 UI code to appgui.py
class DicomCreatorApp(tk.Tk):
    def _build_hl7_panel(self):
        # 200 lines of code here...
```

### ✅ DO: Create separate module
```python
# GOOD: Separate module
# src/hl7_tab.py
class HL7Tab:
    def _build_ui(self):
        # 200 lines here (in separate file)

# appgui.py (minimal wiring)
def _build_hl7_tab(self):
    self._hl7_tab = HL7Tab(self.hl7_frame, self, self.logger)
```

---

### ❌ DON'T: Reinvent HTTP client
```python
# BAD: Custom HTTP implementation
def http_get(url):
    sock = socket.socket()
    # 100 lines of HTTP protocol...
```

### ✅ DO: Use requests
```python
# GOOD: Use requests library
import requests
resp = requests.get(url, timeout=10)
```

---

### ❌ DON'T: Use ✓✓ characters
```python
# BAD: Wrong Unicode
"✓✓ Success"  # Renders as double question marks
```

### ✅ DO: Use proper Unicode
```python
# GOOD: Proper Unicode
"✓ Success"   # U+2713 CHECK MARK
"[OK] Success"  # ASCII safe alternative
```

---

## 🔍 Quick Reference

### Key Files
- `src/appgui.py` - Main GUI (minimize changes, wire new tabs here)
- `src/import_helper.py` - LazyImport implementation
- `src/app_logic.py` - Business logic coordinator
- `doc/INDEX.md` - Documentation navigation hub
- `requirements.txt` - Python dependencies

### Common Tasks
| Task | Command |
|------|---------|
| Install deps | `pip install -r requirements.txt` |
| Run app | `python src/app.py` |
| Run tests | `python -m pytest test/` |
| Build EXE | `python build.py` |
| Check style | `pylint src/*.py` |

### Contact & Resources
- GitHub: https://github.com/piotrrozentreter/dcmcreator
- License: MIT
- Python Version: 3.9+
- DICOM Standard: https://www.dicomstandard.org/

---

**Last Updated:** 2025-02-25  
**Document Version:** 2.0  
**Project Version:** 0.9.0