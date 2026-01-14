# Where to Run All Tests - v0.3.1

## Overview

All advanced testing modules are **NOW FULLY INTEGRATED** into the GUI! Choose your testing approach based on your needs:

- **GUI** - Easy, no coding required, real-time results
- **Python Console** - Advanced, full control, programmatic access

---

## ? What You Can Do from GUI

### 1. **Test/Generate Tab** - DICOM & Transmission
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

### 2. **Connection Test Tab** ? NOW ACTIVE
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

### 3. **Stress Test Tab** ? NOW ACTIVE
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

### 4. **Transmission History Tab** ? NOW ACTIVE
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

### 5. **Benchmarking Tab** ? NOW ACTIVE
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

### 6. **Parallel Send Tab** ? NOW ACTIVE
```
? Configure Workers
   - Set: Worker threads (1-10)
   - More workers = Faster (but more CPU)
   - Enter: Session name

? View Information
   - Learn: Parallel transmission benefits
   - See: Performance improvements (3-5x)
   - Recommended settings

? Use Python API
   - For: Actual transmission
   - Use: With your file list
```

### 7. **Remote Tab** - DICOM Transmission
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

## ?? What You Can Do from Python Console

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
print(f"Level: {quality['level']}")
print(f"Recommendation: {quality['recommendation']}")

# Test multiple ports
ports = validator.test_multiple_ports("192.168.1.100", [4321, 11112, 5000])
for port, result in ports.items():
    print(f"Port {port}: {result['success']}")

# Latency variations (detailed)
variations = validator.test_latency_variations("192.168.1.100", 4321, attempts=20)
print(f"Min: {variations['min']}ms")
print(f"Max: {variations['max']}ms")
print(f"Avg: {variations['avg']}ms")
print(f"StdDev: {variations['std_dev']}ms")

# Validate addresses
result = validator.validate_address("google.com")
print(f"Valid: {result['valid']}")

# Get DNS info
dns = validator.get_dns_info("example.com")
print(f"IP: {dns['ip_address']}")
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
print(f"Plan: {plan}")

# Start test
test = runner.start_stress_test(plan)

# Simulate sending files
total_files = int(50 * 60)  # files/sec * duration
for i in range(total_files):
    success = True  # Your transmission logic
    runner.record_file_sent(bytes_sent=1000000, success=success)

# End test
runner.end_stress_test("COMPLETED")

# Get report
report = runner.get_stress_test_report()
print(f"Success rate: {report['success_rate']}%")
print(f"Throughput: {report['throughput_mbps']} MB/s")
```

### 3. **Transmission History** - Track & Analyze
```python
from src.transmission_history import TransmissionHistory

history = TransmissionHistory()

# Record transmission
history.record_transmission(
    filename="test.dcm",
    server_ip="192.168.1.100",
    server_port=4321,
    success=True,
    bytes_sent=1000000,
    duration_seconds=1.5
)

# Get statistics
stats = history.get_statistics()
print(f"Total: {stats['total_transmissions']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Avg throughput: {stats['avg_throughput_mbps']} MB/s")

# Get recent transmissions
recent = history.get_recent_transmissions(limit=50)
for trans in recent:
    print(f"{trans['timestamp']}: {trans['filename']} -> {trans['success']}")

# Export to JSON
history.export_to_json("transmission_report.json")

# Query by date
from datetime import datetime, timedelta
today = datetime.now().date()
transmissions = history.get_transmissions_by_date(today)
```

### 4. **Performance Benchmarking** - Measure Performance
```python
from src.performance_benchmarking import PerformanceBenchmark

benchmarker = PerformanceBenchmark()

# Define your send function
def mock_send_func(size_mb):
    import time
    time.sleep(size_mb * 0.1)  # Simulate transfer
    return size_mb * 1024 * 1024, size_mb * 0.1  # bytes, time

# Benchmark file sizes
result = benchmarker.run_file_size_benchmark(
    send_function=mock_send_func,
    sizes_mb=[1, 5, 10, 20],
    iterations=3
)

