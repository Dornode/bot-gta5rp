from PyQt5 import QtWidgets

class SimplePage(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()
        self.setStyleSheet("background-color: rgba(60, 60, 60, 180);")
        label = QtWidgets.QLabel(f"Страница: {name}")
        label.setStyleSheet("color: white; font-size: 20px;")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
