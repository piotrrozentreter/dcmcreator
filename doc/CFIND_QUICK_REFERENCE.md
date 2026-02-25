# C-FIND Quick Reference Card

## Access Query PACS

```
Tab: Query PACS
Menu: Remote → Query PACS (C-FIND)
Shortcut: Ctrl+Q
```

## Quick Query Templates

### Find Today's Studies
```
Level: STUDY
Study Date From: [today YYYYMMDD]
Study Date To: [today YYYYMMDD]
```

### Patient Lookup
```
Level: STUDY
Patient ID: [12345]
OR
Patient Name: SMITH*
```

### Accession Lookup
```
Level: STUDY
Accession Number: [ACC123456]
```

### Modality Filter
```
Level: STUDY
Modality: CT
Study Date From: [YYYYMMDD]
```

## Query Levels

| Level | Use For |
|-------|---------|
| PATIENT | All patient's studies |
| STUDY | Finding studies (most common) |
| SERIES | Series within studies |
| IMAGE | Individual instances |

## Wildcards

| Pattern | Matches |
|---------|---------|
| `SMITH*` | SMITH, SMITHSON |
| `*SMITH` | SMITH, GOLDSMITH |
| `*SMITH*` | SMITHSON, GOLDSMITH, SMITH |

## Date Formats

```
Single: 20240220
Range:  20240101-20240131
From:   20240101-
To:     -20240131
```

## Common Modalities

```
CT  - Computed Tomography
MR  - Magnetic Resonance
US  - Ultrasound
CR  - Computed Radiography
DX  - Digital Radiography
MG  - Mammography
NM  - Nuclear Medicine
PT  - Positron Emission Tomography
XA  - X-Ray Angiography
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Association failed | Check server/port/AE titles |
| No results | Broaden search, use wildcards |
| Timeout | Narrow criteria, use Patient ID |
| Module unavailable | `pip install pynetdicom` |

## Performance Tips

✓ Use Patient ID or Accession (fastest)  
✓ Limit date ranges to weeks/months  
✓ Query at STUDY level for most searches  
✓ Use specific wildcards (`SMITH*` not `*SMITH*`)  

✗ Avoid year-long date ranges  
✗ Avoid leading wildcards (`*SMITH`)  
✗ Don't query IMAGE level unnecessarily  

## Next Steps

1. Configure server settings
2. Copy from Remote tab (optional)
3. Fill search criteria
4. Click "Query PACS"
5. Double-click result (C-GET coming soon)

## Integration

- Server settings → Share with Remote tab
- Query results → Future: Download with C-GET
- Results → Future: Load into Patient/Study tabs

---

**DICOM Creator v0.8.0** | C-FIND Implementation | [Full Documentation](QUERY_RETRIEVE_GUIDE.md)
