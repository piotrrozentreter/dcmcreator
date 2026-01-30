# Ready-to-Execute Example Scripts

All scripts in this directory are **ready to run** - just execute them with Python!

---

## ?? Available Examples

### 1. **test_connection.py** - Test Server Connectivity
```bash
python examples/test_connection.py
```

**What it does:**
- Tests TCP connection to DICOM server
- Measures connection quality
- Analyzes latency variations
- Provides connectivity report

**Edit in script:**
```python
SERVER_IP = "192.168.1.100"   # Your server IP
SERVER_PORT = 4321            # Your server port
ATTEMPTS = 5                  # Latency test attempts
```

**Example output:**
```
1. Testing TCP Connection...
   ? Success: True
   ? Latency: 12.34 ms

2. Testing Connection Quality...
   ? Status: OK
   ? Level: EXCELLENT

3. Testing Latency Variations...
   ? Min Latency: 10.12 ms
   ? Max Latency: 15.89 ms
   ? Avg Latency: 12.50 ms
```

---

### 2. **generate_test_dicoms.py** - Create Test DICOM Files
```bash
python examples/generate_test_dicoms.py
```

**What it does:**
- Generates random test DICOM files
- Creates specified number of files
- Sets file sizes as needed
- Saves to output directory

**Edit in script:**
```python
OUTPUT_DIR = "./test_dicom_output"  # Where to save
FILE_COUNT = 10                     # Number of files
FILE_SIZE_MB = 1.0                  # Size per file
```

**Example output:**
```
Generating 10 DICOM files (1.0 MB each)...

? Generated 10 DICOM files
? Location: C:\Users\...\test_dicom_output
? Total size: 10.0 MB

Generated files:
  1. patient_001_study_001.dcm (1.00 MB)
  2. patient_001_study_002.dcm (1.00 MB)
  ...
```

---

### 3. **parallel_send.py** - Simulate Parallel Transmission
```bash
python examples/parallel_send.py
```

**Prerequisites:**
1. Run GUI: `python src/app.py`
2. Go to "Parallel Send" tab
3. Set Worker Threads (e.g., 8)
4. Set Session Name
5. Click "Save Config" ? Creates `parallel_config.json`
6. Then run this script

**What it does:**
- Reads configuration from `parallel_config.json`
- Simulates parallel DICOM transmission
- Shows real performance metrics
- Demonstrates speedup with multiple workers

**Edit in script:**
```python
FILE_COUNT = 50            # Files to simulate
FILE_SIZE_MB = 1.0        # File size
NETWORK_LATENCY_MS = 10   # Simulated latency
```

**Example output:**
```
Loading configuration...
? Workers: 8
? Session: Bulk Upload

Simulating 50 files...
  10% - 5 sent, 0 failed
  20% - 10 sent, 0 failed
  ...

? Files sent: 50
? Success rate: 100.0%
? Throughput: 5.23 MB/s
? Speedup: 8.1x (vs sequential)
```

---

### 4. **stress_test.py** - Run Stress Test Simulation
```bash
python examples/stress_test.py
```

**What it does:**
- Simulates DICOM transmission under load
- Tests server with configurable throughput
- Measures performance metrics
- Shows success/failure rates

**Edit in script:**
```python
TEST_NAME = "Load Test"
FILES_PER_SECOND = 50      # Throughput target
DURATION_SECONDS = 60      # How long to run
FILE_SIZE_MB = 1.0         # Each file
WORKER_THREADS = 5         # Parallel workers
```

**Example output:**
```
Test Configuration:
  Name: Load Test
  Target: 50 files/sec
  Duration: 60 seconds
  Workers: 5

Expected Results:
  Total files: 3000
  Total data: 3000.0 MB
  Expected throughput: 50.00 MB/s

? Files sent: 2850
? Success Rate: 95.0%
? Actual Throughput: 47.50 MB/s
? Test PASSED - Target throughput achieved
```

---

### 5. **view_history.py** - View Transmission History
```bash
python examples/view_history.py
```

**What it does:**
- Shows transmission statistics
- Lists recent transmissions
- Exports history to JSON
- Provides success/failure analysis

**Example output:**
```
STATISTICS
Total Transmissions: 245
Successful: 237
Failed: 8
Success Rate: 96.7%
Total Data Transferred: 237.0 MB
Average Throughput: 4.23 MB/s

RECENT TRANSMISSIONS
1. patient_001.dcm
   Server: 192.168.1.100:4321
   Status: ? OK
   Bytes: 1,048,576
   Time: 2025-01-14 14:30:45

2. patient_002.dcm
   Server: 192.168.1.100:4321
   Status: ? OK
   ...
```

---

## ?? Quick Start Workflows

### Workflow 1: Test Server Then Generate Files

