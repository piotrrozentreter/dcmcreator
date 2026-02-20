# C-GET and C-MOVE Implementation Guide

## Overview

**C-GET** and **C-MOVE** are DICOM operations for retrieving (downloading) images from PACS:

- **C-GET**: PACS sends files directly to your application (simple, recommended)
- **C-MOVE**: PACS sends files to a third-party destination (advanced, requires SCP running)

---

## C-GET (Download to Application)

### What is C-GET?

C-GET requests the PACS to send DICOM files directly to your application using C-STORE.

**Workflow:**
```
1. Your App     →  C-GET Request      →  PACS
2. Your App     ←  C-STORE (File 1)   ←  PACS
3. Your App     ←  C-STORE (File 2)   ←  PACS
...
N. Your App     ←  C-STORE (File N)   ←  PACS
```

### Using C-GET in GUI

#### Step 1: Query for Studies
```
1. Go to "Query PACS" tab
2. Enter search criteria (e.g., Patient Name, Date Range)
3. Click "Query PACS"
4. Results appear in tree view
```

#### Step 2: Download Study
```
1. Select a study in the results
2. Click "Download Study (C-GET)" button
   OR
   Double-click the study
3. Choose output directory
4. Wait for download to complete
```

#### Step 3: View Downloaded Files
```
- Files saved as: {SOPInstanceUID}.dcm
- Organized in selected folder
- Option to load into application after download
```

### Using C-GET Programmatically

```python
from src.query_retrieve import DicomQueryHandler

handler = DicomQueryHandler()

# Download a study
success, count, message = handler.c_get_study(
    server="192.168.1.100",
    port=104,
    calling_ae="DCMCREATOR",
    called_ae="PACS_SCP",
    study_uid="1.2.840.113619.2.55.3.604688119.868.1234567890.1",
    output_dir="./downloads"
)

if success:
    print(f"Downloaded {count} files")
else:
    print(f"Failed: {message}")
```

### Progress Callback

```python
def progress_callback(received, total, status):
    """Called for each file received."""
    print(f"Progress: {received}/{total} - {status}")

success, count, message = handler.c_get_study(
    server="192.168.1.100",
    port=104,
    calling_ae="DCMCREATOR",
    called_ae="PACS_SCP",
    study_uid="1.2.840...",
    output_dir="./downloads",
    on_progress=progress_callback  # ✅ Track progress
)
```

---

## C-MOVE (Send to Third Party)

### What is C-MOVE?

C-MOVE requests PACS to send files to another DICOM node (not your application).

**Workflow:**
```
1. Your App        →  C-MOVE Request       →  PACS
2. PACS            →  C-STORE (Files)      →  Destination AE
3. Your App        ←  Status Updates       ←  PACS
```

**Requirements:**
1. Destination AE must be **known to PACS** (configured in PACS)
2. Destination AE must be **running and accessible** from PACS
3. Destination AE must **accept C-STORE** from PACS

### Using C-MOVE Programmatically

```python
from src.query_retrieve import DicomQueryHandler

handler = DicomQueryHandler()

# Move study to another node
success, count, message = handler.c_move_study(
    server="192.168.1.100",
    port=104,
    calling_ae="DCMCREATOR",
    called_ae="PACS_SCP",
    study_uid="1.2.840.113619.2.55.3.604688119.868.1234567890.1",
    move_destination="WORKSTATION_AE"  # Must be known to PACS
)

if success:
    print(f"Moved {count} instances")
else:
    print(f"Failed: {message}")
```

### C-MOVE vs C-GET

| Feature | C-GET | C-MOVE |
|---------|-------|--------|
| **Files go to** | Your application | Third-party node |
| **Complexity** | Simple | Complex |
| **Setup required** | Your AE title only | Destination AE + PACS config |
| **Use case** | Download for viewing/editing | Route to workstation/archive |
| **Network** | PACS → You | PACS → Destination |
| **Firewall** | Your port must be open | Destination port must be open |

