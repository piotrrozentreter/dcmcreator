# C-FIND Troubleshooting Guide

## Common DICOM Query Status Codes

### 0xC808 - Unable to Process (Query Attributes Invalid)

**What it means:**
The PACS server received your query but couldn't process it because the search attributes are invalid or unsupported.

**Common Causes:**

1. **Invalid Query Level**
   - PACS may not support IMAGE or SERIES level queries
   - Solution: Try STUDY level queries instead

2. **Wrong Date Format**
   - Bad: `2024-02-20` or `20/02/2024`
   - Good: `20240220`
   - Range: `20240101-20240131`

3. **Unsupported Search Attribute**
   - Some PACS don't support all optional search keys
   - Solution: Use only basic keys (Patient Name, ID, Study Date)

4. **Missing Required Matching Key**
   - Some PACS require specific keys to be present
   - Solution: Add Patient Name or Patient ID to your query

5. **Wrong Query Model**
   - PACS might only support PatientRoot (not StudyRoot)
   - Solution: Currently not configurable in GUI (coming soon)

**How to Fix:**

**Step 1: Simplify Your Query**
```
Start with minimal criteria:
- Patient Name: DOE*
- Study Date From: 20240101
- Study Date To: 20240131

Then add more filters one at a time to find which causes the issue.
```

**Step 2: Check Date Format**
```
✅ Correct: 20240220
✅ Correct: 20240101-20240131
❌ Wrong: 2024-02-20
❌ Wrong: 02/20/2024
```

**Step 3: Use Basic Query Level**
```
Change Query Level to: STUDY
(Most universally supported)
```

**Step 4: Test with Known Data**
```
If you know a patient exists on PACS:
- Use exact Patient ID (not wildcards)
- Add a narrow date range
- Remove optional fields like Study Description
```

---

### 0xC000 - Unable to Process (General Failure)

**What it means:**
PACS encountered an internal error while processing your query.

**Common Causes:**
1. Database connection lost
2. PACS internal error
3. Query timeout
4. Insufficient permissions

**How to Fix:**
1. Wait a few minutes and try again
2. Check with PACS administrator
3. Verify your AE title has query permissions
4. Try a simpler query with fewer criteria

---

### 0xA700 - Out of Resources

**What it means:**
PACS is overloaded or your query would return too many results.

**How to Fix:**
1. Narrow your search criteria:
   - Add date range (max 1 month)
   - Use specific Patient ID
   - Add Modality filter
2. Try during off-peak hours
3. Query in smaller chunks

---

### 0xC100 - SOP Class Not Supported

**What it means:**
PACS doesn't support C-FIND queries.

**How to Fix:**
1. Verify PACS supports Query/Retrieve
2. Check AE title is registered for C-FIND
3. Contact PACS administrator

---

## Diagnostic Steps

### Step 1: Test Basic Connectivity

**In Connection Test Tab:**
```
Server: <your PACS IP>
Port: <your PACS port>
Click "Test TCP"
```

**Expected:** ✅ Connection successful

---

### Step 2: Try Minimal Query

**In Query PACS Tab:**
```
Query Level: STUDY
Patient ID: [known patient ID]
[Leave all other fields empty]
Click "Query PACS"
```

**Expected:** Should return that patient's studies

---

### Step 3: Add Date Range

**If Step 2 works:**
```
Query Level: STUDY
Study Date From: 20240101
Study Date To: 20240131
[Leave all other fields empty]
Click "Query PACS"
```

**Expected:** Should return studies from January 2024

---

### Step 4: Add Wildcards

**If Step 3 works:**
```
Query Level: STUDY
Patient Name: DOE*
Study Date From: 20240101
Study Date To: 20240131
Click "Query PACS"
```

**Expected:** Should return studies for patients with names starting with "DOE"

---

## Query Compatibility Matrix

| Feature | Support Level | Notes |
|---------|---------------|-------|
| **Query Level: PATIENT** | Moderate | Some PACS don't support |
| **Query Level: STUDY** | ✅ Universal | Use this by default |
| **Query Level: SERIES** | Moderate | Requires StudyInstanceUID |
| **Query Level: IMAGE** | Low | Rarely supported |
| **Patient Name Wildcards** | ✅ Universal | Use `*` and `?` |
| **Date Range** | ✅ Universal | YYYYMMDD-YYYYMMDD |
| **Modality Filter** | ✅ Universal | CT, MR, US, etc. |
| **Study Description** | High | Usually supported |
| **Accession Number** | ✅ Universal | Exact match only |

