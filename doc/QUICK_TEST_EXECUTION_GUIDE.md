# Quick Test Execution Guide - v0.3.1

## ? ALL TEST MODULES NOW ACTIVE IN GUI!

All test utilities are fully integrated into the application. No more "planned tabs" - they're ready to use!

---

## Where Each Test Module Can Run

### 1. Connection Validator Tests

**Available Right Now:**
```
? GUI - Connection Test Tab (ACTIVE)
? Python interactive shell
? Python scripts
? Unit tests
? Jupyter notebooks
```

**GUI Usage:**
```
1. Open: python src/app.py
2. Go to: Connection Test tab
3. Enter server IP/port
4. Click: Test TCP / Connection Quality / Latency Variations
5. View results in real-time
```

**Python Example:**
```python
from src.connection_validator import ConnectionValidator
v = ConnectionValidator()
result = v.test_tcp_connection("192.168.1.100", 4321)
print(result)
```

---

### 2. Stress Tester Tests

**Available Right Now:**
```
? GUI - Stress Test Tab (ACTIVE)
? Python interactive shell
? Python scripts
? Unit tests
? Jupyter notebooks
```

**GUI Usage:**
```
1. Open: python src/app.py
2. Go to: Stress Test tab
3. Configure: Test name, files/sec, duration, file size, workers
4. Click: Create Plan ? Start Test
5. View results and metrics in real-time
```

**Python Example:**
```python
from src.stress_tester import StressTestRunner
runner = StressTestRunner()
plan = runner.create_test_plan("TestLoad", 50, 60, 1.0, 5)
test = runner.start_stress_test(plan)
# ... send files ...
runner.end_stress_test()
```

---

### 3. Transmission History Tests

**Available Right Now:**
```
? GUI - Transmission History Tab (ACTIVE)
? Python interactive shell
? Python scripts
? Unit tests
? Jupyter notebooks
? Automatic (runs in background during transmissions)
```

**GUI Usage:**
```
1. Open: python src/app.py
2. Go to: Transmission History tab
3. Click: Refresh (shows recent transmissions)
4. Click: Statistics (view success rates, throughput)
5. Click: Export JSON (save for reporting)
```

**Python Example:**
```python
from src.transmission_history import TransmissionHistory
h = TransmissionHistory()
h.record_transmission(filename="test.dcm", success=True, bytes_sent=1000000)
stats = h.get_statistics()
print(stats)
```

---

### 4. Performance Benchmarking Tests

**Available Right Now:**
```
? GUI - Benchmarking Tab (ACTIVE)
? Python interactive shell
? Python scripts
? Unit tests
? Jupyter notebooks
```

**GUI Usage:**
```
1. Open: python src/app.py
2. Go to: Benchmarking tab
3. View: Information panel with benchmarking features
4. Click: Example Code (see usage patterns)
5. Use: Python API for advanced benchmarking
```

**Python Example:**
```python
from src.performance_benchmarking import PerformanceBenchmark
b = PerformanceBenchmark()
result = b.run_file_size_benchmark(my_send_func, sizes_mb=[1, 5, 10])
print(b.get_benchmark_report(0))
```

---

### 5. Parallel Transmission Tests

**Available Right Now:**
```
? GUI - Parallel Send Tab (ACTIVE)
? Python interactive shell
? Python scripts
? Unit tests
? Jupyter notebooks
```

**GUI Usage:**
```
1. Open: python src/app.py
2. Go to: Parallel Send tab
3. Configure: Worker threads (1-10), Session name
4. View: Information and features overview
5. Use: Python API for parallel transmission
```

**Python Example:**
```python
from src.parallel_transmission import ParallelTransmissionManager
mgr = ParallelTransmissionManager(max_workers=5)
session = mgr.start_session("BulkSend")
mgr.queue_batch(files, send_func)
mgr.wait_for_completion()
print(mgr.get_session_report())
```

---

### 6. DICOM Generator Tests

**Available Right Now:**
```
? GUI - Test/Generate Tab (ACTIVE)
? Python interactive shell
? Python scripts
? Unit tests
? Jupyter notebooks
```

**GUI Usage:**
```
1. Open: python src/app.py
2. Go to: Test/Generate tab
3. Set: Count (number of files), Size/File (MB)
4. Click: Browse (select output directory)
5. Click: Generate DICOMs or Generate & Send
6. View: Status and results in real-time
```

---

## Test Execution Matrix

```
????????????????????????????????????????????????????????
?  WHERE TO RUN TESTS - MATRIX                         ?
????????????????????????????????????????????????????????
? Module               ? GUI Tab         ? Status      ?
????????????????????????????????????????????????????????
? Connection Validator ? Connection Test ? ? ACTIVE   ?
? Stress Tester        ? Stress Test     ? ? ACTIVE   ?
? Transmission History ? Trans. History  ? ? ACTIVE   ?
? Perf. Benchmarking   ? Benchmarking    ? ? ACTIVE   ?
? Parallel Trans.      ? Parallel Send   ? ? ACTIVE   ?
? DICOM Generator      ? Test/Generate   ? ? ACTIVE   ?
? Server Presets       ? Remote          ? ? ACTIVE   ?
????????????????????????????????????????????????????????
```

---

## Recommended Usage by Scenario

### Scenario 1: Quick Server Test
```
GUI Method:
1. ?? Launch: python src/app.py
2. Go to: Connection Test tab
3. Enter server IP and port
4. Click: Test TCP
5. Get instant result

Or Python:
from src.connection_validator import ConnectionValidator
v = ConnectionValidator()
print(v.get_connection_quality("192.168.1.100", 4321))
```