```bash
# Step 1: Test if server is reachable
python examples/test_connection.py

# Step 2: Generate test data
python examples/generate_test_dicoms.py

# Step 3: Load in GUI and send
python src/app.py
# ? Load files from test_dicom_output
# ? Send to server via Remote tab
```

### Workflow 2: Test Parallel Transmission

```bash
# Step 1: Configure GUI
python src/app.py
# ? Go to Parallel Send tab
# ? Set workers (e.g., 8)
# ? Click "Save Config"
# ? Close GUI

# Step 2: Run simulation
python examples/parallel_send.py
# ? Shows performance metrics
# ? Demonstrates speedup
```

### Workflow 3: Stress Test Your Server

```bash
# Step 1: Generate test files
python examples/generate_test_dicoms.py

# Step 2: Run stress test
python examples/stress_test.py
# ? Simulates load
# ? Shows throughput
# ? Tests success rate
```

### Workflow 4: Check Transmission History

```bash
# Run after sending files
python examples/view_history.py
# ? Shows statistics
# ? Lists recent transfers
# ? Exports to JSON for analysis
```

---

## ?? Customization Guide

### Test Connection with Different Server

Edit `test_connection.py`:
```python
SERVER_IP = "my.server.com"    # Your server
SERVER_PORT = 11112            # Port (default DICOM is 4321 or 11112)
ATTEMPTS = 10                  # More attempts for detailed latency
```

### Generate More/Larger Files

Edit `generate_test_dicoms.py`:
```python
FILE_COUNT = 100               # Generate 100 files
FILE_SIZE_MB = 5.0            # Each 5 MB (bigger files)
OUTPUT_DIR = "D:/large_test"  # Different location
```

### Simulate Heavy Load

Edit `stress_test.py`:
```python
FILES_PER_SECOND = 100        # 2x higher throughput
DURATION_SECONDS = 300        # 5 minutes instead of 1
WORKER_THREADS = 10           # Maximum workers
```

### Test with Many Parallel Workers

Edit `parallel_send.py` (after setting in GUI):
```python
# In GUI, set to 10 workers
# Then run script to see 10x speedup
```

---

## ?? Common Use Cases

### Use Case 1: Validate Server Before Production

```bash
# Check if server is ready
python examples/test_connection.py

# If successful:
# ? Server is reachable
# ? Quality is good
# ? Latency is acceptable
# ? Ready for production!
```

### Use Case 2: Load Testing

```bash
# Test server under load
python examples/stress_test.py

# Results show:
# ? How many files/sec it can handle
# ? Success rate under load
# ? Whether it meets requirements
```

### Use Case 3: Performance Optimization

```bash
# Test parallel transmission
python examples/parallel_send.py

# Results show:
# ? Speedup with multiple workers
# ? Optimal worker count
# ? Actual throughput achieved
```

### Use Case 4: Historical Analysis

```bash
# After running transmissions
python examples/view_history.py

# Results show:
# ? Success rate over time
# ? Average throughput
# ? Problem files (if any)
# ? Exported to JSON for reporting
```

---

## ?? Troubleshooting

### Script Won't Run: "Module not found"

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Run scripts from project root directory:
```bash
cd C:\Users\username\Documents\dcmcreator
python examples/test_connection.py
```

### Script Hangs During Transmission Test

**Problem:** Script seems frozen when testing connection

**Solution:** May be waiting for network timeout. Press `Ctrl+C` to stop.

### Config File Not Found

**Problem:** `parallel_send.py` says "parallel_config.json not found"

**Solution:**
1. Run GUI: `python src/app.py`
2. Go to "Parallel Send" tab
3. Click "Save Config" button
4. Then run `python examples/parallel_send.py`

### No Transmission History

**Problem:** `view_history.py` shows no transmissions

**Solution:** Send some DICOMs first:
1. Generate files: `python examples/generate_test_dicoms.py`
2. Load in GUI: `python src/app.py` ? Load from test_dicom_output
3. Send files: Use Remote tab
4. Then check history: `python examples/view_history.py`

---

## Example Performance Results

### Connection Test Results
```
Server: 192.168.1.100:4321
? TCP Connection: 12.45 ms
? Quality Level: EXCELLENT
? Recommendation: Optimal for transmission
```

### Parallel Transmission Results (5 files)
```
Sequential (1 worker):  5.2 MB/s
Parallel (5 workers):   24.1 MB/s
Speedup: 4.6x
```

### Stress Test Results (60 second test)
```
Target: 50 files/sec
Actual: 47.8 files/sec
Success Rate: 98.2%
Performance: PASS
```

---

## Next Steps

1. **Test connectivity:** `python examples/test_connection.py`
2. **Generate test data:** `python examples/generate_test_dicoms.py`
3. **Test performance:** `python examples/stress_test.py`
4. **View results:** `python examples/view_history.py`

---

**Everything is ready to use!** Just pick a script, edit the configuration, and run it!