# Get report
report = benchmarker.get_benchmark_report(0)
print(f"1MB: {report['throughput_mbps']} MB/s")
print(f"5MB: {report['throughput_mbps']} MB/s")

# Benchmark latency
result = benchmarker.run_latency_benchmark(
    ping_func=mock_send_func,
    iterations=100
)

# Export results
benchmarker.export_benchmark("benchmark_results.json")

# Get summary
summary = benchmarker.get_all_benchmarks_summary()
```

### 5. **Parallel Transmission** - Fast Bulk Send
```python
from src.parallel_transmission import ParallelTransmissionManager

manager = ParallelTransmissionManager(max_workers=5)

# Start session
session = manager.start_session("Bulk Send")

# Define send function
def send_dicom(file_path):
    # Your transmission logic
    return True

# Queue files
for file_path in file_list:
    manager.queue_transmission(file_path, send_dicom)

# Or queue batch
manager.queue_batch(file_list, send_dicom)

# Wait for completion
manager.wait_for_completion(timeout=3600)

# Get session report
report = manager.get_session_report()
print(f"Files sent: {report['files_sent']}")
print(f"Success rate: {report['success_rate']}%")
print(f"Duration: {report['duration_seconds']}s")
print(f"Throughput: {report['throughput_mbps']} MB/s")
```

### 6. **Random DICOM Generator** - Create Test Data
```python
from src.random_dicom import RandomDicomGenerator

generator = RandomDicomGenerator()

# Generate single DICOM
ds = generator.generate_single(
    filename="test.dcm",
    patient_name="John Doe",
    patient_id="12345",
    width=512,
    height=512
)

# Generate with specific sizes
files = generator.generate_with_sizes(
    count=10,
    size_mb=1.0,
    output_dir="./test_dicoms"
)

# Generate and get pixel arrays
dicoms = []
for i in range(5):
    ds, pixel_array = generator.generate_single_with_array()
    dicoms.append((ds, pixel_array))
```

---

## ?? Feature Comparison

| Feature | GUI Tab | Python API | Effort |
|---------|---------|-----------|--------|
| **Connection Test** | ? Yes | ? Yes | Low/Medium |
| **Stress Test Simulation** | ? Yes | ? Yes | Medium |
| **View Transmission History** | ? Yes | ? Yes | Low |
| **Export Statistics** | ? Yes | ? Yes | Low |
| **DICOM Generation** | ? Yes | ? Yes | Low |
| **Latency Analysis** | ? Yes | ? Yes | Low |
| **Parallel Transmission** | ?? Config | ? Yes | Medium |
| **Performance Benchmarking** | ?? Info | ? Yes | High |
| **Custom Test Scenarios** | ? No | ? Yes | High |
| **Automation/Scripting** | ? No | ? Yes | High |

Legend:
- ? Yes = Direct from tab
- ?? Config/Info = Setup from tab, use Python for execution
- ? No = Not available in GUI

---

## ?? When to Use GUI vs Python

### Use GUI When:
- ? Quick testing needed
- ? No coding wanted
- ? Real-time monitoring needed
- ? Visual feedback desired
- ? Non-technical users
- ? One-off tests

### Use Python When:
- ? Automation needed
- ? Custom test scenarios
- ? Batch processing
- ? Integration with scripts
- ? Advanced analysis
- ? CI/CD pipelines
- ? Data processing
- ? Scheduled testing

---

## ?? Running from Different Locations

### Option 1: GUI Application (EASIEST)
```bash
python src/app.py
# All features available through menu/tabs
# No coding required
# Real-time results
```

### Option 2: Python REPL
```bash
python
>>> from src.connection_validator import ConnectionValidator
>>> v = ConnectionValidator()
>>> v.test_tcp_connection("192.168.1.100", 4321)
```

### Option 3: Python Script
```bash
# File: my_tests.py
from src.connection_validator import ConnectionValidator
# ... your test code ...