**Recommendation:** Use C-GET for most scenarios. Only use C-MOVE if you need to route files to existing DICOM workstations.

---

## Error Handling

### Common C-GET Errors

#### "C-GET not supported by PACS"

**Error Message:**
```
No presentation context for 'Study Root Query/Retrieve Information Model - GET' 
has been accepted by the peer for the SCU role
```

**What it means:**
The PACS does not support C-GET operations. This is actually **very common** - many PACS systems only support C-MOVE, not C-GET.

**Why this happens:**
- C-GET is optional in DICOM standard
- Many vendors only implement C-MOVE
- Some PACS have C-GET disabled by default
- Legacy PACS may not support C-GET at all

**Solutions:**

1. **Check PACS Capabilities First** (Recommended)
   ```
   In GUI: Click "Check Capabilities" button
   Shows: ✅ C-GET Support: Yes/No
          ✅ C-MOVE Support: Yes/No
   ```

2. **Use C-MOVE Instead**
   - C-MOVE is more widely supported
   - Requires destination AE configuration in PACS
   - See C-MOVE section below

3. **Ask PACS Administrator**
   - Request C-GET to be enabled
   - Verify retrieve permissions for your AE title
   - Check if C-GET is supported by PACS version

4. **Alternative Methods**
   - Use PACS web viewer to download
   - Use vendor-specific tools
   - Export via DICOM router/proxy

**Quick Test:**
```python
# Check what PACS supports
c_get, c_move, msg = handler.check_retrieve_support(
    server="192.168.1.100",
    port=104,
    calling_ae="DCMCREATOR",
    called_ae="PACS_SCP"
)

print(f"C-GET: {c_get}, C-MOVE: {c_move}")
```

#### "No files received from PACS"

**Causes:**
1. Study doesn't exist on PACS
2. Your AE title doesn't have retrieve permissions
3. PACS doesn't support C-GET (try C-MOVE)
4. Firewall blocking incoming C-STORE

**Solutions:**
1. Verify Study UID is correct
2. Check AE title permissions with PACS admin
3. Test with simple C-FIND first
4. Open your application's listening port (default: ephemeral)

#### "Failed to establish association"

**Causes:**
1. Wrong server IP/port
2. PACS not responding
3. Firewall blocking connection

**Solutions:**
1. Test with Connection Test tab first
2. Verify PACS is running
3. Check firewall rules

#### "Association released prematurely"

**Causes:**
1. PACS timeout during transfer
2. Network interruption
3. Storage failure on your side

**Solutions:**
1. Ensure stable network connection
2. Check disk space in output directory
3. Increase PACS timeout if possible

### Common C-MOVE Errors

#### "Move destination unknown"

**Cause:** PACS doesn't know the destination AE title

**Solution:** Ask PACS administrator to add destination AE to PACS configuration

#### "Move failed: destination unreachable"

**Cause:** PACS cannot connect to destination node

**Solution:**
1. Verify destination node is running
2. Check destination IP/port accessible from PACS
3. Verify firewall allows PACS → Destination

---

## Advanced Usage

### Download Specific Series

```python
# Query for series first
success, results, message = handler.query_pacs(
    server="192.168.1.100",
    port=104,
    calling_ae="DCMCREATOR",
    called_ae="PACS_SCP",
    query_level="SERIES",
    search_criteria={
        'StudyInstanceUID': '1.2.840...',
        'Modality': 'CT'
    }
)

# Download specific series
# Note: Need to implement c_get_series() method
# Similar to c_get_study() but with SeriesInstanceUID
```

### Batch Download Multiple Studies

```python
import os

study_uids = [
    "1.2.840.113619...",
    "1.2.840.113620...",
    "1.2.840.113621..."
]

for i, study_uid in enumerate(study_uids, 1):
    print(f"Downloading study {i}/{len(study_uids)}")
    
    output_dir = f"./downloads/study_{i}"
    os.makedirs(output_dir, exist_ok=True)
    
    success, count, message = handler.c_get_study(
        server="192.168.1.100",
        port=104,
        calling_ae="DCMCREATOR",
        called_ae="PACS_SCP",
        study_uid=study_uid,
        output_dir=output_dir
    )
    
    if success:
        print(f"  ✅ Downloaded {count} files")
    else:
        print(f"  ❌ Failed: {message}")
```

