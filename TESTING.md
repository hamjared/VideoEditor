# Testing the Executable on Fresh Windows Installation

This guide explains how to test your VideoEditor.exe on a clean Windows system to ensure it works without Python or dependencies installed.

## Option 1: Windows Sandbox (Recommended - Built into Windows 10/11 Pro)

**Pros:** Fast, free, built-in, resets automatically after closing
**Cons:** Requires Windows 10/11 Pro/Enterprise/Education

### Enable Windows Sandbox:

1. Open PowerShell as Administrator and run:
```powershell
Enable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" -All
```

2. Or enable via GUI:
   - Open "Turn Windows features on or off"
   - Check "Windows Sandbox"
   - Restart computer

### Using Windows Sandbox:

1. **Build your executable:**
   ```bash
   build.bat
   ```

2. **Copy files to a test folder:**
   - Create a folder with:
     - `VideoEditor.exe` (from dist folder)
     - A sample video file for testing
     - Optional: `clips_template.csv` for testing import

3. **Launch Windows Sandbox**
   - Search "Windows Sandbox" in Start Menu
   - Opens a fresh Windows VM instantly

4. **Copy test folder into Sandbox:**
   - Drag and drop your test folder into the Sandbox window
   - Or copy to: `C:\Users\WDAGUtilityAccount\Desktop\`

5. **Test the executable:**
   - Navigate to your test folder in Sandbox
   - Double-click `VideoEditor.exe`
   - Test all features:
     - Load video
     - Add clips manually
     - Import from CSV
     - Export clips

6. **Check for issues:**
   - Missing DLL errors
   - Python/dependency errors
   - FFmpeg errors (expected - need to install FFmpeg separately)
   - GUI rendering issues

7. **Close Sandbox when done** (everything resets automatically)

### Installing FFmpeg in Sandbox (for complete testing):

```powershell
# Download FFmpeg in Sandbox browser
# Or copy ffmpeg.exe into the Sandbox along with VideoEditor.exe
```

---

## Option 2: VirtualBox (Free, Full Control)

**Pros:** Free, full control, can save VM state
**Cons:** Requires more setup, uses more disk space

### Setup VirtualBox:

1. **Download and install VirtualBox:**
   - https://www.virtualbox.org/

2. **Get a Windows ISO:**
   - Download Windows 10/11 ISO from Microsoft:
   - https://www.microsoft.com/software-download/windows11

3. **Create a new VM:**
   - Name: "VideoEditor Testing"
   - Type: Microsoft Windows
   - Version: Windows 10/11 (64-bit)
   - Memory: 4096 MB (4 GB)
   - Hard disk: 50 GB (VDI, dynamically allocated)

4. **Install Windows:**
   - Start VM and select the ISO
   - Follow Windows installation
   - You can skip activation for testing

5. **Set up Guest Additions** (optional but recommended):
   - Devices → Insert Guest Additions CD
   - Enables better graphics and shared folders

### Testing in VirtualBox:

1. **Transfer files to VM:**
   - Option A: Shared Folder
     - Devices → Shared Folders → Add folder
     - Access from VM at `\\vboxsvr\ShareName`

   - Option B: Drag and Drop
     - Devices → Drag and Drop → Bidirectional

   - Option C: Network/USB drive

2. **Run tests** (same as Sandbox instructions above)

3. **Take snapshots** to reset VM state:
   - Machine → Take Snapshot
   - Can revert to clean state anytime

---

## Option 3: VMware Workstation Player (Free for Personal Use)

**Pros:** Good performance, easier than VirtualBox
**Cons:** Requires registration

### Setup:

1. **Download VMware Workstation Player:**
   - https://www.vmware.com/products/workstation-player.html

2. **Create VM and install Windows** (similar to VirtualBox)

3. **Use VMware Tools for easy file sharing:**
   - Player → Manage → Install VMware Tools
   - Enable shared folders

---

## Option 4: Hyper-V (Windows 10/11 Pro Built-in)

**Pros:** Built into Windows Pro, good performance
**Cons:** Requires Pro/Enterprise, more complex than Sandbox

### Enable Hyper-V:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

### Create VM:
1. Open Hyper-V Manager
2. Quick Create → Choose Windows 10/11
3. Configure and test similar to VirtualBox

---

## Option 5: Online Windows VMs (Quick Testing)

**Pros:** No local setup needed
**Cons:** Limited time, internet connection required

### Browser-based Windows Testing:
- **BrowserStack** (paid, free trial): https://www.browserstack.com/
- **Azure Virtual Machines** (pay-as-you-go): https://azure.microsoft.com/

---

## Recommended Testing Workflow

### Quick Test (5 minutes):
**Use Windows Sandbox**
1. Build exe
2. Launch Sandbox
3. Copy exe + test video
4. Run and verify it launches
5. Close Sandbox

### Thorough Test (30 minutes):
**Use VirtualBox or VMware**
1. Build exe
2. Boot VM
3. Copy files
4. Test all features:
   - Video loading
   - Manual clip adding
   - CSV import
   - Export functionality
   - Error handling
5. Take VM snapshot for future testing

### Production Test (1 hour):
1. Use VirtualBox
2. Install FFmpeg properly
3. Test complete workflow end-to-end
4. Test with various video formats
5. Test with large CSV files
6. Check for memory leaks (long running)

---

## What to Test

### Basic Functionality:
- [ ] Executable launches without errors
- [ ] GUI renders correctly
- [ ] No missing DLL errors
- [ ] No Python/dependency errors

### With FFmpeg Installed:
- [ ] Load video file (MP4)
- [ ] Video info displays correctly
- [ ] Add clip manually
- [ ] Import clips from CSV
- [ ] Export single clip
- [ ] Export all clips
- [ ] Progress bar works

### Edge Cases:
- [ ] Invalid timestamp handling
- [ ] Invalid CSV format handling
- [ ] Missing output directory
- [ ] Very long video files
- [ ] Special characters in clip names

### Error Scenarios:
- [ ] Run without FFmpeg (should show clear error)
- [ ] Load corrupted video
- [ ] Load invalid file type
- [ ] Export to read-only directory

---

## Common Issues and Solutions

### Issue: "VCRUNTIME140.dll was not found"
**Solution:** Need Visual C++ Redistributable
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Note: This should be documented in distribution requirements

### Issue: FFmpeg not found
**Expected:** Users need to install FFmpeg separately
- Document this clearly in README

### Issue: Application won't start (no error message)
**Solution:** Run from command prompt to see errors:
```cmd
cd path\to\executable
VideoEditor.exe
```

### Issue: Slow startup
**Normal:** First launch extracts files to temp directory (10-30 seconds)

---

## Automated Testing Script

Create a test script to run in the VM:

```batch
@echo off
echo ========================================
echo VideoEditor Executable Test Script
echo ========================================
echo.

