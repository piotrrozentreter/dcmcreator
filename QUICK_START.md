# DICOM Creator v0.3.1 - Quick Reference

## ?? Getting Started

### Option 1: GUI Application (Easiest)
```bash
python src/app.py
```
? Point-and-click interface  
? Real-time results  
? No coding required  

### Option 2: Example Scripts (Ready-to-Run)
```bash
python examples/test_connection.py
python examples/generate_test_dicoms.py
python examples/parallel_send.py
python examples/stress_test.py
python examples/view_history.py
```
? Just run them  
? Edit variables at top of file  
? Get instant results  

### Option 3: Python API (Advanced)
```python
from src.connection_validator import ConnectionValidator
v = ConnectionValidator()
result = v.test_tcp_connection("192.168.1.100", 4321)
```
? Full control  
? Custom integration  
? Automation-ready  

---

## ?? Project Structure

```
dcmcreator/
??? src/                          # Source code
?   ??? app.py                   # GUI launcher
?   ??? appgui.py                # GUI implementation (13 tabs)
?   ??? connection_validator.py  # Connection testing
?   ??? stress_tester.py         # Stress testing
?   ??? transmission_history.py  # Track transmissions
?   ??? performance_benchmarking.py
?   ??? parallel_transmission.py # Parallel sending
?   ??? random_dicom.py          # Test DICOM generator
?   ??? presets.py               # Server presets
?   ??? dcm.py                   # DICOM operations
?   ??? dcmlogger.py             # Logging
?
??? examples/                     # Ready-to-run scripts
?   ??? test_connection.py       # Test server connectivity
?   ??? generate_test_dicoms.py  # Generate test files
?   ??? parallel_send.py         # Simulate parallel transmission
?   ??? stress_test.py           # Run stress test
?   ??? view_history.py          # View transmission history
?   ??? README.md                # Complete guide
?
??? doc/                          # Documentation
?   ??? README.md                # Main documentation
?   ??? WHERE_TO_RUN_TESTS.md   # GUI vs Python comparison
?   ??? PARALLEL_TRANSMISSION_GUIDE.md
?   ??? EXTERNAL_SCRIPT_USAGE.md # Script integration
?   ??? ... (15+ more guides)
?
??? requirements.txt              # Python dependencies
```

---

## ?? By Task

### Test Server Connectivity
**GUI:** Connection Test tab ? Enter IP/port ? Click "Test TCP"  
**Script:** `python examples/test_connection.py`  
**Python API:**
```python
from src.connection_validator import ConnectionValidator
v = ConnectionValidator()
v.test_tcp_connection("192.168.1.100", 4321)
```

### Generate Test DICOM Files
**GUI:** Test/Generate tab ? Set count/size ? Click "Generate DICOMs"  
**Script:** `python examples/generate_test_dicoms.py`  
**Python API:**
```python
from src.random_dicom import RandomDicomGenerator
g = RandomDicomGenerator()
files = g.generate_with_sizes(10, 1.0, "./output")
```

### Send DICOM Files to Server
**GUI:** Remote tab ? Configure server ? Click "Send All Loaded DICOM"  
**Parallel:** Load files ? Parallel Send tab (config) ? Queue & Send  

### Test Performance Under Load
**GUI:** Stress Test tab ? Configure ? Click "Create Plan" ? "Start Test"  
**Script:** `python examples/stress_test.py`  

### Track Transmission History
**GUI:** Transmission History tab ? Click "Refresh" ? View results  
**Script:** `python examples/view_history.py`  
**Export:** Click "Export JSON" for analysis  

---

## ?? Feature Comparison

| Feature | GUI | Scripts | Python API |
|---------|-----|---------|-----------|
| Connection Test | ? | ? | ? |
| Generate DICOMs | ? | ? | ? |
| Send DICOMs | ? | ??? | ? |
| Stress Test | ? | ? | ? |
| View History | ? | ? | ? |
| Export Results | ? | ? | ? |
| Parallel Send | ??? Config | ? | ? |
| Automation | ? | ? | ? |

Legend: ? Direct, ??? Configuration required, ? Not available

---

## ?? Customization Quick Guide

### Change Server Address
Edit any script and change:
```python
SERVER_IP = "your.server.com"
SERVER_PORT = 4321
```

