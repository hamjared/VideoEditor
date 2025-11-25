# Simple Video Editor

A Python-based video editor with a PyQt5 GUI for cutting multiple clips from video files.

## Features

- Load video files (MP4, AVI, MKV, MOV, WMV, FLV)
- Define multiple clips using timestamp format (HH:MM:SS.mmm)
- Preview clip information before exporting
- Export all clips at once with progress tracking
- Re-encode clips for maximum compatibility

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

**Important Notes:**
- This project uses **MoviePy v2.0+** with the latest API
- MoviePy requires ffmpeg to be installed on your system
- Python 3.7+ is required

### Installing FFmpeg:

**Windows:**
- Download from https://ffmpeg.org/download.html
- Add ffmpeg to your PATH

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## Usage

### Running the GUI:

```bash
python main.py
```

### Using the GUI:

1. **Load Video**: Click "Load Video" to select your video file
2. **Add Clips** (two ways):

   **Manual Entry:**
   - Enter a name for your clip
   - Enter start time (e.g., 00:01:30.500)
   - Enter end time (e.g., 00:02:45.000)
   - Click "Add Clip"

   **Import from CSV/Excel:**
   - Click "Import CSV/Excel" button
   - Select a CSV or Excel file with columns: "clip name", "start time", "end time"
   - See `clips_template.csv` for an example format

3. **Manage Clips**:
   - Select clips in the table to remove them
   - Use "Clear All" to remove all clips
4. **Export**:
   - Click "Choose Folder" to select output directory
   - Click "Export All Clips" to export all defined clips

### Using the Backend Programmatically:

```python
from video_editor import VideoEditor

# Create editor and load video
editor = VideoEditor("my_video.mp4")

# Add clips manually
editor.add_clip("intro", "00:00:00", "00:00:15")
editor.add_clip("main_scene", "00:01:30", "00:02:45")
editor.add_clip("outro", "00:05:00", "00:05:20")

# Or import clips from CSV/Excel
stats = editor.import_clips_from_file("clips.csv")
print(f"Imported {stats['success']} clips, {stats['failed']} failed")

# Get clip information
clips = editor.get_clips_info()
print(clips)

# Export all clips
editor.export_all_clips("output/")

# Or export a single clip
editor.export_clip("intro", "output/intro.mp4")

# Clean up
editor.close()
```

### CSV/Excel Import Format

Create a CSV or Excel file with these columns (case-insensitive):

| clip name | start time | end time |
|-----------|------------|----------|
| intro | 00:00:00 | 00:00:15 |
| main_scene | 00:01:30 | 00:02:45 |
| outro | 00:05:00 | 00:05:20 |

**Supported column names:**
- Name: `clip name`, `name`, or `clipname`
- Start: `start time`, `start`, or `starttime`
- End: `end time`, `end`, or `endtime`

See `clips_template.csv` for a ready-to-use template.

## Building Standalone Executable

Want to create a .exe file that runs without Python? See **[PACKAGING.md](PACKAGING.md)** for detailed instructions.

**Quick Start:**
```bash
# Windows
build.bat

# Linux/Mac
chmod +x build.sh
./build.sh
```

The executable will be created in the `dist/` folder.

## Project Structure

```
videoEditor/
├── video_editor.py       # Backend video editing logic
├── gui.py               # PyQt5 GUI implementation
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── clips_template.csv   # CSV template for importing clips
├── build.spec           # PyInstaller configuration
├── build.bat            # Windows build script
├── build.sh             # Linux/Mac build script
├── PACKAGING.md         # Detailed packaging guide
└── README.md            # This file
```

## Timestamp Format

Timestamps must be in the format: `HH:MM:SS` or `HH:MM:SS.mmm`

Examples:
- `00:00:00` - Start of video
- `00:01:30` - 1 minute 30 seconds
- `00:01:30.500` - 1 minute 30 seconds and 500 milliseconds

## Notes

- Exports use H.264 video codec (libx264) and AAC audio codec for maximum compatibility
- All clips are re-encoded during export
- Progress is shown during export operations
- The GUI runs export operations in a background thread to prevent freezing

## License

This is a simple educational project. Use freely as needed.
