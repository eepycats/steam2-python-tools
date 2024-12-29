from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (
        QWidget, QGridLayout, QLabel)
from PyQt5.QtGui import QIcon
from datetime import datetime

class InfoWindow(QWidget):

    def __init__(self, version : int, time :datetime):
        super(InfoWindow, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Blob Info")
        self.setWindowIcon(QIcon("./icons/information.png"))
        self.resize(500,500)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel(f"Version: {version}"))

        self.layout.addWidget(QLabel(f"This blob was acquired at: {time}."))
    
    def wnd_name(self):
        return "Blob info"
