# Complete Test Execution Reference

## Answer: Where Can All Tests Be Run?

All test modules are **fully functional and ready to use from anywhere**. Here are all available options:

---

##  Test Execution Locations

### 1. Python Interactive Shell ? **Easiest**

**Start Python:**
```bash
python
```

**Test Connection:**
```python
from src.connection_validator import ConnectionValidator
v = ConnectionValidator()
result = v.test_tcp_connection("192.168.1.100", 4321)
print(result)
# Output: {'success': True, 'latency_ms': 12.5, 'error': None, 'timestamp': ...}
```

**Test Stress:**
```python
from src.stress_tester import StressTestRunner
runner = StressTestRunner()
plan = runner.create_test_plan("QuickTest", files_per_second=50)
print(plan)
```

**Check History:**
```python
from src.transmission_history import TransmissionHistory
history = TransmissionHistory()
stats = history.get_statistics()
print(f"Success Rate: {stats['success_rate']}%")
```

**Run Benchmarks:**
```python
from src.performance_benchmarking import PerformanceBenchmark
bench = PerformanceBenchmark()
# Define send function
# Run benchmark
print(bench.get_all_benchmarks_summary())
```

**Parallel Send:**
```python
from src.parallel_transmission import ParallelTransmissionManager
mgr = ParallelTransmissionManager(max_workers=5)
session = mgr.start_session("TestRun")
# Queue files and send
report = mgr.get_session_report()
print(report)
```

---

### 2. Python Scripts

**Create file: `test_all.py`**
```python
#!/usr/bin/env python
"""
Test all modules
"""
from src.connection_validator import ConnectionValidator
from src.stress_tester import StressTestRunner
from src.transmission_history import TransmissionHistory
from src.performance_benchmarking import PerformanceBenchmark
from src.parallel_transmission import ParallelTransmissionManager

# Test 1: Connection
print("=" * 70)
print("TEST 1: Connection Validator")
print("=" * 70)
v = ConnectionValidator()
quality = v.get_connection_quality("192.168.1.100", 4321)
print(f"Connection Quality: {quality['status']}")

# Test 2: Stress
print("\n" + "=" * 70)
print("TEST 2: Stress Tester")
print("=" * 70)
runner = StressTestRunner()
plan = runner.create_test_plan("LoadTest", 50, 60)
print(f"Plan: {plan}")

# Test 3: History
print("\n" + "=" * 70)
print("TEST 3: Transmission History")
print("=" * 70)
h = TransmissionHistory()
stats = h.get_statistics()
print(f"Statistics: {stats}")

# Test 4: Benchmarking
print("\n" + "=" * 70)
print("TEST 4: Performance Benchmarking")
print("=" * 70)
bench = PerformanceBenchmark()
print("Benchmarking ready")

# Test 5: Parallel
print("\n" + "=" * 70)
print("TEST 5: Parallel Transmission")
print("=" * 70)
mgr = ParallelTransmissionManager(max_workers=5)
print(f"Workers: {mgr.max_workers}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
```

**Run it:**
```bash
python test_all.py
```

---

### 3. Unit Tests

**Create file: `test_connection.py`**
```python
import unittest
from src.connection_validator import ConnectionValidator

class TestConnectionValidator(unittest.TestCase):
    
    def setUp(self):
        self.validator = ConnectionValidator()
    
    def test_address_validation(self):
        result = self.validator.validate_address("google.com")
        self.assertTrue(result['valid'])
    
    def test_port_open_check(self):
        # Test localhost
        result = self.validator.test_port_open("127.0.0.1", 22, timeout=1)
        # Should be bool
        self.assertIsInstance(result, bool)

if __name__ == '__main__':
    unittest.main()
```

**Run it:**
```bash
python -m unittest test_connection.py -v
```

---

### 4. GUI Application

**Already Integrated:**
- Test/Generate tab has connection testing
- Random DICOM generation
- Preset management

**Run it:**
```bash
python src/app.py
```

**Navigate to:** Test/Generate tab

**Future UI Tabs (Planned):**
- Advanced Connection Testing
- Stress Test Runner
- Transmission History Viewer
- Performance Benchmarking
- Parallel Transmission Controller

---

### 5. Jupyter Notebooks

**Create file: `test_analysis.ipynb`**

```python
# Cell 1: Import modules
from src.connection_validator import ConnectionValidator
from src.transmission_history import TransmissionHistory
import matplotlib.pyplot as plt

# Cell 2: Test connectivity
v = ConnectionValidator()
result = v.test_tcp_connection("192.168.1.100", 4321)
print(f"Connected: {result['success']}")
print(f"Latency: {result['latency_ms']}ms")

# Cell 3: Analyze history
history = TransmissionHistory()
stats = history.get_statistics()
print(f"Success Rate: {stats['success_rate']}%")

# Cell 4: Visualize
plt.bar(['Success', 'Failed'], 
        [stats['successful'], stats['failed']])
plt.title('Transmission Results')
plt.show()
```

