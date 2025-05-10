# home_page.py

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGroupBox, QVBoxLayout
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Import our leaflet map generator
from pidpal.scrapers.working_county_map import generate_leaflet_map_html

class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Title / Heading
        self.headingLabel = QLabel("Welcome to PIDPAL")
        self.headingLabel.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.headingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subheadingLabel = QLabel("Your Comprehensive Parcel Scraping Toolkit")
        self.subheadingLabel.setStyleSheet("font-size: 16px; color: #555;")
        self.subheadingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        instructions = (
            "<h3>How to Use:</h3>"
            "<ol>"
            "<li>Go to the <b>Import Page</b> to upload or enter your parcel data.</li>"
            "<li>Click <b>Go!</b> to scrape data from all counties in one shot.</li>"
            "<li>View results in the <b>DB Viewer</b> to see or filter your data.</li>"
            "</ol>"
            "<p>Use the sidebar at the left to navigate between pages.</p>"
        )
        self.instructionsLabel = QLabel(instructions)
        self.instructionsLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.instructionsLabel.setWordWrap(True)

        # Quick nav buttons
        self.importButton = QPushButton("Go to Import Page")
        self.dbViewButton = QPushButton("Go to Database Viewer")
        navLayout = QHBoxLayout()
        navLayout.addWidget(self.importButton)
        navLayout.addWidget(self.dbViewButton)
        navLayout.addStretch()

        # Generate the Leaflet map HTML (pointing to your CSV file)
        map_html = generate_leaflet_map_html(r"Resources\PidPal Counties Tracker.csv")

        self.mapView = QWebEngineView()
        self.mapView.setHtml(map_html)

        # Put the map in a group box
        mapGroupBox = QGroupBox("Parcel Map")
        mapLayout = QVBoxLayout()
        mapLayout.addWidget(self.mapView)
        mapGroupBox.setLayout(mapLayout)

        # Build the main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.headingLabel)
        mainLayout.addWidget(self.subheadingLabel)
        mainLayout.addSpacing(20)
        mainLayout.addWidget(self.instructionsLabel)
        mainLayout.addSpacing(20)
        mainLayout.addLayout(navLayout)
        mainLayout.addSpacing(20)
        mainLayout.addWidget(mapGroupBox)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