### Download with Verification

```python
import pydicom
import os

def verify_download(output_dir, expected_study_uid):
    """Verify all files belong to the expected study."""
    files = [f for f in os.listdir(output_dir) if f.endswith('.dcm')]
    
    for filename in files:
        filepath = os.path.join(output_dir, filename)
        ds = pydicom.dcmread(filepath, stop_before_pixels=True)
        
        if ds.StudyInstanceUID != expected_study_uid:
            print(f"Warning: {filename} has wrong Study UID")
            return False
    
    return True

# Download and verify
success, count, message = handler.c_get_study(...)

if success:
    if verify_download(output_dir, study_uid):
        print("✅ Download verified")
    else:
        print("⚠️ Verification failed")
```

---

## PACS Compatibility

### Known PACS Support

| PACS Vendor | C-GET | C-MOVE | Notes |
|-------------|-------|--------|-------|
| **DCM4CHEE** | ✅ Yes | ✅ Yes | Full support |
| **Orthanc** | ✅ Yes | ✅ Yes | Full support |
| **Horos** | ✅ Yes | ✅ Yes | Mac PACS/Viewer |
| **Conquest** | ⚠️ Optional | ✅ Yes | C-GET must be enabled |
| **GE PACS** | ❌ Rare | ✅ Yes | Usually C-MOVE only |
| **Philips iSite** | ❌ No | ✅ Yes | C-MOVE only |
| **Agfa IMPAX** | ⚠️ Optional | ✅ Yes | Check with admin |
| **Siemens syngo** | ⚠️ Optional | ✅ Yes | Version dependent |
| **Carestream** | ❌ Rare | ✅ Yes | Usually C-MOVE only |
| **Sectra PACS** | ⚠️ Optional | ✅ Yes | Configuration dependent |

**Legend:**
- ✅ Yes: Commonly supported
- ⚠️ Optional: Supported but may be disabled
- ❌ No/Rare: Usually not supported

**Recommendation:** Always check capabilities before attempting retrieval.

---

## PACS Configuration

### What PACS Administrator Needs to Do

#### For C-GET:
1. Register your AE title in PACS
2. Grant retrieve permissions to your AE
3. Enable C-GET SCP on PACS (if not default)

#### For C-MOVE:
1. Register your AE title in PACS (source)
2. Register destination AE title in PACS
3. Configure destination AE IP/port in PACS
4. Grant move permissions to your AE

### Testing PACS Configuration

```bash
# Test C-GET with dcmtk
getscu -P -k "StudyInstanceUID=1.2.840..." \
    192.168.1.100 104 \
    -aec PACS_SCP \
    -aet DCMCREATOR \
    -od ./downloads

# Test C-MOVE with dcmtk  
movescu -P -k "StudyInstanceUID=1.2.840..." \
    192.168.1.100 104 \
    -aec PACS_SCP \
    -aet DCMCREATOR \
    -aem WORKSTATION_AE
```

---

## Performance Tips

### Optimize Download Speed

1. **Use Wired Connection**: WiFi can be slow for large studies
2. **SSD Storage**: Faster disk I/O for saving files
3. **Increase Buffer Size**: Modify pynetdicom buffer settings
4. **Parallel Downloads**: Download multiple series simultaneously

### Monitor Resource Usage

```python
import psutil
import time

start_time = time.time()
initial_disk = psutil.disk_usage('.').used

# Download study
success, count, message = handler.c_get_study(...)

end_time = time.time()
final_disk = psutil.disk_usage('.').used

duration = end_time - start_time
data_mb = (final_disk - initial_disk) / (1024 * 1024)

print(f"Downloaded {data_mb:.1f} MB in {duration:.1f}s")
print(f"Speed: {data_mb/duration:.1f} MB/s")
```

