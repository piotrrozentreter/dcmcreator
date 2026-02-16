# Where to Run All Tests - v0.3.1

## Overview

All advanced testing modules are **NOW FULLY INTEGRATED** into the GUI! Choose your testing approach based on your needs:

- **GUI** - Easy, no coding required, real-time results
- **Python Console** - Advanced, full control, programmatic access
- **Ready-to-Run Scripts** - Pre-built examples, just execute them (NEW!)

---

## ?? What You Can Do

### Option 1: Ready-to-Run Example Scripts (EASIEST)
Located in `examples/` directory - just execute them!

```bash
# Test server connectivity
python examples/test_connection.py

# Generate test DICOM files
python examples/generate_test_dicoms.py

# Run parallel transmission simulation
python examples/parallel_send.py

# Run stress test simulation
python examples/stress_test.py

# View transmission history
python examples/view_history.py
```

**All scripts are pre-configured and ready to use!**
See `examples/README.md` for complete guide.

---

### Option 2: GUI Application

**Launch:** `python src/app.py`

#### 1. **Test/Generate Tab** - DICOM & Transmission
```
? Generate Test DICOMs
   - Specify count (number of files)
   - Specify size (MB per file)
   - Select output directory
   - Click: Generate DICOMs

? Send Generated Files
   - Loads all generated DICOMs
   - Automatically populates form fields
   - Sends to configured remote server
   - Click: Send All Generated

? Generate & Send (One-Click)
   - Generates DICOMs
   - Immediately sends them
   - View status in real-time
```

#### 2. **Connection Test Tab** ? NOW ACTIVE
```
? Test TCP Connection
   - Enter server IP/hostname
   - Enter port
   - Click: Test TCP
   - Get: Success/Failure + Latency

? Test Connection Quality
   - Analyzes: Status, Quality Level, Latency
   - Provides: Recommendations
   - Click: Connection Quality

? Test Latency Variations
   - Configure: Attempts count
   - Measures: Min, Max, Avg, Std Dev
   - Click: Latency Variations
   - Get: Detailed statistics

? Clear Results
   - Remove previous test output
   - Start fresh
```

#### 3. **Stress Test Tab** ? NOW ACTIVE
```
? Create Test Plan
   - Enter: Test name
   - Enter: Files/Second (throughput)
   - Enter: Duration in seconds
   - Enter: File Size (MB)
   - Enter: Worker threads (1-10)
   - Click: Create Plan
   - View: Plan parameters

? Start Test (Simulation)
   - Runs test simulation
   - Can monitor progress
   - Shows metrics in real-time
   - Click: Start Test

? Clear Results
   - Reset test view
```

#### 4. **Transmission History Tab** ? NOW ACTIVE
```
? Refresh History
   - Shows: Last 50 transmissions
   - Displays: Filename, Server, Status
   - Shows: Bytes sent, Timestamp
   - Click: Refresh

? View Statistics
   - Total transmissions count
   - Success count & percentage
   - Failed count
   - Success rate
   - Total MB transferred
   - Average throughput (MB/s)
   - Click: Statistics

? Export to JSON
   - Saves history as JSON file
   - Use for: Analysis, reporting
   - Click: Export JSON
   - Choose: Save location

? Clear View
   - Remove displayed history
```

#### 5. **Benchmarking Tab** ? NOW ACTIVE
```
? View Information
   - Learn: What benchmarking does
   - See: Features available
   - File size performance (0.5-10MB)
   - Latency analysis
   - Throughput measurements

? View Example Code
   - Copy: Working code examples
   - Learn: How to use Python API
   - Adapt: For your needs

? Use Python API
   - For: Advanced benchmarking
   - Instructions: Provided in tab
```

#### 6. **Parallel Send Tab** ? NOW ACTIVE
```
? Configure Workers
   - Set: Worker threads (1-10)
   - More workers = Faster (but more CPU)
   - Enter: Session name
   - Click: Save Config
   - Generate: parallel_config.json

? Use with Scripts
   - For: Actual transmission
   - Use: examples/parallel_send.py
   - Reads config automatically
```

#### 7. **Remote Tab** - DICOM Transmission
```
? Server Presets
   - Save: Server configurations
   - Load: Saved presets
   - Delete: Presets

? Configure Server
   - Enter: Server IP/hostname
   - Enter: Port
   - Enter: Calling AE Title
   - Enter: Called AE Title

? Send DICOM
   - Click: Send All Loaded DICOM
   - View: Messages/Errors in real-time
```

---

### Option 3: Python Console
**Advanced usage with full control**

```bash
python
>>> from src.connection_validator import ConnectionValidator
>>> v = ConnectionValidator()
>>> v.test_tcp_connection("192.168.1.100", 4321)
```

See documentation below for examples.

---

## ?? Python Console Examples

### 1. **Connection Validator** - Advanced Tests
```python
from src.connection_validator import ConnectionValidator

validator = ConnectionValidator()

# Basic TCP test
result = validator.test_tcp_connection("192.168.1.100", 4321)
print(f"Success: {result['success']}, Latency: {result['latency_ms']}ms")

# Connection quality assessment
quality = validator.get_connection_quality("192.168.1.100", 4321)
print(f"Quality: {quality['status']}")

# Test latency variations
variations = validator.test_latency_variations("192.168.1.100", 4321, attempts=20)
print(f"Avg: {variations['avg']}ms")
```

### 2. **Stress Tester** - Load Simulation
```python
from src.stress_tester import StressTestRunner

runner = StressTestRunner()

# Create test plan
plan = runner.create_test_plan(
    name="Load Test",
    files_per_second=50,
    duration_seconds=60,
    file_size_mb=1.0,
    concurrent_threads=5
)

# Start test
runner.start_stress_test(plan)
# ... record file sends ...
report = runner.get_stress_test_report()
print(f"Success rate: {report['success_rate']}%")
```

