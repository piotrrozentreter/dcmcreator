# Using Parallel Transmission Values in External Scripts

## Quick Option: Use Pre-Built Example Scripts (NEW!)

**Don't want to write code?** Use our ready-to-run example scripts in `examples/` directory:

```bash
# Examples are already written and ready to use!
python examples/test_connection.py
python examples/generate_test_dicoms.py
python examples/parallel_send.py
python examples/stress_test.py
python examples/view_history.py
```

See `examples/README.md` for complete guide and customization options.

---

## Advanced: Create Custom External Scripts

If you need to write your own scripts, follow these guidelines:

### ? The Problem with Different Processes

When you run the GUI app and a separate script, they are **different Python processes**. Values in one process are NOT accessible from the other.

```
GUI App Process (PID 1234)          External Script Process (PID 5678)
? self.parallel_workers             ? Can't access these values!
? self.parallel_session_name        ? Different process
? All GUI state                     ? Separate memory space
```

**This WON'T work:**
```python
# external_script.py (running in different process)
from src.appgui import DicomCreatorApp
app = DicomCreatorApp()  # Creates NEW app, not connected to running one
workers = app.parallel_workers.get()  # Gets default "5", not user's value!
```

---

## ? Solution 1: Read Values from Config File (RECOMMENDED)

**BEST for most users** - Simple and reliable

### Step 1: Save Configuration from GUI

```
1. Launch: python src/app.py
2. Go to Parallel Send tab
3. Set Worker Threads (e.g., 8)
4. Set Session Name (e.g., "Bulk Upload")
5. Click "Save Config" button
6. This creates: parallel_config.json
```

### Step 2: Write Script That Reads Config

```python
# my_parallel_send.py
import json
from src.parallel_transmission import ParallelTransmissionManager

# Read configuration
with open("parallel_config.json", "r") as f:
    config = json.load(f)

workers = config["workers"]
session_name = config["session_name"]

print(f"Using {workers} workers for session: {session_name}")

# Create manager with config values
mgr = ParallelTransmissionManager(max_workers=workers)
session = mgr.start_session(session_name)

# Queue your files
file_list = ["file1.dcm", "file2.dcm", "file3.dcm"]
mgr.queue_batch(file_list, your_send_function)

# Execute
mgr.wait_for_completion()
report = mgr.get_session_report()
print(f"Report: {report}")
```

### Usage Flow:

```
1. User opens app: python src/app.py
2. User configures Parallel Send tab
3. User clicks "Save Config" ? parallel_config.json created
4. User runs script: python my_parallel_send.py
5. Script reads parallel_config.json
6. Script uses GUI values automatically!
```

---

## ? Solution 2: Command-Line Arguments

**BEST for automation/scripting**

### Write Script That Accepts Arguments

```python
# external_script.py
import sys
from src.parallel_transmission import ParallelTransmissionManager

# Parse arguments
if len(sys.argv) > 1:
    workers = int(sys.argv[1])
else:
    workers = 5

if len(sys.argv) > 2:
    session_name = sys.argv[2]
else:
    session_name = "Default Session"

print(f"Using {workers} workers, session: {session_name}")

mgr = ParallelTransmissionManager(max_workers=workers)
# ... rest of code
```

### Usage:

```bash
# Use default values
python external_script.py

# Use custom values
python external_script.py 8 "Night Batch"

# Use 10 workers, "Large Upload"
python external_script.py 10 "Large Upload"
```

---

## ? Solution 3: Environment Variables

**BEST for scheduled tasks/cron jobs**

### Set Environment & Run Script

```bash
# Linux/Mac
export PARALLEL_WORKERS=8
export PARALLEL_SESSION="Night Batch"
python external_script.py

# Windows (PowerShell)
$env:PARALLEL_WORKERS="8"
$env:PARALLEL_SESSION="Night Batch"
python external_script.py

# Windows (Command Prompt)
set PARALLEL_WORKERS=8
set PARALLEL_SESSION=Night Batch
python external_script.py
```

### Script That Reads Environment Variables

```python
# external_script.py
import os
from src.parallel_transmission import ParallelTransmissionManager

# Read environment variables with defaults
workers = int(os.getenv("PARALLEL_WORKERS", "5"))
session_name = os.getenv("PARALLEL_SESSION", "Default Send")

print(f"Workers: {workers}, Session: {session_name}")

mgr = ParallelTransmissionManager(max_workers=workers)
# ... rest of code
```

