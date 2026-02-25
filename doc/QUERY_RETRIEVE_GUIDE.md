# DICOM Query/Retrieve (C-FIND) Guide

## Overview

The **Query PACS** feature enables you to search for patients, studies, series, and images on remote PACS servers using the DICOM C-FIND protocol.

## Quick Start

### 1. Access Query PACS Tab

**Three ways to access:**
- Click the **"Query PACS"** tab in the main window
- Menu: **Remote → Query PACS (C-FIND)**
- Keyboard: **Ctrl+Q**

### 2. Configure PACS Server

```
Server: pacs.hospital.local
Port: 104
Calling AE: DCMCREATOR
Called AE: PACS_SCP
```

**Quick Tip:** Use the **"Copy from Remote Tab"** button to reuse your C-STORE server settings.

### 3. Build Your Search Query

#### Query Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **PATIENT** | Search for patients | Find all studies for a patient |
| **STUDY** | Search for studies | Most common - find studies by date/modality |
| **SERIES** | Search for series | Find specific series within a study |
| **IMAGE** | Search for instances | Find individual DICOM files |

#### Search Fields

**Patient Filters:**
- Patient Name (supports wildcards: `DOE*` or `*JOHN*`)
- Patient ID

**Study Filters:**
- Study Date From/To (format: YYYYMMDD)
- Study Description
- Accession Number
- Modality (CT, MR, US, etc.)

### 4. Execute Query

Click **"Query PACS"** → Results appear in the tree view below

---

## Search Examples

### Example 1: Find All CT Studies from January 2024

```
Query Level: STUDY
Patient Name: [leave empty]
Patient ID: [leave empty]
Study Date From: 20240101
Study Date To: 20240131
Modality: CT
```

### Example 2: Find Studies for Specific Patient

```
Query Level: STUDY
Patient Name: SMITH^JOHN
Patient ID: [or use ID: 12345]
Study Date From: [leave empty for all dates]
```

### Example 3: Find Series in a Specific Study

```
Query Level: SERIES
Patient Name: [leave empty]
Study Instance UID: [paste UID from previous search]
```

### Example 4: Search by Accession Number

```
Query Level: STUDY
Accession Number: ACC123456
```

---

## Wildcard Matching

DICOM C-FIND supports wildcards in text fields:

| Pattern | Description | Example |
|---------|-------------|---------|
| `*` | Zero or more characters | `SMITH*` matches SMITH, SMITHSON |
| `?` | Single character | `SMI?H` matches SMITH, SMIAH |
| `DOE*` | Starts with DOE | Finds DOE, DOESON |
| `*JOHN*` | Contains JOHN | Finds JOHNSON, JOHN, JOHNNY |

---

## Understanding Results

### Result Columns

| Column | Description |
|--------|-------------|
| **Level** | Query level (PATIENT/STUDY/SERIES/IMAGE) |
| **Patient ID** | Patient identifier |
| **Patient Name** | Patient name (LASTNAME^FIRSTNAME) |
| **Study Date** | Study date (YYYYMMDD) |
| **Study Description** | Study description/procedure |
| **Modality** | Imaging modality (CT, MR, etc.) |
| **Accession #** | Order/accession number |

### Next Steps (Coming Soon)

- **Double-click** a result to download the study (C-GET)
- **Right-click** for context menu options
- **Load into app** for editing metadata

---

## Date Range Formats

### Supported Formats

```
Single Date:     20240115
Date Range:      20240101-20240131
From Date:       20240101-
To Date:         -20240131
```

---

## Common Use Cases

### 1. Daily Quality Check
```
Query Level: STUDY
Study Date From: [today's date]
Study Date To: [today's date]
```

### 2. Find Lost Study by Accession
```
Query Level: STUDY
Accession Number: [from order system]
```

### 3. Patient History Lookup
```
Query Level: STUDY
Patient ID: [from EMR]
```

### 4. Modality Performance Review
```
Query Level: STUDY
Modality: CT
Study Date From: [last week]
Study Date To: [yesterday]
```

---

## Troubleshooting

### "Association Failed"

**Cause:** Cannot connect to PACS server or DICOM association rejected

**Solutions:**
1. **TCP Connection Failed**: 
   - Verify server IP address is correct
   - Check port number (typically 104 or 11112)
   - Test with Connection Test tab first
   - Check firewall settings (allow port)

2. **DICOM Association Rejected**:
   - Verify Calling AE Title is registered on PACS
   - Confirm Called AE Title matches PACS configuration
   - Check PACS supports C-FIND (Query/Retrieve SCP)
   - Review PACS logs for rejection reason

3. **Network Issues**:
   - Ping server to verify network connectivity
   - Use `telnet <server> <port>` to test port accessibility
   - Check VPN connection if accessing remote PACS
   - Verify no proxy blocking connection

