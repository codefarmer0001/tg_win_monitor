from config import CONFIG
import sys
from PySide6.QtWidgets import QApplication
from win import AuthorizeWindow, MainWindow
from PySide6.QtGui import QIcon
from dao import Accounts

if __name__ == '__main__':
    # print(CONFIG.TELEGRAM_BOT_TOKEN)
    Accounts()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/assets/tg.png"))
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()