from config import CONFIG
import sys
from PySide6.QtWidgets import QApplication
from win import AuthorizeWindow, MainWindow
from PySide6.QtGui import QIcon
from dao import Accounts
from datetime import datetime
import time

def is_date_before(today_int, target_date_str):
    target_date_obj = datetime.strptime(target_date_str, "%Y-%m-%d")
    timestamp = int(target_date_obj.timestamp())
    return today_int < timestamp

if __name__ == '__main__':
    # print(CONFIG.TELEGRAM_BOT_TOKEN)
    Accounts()

    timestamp = int(time.time())

    if is_date_before(timestamp, '2024-04-25'):
        print(f"{timestamp} 在目标日期之前")
    else:
        print(f"{timestamp} 不在目标日期之前")
        sys.exit()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/assets/tg.png"))
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()