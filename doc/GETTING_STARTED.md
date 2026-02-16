# Getting Started with DICOM Creator v0.7.0

## What You Have

### Recent Features Added

1. **SSL/TLS Certificate Support (v0.7.0)**
   - Configure certificates in TLS Settings dialog
   - Secure DICOM transmission with encryption
   - Support for PEM, CRT, PKCS#12 formats

2. **Server Presets (v0.3.0+)**
   - Save frequently used server configurations
   - Quick-load presets from dropdown
   - Delete presets with confirmation

3. **Random DICOM Generator (v0.3.1+)**
   - Generate test DICOM files
   - Batch creation (1-1000 files)
   - Configurable sizes
   - Test transmission

4. **Connection Testing (v0.3.1+)**
   - Verify server is reachable
   - Quick pre-flight checks
   - Connection quality assessment
   - Latency analysis

5. **Advanced Testing Features (v0.6.0+)**
   - Stress testing
   - Performance benchmarking
   - Transmission history tracking
   - Parallel transmission

---

## Quick Start

### Step 1: Run the App
```bash
python src/app.py
```

### Step 2: Try the Features

#### Option A - Test Server Connectivity
```
1. Click "Remote" tab
2. Enter server IP and port
3. (Optional) Configure certificates in "TLS Settings..."
4. Click "Send to Remote" to test
```

#### Option B - Generate and Send Test Files
```
1. Click "Test/Generate" tab
2. Set Studies/Patient: 1
3. Set Series/Study: 1
4. Set Instances/Series: 10
5. Set Size/File: 1.0 MB
6. Click "Browse" to select output folder
7. Click "Generate DICOMs"
8. Click "Generate & Send" to send to server
```

#### Option C - Advanced Connection Testing
```
1. Click "Connection Test" tab
2. Enter server details
3. Click "Test TCP" for basic connectivity
4. Click "Connection Quality" for detailed assessment
5. Click "Latency Variations" to test consistency
```

#### Option D - Stress Testing
```
1. Click "Stress Test" tab
2. Configure test parameters:
   - Files/Second: 50
   - Duration: 60 seconds
   - File Size: 1.0 MB
3. Click "Create Plan"
4. Click "Start Test"
5. View results in the results area
```

---

## Certificate Configuration (v0.7.0)

### For SSL/TLS Secure Transmission

1. **Generate or obtain certificates**:
   ```bash
   python generate_certs.py  # Generate self-signed certs
   ```

2. **Configure in application**:
   - Go to **Remote -> TLS Settings...**
   - Enter paths to your certificates
   - Select certificate types (PEM, CRT, PKCS#12)
   - Click "Save"

3. **Enable TLS for transmission**:
   - On Remote tab, check "Use TLS/SSL"
   - Send DICOM as normal

---

## Key Tabs Explained

### Core Tabs
- **Patient** - Patient demographic information
- **Study** - Study metadata
- **Series/Modality** - Series information and modality type
- **Image** - Load and preview images
- **Load DICOM** - Load and view existing DICOM files
- **Save** - Save current DICOM
- **Remote** - Configure and send to remote servers

### Test Tabs (Toggle via View menu)
- **Test/Generate** - Generate test DICOM files
- **Connection Test** - Test server connectivity
- **Stress Test** - Perform load testing
- **Transmission History** - View transmission logs
- **Benchmarking** - Performance analysis
- **Parallel Send** - Parallel transmission configuration

---

## Tips & Tricks

1. **View -> Show All** - Display all tabs including test features
2. **View -> Hide Test Tabs** - Show only core tabs for cleaner interface
3. **DICOM -> View Tags** - Inspect all DICOM tags in loaded file
4. **Ctrl+V** - Validate current form data
5. **Ctrl+Shift+V** - Manual validation check

---

## What's New in v0.7.0

- Full SSL/TLS certificate support
- Enhanced `.gitignore` for certificates
- Updated documentation
- Better error handling for certificate operations
- 100% backward compatible with v0.6.1

---

## Next Steps

1. **Create DICOM** - Fill in patient/study/series, load image, click Save
2. **Send to Server** - Configure remote server, click "Send to Remote"
3. **Test Features** - Explore Connection Test, Stress Test tabs
4. **Read Docs** - See [INDEX.md](INDEX.md) for complete documentation

---

**Version**: 0.7.0  
**Last Updated**: March 2026

