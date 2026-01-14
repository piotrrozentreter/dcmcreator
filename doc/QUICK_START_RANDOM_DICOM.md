# Quick Start: Random DICOM Generator

## First Time Using It?

### Step 1: Launch App
```bash
python src/app.py
```

### Step 2: Open Test/Generate Tab
Click the "Test/Generate" tab at the bottom

### Step 3: Generate Test Files
```
1. Set Count: 10
2. Set Size/File: 1.0 MB
3. Click "Browse" and select output folder
4. Click "Generate DICOMs"
```

**You'll see:**
```
Generating 10 test DICOMs (1.0MB each)...
? Generated 10 test DICOM files
  Location: C:\Users\...\test_data
```

### Step 4: Test Connection
```
1. Fill in Remote tab first:
   - Server: 192.168.1.100 (or your server)
   - Port: 4321
2. Go back to Test/Generate tab
3. Click "Test Connection"
```

**You'll see:**
```
Testing connection...
  Connecting to 192.168.1.100:4321...
  ? Connection successful
```

### Step 5: Send Files
Click "Send All Generated" to transmit the test files

---

## Use Cases

### Case 1: Quick Demo
```
Goal: Show working DICOM transmission

Steps:
  1. Generate 5 small files (0.5 MB each)
  2. Test connection
  3. Send files
  Done!
```

### Case 2: Server Testing
```
Goal: Verify server is working

Steps:
  1. Test connection
  2. If passes ? Generate files
  3. Send to server
  4. Check server logs
```

### Case 3: Performance Testing
```
Goal: Check transmission speed

Steps:
  1. Generate 100 files (1 MB each)
  2. Monitor progress
  3. Check average time per file
  4. Calculate throughput
```

---

## Settings Explained

| Setting | Default | What It Does |
|---------|---------|-------------|
| Count | 10 | How many test files to create (1-1000) |
| Size/File | 1.0 | File size target in MB per file (0.5-100) |
| Output Dir | - | Where to save the files (required) |

---

## What Gets Generated?

Each test DICOM file includes:
- Random patient name (realistic)
- Random patient ID
- Medical study data
- Proper DICOM headers
- Synthetic 16-bit grayscale image

**Example File:**
```
Patient: John Smith
ID: TEST512345
Study: General radiology
Size: ~1 MB
Format: Valid DICOM file (.dcm)
```

---

## Common Workflows

### Workflow 1: Generate ? Test ? Send
```
1. Click "Generate DICOMs"
   Wait ~10 seconds
2. Click "Test Connection"
   Wait ~2 seconds
3. Click "Send All Generated"
   Watch progress
```

### Workflow 2: Auto Generate & Send
```
1. Set all parameters
2. Click "Generate & Send"
   Does both steps automatically
```

### Workflow 3: Manual Sending
```
1. Generate files manually
2. Go to Load DICOM tab
3. Load the generated folder
4. Use regular Send button
```

---

## Troubleshooting

**Q: "pydicom not available"**
A: Install dependencies: `pip install -r requirements.txt`

**Q: Connection fails**
A: Check server IP/port, verify network connectivity

**Q: Files not generating**
A: Select output directory first with Browse button

**Q: Generation is slow**
A: Normal for large batches (100+ files). Takes ~1 min for 100 files.

---

## Tips

? Test connection BEFORE generating large batches
? Start small (10 files) before trying 500+ files  
? Check Messages area for detailed status
? Files are saved to disk - reuse them multiple times
? Generated files are real DICOM files - usable anywhere

---

## File Locations

**Where are generated files?**
```
C:\Users\[Username]\your_selected_folder\
  ??? test_dicom_0001.dcm
  ??? test_dicom_0002.dcm
  ??? ... etc
```

**Can I delete them?**
Yes, they're just test files. Delete after you're done.

**Can I move them?**
Yes, they're standard DICOM files. Move/copy anywhere.

---

## What's Next?

Try these:
1. Generate 5 small files (~30 seconds)
2. Send them to your test server
3. Verify they arrive
4. Try larger batch next time

---

## Need More Info?

See: `doc/RANDOM_DICOM_GENERATOR.md` for complete documentation

