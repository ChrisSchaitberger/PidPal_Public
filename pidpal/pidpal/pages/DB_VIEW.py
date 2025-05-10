# DB_VIEW.py

import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QMessageBox, QLineEdit, QComboBox, QFormLayout
)
from PyQt6.QtGui import QBrush, QColor, QFont

# Your DB helpers (adjust the actual import path if needed)
from pidpal.db_func import query_parcels, get_screenshot_path
# Import the separate card dialog
from pidpal.pages.CARD_DIALOG import ParcelCardDialog

class DBViewPage(QWidget):
    """
    A page that queries the DB (Parcels, etc.) and displays results in a QTableWidget.
    If user double-clicks on ParcelID, it opens a 'card' dialog with more details.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Heading label
        self.headingLabel = QLabel("Database Viewer")
        self.headingLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.headingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Filter inputs (example: filter by ParcelID, State, County)
        self.parcelIDInput = QLineEdit()
        self.parcelIDInput.setPlaceholderText("Filter by ParcelID (exact)")

        self.stateInput = QLineEdit()
        self.stateInput.setPlaceholderText("Filter by State (exact)")

        self.countyInput = QLineEdit()
        self.countyInput.setPlaceholderText("Filter by County (exact)")

        filterForm = QFormLayout()
        filterForm.addRow("ParcelID:", self.parcelIDInput)
        filterForm.addRow("State:", self.stateInput)
        filterForm.addRow("County:", self.countyInput)

        filterGroupBox = QGroupBox("Filters (Exact Match)")
        filterGroupBox.setLayout(filterForm)

        # Sorting options
        self.sortColumnCombo = QComboBox()
        self.sortColumnCombo.addItem("No Sorting")
        self.sortColumnCombo.addItems([
            "ParcelID", "State", "County", "LandValue", "BuildingValue",
            "TotalValue", "AssessmentYear", "LastScraped",
            "PropertyID", "Owner"
        ])
        self.sortOrderCombo = QComboBox()
        self.sortOrderCombo.addItems(["ASC", "DESC"])

        sortLayout = QHBoxLayout()
        sortLayout.addWidget(self.sortColumnCombo)
        sortLayout.addWidget(self.sortOrderCombo)
        sortGroupBox = QGroupBox("Sort By")
        sortGroupBox.setLayout(sortLayout)

        # Buttons: Search / Clear
        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.loadData)
        self.clearButton = QPushButton("Clear Filters")
        self.clearButton.clicked.connect(self.clearFilters)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.searchButton)
        buttonLayout.addWidget(self.clearButton)
        buttonLayout.addStretch()

        # The table
        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.cellDoubleClicked.connect(self.onCellDoubleClicked)

        tableGroupBox = QGroupBox("Query Results")
        tableLayout = QVBoxLayout()
        tableLayout.addWidget(self.tableWidget)
        tableGroupBox.setLayout(tableLayout)

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.headingLabel)

        topRowLayout = QHBoxLayout()
        topRowLayout.addWidget(filterGroupBox)
        topRowLayout.addWidget(sortGroupBox)

        mainLayout.addLayout(topRowLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(tableGroupBox)

        self.setLayout(mainLayout)

        # Optionally auto-load
        self.loadData()

        # Enable the row index column (vertical header).
        self.tableWidget.setCornerButtonEnabled(True)
        self.tableWidget.verticalHeader().setVisible(True)

         # Lighter gray for horizontal header
        self.tableWidget.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #777; /* a medium gray */
                color: white;           /* white text for contrast */
                padding: 4px;
                border: 1px solid #666; /* slightly darker border */
            }
        """)

        # Slightly different gray for vertical header
        self.tableWidget.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #888; /* slightly different gray */
                color: white;           /* white text */
                padding: 4px;
                border: 1px solid #666;
            }
        """)


    def buildFilters(self):
        """
        Return a dict of filters for query_parcels. E.g. {"ParcelID": "123"}
        """
        filters = {}
        if self.parcelIDInput.text().strip():
            filters["ParcelID"] = self.parcelIDInput.text().strip()
        if self.stateInput.text().strip():
            filters["State"] = self.stateInput.text().strip()
        if self.countyInput.text().strip():
            filters["County"] = self.countyInput.text().strip()
        return filters

    def loadData(self):
        """Fetch and display data in the table."""
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

        # Build filters
        filters = self.buildFilters()

        # Sorting
        selected_sort_col = self.sortColumnCombo.currentText()
        if selected_sort_col == "No Sorting":
            sort_by = None
        else:
            sort_by = selected_sort_col
        sort_order = self.sortOrderCombo.currentText()

        try:
            data_list = query_parcels(filters=filters, sort_by=sort_by, sort_order=sort_order)
        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Error fetching data:\n{e}")
            return

        if not data_list:
            QMessageBox.information(self, "No Data", "No records found in the database.")
            return

        # Store for later reference
        self.current_data = data_list

        columns = list(data_list[0].keys())  # e.g. ["ParcelID","State","County",...,"Owner"]
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)

        # Identify ParcelID column
        self.parcel_id_col_idx = columns.index("ParcelID") if "ParcelID" in columns else -1

        # Insert rows
        for row_idx, row_dict in enumerate(data_list):
            self.tableWidget.insertRow(row_idx)
            for col_idx, col_name in enumerate(columns):
                val = str(row_dict.get(col_name, ""))
                item = QTableWidgetItem(val)

                # If it's ParcelID, style as hyperlink
                if col_idx == self.parcel_id_col_idx:
                    self.makeHyperlink(item)

                self.tableWidget.setItem(row_idx, col_idx, item)

        self.tableWidget.resizeColumnsToContents()

    def makeHyperlink(self, item):
        """Visually style the item like a hyperlink."""
        item.setForeground(QBrush(QColor("blue")))
        font = item.font()
        font.setUnderline(True)
        item.setFont(font)

    def onCellDoubleClicked(self, row, col):
        """Open the ParcelCardDialog if user double-clicks the ParcelID column."""
        if not hasattr(self, "current_data"):
            return

        if col == self.parcel_id_col_idx and self.parcel_id_col_idx >= 0:
            row_data = self.current_data[row]
            parcel_id = row_data.get("ParcelID", "")
            # Optionally get the screenshot path
            screenshot_path = get_screenshot_path(parcel_id)

            dlg = ParcelCardDialog(parcel_id, screenshot_path, self)
            dlg.exec()
        else:
            # Double-clicked some other column
            pass

    def clearFilters(self):
        """Reset filters, reload the table."""
        self.parcelIDInput.clear()
        self.stateInput.clear()
        self.countyInput.clear()
        self.sortColumnCombo.setCurrentIndex(0)  # "No Sorting"
        self.sortOrderCombo.setCurrentIndex(0)   # "ASC"
        self.loadData()
