"""
PyQt5 GUI for Video Editor
Provides a graphical interface for the video editor functionality
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QProgressBar, QGroupBox, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from video_editor import VideoEditor
from video_player.media_player_factory import MediaPlayerFactory


class ExportWorker(QThread):
    """Worker thread for exporting clips without blocking the GUI."""

    progress = pyqtSignal(int, int, str)  # current, total, clip_name
    finished = pyqtSignal(list)  # exported files
    error = pyqtSignal(str)  # error message

    def __init__(self, editor, output_dir):
        super().__init__()
        self.editor = editor
        self.output_dir = output_dir

    def run(self):
        """Run the export operation in a separate thread."""
        try:
            exported_files = self.editor.export_all_clips(
                self.output_dir,
                progress_callback=self.on_progress
            )
            self.finished.emit(exported_files)
        except Exception as e:
            self.error.emit(str(e))

    def on_progress(self, current, total, clip_name):
        """Callback for export progress."""
        self.progress.emit(current, total, clip_name)


class VideoEditorGUI(QMainWindow):
    """Main GUI window for the video editor."""

    def __init__(self):
        super().__init__()
        self.editor = VideoEditor()
        self.output_dir = None
        self.export_worker = None
        self.updating_table = False  # Flag to prevent recursive updates
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Simple Video Editor')
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left side - Video player
        left_layout = QVBoxLayout()

        # File section
        file_group = self.create_file_section()
        left_layout.addWidget(file_group)

        # Video player section
        player_group = self.create_player_section()
        left_layout.addWidget(player_group)

        # Video info section
        info_group = self.create_info_section()
        left_layout.addWidget(info_group)

        main_layout.addLayout(left_layout, 1)

        # Right side - Clip management
        right_layout = QVBoxLayout()

        # Add clip section
        add_clip_group = self.create_add_clip_section()
        right_layout.addWidget(add_clip_group)

        # Clips list section
        clips_group = self.create_clips_list_section()
        right_layout.addWidget(clips_group)

        # Export section
        export_group = self.create_export_section()
        right_layout.addWidget(export_group)

        main_layout.addLayout(right_layout, 1)

        # Status bar
        self.statusBar().showMessage('Ready')

    def create_file_section(self):
        """Create the file loading section."""
        group = QGroupBox("Video File")
        layout = QHBoxLayout()

        self.file_label = QLabel("No video loaded")
        self.file_label.setStyleSheet("padding: 5px;")

        load_btn = QPushButton("Load Video")
        load_btn.clicked.connect(self.load_video)
        load_btn.setFixedWidth(120)

        layout.addWidget(self.file_label)
        layout.addWidget(load_btn)

        group.setLayout(layout)
        return group

    def create_player_section(self):
        """Create the video player section."""
        group = QGroupBox("Video Player")
        layout = QVBoxLayout()

        # Create video player widget
        self.video_player = MediaPlayerFactory.create_player()

        if self.video_player:
            # Connect mark buttons to populate input fields
            self.video_player.mark_start_clicked.connect(self.on_mark_start)
            self.video_player.mark_end_clicked.connect(self.on_mark_end)
            layout.addWidget(self.video_player)
        else:
            # No player available
            no_player_label = QLabel(
                "No video player available.\n\n"
                "Install opencv-python for video preview:\n"
                "pip install opencv-python"
            )
            no_player_label.setStyleSheet("padding: 20px; color: #888;")
            no_player_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_player_label)

        group.setLayout(layout)
        return group

    def create_info_section(self):
        """Create the video information section."""
        group = QGroupBox("Video Information")
        layout = QVBoxLayout()

        self.info_label = QLabel("Load a video to see information")
        self.info_label.setStyleSheet("padding: 10px;")
        self.info_label.setWordWrap(True)

        layout.addWidget(self.info_label)

        group.setLayout(layout)
        return group

    def create_add_clip_section(self):
        """Create the add clip section."""
        group = QGroupBox("Add Clips")
        main_layout = QVBoxLayout()

        # Manual add clip row
        manual_layout = QHBoxLayout()

        # Name input
        manual_layout.addWidget(QLabel("Name:"))
        self.clip_name_input = QLineEdit()
        self.clip_name_input.setPlaceholderText("clip_name")
        self.clip_name_input.setFixedWidth(150)
        manual_layout.addWidget(self.clip_name_input)

        # Start time input
        manual_layout.addWidget(QLabel("Start:"))
        self.start_time_input = QLineEdit()
        self.start_time_input.setPlaceholderText("00:00:00.000")
        self.start_time_input.setFixedWidth(120)
        manual_layout.addWidget(self.start_time_input)

        # Duration input
        manual_layout.addWidget(QLabel("Duration:"))
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("30 or 1:30 or 0:01:30")
        self.duration_input.setFixedWidth(140)
        self.duration_input.textChanged.connect(self.on_duration_changed)
        manual_layout.addWidget(self.duration_input)

        # End time input
        manual_layout.addWidget(QLabel("End:"))
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("00:00:00.000")
        self.end_time_input.setFixedWidth(120)
        self.end_time_input.textChanged.connect(self.on_end_time_changed)
        manual_layout.addWidget(self.end_time_input)

        # Add button
        add_btn = QPushButton("Add Clip")
        add_btn.clicked.connect(self.add_clip)
        add_btn.setFixedWidth(100)
        manual_layout.addWidget(add_btn)

        manual_layout.addStretch()

        main_layout.addLayout(manual_layout)

        # Import from file row
        import_layout = QHBoxLayout()
        import_layout.addWidget(QLabel("Or import from file:"))

        import_btn = QPushButton("Import CSV/Excel")
        import_btn.clicked.connect(self.import_clips)
        import_btn.setFixedWidth(150)
        import_layout.addWidget(import_btn)

        import_layout.addStretch()
        main_layout.addLayout(import_layout)

        group.setLayout(main_layout)
        return group

    def create_clips_list_section(self):
        """Create the clips list section."""
        group = QGroupBox("Clips List")
        layout = QVBoxLayout()

        # Table for clips
        self.clips_table = QTableWidget()
        self.clips_table.setColumnCount(4)
        self.clips_table.setHorizontalHeaderLabels(['Name', 'Start', 'End', 'Duration (s)'])

        # Set column widths
        header = self.clips_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.clips_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.clips_table.setEditTriggers(QTableWidget.DoubleClicked)
        self.clips_table.itemChanged.connect(self.on_table_cell_changed)

        layout.addWidget(self.clips_table)

        # Buttons
        btn_layout = QHBoxLayout()

        seek_btn = QPushButton("Seek to Selected")
        seek_btn.clicked.connect(self.seek_to_selected_clip)
        btn_layout.addWidget(seek_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected_clip)
        btn_layout.addWidget(remove_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all_clips)
        btn_layout.addWidget(clear_btn)

        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def create_export_section(self):
        """Create the export section."""
        group = QGroupBox("Export")
        layout = QVBoxLayout()

        # Output directory selection
        dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("No output directory selected")
        self.output_dir_label.setStyleSheet("padding: 5px;")

        choose_dir_btn = QPushButton("Choose Folder")
        choose_dir_btn.clicked.connect(self.choose_output_dir)
        choose_dir_btn.setFixedWidth(120)

        dir_layout.addWidget(self.output_dir_label)
        dir_layout.addWidget(choose_dir_btn)

        layout.addLayout(dir_layout)

        # Export button
        self.export_btn = QPushButton("Export All Clips")
        self.export_btn.clicked.connect(self.export_all_clips)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        group.setLayout(layout)
        return group

    def load_video(self):
        """Load a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv *.flv);;All Files (*.*)"
        )

        if file_path:
            try:
                # Load into editor backend
                self.editor.load_video(file_path)
                self.file_label.setText(f"Loaded: {os.path.basename(file_path)}")
                self.update_video_info()
                self.refresh_clips_table()

                # Load into video player if available
                if self.video_player:
                    self.video_player.load_video(file_path)

                self.statusBar().showMessage(f"Video loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load video:\n{str(e)}")
                self.statusBar().showMessage("Failed to load video")

    def update_video_info(self):
        """Update the video information display."""
        try:
            info = self.editor.get_video_info()
            info_text = (
                f"Filename: {info['filename']}\n"
                f"Duration: {info['duration_formatted']} ({info['duration']:.2f} seconds)\n"
                f"Resolution: {info['width']}x{info['height']}\n"
                f"FPS: {info['fps']:.2f}"
            )
            self.info_label.setText(info_text)
        except Exception as e:
            self.info_label.setText("No video information available")

    def parse_timestamp_to_seconds(self, timestamp: str) -> float:
        """Parse timestamp string to seconds (helper for GUI calculations)."""
        try:
            return self.editor.parse_timestamp(timestamp)
        except:
            return None

    def parse_flexible_duration(self, duration: str) -> float:
        """
        Parse flexible duration format to seconds.
        Supports:
        - Seconds only: "30" or "30.5" -> 30.5 seconds
        - MM:SS: "1:30" -> 90 seconds
        - HH:MM:SS: "1:00:30" -> 3630 seconds
        - HH:MM:SS.mmm: "1:00:30.500" -> 3630.5 seconds
        """
        if not duration:
            return None

        duration = duration.strip()

        try:
            # Check if it's just a number (seconds only)
            if ':' not in duration:
                return float(duration)

            # Split by colon
            parts = duration.split(':')

            if len(parts) == 2:
                # MM:SS or MM:SS.mmm format
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            elif len(parts) == 3:
                # HH:MM:SS or HH:MM:SS.mmm format
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            else:
                return None
        except:
            return None

    def format_seconds_to_timestamp(self, seconds: float) -> str:
        """Format seconds to timestamp string (helper for GUI calculations)."""
        try:
            return self.editor.format_timestamp(seconds)
        except:
            return ""

    def on_duration_changed(self):
        """Calculate end time when duration is changed."""
        start_time = self.start_time_input.text().strip()
        duration = self.duration_input.text().strip()

        if not start_time or not duration:
            return

        start_seconds = self.parse_timestamp_to_seconds(start_time)
        duration_seconds = self.parse_flexible_duration(duration)

        if start_seconds is not None and duration_seconds is not None:
            end_seconds = start_seconds + duration_seconds
            end_time = self.format_seconds_to_timestamp(end_seconds)

            # Temporarily disconnect to avoid triggering on_end_time_changed
            self.end_time_input.textChanged.disconnect(self.on_end_time_changed)
            self.end_time_input.setText(end_time)
            self.end_time_input.textChanged.connect(self.on_end_time_changed)

    def on_end_time_changed(self):
        """Calculate duration when end time is changed."""
        start_time = self.start_time_input.text().strip()
        end_time = self.end_time_input.text().strip()

        if not start_time or not end_time:
            return

        start_seconds = self.parse_timestamp_to_seconds(start_time)
        end_seconds = self.parse_timestamp_to_seconds(end_time)

        if start_seconds is not None and end_seconds is not None and end_seconds > start_seconds:
            duration_seconds = end_seconds - start_seconds
            duration = self.format_seconds_to_timestamp(duration_seconds)

            # Temporarily disconnect to avoid triggering on_duration_changed
            self.duration_input.textChanged.disconnect(self.on_duration_changed)
            self.duration_input.setText(duration)
            self.duration_input.textChanged.connect(self.on_duration_changed)

    def on_mark_start(self, timestamp):
        """Handle mark start button from video player."""
        self.start_time_input.setText(timestamp)
        self.statusBar().showMessage(f"Start time marked: {timestamp}")

    def on_mark_end(self, timestamp):
        """Handle mark end button from video player."""
        self.end_time_input.setText(timestamp)
        self.statusBar().showMessage(f"End time marked: {timestamp}")

        # Auto-create clip if both start and end times are set
        start_time = self.start_time_input.text().strip()
        if start_time and timestamp:
            # Generate a filler name based on clip count
            clip_count = len(self.editor.get_clips_info()) + 1
            filler_name = f"Clip_{clip_count}"

            try:
                # Add clip with filler name
                self.editor.add_clip(filler_name, start_time, timestamp)
                self.refresh_clips_table()
                self.update_export_button()

                # Clear the input fields for next clip
                self.clip_name_input.clear()
                self.start_time_input.clear()
                self.end_time_input.clear()

                self.statusBar().showMessage(f"Clip '{filler_name}' created. Edit name in table if needed.")
            except Exception as e:
                self.statusBar().showMessage(f"Failed to create clip: {e}")

    def add_clip(self):
        """Add a new clip."""
        clip_name = self.clip_name_input.text().strip()
        start_time = self.start_time_input.text().strip()
        end_time = self.end_time_input.text().strip()

        if not clip_name:
            QMessageBox.warning(self, "Warning", "Please enter a clip name")
            return

        if not start_time or not end_time:
            QMessageBox.warning(self, "Warning", "Please enter start and end times (or start and duration)")
            return

        try:
            self.editor.add_clip(clip_name, start_time, end_time)
            self.refresh_clips_table()
            self.update_export_button()

            # Clear inputs
            self.clip_name_input.clear()
            self.start_time_input.clear()
            self.duration_input.clear()
            self.end_time_input.clear()

            self.statusBar().showMessage(f"Clip '{clip_name}' added successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add clip:\n{str(e)}")
            self.statusBar().showMessage("Failed to add clip")

    def on_table_cell_changed(self, item):
        """Handle cell editing in the clips table."""
        if self.updating_table:
            return

        row = item.row()
        col = item.column()

        # Get all clip data from the row
        clips_info = self.editor.get_clips_info()
        if row >= len(clips_info):
            return

        old_clip = clips_info[row]
        old_name = old_clip['name']

        # Get current values from table
        new_name = self.clips_table.item(row, 0).text().strip()
        new_start = self.clips_table.item(row, 1).text().strip()
        new_end = self.clips_table.item(row, 2).text().strip()
        new_duration = self.clips_table.item(row, 3).text().strip()

        try:
            # If duration was edited (column 3), calculate new end time
            if col == 3:
                # Parse duration using flexible parser
                duration_seconds = self.parse_flexible_duration(new_duration)
                if duration_seconds is None:
                    raise ValueError(f"Invalid duration format: {new_duration}")

                # Parse start time
                start_seconds = self.parse_timestamp_to_seconds(new_start)
                if start_seconds is None:
                    raise ValueError(f"Invalid start time: {new_start}")

                # Calculate new end time
                end_seconds = start_seconds + duration_seconds
                new_end = self.format_seconds_to_timestamp(end_seconds)

            # Validate and update the clip
            self.editor.edit_clip(old_name, new_name, new_start, new_end)
            self.statusBar().showMessage(f"Clip '{new_name}' updated successfully")

            # Refresh to update duration and format timestamps
            self.refresh_clips_table()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update clip:\n{str(e)}")
            # Revert the change
            self.refresh_clips_table()
            self.statusBar().showMessage("Failed to update clip")

    def import_clips(self):
        """Import clips from a CSV or Excel file."""
        if not self.editor.video_clip:
            QMessageBox.warning(
                self,
                "Warning",
                "Please load a video file first before importing clips."
            )
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV or Excel File",
            "",
            "Spreadsheet Files (*.csv *.xlsx *.xls);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )

        if not file_path:
            return

        # Ask if user wants to clear existing clips
        if self.editor.clips:
            reply = QMessageBox.question(
                self,
                "Clear Existing Clips?",
                "Do you want to clear existing clips before importing?\n\n"
                "Yes: Replace all clips with imported ones\n"
                "No: Add imported clips to existing ones",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return

            clear_existing = (reply == QMessageBox.Yes)
        else:
            clear_existing = False

        try:
            stats = self.editor.import_clips_from_file(file_path, clear_existing)

            # Show results
            if stats['failed'] > 0:
                error_details = "\n".join(stats['errors'][:10])  # Show first 10 errors
                if len(stats['errors']) > 10:
                    error_details += f"\n... and {len(stats['errors']) - 10} more errors"

                QMessageBox.warning(
                    self,
                    "Import Complete with Errors",
                    f"Successfully imported: {stats['success']} clip(s)\n"
                    f"Failed: {stats['failed']} clip(s)\n\n"
                    f"Errors:\n{error_details}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Successfully imported {stats['success']} clip(s)!"
                )

            self.refresh_clips_table()
            self.statusBar().showMessage(
                f"Imported {stats['success']} clips ({stats['failed']} failed)"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import clips:\n{str(e)}"
            )
            self.statusBar().showMessage("Import failed")

    def refresh_clips_table(self):
        """Refresh the clips table."""
        self.updating_table = True  # Prevent itemChanged signals during refresh

        clips_info = self.editor.get_clips_info()
        self.clips_table.setRowCount(len(clips_info))

        for row, clip in enumerate(clips_info):
            name_item = QTableWidgetItem(clip['name'])
            start_item = QTableWidgetItem(clip['start'])
            end_item = QTableWidgetItem(clip['end'])
            duration_item = QTableWidgetItem(f"{clip['duration']:.2f}")

            self.clips_table.setItem(row, 0, name_item)
            self.clips_table.setItem(row, 1, start_item)
            self.clips_table.setItem(row, 2, end_item)
            self.clips_table.setItem(row, 3, duration_item)

        self.updating_table = False
        self.update_export_button()

    def seek_to_selected_clip(self):
        """Seek video player to the start of the selected clip."""
        selected_rows = self.clips_table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a clip to seek to")
            return

        # Get start time from the second column (index 1)
        row = selected_rows[0].row()
        start_time = self.clips_table.item(row, 1).text()
        clip_name = self.clips_table.item(row, 0).text()

        # Seek the video player to this timestamp
        if self.video_player and hasattr(self.video_player, 'seek_to_timestamp'):
            self.video_player.seek_to_timestamp(start_time)
            self.statusBar().showMessage(f"Seeked to clip '{clip_name}' at {start_time}")
        else:
            QMessageBox.warning(self, "Warning", "Video player not available")

    def remove_selected_clip(self):
        """Remove the selected clip."""
        selected_rows = self.clips_table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a clip to remove")
            return

        # Get clip name from the first column
        row = selected_rows[0].row()
        clip_name = self.clips_table.item(row, 0).text()

        try:
            self.editor.remove_clip(clip_name)
            self.refresh_clips_table()
            self.statusBar().showMessage(f"Clip '{clip_name}' removed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove clip:\n{str(e)}")

    def clear_all_clips(self):
        """Clear all clips."""
        if not self.editor.clips:
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to clear all clips?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.editor.clear_clips()
            self.refresh_clips_table()
            self.statusBar().showMessage("All clips cleared")

    def choose_output_dir(self):
        """Choose output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            ""
        )

        if directory:
            self.output_dir = directory
            self.output_dir_label.setText(f"Output: {directory}")
            self.update_export_button()
            self.statusBar().showMessage(f"Output directory: {directory}")

    def update_export_button(self):
        """Update the export button state."""
        has_clips = len(self.editor.clips) > 0
        has_output_dir = self.output_dir is not None
        self.export_btn.setEnabled(has_clips and has_output_dir)

    def export_all_clips(self):
        """Export all clips to the output directory."""
        if not self.editor.clips:
            QMessageBox.warning(self, "Warning", "No clips to export")
            return

        if not self.output_dir:
            QMessageBox.warning(self, "Warning", "Please select an output directory")
            return

        # Disable export button and show progress bar
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.editor.clips))

        # Create and start export worker thread
        self.export_worker = ExportWorker(self.editor, self.output_dir)
        self.export_worker.progress.connect(self.on_export_progress)
        self.export_worker.finished.connect(self.on_export_finished)
        self.export_worker.error.connect(self.on_export_error)
        self.export_worker.start()

        self.statusBar().showMessage("Exporting clips...")

    def on_export_progress(self, current, total, clip_name):
        """Handle export progress updates."""
        self.progress_bar.setValue(current)
        if current < total:
            self.statusBar().showMessage(f"Exporting: {clip_name} ({current + 1}/{total})")
        else:
            self.statusBar().showMessage("Export complete!")

    def on_export_finished(self, exported_files):
        """Handle export completion."""
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)

        QMessageBox.information(
            self,
            "Success",
            f"Successfully exported {len(exported_files)} clip(s) to:\n{self.output_dir}"
        )

        self.statusBar().showMessage(f"Exported {len(exported_files)} clips successfully")

    def on_export_error(self, error_msg):
        """Handle export errors."""
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)

        QMessageBox.critical(
            self,
            "Export Error",
            f"Failed to export clips:\n{error_msg}"
        )

        self.statusBar().showMessage("Export failed")

    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up video player if available
        if self.video_player:
            self.video_player.close_player()

        # Clean up video editor
        self.editor.close()

        # Wait for export worker to finish if running
        if self.export_worker and self.export_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm",
                "Export is in progress. Do you want to quit?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.export_worker.terminate()
                self.export_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    window = VideoEditorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