### Scenario 2: Load Testing
```
GUI Method:
1. ?? Launch: python src/app.py
2. Go to: Stress Test tab
3. Configure test parameters
4. Click: Create Plan ? Start Test
5. Monitor results in real-time

Or Python:
runner = StressTestRunner()
plan = runner.create_test_plan("LoadTest", 50, 60, 1.0, 5)
runner.start_stress_test(plan)
```

### Scenario 3: Generate & Send Test Files
```
GUI Method:
1. ?? Launch: python src/app.py
2. Go to: Test/Generate tab
3. Set count and size
4. Click: Browse (select output directory)
5. Click: Generate & Send
6. View results and status

Or Python:
generator = RandomDicomGenerator()
files = generator.generate_with_sizes(10, 1.0, "output_dir")
# Then transmit files...
```

### Scenario 4: Performance Analysis
```
GUI Method:
1. ?? Launch: python src.app.py
2. Go to: Benchmarking tab
3. Review example code
4. Run benchmarks from Python

Or Python:
bench = PerformanceBenchmark()
result = bench.run_file_size_benchmark(send_func, [1, 5, 10])
print(bench.get_benchmark_report(0))
```

### Scenario 5: Transmission Tracking
```
GUI Method:
1. ?? Launch: python src.app.py
2. Go to: Transmission History tab
3. Click: Refresh (see recent transmissions)
4. Click: Statistics (view success rates)
5. Click: Export JSON (save report)

Or Python:
history = TransmissionHistory()
stats = history.get_statistics()
history.export_to_json("report.json")
```

### Scenario 6: Fast Parallel Send
```
GUI Method:
1. ?? Launch: python src.app.py
2. Go to: Parallel Send tab
3. Set worker threads (5-10)
4. Use Python API for transmission

Or Python:
mgr = ParallelTransmissionManager(max_workers=5)
mgr.queue_batch(files, send_function)
mgr.wait_for_completion()
print(mgr.get_session_report())
```

---

## Running from Different Environments

### Option 1: GUI Application (RECOMMENDED)
```bash
python src/app.py
# Easiest for most users
# All features integrated
# Real-time results
# No coding required
```

### Option 2: Python REPL
```bash
python
>>> from src.connection_validator import ConnectionValidator
>>> v = ConnectionValidator()
>>> result = v.test_tcp_connection("192.168.1.100", 4321)
>>> print(result)
```

### Option 3: Python Script
```bash
# test_script.py
from src.connection_validator import ConnectionValidator
v = ConnectionValidator()
result = v.test_tcp_connection("192.168.1.100", 4321)
print(result)

# Run it:
python test_script.py
```

### Option 4: Jupyter Notebook
```bash
jupyter notebook
# Create cells with test code
# Run interactively
# Visualize results
```

### Option 5: Unit Tests
```bash
python -m unittest test_connection.py
# Or discover all tests:
python -m unittest discover -s tests
```

---

## Module Availability Check

```python
# Verify all modules are available
import sys

modules = [
    'src.connection_validator',
    'src.stress_tester',
    'src.transmission_history',
    'src.performance_benchmarking',
    'src.parallel_transmission',
    'src.random_dicom'
]

print("Module Availability:")
for mod in modules:
    try:
        __import__(mod)
        print(f"  ? {mod}")
    except ImportError:
        print(f"  ? {mod}")
```

---

## Quick Reference: GUI Tab Access

```
python src/app.py

?? Tabs Available:
   ?? Patient (metadata)
   ?? Study (metadata)
   ?? Series/Modality (metadata)
   ?? Image (preview/loading)
   ?? Load DICOM (file browser)
   ?? Save (export)
   ?? Remote (transmission)
   ?? Test/Generate ? DICOM generation
   ?? Connection Test ? TCP/Quality/Latency
   ?? Stress Test ? Load simulation
   ?? Transmission History ? Tracking & stats
   ?? Benchmarking ? Performance analysis
   ?? Parallel Send ? Multi-threaded transmission
```

---

## Next Steps

### Immediate (Ready Now - v0.3.1)
- ? Run tests from GUI (all tabs active)
- ? Run tests from Python
- ? Use in scripts
- ? Integrate into tests
- ? Use in Jupyter

### Short Term Enhancement
- Add advanced filtering to history
- Web dashboard for monitoring
- Real-time performance graphs
- Email alerts for failures

### Medium Term
- CI/CD integration
- Automated scheduled testing
- Performance trend analysis
- Predictive analytics

### Long Term
- Machine learning integration
- AI-powered optimization
- Cloud deployment
- Enterprise features

---

## Summary

**v0.3.1 Status:**

? **All test modules are fully functional and integrated:**
- Connection Validator (GUI + Python)
- Stress Tester (GUI + Python)
- Transmission History (GUI + Python)
- Performance Benchmarking (GUI + Python)
- Parallel Transmission (GUI + Python)
- DICOM Generator (GUI + Python)

? **Access methods:**
1. GUI Application (easiest - recommended)
2. Python shell (quick tests)
3. Scripts (automation)
4. Unit tests (CI/CD)
5. Jupyter (analysis)

? **No waiting - everything is ready now!**

---

## Getting Started

1. **For Quick Test:** `python src/app.py` ? Go to Connection Test tab
2. **For Load Testing:** Go to Stress Test tab
3. **For DICOM Generation:** Go to Test/Generate tab
4. **For Advanced Users:** Use Python API directly
5. **For Analysis:** Export data from GUI or use Python API

**Start testing immediately! ??**

