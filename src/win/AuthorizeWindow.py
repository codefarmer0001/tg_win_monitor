import sys
from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

class AuthorizeWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("app授权")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.label = QLabel("Main Interface")
        layout.addWidget(self.label)
        self.button = QPushButton("Open Second Interface")
        # self.button.clicked.connect(self.open_second_interface)
        layout.addWidget(self.button)
        self.setFixedSize(400, 200)

        self.central_widget.setLayout(layout)

    # def open_second_interface(self):
    #     self.second_interface = SecondWindow()
    #     self.second_interface.show()


