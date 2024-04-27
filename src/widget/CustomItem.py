from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt



class CustomItem(QWidget):
    def __init__(self, item, type, online, parent=None):
        super().__init__(parent)

        self.item = item
        
        layout = QHBoxLayout()
        self.label1 = QLabel(item['user_nickname'])
        self.label1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label2 = QLabel(type)
        self.label2.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 创建一个圆点
        dot_label = QLabel()
        dot_label.setFixedSize(10, 10)  # 设置圆点大小
        if online == 1:
            dot_label.setStyleSheet("background-color: green; border-radius: 5px;")  # 设置背景色和圆角
        else:
            dot_label.setStyleSheet("background-color: gray; border-radius: 5px;")  # 设置背景色和圆角

        layout.addWidget(dot_label)

        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        
        self.setLayout(layout)