---

## Troubleshooting

### No Files Received

1. **Check Query Works**: Run C-FIND first to verify study exists
2. **Test Association**: Use Connection Test tab
3. **Check Permissions**: Verify retrieve rights with PACS admin
4. **Check Firewall**: Ensure incoming C-STORE not blocked
5. **Check Disk Space**: Ensure enough space in output directory

### Slow Downloads

1. **Network Bandwidth**: Check network speed
2. **PACS Performance**: PACS might be busy
3. **Disk I/O**: Check disk write speed
4. **Transfer Syntax**: Some compressions slower than others

### Partial Downloads

1. **Check Logs**: Look for C-STORE failures
2. **Network Stability**: Ensure stable connection
3. **Timeout Settings**: Increase timeout if network slow
4. **Storage Space**: Verify disk space during download

---

## Security Considerations

### Network Security

1. **Use TLS**: Enable TLS for encrypted transfer (future feature)
2. **Firewall Rules**: Only allow specific PACS IPs
3. **VPN**: Use VPN for remote PACS access
4. **Port Security**: Don't expose ports to internet

### Data Security

1. **Encrypt Storage**: Use encrypted filesystem
2. **Access Control**: Restrict directory permissions
3. **Audit Logging**: Log all downloads
4. **Auto-Delete**: Consider auto-deleting after viewing

---

## Status Codes

### C-GET Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0x0000 | Success | ✅ Download complete |
| 0xFF00 | Pending | ⏳ Files transferring |
| 0xA701 | Out of resources | 🔄 Retry later |
| 0xA702 | Unable to calculate matches | ❌ Invalid Study UID |
| 0xA900 | Identifier doesn't match | ❌ Wrong SOP Class |
| 0xC000 | Unable to process | ❌ PACS error |
| 0xFE00 | Cancelled | ⛔ User cancelled |

### C-MOVE Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0x0000 | Success | ✅ Move complete |
| 0xFF00 | Pending | ⏳ Files moving |
| 0xA702 | Unable to calculate matches | ❌ Invalid Study UID |
| 0xA801 | Move destination unknown | ❌ Configure destination in PACS |
| 0xA900 | Identifier doesn't match | ❌ Wrong SOP Class |
| 0xC000 | Unable to process | ❌ PACS error |

---

## Future Enhancements

### Planned Features

1. **Series-level C-GET**: Download specific series
2. **Image-level C-GET**: Download specific instances
3. **Resume Downloads**: Continue interrupted downloads
4. **Compression Selection**: Choose transfer syntax
5. **Concurrent Downloads**: Parallel study downloads
6. **C-MOVE GUI**: C-MOVE support in GUI
7. **TLS Support**: Encrypted transfers
8. **Progress Visualization**: Graphical progress bars
9. **Download Queue**: Queue multiple studies
10. **Automatic Organization**: Organize by patient/study/series

---

## Quick Reference

### C-GET Study
```python
success, count, msg = handler.c_get_study(
    server="192.168.1.100",
    port=104,
    calling_ae="DCMCREATOR",
    called_ae="PACS_SCP",
    study_uid="1.2.840...",
    output_dir="./downloads"
)
```

### C-MOVE Study
```python
success, count, msg = handler.c_move_study(
    server="192.168.1.100",
    port=104,
    calling_ae="DCMCREATOR",
    called_ae="PACS_SCP",
    study_uid="1.2.840...",
    move_destination="WORKSTATION_AE"
)
```

---

**Status:** ✅ Implemented in v0.8.2  
**Last Updated:** 2026-02-20  
**See Also:** 
- [`QUERY_RETRIEVE_GUIDE.md`](QUERY_RETRIEVE_GUIDE.md) - Complete Query/Retrieve guide
- [`CFIND_TROUBLESHOOTING.md`](CFIND_TROUBLESHOOTING.md) - C-FIND troubleshooting
