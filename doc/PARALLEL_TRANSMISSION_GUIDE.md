# Parallel Transmission Tab - Complete Guide

## Overview

The Parallel Transmission tab allows you to configure multi-threaded DICOM file transmission. It provides configuration options but requires Python API usage for actual transmission.

---

## ?? Where Values Are Stored

### In the GUI (appgui.py)

```python
# Line 2067 - Worker Threads value
self.parallel_workers = tk.StringVar(value="5")

# Line 2071 - Session Name value
self.parallel_session_name = tk.StringVar(value="Bulk Transmission")
```

### Accessing These Values in Python

```python
# Inside the DicomCreatorApp class, you can access:
workers = int(self.parallel_workers.get())          # Get worker count (1-10)
session_name = self.parallel_session_name.get()     # Get session name
```

---

## ??? GUI Configuration Tab

### What You See in the GUI:

```
?? Parallel Transmission Manager ??????????????????????
?                                                     ?
? Configuration                                      ?
?  Worker Threads: [5]  (spinbox 1-10)              ?
?  Session Name:   [Bulk Transmission          ]    ?
?                                                     ?
? Information                                         ?
?  - Multi-threaded file transmission (1-10)        ?
?  - 3-5x speed improvement over sequential         ?
?  - Session management and progress tracking       ?
?  - Real-time performance metrics                  ?
?                                                    ?
?  Note: Configure workers and use Python API       ?
?                                                    ?
?  [Example Code] [Documentation]                   ?
???????????????????????????????????????????????????????
```

### Controls:

| Control | Type | Range | Default | Purpose |
|---------|------|-------|---------|---------|
| Worker Threads | Spinbox | 1-10 | 5 | Number of parallel transmission threads |
| Session Name | Text Entry | Any | Bulk Transmission | Name for this transmission session |

---

## ?? How It Works - Architecture

### Flow Diagram

```
???????????????????????????????????????????????????????
? Parallel Transmission Manager                       ?
???????????????????????????????????????????????????????
?                                                     ?
?  1. Create Manager (with worker count)             ?
?     mgr = ParallelTransmissionManager(max_workers) ?
?                                                     ?
?  2. Start Session (with session name)              ?
?     session = mgr.start_session("name")            ?
?                                                     ?
?  3. Queue Files (add to transmission queue)        ?
?     mgr.queue_transmission(file, send_func)        ?
?                                                     ?
?  4. Process in Parallel (workers distribute load)  ?
?     Worker 1 ??                                    ?
?     Worker 2 ??? Send Files ? Remote Server       ?
?     Worker 3 ??                                    ?
?     ...                                            ?
?                                                     ?
?  5. Wait & Report (get results)                    ?
?     mgr.wait_for_completion()                      ?
?     report = mgr.get_session_report()              ?
?                                                     ?
???????????????????????????????????????????????????????
```

### Performance Comparison

```
Sequential Transmission:
File 1 ? Send ??? File 2 ? Send ??? File 3 ? Send
?? 10s ???? 10s ???? 10s ??
Total: 30 seconds

Parallel Transmission (3 workers):
File 1 ??                          
File 2 ??? Send ??? Remote Server
File 3 ??
Total: 10 seconds (3x faster!)
```

---

## ?? Usage Scenarios

### Scenario 1: Get Current Settings from GUI

```python
# Inside appgui.py DicomCreatorApp class
def get_parallel_config(self):
    """Get current parallel transmission configuration."""
    workers = int(self.parallel_workers.get())
    session_name = self.parallel_session_name.get()
    return {"workers": workers, "session_name": session_name}

# Returns: {"workers": 5, "session_name": "Bulk Transmission"}
```

### Scenario 2: Use Values in External Script

```python
# external_script.py
import tkinter as tk
from src.appgui import DicomCreatorApp

# Create app instance
app = DicomCreatorApp()

# Get the configured values
workers = int(app.parallel_workers.get())
session_name = app.parallel_session_name.get()

print(f"Using {workers} workers for session: {session_name}")

# Now use these values with ParallelTransmissionManager
from src.parallel_transmission import ParallelTransmissionManager

manager = ParallelTransmissionManager(max_workers=workers)
session = manager.start_session(session_name)
```

### Scenario 3: Full Transmission with GUI Configuration

```python
from src.appgui import DicomCreatorApp
from src.parallel_transmission import ParallelTransmissionManager

# Assume app is running
app = DicomCreatorApp()

# Get configuration from GUI tab
workers = int(app.parallel_workers.get())
session_name = app.parallel_session_name.get()

# Create manager with GUI-configured workers
mgr = ParallelTransmissionManager(max_workers=workers)

# Start session with GUI-configured name
session = mgr.start_session(session_name)

# Queue your files
files_to_send = [
    "path/to/file1.dcm",
    "path/to/file2.dcm",
    "path/to/file3.dcm",
]

# Define your send function
def send_dicom_file(file_path):
    # Your transmission logic
    # This will be called by worker threads
    from src.remote import send_dicom
    return send_dicom(file_path, config)

# Queue all files
mgr.queue_batch(files_to_send, send_dicom_file)

# Wait for all to complete
mgr.wait_for_completion(timeout=3600)

# Get results
report = mgr.get_session_report()
print(f"Sent: {report['files_sent']}")
print(f"Success rate: {report['success_rate']}%")
print(f"Speed: {report['throughput_mbps']} MB/s")
```

---

## ?? Worker Thread Selection Guide

### How Many Workers Should I Use?