REM Test 1: Check if exe exists
if exist VideoEditor.exe (
    echo [PASS] VideoEditor.exe found
) else (
    echo [FAIL] VideoEditor.exe not found
    exit /b 1
)

REM Test 2: Try to run (will fail without video, but checks if exe starts)
echo.
echo [TEST] Launching VideoEditor...
echo If GUI appears, test passed. Press Ctrl+C to continue.
start VideoEditor.exe

echo.
echo ========================================
echo Manual Testing Required:
echo 1. Did the application launch?
echo 2. Can you load a video?
echo 3. Can you add clips?
echo 4. Can you export?
echo ========================================
pause
```

---

## Best Practice: Testing Checklist

Before distributing your executable:

1. ✅ Build exe with `build.bat`
2. ✅ Test on development machine
3. ✅ Test in Windows Sandbox (clean Windows)
4. ✅ Test in VM with FFmpeg installed
5. ✅ Document FFmpeg requirement clearly
6. ✅ Create user guide with screenshots
7. ✅ Test on Windows 10 and Windows 11
8. ✅ Test with different video formats
9. ✅ Test CSV/Excel import feature
10. ✅ Verify no Python installation needed

---

## My Recommendation

**For quick testing:** Use **Windows Sandbox** (if you have Windows 10/11 Pro)
- Fastest setup (already built-in)
- Perfect for quick verification
- Resets automatically
- No disk space concerns

**For thorough testing:** Use **VirtualBox**
- Free and full-featured
- Can save VM states
- Good for repeated testing
- Can test on different Windows versions

**For CI/CD pipelines:** Consider cloud VMs like Azure or AWS for automated testing