### "Query Status: 0xC808" (Unable to Process)

**⚠️ Most Common Error - Invalid Query Attributes**

**Cause:** PACS couldn't process query due to invalid or unsupported search criteria

**Quick Fixes:**
1. **Simplify Query**: Start with just Patient ID or Accession Number
2. **Check Date Format**: Use `YYYYMMDD` (not `2024-02-20` or `02/20/2024`)
3. **Use STUDY Level**: Change Query Level from SERIES/IMAGE to STUDY
4. **Remove Optional Fields**: Clear Study Description and other optional fields

**Detailed Guide:** See [`CFIND_TROUBLESHOOTING.md`](CFIND_TROUBLESHOOTING.md) for comprehensive 0xC808 troubleshooting

### "No Results Found"

**Cause:** Search criteria too restrictive or data not on PACS

**Solutions:**
1. Broaden search (remove some filters)
2. Check date format (YYYYMMDD)
3. Try wildcards: `*SMITH*` instead of `SMITH`
4. Verify data exists on target PACS

### "Query Timeout"

**Cause:** PACS server slow to respond

**Solutions:**
1. Narrow search criteria
2. Increase timeout (future enhancement)
3. Use more specific filters (Patient ID, Accession #)

---

## Advanced Topics

### Query Model: StudyRoot vs PatientRoot

**StudyRoot (Default):**
- Recommended for most PACS systems
- Organizes by Study → Series → Image hierarchy

**PatientRoot:**
- Organizes by Patient → Study → Series → Image
- Required by some older PACS systems

*Current implementation uses **StudyRoot** by default*

### Performance Tips

1. **Use specific filters**: Patient ID > Name wildcards
2. **Limit date ranges**: Week or month, not years
3. **Query at appropriate level**: STUDY for most searches
4. **Use Accession Number**: Fastest query method

---

## Integration with DICOM Creator

### Current Integration

- Query results display patient/study metadata
- Server settings shareable with Remote tab
- Results logged for audit trail

### Future Integration (Roadmap)

- **C-GET Download**: Double-click to download studies
- **Auto-populate forms**: Load metadata into Patient/Study tabs
- **Bulk download**: Select multiple studies
- **Export results**: Save query results to CSV/JSON

---

## Security Considerations

### Data Privacy

- C-FIND returns metadata only (no pixel data)
- PHI (Protected Health Information) is transmitted
- Use TLS for encrypted queries (future enhancement)

### Access Control

- Queries are logged with timestamp
- PACS enforces AE title restrictions
- Configure AE titles in PACS admin console

---

## Technical Details

### DICOM Tags Queried

#### Study Level Query
```
(0010,0020) Patient ID
(0010,0010) Patient Name
(0010,0030) Patient Birth Date
(0010,0040) Patient Sex
(0020,000D) Study Instance UID
(0008,0020) Study Date
(0008,0030) Study Time
(0008,1030) Study Description
(0008,0050) Accession Number
(0008,0060) Modality
```

#### Series Level Query (Additional)
```
(0020,000E) Series Instance UID
(0020,0011) Series Number
(0008,103E) Series Description
(0020,1209) Number of Series Related Instances
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+Q** | Open Query PACS tab |
| **Enter** | Execute query (when in form field) |
| **Escape** | Clear form |

---

## FAQ

**Q: Can I download studies from query results?**  
A: Not yet. C-GET download functionality is planned for the next phase.

**Q: Does this work with all PACS systems?**  
A: Yes, any DICOM-compliant PACS that supports C-FIND should work.

**Q: Can I save query results?**  
A: Currently results are temporary. Export functionality coming soon.

**Q: What's the difference between Query PACS and Load DICOM?**  
A: Query PACS searches *remote* PACS servers. Load DICOM loads *local* files.

**Q: Can I query multiple PACS servers?**  
A: Run separate queries for each PACS. Batch querying planned for future.

---

## Related Features

- **Remote Tab**: Send DICOM (C-STORE) to PACS
- **Load DICOM Tab**: Load local DICOM files
- **Connection Test**: Test PACS connectivity
- **Server Presets**: Save frequently-used PACS servers

---

## Support & Feedback

For issues or feature requests:
- Check logs in `dicomcreator.log`
- Enable debug logging for detailed diagnostics
- Report issues on GitHub

---

## Version History

### v0.8.0 (Current)
- ✅ C-FIND implementation
- ✅ Study/Series/Patient/Image level queries
- ✅ Wildcard matching support
- ✅ Date range queries
- ✅ Results tree view
- 🔄 C-GET download (coming soon)

### Future Enhancements
- C-MOVE support
- C-GET direct download
- Multi-PACS query
- Query result export
- TLS encryption
- Advanced filters
