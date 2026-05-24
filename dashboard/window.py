#!/usr/bin/env python3
"""
Dashboard Main Window using PySide6
"""

try:
    from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont, QColor
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DashboardWindow(QMainWindow if HAS_PYSIDE6 else object):
    """Main dashboard window"""

    def __init__(self, config, parent=None):
        """Initialize dashboard window"""
        if not HAS_PYSIDE6:
            logger.error("PySide6 not installed")
            raise ImportError("PySide6 required for dashboard")

        super().__init__(parent)
        self.config = config
        self.setup_ui()
        logger.info("Dashboard window created")

    def setup_ui(self) -> None:
        """Setup UI"""
        self.setWindowTitle("π Tech Interactive - WiFi Spatial Intelligence Observatory")
        self.setGeometry(100, 100, 1920, 1080)
        self.setStyleSheet("background-color: #0a0e27;")

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Title label
        title = QLabel("π Tech Interactive")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setStyleSheet("color: #00ff88; text-shadow: 0 0 10px #00ff88;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("WIFI SPATIAL INTELLIGENCE OBSERVATORY")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #00ccff; text-shadow: 0 0 5px #00ccff;")
        layout.addWidget(subtitle)

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(QFont("Courier", 12))
        self.status_label.setStyleSheet("color: #00ff88;")
        layout.addWidget(self.status_label)

        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)

    def update_display(self) -> None:
        """Update display"""
        self.status_label.setText(f"System running at {self.timer.interval()}ms")

    def closeEvent(self, event) -> None:
        """Handle window close"""
        logger.info("Dashboard window closed")
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)