```
??????????????????????????????????????????????????????????????
? Recommended Settings by Use Case                           ?
??????????????????????????????????????????????????????????????
?                                                            ?
? Light Load (Home/Test):                                   ?
?   Workers: 2-3                                            ?
?   Use: Local testing, small batches                       ?
?   CPU Impact: Low                                         ?
?                                                            ?
? Medium Load (Office/Clinical):                            ?
?   Workers: 5 (DEFAULT)                                    ?
?   Use: Regular daily operations                           ?
?   CPU Impact: Moderate                                    ?
?                                                            ?
? Heavy Load (Enterprise/Bulk):                             ?
?   Workers: 8-10                                           ?
?   Use: Bulk transmission, overnight jobs                  ?
?   CPU Impact: High                                        ?
?                                                            ?
? Performance Improvements:                                 ?
?   1 worker:  100% baseline speed                         ?
?   2 workers:  ~2x faster (200%)                          ?
?   5 workers:  ~5x faster (500%)                          ?
?   10 workers: ~10x faster (1000%)                        ?
?                                                            ?
? BUT: Network bandwidth is the limiting factor!           ?
?   If you have 1 Mbps link:                              ?
?   - 5 workers × 1 Mbps = still capped at 1 Mbps        ?
?   - Better to use 2-3 workers                           ?
?                                                            ?
?   If you have 100 Mbps link:                            ?
?   - 5-10 workers will saturate the link                 ?
?   - All 5-10 files can transmit simultaneously         ?
?                                                            ?
??????????????????????????????????????????????????????????????
```

---

## ?? Integration Points

### Where Tab Values Connect

```python
# In appgui.py - _build_parallel_tab() creates these:
self.parallel_workers         # User configured value
self.parallel_session_name    # User configured name

# These values can be accessed anywhere in the app:
# Option 1: Direct access (if you have app instance)
app.parallel_workers.get()

# Option 2: Create a method to use them
def start_parallel_send(self, files, send_func):
    workers = int(self.parallel_workers.get())
    session = self.parallel_session_name.get()
    
    mgr = ParallelTransmissionManager(max_workers=workers)
    mgr.start_session(session)
    mgr.queue_batch(files, send_func)
    return mgr
```

---

## ?? How to Actually Use Parallel Transmission

### Step 1: Configure in GUI

1. Launch app: `python src/app.py`
2. View ? Show All (if test tabs hidden)
3. Go to "Parallel Send" tab
4. Set Worker Threads (e.g., 5)
5. Set Session Name (e.g., "Batch Upload")

### Step 2: Get Configuration Values

```python
# Inside your Python script
from src.appgui import DicomCreatorApp

app = DicomCreatorApp()
workers = int(app.parallel_workers.get())
session_name = app.parallel_session_name.get()
```

### Step 3: Create Manager & Queue Files

```python
from src.parallel_transmission import ParallelTransmissionManager

# Create with configured worker count
mgr = ParallelTransmissionManager(max_workers=workers)

# Start with configured session name
session = mgr.start_session(session_name)

# Queue your files
file_list = ["file1.dcm", "file2.dcm", "file3.dcm"]
mgr.queue_batch(file_list, your_send_function)
```

### Step 4: Execute & Get Report

```python
# Wait for all to complete
mgr.wait_for_completion(timeout=3600)

# Get performance report
report = mgr.get_session_report()
print(report)
```

---

## ?? What the Session Reports

```python
report = mgr.get_session_report()

# Returns dictionary with:
{
    'session_name': 'Bulk Transmission',
    'files_queued': 100,
    'files_sent': 98,
    'files_failed': 2,
    'success_rate': 98.0,
    'total_bytes': 98765432,
    'duration_seconds': 45.5,
    'throughput_mbps': 4.2,
    'workers_used': 5,
    'start_time': '2025-01-14 14:30:00',
    'end_time': '2025-01-14 14:30:45'
}
```

---

## ?? Advanced: Monitoring Progress

```python
import time
from src.parallel_transmission import ParallelTransmissionManager

mgr = ParallelTransmissionManager(max_workers=5)
session = mgr.start_session("Monitored Send")

# Queue files
mgr.queue_batch(1000_files, send_func)

# Monitor progress
while not mgr.is_complete():
    progress = mgr.get_progress()
    print(f"Progress: {progress['completed']}/{progress['total']} "
          f"({progress['percentage']:.1f}%)")
    print(f"Speed: {progress['throughput_mbps']:.1f} MB/s")
    time.sleep(1)

# Get final report
report = mgr.get_session_report()
```

---

## ?? Key Points

? **Worker Threads stored in:**
- `self.parallel_workers` (StringVar)
- Accessible via `.get()` to get string value
- Range: 1-10

? **Session Name stored in:**
- `self.parallel_session_name` (StringVar)
- Accessible via `.get()` to get string value

? **How it works:**
- GUI is for configuration only
- Actual transmission requires Python API
- Values from GUI can be read and used in scripts
- Workers distribute file transmission load
- Speed improves with more workers (until network saturated)

? **Best practices:**
- Use 5 workers for standard operations
- Use more for high-speed networks
- Use fewer for constrained networks
- Monitor throughput to see if adding workers helps

---

## Summary Table

| Aspect | Details |
|--------|---------|
| **Storage Location** | `self.parallel_workers`, `self.parallel_session_name` |
| **Data Type** | tkinter StringVar |
| **Default Workers** | 5 |
| **Worker Range** | 1-10 |
| **Default Session** | "Bulk Transmission" |
| **Access Method** | `.get()` to retrieve string |
| **Convert to Int** | `int(self.parallel_workers.get())` |
| **Usage** | Configuration only (GUI), execution requires Python API |
| **Speed Benefit** | 3-5x with 5 workers, up to 10x with 10 workers |

---

Everything is documented and ready to use! ??