### Generate More Files
Edit `examples/generate_test_dicoms.py`:
```python
FILE_COUNT = 100        # 100 files instead of 10
FILE_SIZE_MB = 5.0      # 5 MB each instead of 1 MB
```

### Stress Test with Higher Load
Edit `examples/stress_test.py`:
```python
FILES_PER_SECOND = 100     # Higher throughput
WORKER_THREADS = 10        # More parallel workers
```

---

## ?? Documentation

### For Quick Start
? Read: `examples/README.md`

### For Comprehensive Guide
? Read: `doc/README.md`

### For Testing Details
? Read: `doc/WHERE_TO_RUN_TESTS.md`

### For Parallel Transmission
? Read: `doc/PARALLEL_TRANSMISSION_GUIDE.md`

### For External Scripts
? Read: `doc/EXTERNAL_SCRIPT_USAGE.md`

---

## ?? Command Reference

### GUI
```bash
python src/app.py
```

### Examples
```bash
python examples/test_connection.py
python examples/generate_test_dicoms.py
python examples/parallel_send.py
python examples/stress_test.py
python examples/view_history.py
```

### Python Shell
```bash
python
>>> from src.connection_validator import ConnectionValidator
>>> v = ConnectionValidator()
>>> v.test_tcp_connection("192.168.1.100", 4321)
```

### Jupyter Notebook
```bash
jupyter notebook
# Create cells with test code
```

---

## ?? Learning Path

### For First-Time Users
1. Read: `README.md`
2. Run: `python src/app.py`
3. Explore: Patient, Study, Series tabs
4. Try: Load DICOM tab

### For Testing Users
1. Read: `examples/README.md`
2. Run: `python examples/test_connection.py`
3. Run: `python examples/generate_test_dicoms.py`
4. Use: GUI to send files

### For Advanced Users
1. Read: `doc/EXTERNAL_SCRIPT_USAGE.md`
2. Modify: Example scripts for your needs
3. Integrate: With your existing workflows
4. Automate: Scheduled tests with cron/Task Scheduler

### For Developers
1. Read: `doc/DEVELOPER_GUIDE_PRESETS.md`
2. Study: Module documentation
3. Extend: Create custom modules
4. Integrate: With CI/CD pipelines

---

## ?? Troubleshooting

### Issue: "Module not found"
**Solution:** Run from project root directory
```bash
cd C:\Users\username\Documents\dcmcreator
python examples/test_connection.py
```

### Issue: Connection times out
**Solution:** Check server IP, port, and network connectivity
```bash
python examples/test_connection.py
# Edit SERVER_IP and SERVER_PORT first
```

### Issue: Scripts don't generate output
**Solution:** Check permissions in output directory
```bash
python examples/generate_test_dicoms.py
# Make sure OUTPUT_DIR is writable
```

### Issue: No transmission history
**Solution:** Send files first before checking history
```bash
# 1. Generate files: python examples/generate_test_dicoms.py
# 2. Send in GUI or script
# 3. Then check: python examples/view_history.py
```

---

## ?? What's New in v0.3.1

? **6 New Test Tabs** - Connection, Stress, History, Benchmarking, Parallel  
? **View Menu** - Hide/show tabs dynamically  
? **Ready-to-Run Scripts** - 5 example scripts in `examples/`  
? **Fixed Tree Selection** - Study and Series nodes now work properly  
? **Professional Documentation** - 16+ comprehensive guides  
? **Clean Repository** - 38% reduction in doc clutter  

---

## ?? Next Steps

**New Users:**
- Launch GUI: `python src/app.py`
- Read: `README.md`

**Testing:**
- Run scripts: `python examples/test_connection.py`
- Customize: Edit variables in script
- Share: Results with team

**Integration:**
- Read: `EXTERNAL_SCRIPT_USAGE.md`
- Modify: Example scripts
- Deploy: In your environment

---

## ?? Support

**For usage questions:** See `examples/README.md`  
**For API reference:** See `doc/COMPLETE_TEST_EXECUTION_REFERENCE.md`  
**For troubleshooting:** See Troubleshooting section above  
**For feature requests:** Contribute to GitHub  

---

**Happy Testing! ??**

Version: v0.3.1  
Status: Production Ready  
Repository: https://github.com/piotrrozentreter/dcmcreator
