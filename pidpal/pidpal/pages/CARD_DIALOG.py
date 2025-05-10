import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap

class ParcelCardDialog(QDialog):
    """
    A simple dialog ("card") for displaying Parcel info.
    Here, we show the ParcelID as a title and an optional screenshot.
    """
    def __init__(self, parcel_id: str, screenshot_path: str = None, parent=None):
        super().__init__(parent)
        self.parcel_id = parcel_id
        self.screenshot_path = screenshot_path

        self.setWindowTitle(f"Parcel Card: {parcel_id}")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Title
        label_title = QLabel(f"<h3>Parcel: {self.parcel_id}</h3>")
        layout.addWidget(label_title)

        # If there's a screenshot_path, load that image
        if self.screenshot_path and os.path.exists(self.screenshot_path):
            pixmap = QPixmap(self.screenshot_path)
            lbl_img = QLabel()
            lbl_img.setPixmap(pixmap)
            layout.addWidget(lbl_img)
        else:
            layout.addWidget(QLabel("No screenshot found for this parcel."))

        # If you want more details (e.g. Owner, County, etc.),
        # you could add more widgets here.

        self.setLayout(layout)
