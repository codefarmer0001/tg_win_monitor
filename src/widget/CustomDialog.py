# import sys
# from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
# import psutil
# import cpuinfo
# import wmi
# from PyQt6.QtCore import Qt

# class CustomDialog(QDialog):
    # def __init__(self):
    #     super().__init__()

    #     self.setWindowTitle("应用授权")
    #     self.setFixedSize(600, 300)

    #     # 创建布局
    #     layout = QVBoxLayout(self)
    #     # layout.setSpacing(10)
    #     layout.setSpacing(0)

    #     h_item1 = QHBoxLayout()
    #     h_item1.setContentsMargins(0, 20, 0, 0)

    #     label1 = QLabel("设备号:")
    #     label1.setFixedWidth(60)
    #     label1.setAlignment(Qt.AlignmentFlag.AlignLeft)
    #     line_edit1 = QLineEdit()
    #     h_item1.addWidget(label1)
    #     label2 = QLabel(self.get_code())
    #     label2.setAlignment(Qt.AlignmentFlag.AlignLeft)
    #     h_item1.addWidget(label2)

    #     copy_button = QPushButton("复制")
    #     copy_button.setFixedWidth(100)
    #     h_item1.addWidget(copy_button)

    #     layout.addLayout(h_item1)

        
    #     h_item2 = QHBoxLayout()
    #     h_item2.setContentsMargins(0, 20, 0, 0)
    #     # 创建展示文本标签
    #     display_label = QLabel("授权码:")
    #     h_item2.addWidget(display_label)

    #     # 创建文本输入框
    #     text_edit = QLineEdit()
    #     h_item2.addWidget(text_edit)

    #     layout.addLayout(h_item2)

    #     # 创建确定按钮
    #     self.ok_button = QPushButton("确定")
    #     self.ok_button.clicked.connect(self.on_ok_clicked)
    #     layout.addWidget(self.ok_button)

    #     self.setLayout(layout)

    # def on_ok_clicked(self):
    #     # 获取文本输入框中的内容
    #     input_text = self.text_edit.text()
    #     self.display_label.setText(f"Display Text: {input_text}")

    #     # 关闭对话框
    #     self.close()


    # def get_board_serial(self):
    #     try:
    #         c = wmi.WMI()
    #         for board in c.Win32_BaseBoard():
    #             return board.SerialNumber.strip()
    #     except Exception as e:
    #         print(f"Error retrieving board serial number: {e}")
    #         return None

    # def get_code(self):

    #     # 获取主板序列号
    #     # info = cpuinfo.get_cpu_info()
    #     board_serial = self.get_board_serial()
    #     # board_serial = psutil.disk_partitions()[0].serial

    #     # 获取CPU信息
    #     cpu_info = psutil.cpu_freq()
    #     cpu_freq = cpu_info.current
    #     cpu_count = psutil.cpu_count(logical=False)

    #     # 获取内存信息
    #     mem_info = psutil.virtual_memory()
    #     mem_size = mem_info.total

    #     # 拼接各项信息作为机器码
    #     machine_id = f"{board_serial}_{cpu_freq}_{cpu_count}_{mem_size}"
    #     print(machine_id)
    #     return machine_id