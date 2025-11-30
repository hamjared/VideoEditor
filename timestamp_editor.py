"""
Timestamp Editor Widget and Delegate
Provides a custom editor for timestamp fields with up/down arrow support.
"""

from PyQt5.QtWidgets import QLineEdit, QStyledItemDelegate
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
import re


class TimestampEditor(QLineEdit):
    """
    Custom line edit for timestamp editing with arrow key support.

    Format: HH:MM:SS.mmm
    Arrow keys increment/decrement the component at cursor position.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("00:00:00.000")

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events, especially up/down arrows."""
        if event.key() in (Qt.Key_Up, Qt.Key_Down):
            self.adjust_timestamp(event.key() == Qt.Key_Up)
            event.accept()
        else:
            super().keyPressEvent(event)

    def adjust_timestamp(self, increment: bool):
        """
        Adjust the timestamp component at the cursor position.

        Args:
            increment: True to increment, False to decrement
        """
        text = self.text()
        cursor_pos = self.cursorPosition()

        # Parse the timestamp
        try:
            hours, minutes, seconds_with_ms = self.parse_timestamp_components(text)
            if seconds_with_ms is None:
                return

            seconds = int(seconds_with_ms)
            milliseconds = int((seconds_with_ms - seconds) * 1000)
        except:
            return

        # Determine which component to adjust based on cursor position
        # Format: HH:MM:SS.mmm
        # Positions: 0-2 = hours, 3-5 = minutes, 6-8 = seconds, 9-12 = milliseconds
        delta = 1 if increment else -1

        if cursor_pos <= 2:
            # Adjust hours
            hours = max(0, hours + delta)
        elif cursor_pos <= 5:
            # Adjust minutes
            minutes += delta
            if minutes >= 60:
                minutes = 0
                hours += 1
            elif minutes < 0:
                minutes = 59
                hours = max(0, hours - 1)
        elif cursor_pos <= 8:
            # Adjust seconds
            seconds += delta
            if seconds >= 60:
                seconds = 0
                minutes += 1
                if minutes >= 60:
                    minutes = 0
                    hours += 1
            elif seconds < 0:
                if minutes > 0 or hours > 0:
                    seconds = 59
                    minutes -= 1
                    if minutes < 0:
                        if hours > 0:
                            minutes = 59
                            hours -= 1
                        else:
                            minutes = 0
                            seconds = 0
                else:
                    seconds = 0
        else:
            # Adjust milliseconds (in steps of 100ms for easier control)
            milliseconds += delta * 100
            if milliseconds >= 1000:
                milliseconds = 0
                seconds += 1
                if seconds >= 60:
                    seconds = 0
                    minutes += 1
                    if minutes >= 60:
                        minutes = 0
                        hours += 1
            elif milliseconds < 0:
                if seconds > 0 or minutes > 0 or hours > 0:
                    milliseconds = 900
                    seconds -= 1
                    if seconds < 0:
                        if minutes > 0 or hours > 0:
                            seconds = 59
                            minutes -= 1
                            if minutes < 0:
                                if hours > 0:
                                    minutes = 59
                                    hours -= 1
                                else:
                                    minutes = 0
                                    seconds = 0
                        else:
                            seconds = 0
                else:
                    milliseconds = 0

        # Format back to timestamp
        new_timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

        # Update text and restore cursor position
        old_cursor = cursor_pos
        self.setText(new_timestamp)
        self.setCursorPosition(old_cursor)

    def parse_timestamp_components(self, timestamp: str):
        """
        Parse timestamp string into components.

        Args:
            timestamp: Timestamp string (HH:MM:SS.mmm or MM:SS.mmm or SS.mmm)

        Returns:
            Tuple of (hours, minutes, seconds_with_ms) or (None, None, None) if invalid
        """
        if not timestamp:
            return (0, 0, 0.0)

        timestamp = timestamp.strip()

        # Match timestamp pattern
        pattern = r'^(?:(\d+):)?(?:(\d+):)?(\d+(?:\.\d+)?)$'
        match = re.match(pattern, timestamp)

        if not match:
            return (None, None, None)

        groups = match.groups()

        if groups[0] is not None and groups[1] is not None:
            # HH:MM:SS.mmm format
            hours = int(groups[0])
            minutes = int(groups[1])
            seconds = float(groups[2])
        elif groups[0] is not None:
            # MM:SS.mmm format (no hours)
            hours = 0
            minutes = int(groups[0])
            seconds = float(groups[2])
        else:
            # SS.mmm format (no hours or minutes)
            hours = 0
            minutes = 0
            seconds = float(groups[2])

        return (hours, minutes, seconds)


class TimestampDelegate(QStyledItemDelegate):
    """
    Custom delegate for timestamp columns in the clips table.
    Uses TimestampEditor for editing.
    """

    def createEditor(self, parent, option, index):
        """Create the custom timestamp editor."""
        editor = TimestampEditor(parent)
        return editor

    def setEditorData(self, editor, index):
        """Set the editor's initial value from the model."""
        value = index.model().data(index, Qt.EditRole)
        editor.setText(str(value))
        editor.selectAll()

    def setModelData(self, editor, model, index):
        """Save the editor's value back to the model."""
        value = editor.text()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        """Update the editor's geometry to match the cell."""
        editor.setGeometry(option.rect)
