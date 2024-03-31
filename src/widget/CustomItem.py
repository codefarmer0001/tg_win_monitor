from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt



class CustomItem(QWidget):
    def __init__(self, item, type, parent=None):
        super().__init__(parent)

        self.item = item
        
        layout = QHBoxLayout()
        self.label1 = QLabel(item['user_nickname'])
        self.label1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label2 = QLabel(type)
        self.label2.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        
        self.setLayout(layout)