### 3. **Transmission History** - Track & Analyze
```python
from src.transmission_history import TransmissionHistory

history = TransmissionHistory()

# Get statistics
stats = history.get_statistics()
print(f"Total: {stats['total_transmissions']}")
print(f"Success rate: {stats['success_rate']}%")

# Export to JSON
history.export_to_json("report.json")
```

### 4. **Performance Benchmarking** - Measure Performance
```python
from src.performance_benchmarking import PerformanceBenchmark

benchmarker = PerformanceBenchmark()

# Define send function
def mock_send_func(size_mb):
    import time
    time.sleep(size_mb * 0.1)
    return size_mb * 1024 * 1024, size_mb * 0.1

# Benchmark file sizes
result = benchmarker.run_file_size_benchmark(
    send_function=mock_send_func,
    sizes_mb=[1, 5, 10, 20],
    iterations=3
)

report = benchmarker.get_benchmark_report(0)
print(f"Throughput: {report['throughput_mbps']} MB/s")
```

### 5. **Parallel Transmission** - Fast Bulk Send
```python
from src.parallel_transmission import ParallelTransmissionManager

manager = ParallelTransmissionManager(max_workers=5)
session = manager.start_session("Bulk Send")

# Define send function
def send_dicom(file_path):
    # Your transmission logic
    return True

# Queue files
manager.queue_batch(file_list, send_dicom)

# Wait and get report
manager.wait_for_completion(timeout=3600)
report = manager.get_session_report()
print(f"Files sent: {report['files_sent']}")
```

---

## ?? Feature Comparison

| Feature | GUI Tab | Script | Python API | Effort |
|---------|---------|--------|-----------|--------|
| **Connection Test** | ? | ? | ? | Low |
| **Stress Test** | ? | ? | ? | Medium |
| **View History** | ? | ? | ? | Low |
| **Export Statistics** | ? | ? | ? | Low |
| **DICOM Generation** | ? | ? | ? | Low |
| **Latency Analysis** | ? | ? | ? | Low |
| **Parallel Transmission** | ?? Config | ? | ? | Medium |
| **Custom Scenarios** | ? | ? | ? | High |
| **Automation** | ? | ? | ? | Medium |

Legend:
- ? = Available
- ? = Not available
- ?? = Setup available

---

## ?? When to Use Each Approach

### Use GUI When:
- Quick testing needed
- No coding wanted
- Real-time monitoring desired
- Visual feedback preferred
- Non-technical users

### Use Example Scripts When:
- Want production-ready examples
- Need quick setup and execution
- Easy customization via file editing
- No deep Python knowledge needed
- Want to see how things work

### Use Python When:
- Custom test scenarios needed
- Integration with existing code
- Advanced analysis required
- Automation/scripting needed
- CI/CD pipelines

---

## ?? Running Tests from Different Locations

### 1. GUI Application (EASIEST)
```bash
python src/app.py
# All features available through menu/tabs
# No coding required
# Real-time results
```

### 2. Ready-to-Run Scripts (NEW!)
```bash
# Test connection
python examples/test_connection.py

# Generate files
python examples/generate_test_dicoms.py

# Parallel transmission
python examples/parallel_send.py

# Stress test
python examples/stress_test.py

# View history
python examples/view_history.py
```

### 3. Python REPL
```bash
python
>>> from src.connection_validator import ConnectionValidator
>>> v = ConnectionValidator()
>>> v.test_tcp_connection("192.168.1.100", 4321)
```

### 4. Python Script
```bash
# File: my_tests.py
from src.connection_validator import ConnectionValidator
# ... your test code ...

# Run it:
python my_tests.py
```

### 5. Unit Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 6. Jupyter Notebook
```bash
jupyter notebook
# Create cells with test code
# Run interactively
```

---

## ?? Quick Start Workflows

### Workflow 1: Quickest Start (Scripts)
```bash
# 1. Test connectivity
python examples/test_connection.py

# 2. Generate test files
python examples/generate_test_dicoms.py

# 3. View results
python examples/view_history.py
```

### Workflow 2: Full Testing (GUI)
```bash
# 1. Launch GUI
python src/app.py

# 2. Use Connection Test tab
# 3. Use Test/Generate tab
# 4. Use Stress Test tab
# 5. View Transmission History tab
```

### Workflow 3: Automation (Scripts + Config)
```bash
# 1. Configure in GUI
python src/app.py
# ? Set up Parallel Send tab
# ? Click "Save Config"

# 2. Run script
python examples/parallel_send.py
```

---

## ? Status: v0.3.1

? **All test modules fully integrated into GUI**
? **All test modules accessible from Python**
? **Ready-to-run example scripts available**
? **Choose your approach based on your needs**
? **Documentation provided for all methods**

---

## ?? Documentation Files

- `examples/README.md` - Complete guide for ready-to-run scripts
- `doc/PARALLEL_TRANSMISSION_GUIDE.md` - Parallel transmission details
- `doc/EXTERNAL_SCRIPT_USAGE.md` - How to write custom scripts
- `doc/WHERE_TO_RUN_TESTS.md` - This file

---

## Next Steps

- **Quick Users**: Run `python examples/test_connection.py`
- **GUI Users**: Run `python src/app.py` then explore tabs
- **Developers**: Read `examples/README.md` and customize scripts
- **Automation**: See `doc/EXTERNAL_SCRIPT_USAGE.md`

**Everything is ready to use NOW!** ??