---

## ? Solution 4: Recommended Hybrid Approach

**Combines flexibility of all options**

```python
# external_script.py
import json
import os
from src.parallel_transmission import ParallelTransmissionManager

# Try config file first, then fall back to environment variables
try:
    with open("parallel_config.json", "r") as f:
        config = json.load(f)
        workers = config["workers"]
        session_name = config["session_name"]
        print("Loaded from: parallel_config.json")
except FileNotFoundError:
    # Fall back to environment variables
    workers = int(os.getenv("PARALLEL_WORKERS", "5"))
    session_name = os.getenv("PARALLEL_SESSION", "Default Session")
    print("Loaded from: environment variables")

print(f"Using {workers} workers, session: {session_name}")

mgr = ParallelTransmissionManager(max_workers=workers)
# ... rest of code
```

### Usage Options:

```bash
# Option 1: Use config file (from GUI)
python external_script.py

# Option 2: Override with environment variables
PARALLEL_WORKERS=10 python external_script.py

# Option 3: Use defaults
python external_script.py  # If no config or env vars
```

---

## ?? Comparison of Solutions

| Solution | Pros | Cons | Best For |
|----------|------|------|----------|
| **Config File** | Simple, values persist, GUI-friendly | Requires manual save step | Most users |
| **Command-Line Args** | Easy to remember, scriptable | Must pass args every time | One-off tests |
| **Environment Vars** | Great for scheduled tasks | Not visible, harder to debug | Cron/Task Scheduler |
| **Hybrid** | Flexible, covers all cases | Slightly more complex | Power users |

---

## ?? Quick Reference

| Task | Solution | Command |
|------|----------|---------|
| Save config from GUI | Config File | In GUI: Parallel Send ? Save Config |
| Run with GUI values | Config File | `python my_script.py` |
| Quick one-time run | Command-line | `python my_script.py 8 "Batch1"` |
| Scheduled task | Environment | Set env vars, then `python my_script.py` |
| Maximum flexibility | Hybrid | All three methods work |

---

## ?? Complete Example: Step-by-Step

### Step 1: Configure and Save (One-time)

```bash
# Launch GUI
python src/app.py

# In GUI:
# 1. Go to Parallel Send tab
# 2. Set Worker Threads to 8
# 3. Set Session Name to "Production Batch"
# 4. Click "Save Config"
# This creates: parallel_config.json
```

### Step 2: Create Your Script

```python
# production_send.py
import json
from src.parallel_transmission import ParallelTransmissionManager
from src.remote import send_dicom

# Read configuration
with open("parallel_config.json", "r") as f:
    config = json.load(f)

workers = config["workers"]
session_name = config["session_name"]

# Initialize manager
mgr = ParallelTransmissionManager(max_workers=workers)
mgr.start_session(session_name)

# Define your send function
def my_send_func(file_path):
    # Your transmission logic
    return send_dicom(file_path, server="192.168.1.100", port=4321)

# Queue files
file_list = [
    "patient_001.dcm",
    "patient_002.dcm",
    "patient_003.dcm",
]

mgr.queue_batch(file_list, my_send_func)

# Execute
mgr.wait_for_completion(timeout=3600)
report = mgr.get_session_report()

# Print results
print(f"Files sent: {report['files_sent']}")
print(f"Success rate: {report['success_rate']}%")
print(f"Throughput: {report['throughput_mbps']} MB/s")
```

### Step 3: Run Your Script

```bash
# Every time you need to send files:
python production_send.py

# Output:
# Files sent: 3
# Success rate: 100.0%
# Throughput: 4.23 MB/s
```

---

## ?? Getting Started

### For Quick Testing:
Use ready-to-run scripts in `examples/` directory!

### For Custom Needs:
1. Save config from GUI
2. Create script that reads config
3. Add your business logic
4. Run whenever needed

### For Automation:
1. Use environment variables
2. Schedule with cron or Task Scheduler
3. Monitor results in transmission history

---

## ?? Additional Resources

- `examples/README.md` - Ready-to-run example scripts
- `doc/PARALLEL_TRANSMISSION_GUIDE.md` - Parallel transmission API details

**Happy scripting!** ??
