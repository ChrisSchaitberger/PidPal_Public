import os
import csv
from itertools import islice

# For Excel support
import pandas as pd

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QLabel, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView
)

# Import custom modules
from pidpal.scrapers.scrape_all import scrape_all_counties
from pidpal.db_func import insert_initial_parcels, insert_scraped_data
from pidpal.func import clean_record



class ImportPage(QWidget):
    """
    Page for importing spreadsheets (CSV/XLSX), displaying
    parcels in a table, and performing the scraping/DB insertion.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Title/Heading
        self.headingLabel = QLabel("Import Parcels")
        self.headingLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.headingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons: Download Template & Import
        self.downloadTemplateButton = QPushButton("Download CSV Template")
        self.downloadTemplateButton.clicked.connect(self.downloadCSVTemplate)

        self.importButton = QPushButton("Import Spreadsheet")
        self.importButton.clicked.connect(self.addRowToTable)

        # TableWidget
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ParcelID", "County", "State", "PropertyID", "Owner"])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setRowCount(0)

        # Go! button
        self.goButton = QPushButton("Go!")
        self.goButton.setFixedSize(70, 30)
        self.goButton.clicked.connect(self.processAllRows)

        # GroupBox for the table
        tableGroupBox = QGroupBox("Parcel Information")
        tableLayout = QVBoxLayout()
        tableLayout.addWidget(self.tableWidget)
        tableGroupBox.setLayout(tableLayout)

        # Layout: Top buttons
        topButtonsLayout = QHBoxLayout()
        topButtonsLayout.addWidget(self.downloadTemplateButton)
        topButtonsLayout.addWidget(self.importButton)
        topButtonsLayout.addStretch()

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.headingLabel)
        mainLayout.addLayout(topButtonsLayout)
        mainLayout.addWidget(tableGroupBox)
        mainLayout.addWidget(self.goButton, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(mainLayout)

    ############################
    #   Methods for ImportPage #
    ############################

    def browse(self) -> str:
        """
        Opens a file dialog and returns the selected file path.
        Returns an empty string if canceled.
        """
        file_filter = 'Data File (*.xlsx *.csv *.dat)'
        filename, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a file',
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='Data File (*.xlsx *.csv *.dat)'
        )
        return filename  # '' if canceled

    def addRowToTable(self):
        """
        Prompts user to select CSV or XLSX, then populates the table.
        """
        importedSpreadsheet = self.browse()
        if not importedSpreadsheet:
            QMessageBox.warning(self, "No File Selected", "No file was selected. Import canceled.")
            return

        file_ext = os.path.splitext(importedSpreadsheet)[1].lower()

        # -- CSV --
        if file_ext == '.csv':
            try:
                with open(importedSpreadsheet, 'r', encoding='utf-8-sig') as file:
                    csv_reader = csv.reader(file)
                    # Skip header row
                    for row in islice(csv_reader, 1, None):
                        parcelID   = row[0] if len(row) > 0 else ""
                        county     = row[1] if len(row) > 1 else ""
                        state      = row[2] if len(row) > 2 else ""
                        propertyID = row[3] if len(row) > 3 else ""
                        owner      = row[4] if len(row) > 4 else ""

                        rowPos = self.tableWidget.rowCount()
                        self.tableWidget.insertRow(rowPos)
                        self.tableWidget.setItem(rowPos, 0, QTableWidgetItem(parcelID))
                        self.tableWidget.setItem(rowPos, 1, QTableWidgetItem(county))
                        self.tableWidget.setItem(rowPos, 2, QTableWidgetItem(state))
                        self.tableWidget.setItem(rowPos, 3, QTableWidgetItem(propertyID))
                        self.tableWidget.setItem(rowPos, 4, QTableWidgetItem(owner))

                QMessageBox.information(
                    self, "Import Successful",
                    f"Successfully imported CSV from:\n{importedSpreadsheet}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to read CSV file:\n{e}")

        # -- XLSX --
        elif file_ext == '.xlsx':
            try:
                df = pd.read_excel(importedSpreadsheet)
                for _, row in df.iterrows():
                    parcelID   = str(row[0]) if 0 in row else ""
                    county     = str(row[1]) if 1 in row else ""
                    state      = str(row[2]) if 2 in row else ""
                    propertyID = str(row[3]) if 3 in row else ""
                    owner      = str(row[4]) if 4 in row else ""

                    rowPos = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(rowPos)
                    self.tableWidget.setItem(rowPos, 0, QTableWidgetItem(parcelID))
                    self.tableWidget.setItem(rowPos, 1, QTableWidgetItem(county))
                    self.tableWidget.setItem(rowPos, 2, QTableWidgetItem(state))
                    self.tableWidget.setItem(rowPos, 3, QTableWidgetItem(propertyID))
                    self.tableWidget.setItem(rowPos, 4, QTableWidgetItem(owner))

                QMessageBox.information(
                    self, "Import Successful",
                    f"Successfully imported Excel file from:\n{importedSpreadsheet}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to read Excel file:\n{e}")

        # -- Otherwise --
        else:
            QMessageBox.warning(
                self, "Unsupported File",
                "Unsupported file extension. Please select a CSV or XLSX file."
            )

    def downloadCSVTemplate(self):
        """
        Lets user save a blank CSV with the expected columns.
        """
        filepath, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save CSV Template",
            directory="template.csv",
            filter="CSV File (*.csv)"
        )
        if not filepath:
            QMessageBox.warning(self, "Save Canceled", "No file created.")
            return

        columns = ["ParcelID", "County", "State", "PropertyID", "Owner"]

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
        except Exception as e:
            QMessageBox.critical(self, "Template Error", f"Error writing template:\n{e}")
        else:
            QMessageBox.information(
                self, "Template Saved",
                f"Template saved successfully to:\n{filepath}"
            )

    def processAllRows(self):
        """
        Reads all rows, calls scrape & DB functions, then clears the table.
        """
        row_count = self.tableWidget.rowCount()
        data_list = []

        for row in range(row_count):
            parcelID = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ""
            county   = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ""
            state    = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else ""
            propID   = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ""
            owner    = self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else ""

            data_list.append({
                "ParcelID": parcelID,
                "County": county,
                "State": state,
                "PropertyID": propID,
                "Owner": owner
            })

        # Insert into DB
        insert_initial_parcels(data_list)

        # Scrape data
        all_scraped_data = scrape_all_counties(data_list, screenshot_dir="Screenshots")

        for data_obj in all_scraped_data:
            # Convert to a dict
            record = data_obj.to_dict()
            clean_record(record)
            # Optionally write the cleaned values back to the DataObject
            # so that data_obj is updated too:
            data_obj.LandValue = record["LandValue"]
            data_obj.BuildingValue = record["BuildingValue"]
            data_obj.TotalValue = record["TotalValue"]
            data_obj.AssessmentYear = record["AssessmentYear"]
            # if you store LastScraped or PropertyID in the DataObject, do that too

        # Insert scraped data
        insert_scraped_data(all_scraped_data)

        QMessageBox.information(self, "Scrape Complete", "Data scraped and inserted.")

        # Debug prints (optional)
        print("\nScraped Data Objects:")
        for obj in all_scraped_data:
            print(f"ParcelID: {obj.ParcelID}")
            print(f"  LandValue: {obj.LandValue}")
            print(f"  BuildingValue: {obj.BuildingValue}")
            print(f"  TotalValue: {obj.TotalValue}")
            print(f"  AssessmentYear: {obj.AssessmentYear}")
            print(f"  ScreenshotPath: {obj.ScreenshotPath}")
            print("-----")

        # Clear table
        self.tableWidget.setRowCount(0)
