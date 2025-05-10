import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton
)

from pidpal.pages.INPUT_PAGE import ImportPage
from pidpal.pages.DB_VIEW import DBViewPage
from pidpal.pages.HOME_PAGE import HomePage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PIDPAL - Multi-Page Example")
        self.setGeometry(300, 100, 1200, 700)

        # Stylesheet (optional)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #007B8F;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #005f6f;
            }
        """)

        # Central widget with horizontal layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout(centralWidget)

        #########################
        #       Sidebar         #
        #########################
        self.sidebarLayout = QVBoxLayout()
        self.sidebarLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Home Page button
        self.homePageButton = QPushButton("Home Page")
        self.homePageButton.clicked.connect(self.showHomePage)

        # Import Page button
        self.importPageButton = QPushButton("Import Page")
        self.importPageButton.clicked.connect(self.showImportPage)

        # DB Viewer button
        self.dbViewPageButton = QPushButton("DB Viewer")
        self.dbViewPageButton.clicked.connect(self.showDBViewPage)

        # Add buttons to sidebar
        self.sidebarLayout.addWidget(self.homePageButton)
        self.sidebarLayout.addWidget(self.importPageButton)
        self.sidebarLayout.addWidget(self.dbViewPageButton)
        self.sidebarLayout.addStretch()

        #########################
        #   Stacked Widget      #
        #########################
        self.pagesWidget = QStackedWidget()

        # Create instances of each page
        self.homePage = HomePage()
        self.importPage = ImportPage()
        self.dbViewPage = DBViewPage()

        # Add pages to the stack (the order determines their index)
        self.pagesWidget.addWidget(self.homePage)    # index 0
        self.pagesWidget.addWidget(self.importPage)  # index 1
        self.pagesWidget.addWidget(self.dbViewPage)  # index 2

        # Start with the Home page (index 0)
        self.pagesWidget.setCurrentIndex(0)

        # Add sidebar + stacked widget to the main layout
        mainLayout.addLayout(self.sidebarLayout, 1)
        mainLayout.addWidget(self.pagesWidget, 4)

    ##################
    #  Page Switchers
    ##################
    def showHomePage(self):
        self.pagesWidget.setCurrentWidget(self.homePage)

    def showImportPage(self):
        self.pagesWidget.setCurrentWidget(self.importPage)

    def showDBViewPage(self):
        self.pagesWidget.setCurrentWidget(self.dbViewPage)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