# Run it:
python my_tests.py
```

### Option 4: Command Line One-Liner
```bash
python -c "
from src.connection_validator import ConnectionValidator as CV
print(CV().test_tcp_connection('192.168.1.100', 4321))
"
```

### Option 5: Unit Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Option 6: Jupyter Notebook
```bash
jupyter notebook
# Create cells with test code
# Run interactively
```

---

## ?? Quick Start Guide

### For Casual Users (GUI)
```
1. Launch: python src/app.py
2. View ? Show All (to see test tabs)
3. Test Connection tab ? Enter server info
4. Click: Connection Quality
5. View results immediately
```

### For Testing Users (GUI)
```
1. Launch: python src/app.py
2. Test/Generate tab ? Generate DICOMs
3. Connection Test tab ? Validate connectivity
4. Remote tab ? Send files
5. Transmission History ? View results
```

### For Developers (Python)
```python
# Quick connection test
from src.connection_validator import ConnectionValidator
result = ConnectionValidator().test_tcp_connection("192.168.1.100", 4321)
print(result)

# Generate test data
from src.random_dicom import RandomDicomGenerator
files = RandomDicomGenerator().generate_with_sizes(10, 1.0, "./output")
print(f"Generated {len(files)} files")

# Track results
from src.transmission_history import TransmissionHistory
stats = TransmissionHistory().get_statistics()
print(stats)
```

### For Automation (Scripts)
```bash
# test_and_report.py
from src.connection_validator import ConnectionValidator
from src.transmission_history import TransmissionHistory
from datetime import datetime

# Test connectivity
validator = ConnectionValidator()
result = validator.test_tcp_connection("192.168.1.100", 4321)
print(f"[{datetime.now()}] Connection: {result['success']}")

# Get stats
history = TransmissionHistory()
stats = history.get_statistics()
print(f"Success rate: {stats['success_rate']}%")

# Run: python test_and_report.py
```

---

## Summary Table: GUI vs Python

```
????????????????????????????????????????????????????????????????????????????????
?                          GUI vs PYTHON CONSOLE                              ?
????????????????????????????????????????????????????????????????????????????????
? Task                      ? GUI Easy? ? Python Power? ? Best Choice          ?
????????????????????????????????????????????????????????????????????????????????
? Quick connection test     ? ? YES   ? ? YES        ? GUI (easiest)        ?
? Validate server quality   ? ? YES   ? ? YES        ? GUI (visual)         ?
? Generate test DICOMs      ? ? YES   ? ? YES        ? GUI (simpler)        ?
? Send DICOM files          ? ? YES   ? ? YES        ? GUI (integrated)     ?
? View transmission history ? ? YES   ? ? YES        ? GUI (nice display)   ?
? Export test results       ? ? YES   ? ? YES        ? Either              ?
? Simulate load testing     ? ? YES   ? ? YES        ? GUI (monitoring)     ?
? Batch generate DICOMs     ? ??  MAYBE? ? YES        ? Python (loop)       ?
? Custom test scenarios     ? ? NO    ? ? YES        ? Python (flexible)   ?
? Automate testing          ? ? NO    ? ? YES        ? Python (script)     ?
? Schedule recurring tests  ? ? NO    ? ? YES        ? Python (cron)       ?
? CI/CD integration         ? ? NO    ? ? YES        ? Python (pipeline)   ?
????????????????????????????????????????????????????????????????????????????????
```

---

## Status: v0.3.1

? **All test modules fully integrated into GUI**
? **All test modules accessible from Python**
? **Choose your approach based on your needs**
? **Documentation provided for both methods**

---

## Next Steps

- **New Users**: Start with GUI (Test/Generate tab)
- **Testing Users**: Explore all test tabs in View menu
- **Developers**: Use Python API for custom scenarios
- **Automation**: Create scripts for repeated tests

**Everything is ready to use NOW!** ??

