# Random DICOM Generator & Test Tools

## Overview

DICOM Creator now includes powerful tools for generating random test DICOM files and testing transmission functionality. Perfect for testing, demonstration, and stress testing DICOM servers.

## Features

### 1. Random DICOM Generator ?

Generate realistic test DICOM files with:
- Random patient data
- Configurable image sizes
- Various DICOM modalities
- Synthetic pixel data
- Complete DICOM metadata

**Use Cases:**
- Create test data without real medical images
- Bulk testing of DICOM servers
- Performance testing
- Demonstration purposes
- Training and tutorials

### 2. Batch Generation ??

Generate multiple DICOMs at once:
- Specify number of files
- Control file size per DICOM
- Randomized or template patient data
- Batch save to directory

### 3. Connection Testing ?

Test DICOM server connectivity:
- TCP connection validation
- Latency measurement
- Port reachability testing
- Pre-transmission verification

### 4. Bulk Transmission ??

Send all generated files to remote server:
- Load generated DICOMs
- Send to configured server
- Track transmission progress
- Generate test reports

---

## How to Use

### Generate Test DICOMs

**Step 1: Open Test/Generate Tab**
1. Click "Test/Generate" tab in application
2. Specify generation parameters

**Step 2: Configure Generator**
```
Count:            10        (number of files to generate)
Size/File (MB):   1.0       (each file ~1MB)
Output Dir:       [Browse]  (where to save files)
```

**Step 3: Generate**
Click one of:
- **"Generate DICOMs"** - Just create files
- **"Generate & Send"** - Create and immediately send to server

**Status window shows:**
```
Generating 10 test DICOMs (1.0MB each)...
? Generated 10 test DICOM files
  Location: C:\Users\...\test_dicoms
```

### Test Server Connection

**Before sending files:**
1. Click "Test Connection"
2. Application connects to server IP:port
3. Get instant feedback:

```
Testing connection...
  Connecting to 192.168.1.100:4321...
  ? Connection successful
```

**If connection fails:**
```
  ? Connection failed (errno 111)
```

### Send Generated Files

**Option 1: Generate & Send**
1. Fill generator parameters
2. Click "Generate & Send"
3. Files are created and sent automatically

**Option 2: Manual Send**
1. Generate DICOMs with "Generate DICOMs"
2. Click "Send All Generated"
3. Application loads files and sends them

---

## Configuration Options

### Generator Settings

| Option | Default | Range | Notes |
|--------|---------|-------|-------|
| Count | 10 | 1-1000 | Number of test files |
| Size/File (MB) | 1.0 | 0.5-100 | File size per DICOM |
| Output Dir | - | - | Required: where to save |

### Generated DICOM Properties

Each generated DICOM includes:
- **Patient Data:** Random name, ID, age, sex
- **Study Data:** Unique study/series UIDs
- **Image Data:** Synthetic 16-bit grayscale
- **Metadata:** Complete DICOM header

**Example Generated File:**
```
Patient Name:     John Smith
Patient ID:       TEST512345
Study UID:        1.2.3.4.5.6.7.8.9.0.1
Series UID:       1.2.3.4.5.6.7.8.9.0.2
Modality:         SC (Secondary Capture)
Image Size:       256 x 256 pixels
Pixel Data:       16-bit grayscale
```

---

## Use Cases

### Testing DICOM Server

```
Scenario: Verify DICOM server accepts transmissions

Steps:
1. Open Test/Generate tab
2. Set Count: 5, Size: 1.0 MB
3. Click "Test Connection"
   ?? Verify server is reachable
4. Click "Generate & Send"
   ?? Create 5 test files and send them
5. Check "View Results" for summary
```

### Performance Testing

```
Scenario: Test server performance with different file sizes

Test 1 - Small Files:
  Count: 100, Size: 0.1 MB
  
Test 2 - Large Files:
  Count: 10, Size: 10 MB
  
Test 3 - Mixed:
  Generate manually with different sizes
```

### Bulk Load Testing

```
Scenario: Stress test with many files

Configuration:
  Count: 500
  Size: 1.0 MB each
  Output Dir: C:\test_data
  
Process:
  1. Generate all 500 files (~500 MB total)
  2. Send to server
  3. Monitor transmission progress
  4. View results and statistics
```

---

## Generated Data Quality

### Patient Data
Random but realistic:
- Real-looking names (first + last)
- Valid patient IDs
- Believable ages (18-90)
- Random birth dates
- Height/weight ranges

### Medical Data
Proper DICOM format:
- Valid UIDs (generated per DICOM standard)
- Proper DICOM tags and values
- Standard modalities (CR, DX, CT, MR, XC, SC)
- Valid pixel data (16-bit grayscale)
- Complete metadata headers

### Images
Synthetic but realistic:
- Random grayscale pixel data
- Configurable dimensions (256x256 default, up to 4096x4096)
- 16-bit depth (medical standard)
- Size scales with dimensions