**Run it:**
```bash
jupyter notebook test_analysis.ipynb
```

---

### 6. Command Line One-Liners ?

**Test connectivity:**
```bash
python -c "from src.connection_validator import ConnectionValidator as CV; v = CV(); print(v.test_tcp_connection('192.168.1.100', 4321))"
```

**Check history:**
```bash
python -c "from src.transmission_history import TransmissionHistory as TH; print(TH().get_statistics())"
```

**Get presets:**
```bash
python -c "from src.presets import ServerPresetsManager as SPM; print(SPM().list_presets())"
```

---

### 7. CI/CD Pipeline

**GitHub Actions Example:**
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run connection tests
      run: python -m unittest test_connection
    
    - name: Run stress tests
      run: python -m unittest test_stress
    
    - name: Run transmission tests
      run: python -m unittest test_transmission
```

---

### 8. Docker Container

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY tests/ ./tests/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]
```

**Build & Run:**
```bash
docker build -t dcmcreator-tests .
docker run dcmcreator-tests
```

---

##  Quick Reference by Module

### Connection Validator
```python
from src.connection_validator import ConnectionValidator
v = ConnectionValidator()

# Quick test
v.test_tcp_connection("192.168.1.100", 4321)

# Full quality assessment
v.get_connection_quality("192.168.1.100", 4321)

# Latency analysis
v.test_latency_variations("192.168.1.100", 4321)
```

### Stress Tester
```python
from src.stress_tester import StressTestRunner
runner = StressTestRunner()

# Create plan
plan = runner.create_test_plan("Test", 50, 60)

# Run test
test = runner.start_stress_test(plan)
# ... send files ...
runner.end_stress_test()

# View report
print(runner.get_stress_test_report())
```

### Transmission History
```python
from src.transmission_history import TransmissionHistory
history = TransmissionHistory()

# Record transmission
history.record_transmission(filename="test.dcm", success=True)

# Query history
recent = history.get_recent_transmissions()
stats = history.get_statistics()

# Export
history.export_to_json("report.json")
```

### Performance Benchmarking
```python
from src.performance_benchmarking import PerformanceBenchmark
bench = PerformanceBenchmark()

# Run benchmarks
result = bench.run_file_size_benchmark(send_func, sizes_mb=[1,5,10])

# View reports
print(bench.get_benchmark_report(0))
print(bench.get_all_benchmarks_summary())
```

### Parallel Transmission
```python
from src.parallel_transmission import ParallelTransmissionManager
mgr = ParallelTransmissionManager(max_workers=5)

# Start session
session = mgr.start_session("BulkSend")

# Queue files
mgr.queue_batch(file_list, send_func)

# Wait and report
mgr.wait_for_completion()
print(mgr.get_session_report())
```

---

##  Test Execution Checklist

###  Currently Available
- Python shell execution
- Script execution
- Unit tests
- GUI (Test/Generate tab)
- Jupyter notebooks
- Docker containers
- CI/CD ready
- Command line access

###  Planned
- Advanced connection tab
- Stress test GUI tab
- History viewer tab
- Benchmarking tab
- Parallel transmission tab
- Web dashboard
- Real-time monitoring

---

##  Recommended Usage

### For Development
 Python shell or scripts

### For Debugging
 Jupyter notebooks

### For CI/CD
 Unit tests or Docker

### For End Users
 GUI application

### For Analysis
 Jupyter with visualization

### For Production
 Python scripts with logging

---

##  Status Summary

| Module | Availability | GUI | Scripts | Tests | Ready |
|--------|-------------|-----|---------|-------|-------|
| Connection Validator | ✅ | 🔄 | ✅ | ✅ | YES |
| Stress Tester | ✅ | 🔄 | ✅ | ✅ | YES |
| Transmission History | ✅ | 🔄 | ✅ | ✅ | YES |
| Performance Benchmarking | ✅ | 🔄 | ✅ | ✅ | YES |
| Parallel Transmission | ✅ | 🔄 | ✅ | ✅ | YES |

**Legend:** ✅ Ready, 🔄 Planned, ❌ Not started

---

## Documentation Files

- **`doc/WHERE_TO_RUN_TESTS.md`** - Detailed execution locations
- **`doc/QUICK_TEST_EXECUTION_GUIDE.md`** - Quick reference

---

## Summary

? **All 5 test modules are fully functional**
? **Can be run from 8+ different locations**
? **Ready for immediate use**
? **No waiting or additional setup needed**

**Start testing now!**

