# Server Presets - Quick Start Guide

## What is Server Presets?

Save and quickly load your frequently used DICOM server configurations. No more typing the same server address, port, and AE titles every time!

## How to Use

### 1. Save Your First Preset

1. Go to **Remote** tab
2. Fill in your server details:
   - **Server:** Your DICOM server IP or hostname
   - **Port:** Server port (e.g., 4321)
   - **Calling AE Title:** Your application's AE title (e.g., DCMCREATOR)
   - **Called AE Title:** The server's AE title (e.g., PACS01)
3. Enter a name in the **Preset:** field (e.g., "Hospital PACS")
4. Click **Save Current**
5. Done! Your preset is saved.

### 2. Load a Preset

**Quick Method:**
1. Click the **Preset:** dropdown
2. Select your saved preset
3. Configuration auto-loads! ?

**Manual Method:**
1. Click the **Preset:** dropdown and select a preset
2. Click **Load**
3. Server configuration updates

### 3. Manage Presets

**Delete a Preset:**
1. Click the **Preset:** dropdown and select a preset
2. Click **Delete**
3. Confirm deletion
4. Preset is removed

## Example Presets

### Hospital PACS
- Server: 192.168.1.100
- Port: 4321
- Calling AE: DCMCREATOR
- Called AE: PACS01

### Remote Clinic
- Server: clinic.example.com
- Port: 11112
- Calling AE: DCMCREATOR
- Called AE: REMOTE-SCP

### Research Center
- Server: research.university.edu
- Port: 5000
- Calling AE: DCMCREATOR
- Called AE: RESEARCH-PACS

## Tips

? **Use descriptive names** for your presets (e.g., "MainHospital" instead of "Server1")

? **Save presets for servers you use regularly** to speed up DICOM transmission

? **Presets are stored locally** on your computer at `~/.dcmcreator/server_presets.json`

? **You can have unlimited presets** - organize by department, hospital, or use case

?? **Presets are not encrypted** - store sensitive information carefully

## Where Are My Presets?

**Windows:** `C:\Users\[YourUsername]\.dcmcreator\server_presets.json`

**macOS:** `/Users/[YourUsername]/.dcmcreator/server_presets.json`

**Linux:** `/home/[YourUsername]/.dcmcreator/server_presets.json`

You can edit this file directly if needed (JSON format).

## Common Questions

**Q: Can I have multiple presets?**
A: Yes! Save as many as you need. The dropdown shows all saved presets.

**Q: What happens if I overwrite a preset name?**
A: The old preset is replaced with the new configuration.

**Q: How do I backup my presets?**
A: Copy the `server_presets.json` file to a backup location.

**Q: Can I move presets to another computer?**
A: Yes, copy the `server_presets.json` file to `~/.dcmcreator/` on the other computer.

**Q: Do I need to restart the app to see new presets?**
A: No, click "Save Current" and the preset immediately appears in the dropdown.

**Q: Can I export presets as a file?**
A: Currently, you can copy the `server_presets.json` file directly. Future versions may include import/export features.

## Need Help?

If you encounter any issues:

1. Check that you've filled in all required server fields
2. Ensure the server address and port are correct
3. Verify your AE titles match your DICOM server configuration
4. Check the Messages area in the Remote tab for error details
5. See `SERVER_PRESETS.md` for detailed documentation