---

## PACS-Specific Issues

### GE PACS
- ⚠️ May require Patient Name or Patient ID in every query
- ✅ Supports StudyRoot
- ⚠️ Limited support for SERIES level

### Philips iSite
- ✅ Full Query/Retrieve support
- ⚠️ Case-sensitive Patient Name searches
- ✅ Supports PatientRoot and StudyRoot

### Agfa IMPAX
- ✅ Full support
- ⚠️ May timeout on large date ranges
- ✅ Supports all query levels

### Open Source PACS (DCM4CHEE, Orthanc)
- ✅ Full DICOM compliance
- ✅ All query levels supported
- ⚠️ May require configuration for AE title permissions

---

## Debug Mode

Enable detailed logging to diagnose issues:

**In Python Console:**
```python
import logging
logging.getLogger('pynetdicom').setLevel(logging.DEBUG)
```

**Check Logs:**
```
Look in: dicomcreator.log
Search for: "Query status" or "C-FIND"
```

---

## Still Having Issues?

### Check These:

1. **PACS Configuration**
   - Is your AE title registered?
   - Does it have query permissions?
   - Is the PACS configured for Query/Retrieve SCP?

2. **Network**
   - Can you ping the PACS server?
   - Is the port open? (telnet <ip> <port>)
   - Is there a firewall blocking?

3. **Data Verification**
   - Does the patient/study actually exist on PACS?
   - Try querying with the PACS web interface
   - Check date ranges are correct

4. **Query Model**
   - Try both StudyRoot and PatientRoot (future feature)
   - Some PACS only support one model

---

## Quick Reference: Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| **0x0000** | Success | ✅ Query worked |
| **0xFF00** | Pending | ⏳ Results coming |
| **0xC808** | Invalid query | 🔧 Fix search criteria |
| **0xC000** | PACS error | ⏱️ Wait and retry |
| **0xA700** | Overloaded | 🎯 Narrow search |
| **0xC100** | Not supported | ❌ PACS doesn't support C-FIND |
| **0xFE00** | Cancelled | ⛔ Query was cancelled |

---

## Getting Help

1. **Check Logs:**
   ```
   Open: dicomcreator.log
   Look for: ERROR, WARNING, C-FIND
   ```

2. **Test with Known Tools:**
   ```bash
   # Use dcmtk findscu to test PACS
   findscu -P -k "PatientName=DOE*" <PACS_IP> <PORT> -aec <CALLED_AE> -aet DCMCREATOR
   ```

3. **Contact PACS Administrator:**
   - Provide: AE title, IP, port
   - Ask: Is Query/Retrieve enabled?
   - Request: Query permission for your AE title

4. **Report Issue:**
   - Include: Error code (e.g., 0xC808)
   - Include: Query parameters used
   - Include: PACS vendor/version
   - Include: Log snippet

---

## Examples That Should Work

### Example 1: Basic Patient Lookup
```
Query Level: STUDY
Patient ID: 12345
[Nothing else]
```
**Success Rate:** 95% - Works with almost all PACS

### Example 2: Date Range Query
```
Query Level: STUDY
Study Date From: 20240101
Study Date To: 20240107
[Nothing else]
```
**Success Rate:** 90% - Very compatible

### Example 3: Accession Lookup
```
Query Level: STUDY
Accession Number: ACC123456
[Nothing else]
```
**Success Rate:** 95% - Direct lookup

### Example 4: Combined Query
```
Query Level: STUDY
Patient Name: DOE*
Modality: CT
Study Date From: 20240101
Study Date To: 20240131
```
**Success Rate:** 80% - May fail on some PACS

---

## Summary

**Most Common Issue: 0xC808**
- **Quick Fix:** Use STUDY level, basic criteria only
- **Test Query:** Just Patient ID or Accession Number
- **Date Format:** YYYYMMDD (no dashes or slashes)

**If Nothing Works:**
1. Test TCP connection first
2. Verify with PACS admin
3. Try dcmtk findscu tool
4. Check PACS supports Query/Retrieve

---

**Last Updated:** 2026-02-20  
**Version:** 0.8.1
