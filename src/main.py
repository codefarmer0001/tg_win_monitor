from config import CONFIG
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from win import AuthorizeWindow, MainWindow
from PySide6.QtGui import QIcon
from dao import Accounts
from datetime import datetime
import time
# from widget import CustomDialog

def is_date_before(today_int, target_date_str):
    target_date_obj = datetime.strptime(target_date_str, "%Y-%m-%d")
    timestamp = int(target_date_obj.timestamp())
    return today_int < timestamp




def show_info_dialog():
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle("Info")
    msg_box.setText("This is a small info dialog.")
    msg_box.exec()

if __name__ == '__main__':
    # print(CONFIG.TELEGRAM_BOT_TOKEN)
    Accounts()

    

    timestamp = int(time.time())

    if is_date_before(timestamp, '2024-06-30'):
        # print(f"{timestamp} 在目标日期之前")
        pass
    else:
        # print(f"{timestamp} 不在目标日期之前")
        sys.exit()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/assets/tg.png"))

    # 创建并显示自定义对话框
    # dialog = CustomDialog()
    # dialog.exec()

    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()