---

## Advanced Features

### File Size Control

Files are generated to approximately requested size:

**Example:**
```
Requested: 5 MB per file
Generated: ~256 x 256 pixel images scaled to fit

Formula: pixels_needed = (size_mb * 1024 * 1024) / 2
Dimensions: sqrt(pixels_needed)
Result: ~1826 x 1826 pixels for 5 MB
```

### Batch Processing

Generate many files efficiently:
- Sequential generation
- Multi-file save
- Progress tracking
- Error recovery

### Output Organization

All files saved to specified directory:
```
C:\test_data\
??? test_dicom_0001.dcm
??? test_dicom_0002.dcm
??? test_dicom_0003.dcm
??? ... (up to 1000 files)
```

---

## Troubleshooting

### Generation Fails

**Problem:** "pydicom not available"
- **Solution:** Install pydicom: `pip install pydicom`

**Problem:** "No output directory selected"
- **Solution:** Click "Browse" and select output folder

### Connection Test Fails

**Problem:** "Connection failed (errno 111)"
- **Solution:** 
  1. Check server is running
  2. Verify IP address and port
  3. Check firewall allows connection
  4. Try connecting to localhost:4321 first

**Problem:** "Connection timeout"
- **Solution:**
  1. Check network connectivity
  2. Increase timeout (contact admin)
  3. Verify server port is correct

### Transmission Issues

**Problem:** "Send fails after generation"
- **Solution:**
  1. Test connection first
  2. Check server has space
  3. Verify AE titles match server
  4. Check file permissions

---

## Performance Notes

### Generation Speed

| File Count | File Size | Approx. Time | RAM Used |
|-----------|-----------|-------------|----------|
| 10 | 1 MB | 5 seconds | 150 MB |
| 50 | 1 MB | 25 seconds | 200 MB |
| 100 | 1 MB | 50 seconds | 250 MB |
| 500 | 1 MB | 4 minutes | 400 MB |
| 1000 | 1 MB | 8 minutes | 500 MB |

### Transmission Speed

| File Size | Network | Approx. Time per File | Throughput |
|-----------|---------|----------------------|-----------|
| 1 MB | LAN | 1-2 seconds | 0.5-1 MB/s |
| 5 MB | LAN | 2-5 seconds | 1-2 MB/s |
| 10 MB | LAN | 5-10 seconds | 1-2 MB/s |
| 1 MB | WAN | 2-5 seconds | 0.2-0.5 MB/s |

---

## API Reference

### RandomDicomGenerator

```python
from src.random_dicom import RandomDicomGenerator

# Create generator
gen = RandomDicomGenerator(logger=my_logger)

# Generate single DICOM
ds = gen.generate_single(
    filename="test.dcm",
    patient_name="John Doe",
    width=256,
    height=256
)

# Generate batch
dicoms = gen.generate_batch(
    count=10,
    output_dir="./test_data",
    width=512,
    height=512,
    randomize_patient=True
)

# Generate with size
dicoms = gen.generate_with_sizes(
    count=5,
    size_mb=2.0,
    output_dir="./test_data"
)
```

### TestRunner

```python
from src.test_runner import TestRunner

# Create runner
runner = TestRunner(logger=my_logger)

# Start test
runner.start_test("Transmission Test", "Send 50 files")

# Record results
runner.add_file_result("file1.dcm", True, bytes_sent=1000000, time_taken=1.5)
runner.add_file_result("file2.dcm", False, error="Connection timeout")

# End test
runner.end_test("PASSED")

# Get report
print(runner.get_test_report())
print(runner.get_all_tests_summary())

# Export results
runner.export_results("test_results.txt")
```

---

## Tips & Best Practices

? **Test Before Bulk Send**
- Always test connection first
- Start with small batch (5-10 files)
- Verify results before large transmission

? **Monitor Performance**
- Check transmission progress
- Note any failures
- Review results after completion

? **Use for Different Purposes**
- Demo: Small files (10 x 0.5 MB)
- Testing: Medium batch (50 x 1 MB)
- Stress test: Large batch (500+ x 1-5 MB)

?? **Avoid**
- Don't send random data to production PACS without testing
- Don't overwhelm server with simultaneous sends
- Don't keep old test data unnecessarily (clean up when done)

---

## Version History

### v0.3.1 (Current)
- ? Random DICOM Generator
- ? Batch generation support
- ? Connection testing
- ? Test/Generate tab

### v0.3.0
- Server Presets feature
- Image loading bug fix

---

## Future Enhancements

Potential additions:
- [ ] Stress testing mode (rapid-fire sends)
- [ ] Performance benchmarking
- [ ] Test report generation
- [ ] Automated test suites
- [ ] C-ECHO testing
- [ ] Server load monitoring
- [ ] Parallel transmission threads
- [ ] Transmission history tracking

---

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in Status window
3. Test connection before transmission
4. Check server logs
5. Consult administrator if needed

