import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QMenu, QDialog, QLineEdit, QFileDialog, QTextEdit
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, Signal, Slot, QObject, QTimer
import random
import shutil
from widget import CustomItem
import re
from woker import Worker
from dao import Accounts
from telegram import TgClient
import asyncio
from functools import partial
import time

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.accounts = Accounts()

        self.setWindowTitle("telegram 监控/信息发送")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setWindowIcon(QIcon(":/assets/tg.png"))

        self.setFixedSize(900, 550)

        # 创建左右布局
        self.h_layout = QHBoxLayout(self.central_widget)

        # 左侧部件
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.label = QLabel("账号列表")
        self.left_layout.addWidget(self.label)

        # 右侧部件
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_label = QLabel("联系人列表")
        self.right_layout.addWidget(self.right_label)

        self.load_panal()
        self.tool_bar()
        self.load_init_data()

    # 加载左侧账号的数据
    def load_init_data(self):
        list = self.accounts.get_all()
        phones_sessions = []
        if list:
            for data in list:
                session = (data['phone'], data['session_path'])
                phones_sessions.append(session)

            self.worker = Worker(phones_sessions)
            self.worker.start()

        list = self.accounts.get_all()
        print(list)
        if list:
            for data in list:
                custom_item = CustomItem(data, '监控账号' if data['type'] == 1 else '消息账号')
                item = QListWidgetItem()
                item.setSizeHint(custom_item.sizeHint())
                self.lift_list_widget.addItem(item)
                self.lift_list_widget.setItemWidget(item, custom_item)

        self.lift_list_widget.itemClicked.connect(self.load_right_data)


    def load_panal(self):
        # 添加列表部件
        self.lift_list_widget = QListWidget()

        self.lift_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lift_list_widget.customContextMenuRequested.connect(self.show_context_menu)


        self.left_layout.addWidget(self.lift_list_widget)


        # 添加列表部件
        self.right_list_widget = QListWidget()
        self.right_layout.addWidget(self.right_list_widget)



        # 使用QSplitter创建可调整大小的分隔窗口
        splitter = QSplitter()
        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.right_widget)

        # 将QSplitter添加到水平布局中
        self.h_layout.addWidget(splitter)

    def load_contacts(self, result):
        print(result)


    def process_async_method(self, phone, session_path):
        # 在这里调用异步方法
        asyncio.create_task(self.get_dialos(phone, session_path))


    async def get_dialos(self, phone, session_path):
        tgClient = TgClient(phone, session_path)
        return await tgClient.get_dialogs()

    # @asyncSlot()
    def load_right_data(self, item):
        # 通过 item 获取与之关联的 CustomItem 实例
        custom_item = self.lift_list_widget.itemWidget(item)

        print(custom_item.item)

        # 获取 CustomItem 中 label1 的文本内容
        custom_text = custom_item.label1.text()
        # 根据左侧列表项的点击加载右侧数据
        # text = item.text()
        self.right_label.setText(f"加载 {custom_text} 的联系人数据")
        self.right_list_widget.clear()

        phone = custom_item.item['phone']  # Assuming item.data() contains the phone information
        session_path = custom_item.item['session_path']  # Assuming item.toolTip() contains the session path information
        QTimer.singleShot(0, partial(self.process_async_method, phone, session_path))
        

        # 模拟加载数据，这里只是添加新的群组项
        random_int = random.randint(1, 50)
        for i in range(random_int):
            self.right_list_widget.addItem(f"{custom_text} 的联系人{i}")


    def show_context_menu(self, pos):
        # 创建右键菜单
        menu = QMenu(self.lift_list_widget)

        # 添加菜单项
        action1 = menu.addAction("监控账号")
        action2 = menu.addAction("发送策略")
        action3 = menu.addAction("启用/停用")

        # 显示菜单，并获取用户选择的操作
        action = menu.exec_(self.lift_list_widget.mapToGlobal(pos))

        # 根据用户选择的操作执行相应的逻辑
        if action == action1:
            print("执行 Action 1")
        elif action == action2:
            # print("执行 Action 2")
            self.open_modal_window()
        elif action == action3:
            print("执行 Action 3")



    def open_modal_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("发送设置")
        layout = QVBoxLayout(dialog)

        # 发送速度输入框
        speed_label = QLabel("发送速度（秒）:")
        speed_input = QLineEdit()
        layout.addWidget(speed_label)
        layout.addWidget(speed_input)

        # 每天发送用户数输入框
        users_label = QLabel("每天发送用户数:")
        users_input = QLineEdit()
        layout.addWidget(users_label)
        layout.addWidget(users_input)

        # 发送周期输入框
        cycle_label = QLabel("发送周期（天）:")
        cycle_input = QLineEdit()
        layout.addWidget(cycle_label)
        layout.addWidget(cycle_input)

        # 发送时间范围输入框
        time_label = QLabel("发送时间范围（小时）:")
        time_input = QLineEdit()
        layout.addWidget(time_label)
        layout.addWidget(time_input)

        # 确定按钮
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(dialog.accept)
        layout.addWidget(confirm_button)

        # 显示模态窗口
        dialog.exec_()

    
    def tool_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()

        # 创建文件菜单
        file_menu = menu_bar.addMenu("文件")

        # 添加文件菜单项
        new_action = QAction("导入session", self)
        new_action.triggered.connect(self.import_file_dialog)
        file_menu.addAction(new_action)

        open_action = QAction("导出session", self)
        file_menu.addAction(open_action)

        # 添加分隔符
        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 创建编辑菜单
        edit_menu = menu_bar.addMenu("编辑")

        # 添加编辑菜单项
        cut_action = QAction("剪切", self)
        edit_menu.addAction(cut_action)

        copy_action = QAction("复制", self)
        edit_menu.addAction(copy_action)

        paste_action = QAction("粘贴", self)
        edit_menu.addAction(paste_action)


    def import_file_dialog(self):
        folder_dialog = QFileDialog(self)
        folder_dialog.setWindowTitle("选择要导入的文件夹")
        folder_path = folder_dialog.getExistingDirectory()
        if folder_path:
            self.import_folder(folder_path)


    def finish_login(self):
        time.sleep(3)
        print(11111111)
        self.load_init_data()


    # 导入登陆的session
    def import_folder(self, folder_path):
        try:
            phones_sessions = []
            # self.text_edit.clear()
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:
                    if file_name.endswith(".session"):  # 指定要导入的文件后缀
                        phone = re.sub('.session', '', file_name)
                        file_path = os.path.join(root, file_name)
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                            project_directory = sys.path[0]
                            dir = f"{project_directory}/assets/sessions"
                            shutil.copy(file_path, dir)
                            # print(f"文件 '{file_name}' 成功拷贝到目录 {dir}, session文件 {print}")

                            session = (phone, f'{dir}/{file_name}')
                            phones_sessions.append(session)
            self.worker = Worker(phones_sessions)
            self.worker.start()
            self.worker.finished_signal.connect(self.finish_login)

        except Exception as e:
            print(f"导入文件夹失败：{e}")
