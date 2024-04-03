import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QMenu, QDialog, QLineEdit, QFileDialog, QTextEdit, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, Signal, Slot, QObject, QTimer, QThread
import random
import shutil
from widget import CustomItem
import re
from woker import Worker
from dao import Accounts, Proxys, MonitorKeyWords
from telegram import TgClient
import asyncio
from functools import partial
from telegram import SessionManager
from cache import ContactCache, AccountCache
from datetime import datetime

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        # self.accounts = Accounts()
        self.proxys = Proxys()
        self.contactCache = ContactCache()
        self.manager = SessionManager()
        self.accountCache = AccountCache()
        self.monitorKeyWords = MonitorKeyWords()

        self.setWindowTitle("telegram 监控/信息发送")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setWindowIcon(QIcon(":/assets/tg.png"))

        self.setFixedSize(1200, 700)

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
        accounts = Accounts()
        list = accounts.get_all()
        phones_sessions = []
        if list:
            proxy_list = self.proxys.get_all()
            index = 0
            for data in list:
                print(f'proxy代理index：{index % len(proxy_list)}, proxy_list 长度为：{len(proxy_list)}')
                proxy = proxy_list[index % len(proxy_list)]
                index += 1
                session = (data['session_path'], data['phone'], proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'])
                phones_sessions.append(session)

            self.worker = Worker(self.manager, phones_sessions)
            self.worker.login_done.connect(self.finish_login)
            self.worker.start()

        

    def init_account_list(self):
        accounts = Accounts()
        list = accounts.get_all()
        print(list)
        if list:
            self.lift_list_widget.clear()
            for data in list:
                self.accountCache.set_data(data['user_id'], data)
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


    def load_right_data(self, item):
        # 通过 item 获取与之关联的 CustomItem 实例
        custom_item = self.lift_list_widget.itemWidget(item)

        # print(custom_item.item)

        # 获取 CustomItem 中 label1 的文本内容
        custom_text = custom_item.label1.text()
        # 根据左侧列表项的点击加载右侧数据
        # text = item.text()
        self.right_label.setText(f"加载 {custom_text} 的联系人数据")
        self.right_list_widget.clear()

        phone = custom_item.item['phone']  # Assuming item.data() contains the phone information
        session_path = custom_item.item['session_path']  # Assuming item.toolTip() contains the session path information

        dialogs = self.contactCache.get_data(phone)
        if dialogs:
            for dialog in dialogs:
                self.right_list_widget.addItem(f'{dialog.name}')
                # print(dialog)


    def show_context_menu(self, pos):

        selected_item = self.lift_list_widget.currentItem()
        if selected_item:
            self.current_item = self.lift_list_widget.itemWidget(selected_item)
            print("Selected Item:", self.current_item.item)

        # 创建右键菜单
        menu = QMenu(self.lift_list_widget)

        action1 = None
        action2 = None
        action3 = None
        action4 = None
        # 添加菜单项
        if self.current_item and self.current_item.item['type'] == 0:
            action1 = menu.addAction("设为监控账号")
        if self.current_item and self.current_item.item['type'] == 1:
            action2 = menu.addAction("设为消息账号")
        if self.current_item and self.current_item.item['type'] == 0:
            action3 = menu.addAction("发送策略")
        if self.current_item and self.current_item.item['type'] == 1:
            action4 = menu.addAction("监听设定")
        action5 = menu.addAction("启用/停用")

        # 显示菜单，并获取用户选择的操作
        action = menu.exec_(self.lift_list_widget.mapToGlobal(pos))

        # 根据用户选择的操作执行相应的逻辑
        if action1 and action == action1:
            print("执行 Action 1")
            accounts = Accounts()
            accounts.update_account_type(self.current_item.item['id'], 1)
            self.init_account_list()
        elif action2 and action == action2:
            print("执行 Action 2")
            accounts = Accounts()
            accounts.update_account_type(self.current_item.item['id'], 0)
            self.init_account_list()
        elif action3 and action == action3:
            print("执行 Action 3")
            self.open_send_message_modal_window()
        elif action4 and action == action4:
            print("执行 Action 4")
            self.open_watch_message_list_modal_window()
        elif action5 and action == action4:
            print("执行 Action 5")

    def open_send_message_modal_window(self):
        dialog = QDialog(self)
        dialog.resize(450, 400)
        dialog.setWindowTitle("发送设置")
        layout = QVBoxLayout(dialog)

        # 发送速度输入框
        speed_label = QLabel("发送间隔（秒）:")
        speed_input = QLineEdit()
        layout.addWidget(speed_label)
        layout.addWidget(speed_input)

        # 每天发送用户数输入框
        users_label = QLabel("每天发送用户数:")
        users_input = QLineEdit()
        layout.addWidget(users_label)
        layout.addWidget(users_input)

        # 发送周期输入框
        cycle_label = QLabel("每天发送起始时间:")
        cycle_input = QLineEdit()
        layout.addWidget(cycle_label)
        layout.addWidget(cycle_input)

        # 发送时间范围输入框
        time_label = QLabel("每天发送结束时间:")
        time_input = QLineEdit()
        layout.addWidget(time_label)
        layout.addWidget(time_input)

        # 确定按钮
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(dialog.accept)
        layout.addWidget(confirm_button)

        # 显示模态窗口
        dialog.exec_()

    def open_watch_message_list_modal_window(self):
        self.watchListDialog = QDialog(self)
        self.watchListDialog.resize(650, 500)

        # 创建垂直布局，并将表格添加到布局中
        layout = QVBoxLayout(self.watchListDialog)

        list = self.monitorKeyWords.get_all()

        print(list)

        # 创建一个 QTableWidget 实例，并设置行列数
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(list))
        self.tableWidget.setColumnCount(4)

        # 确定按钮
        confirm_button = QPushButton("新增")
        confirm_button.setFixedSize(100, 40)
        confirm_button.clicked.connect(self.open_watch_message_modal_window)
        layout.addWidget(confirm_button)

        # 设置表头标签
        self.tableWidget.setHorizontalHeaderLabels(['关键词', '发送信息', '发送到群组', '操作'])

        # 添加数据到表格中
        for row, item in enumerate(list):
            keywordValue = item['keyword']  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.tableWidget.setItem(row, 0, keywordValue_item)

            keywordValue = item['send_message']  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.tableWidget.setItem(row, 1, keywordValue_item)

            keywordValue = item['send_to_group']  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.tableWidget.setItem(row, 2, keywordValue_item)

        layout.addWidget(self.tableWidget)

        # 设置对话框的主布局
        self.setLayout(layout)

        self.watchListDialog.exec_()

    def open_watch_message_modal_window(self, data=None):

        self.watchListDialog.accept()

        self.watchEditDialog = QDialog(self)
        self.watchEditDialog.resize(450, 400)
        self.watchEditDialog.setWindowTitle("监听列表")
        layout = QVBoxLayout(self.watchEditDialog)

        # 发送速度输入框
        self.key_word_label = QLabel("关键词:")
        self.key_word_input = QLineEdit()
        layout.addWidget(self.key_word_label)
        layout.addWidget(self.key_word_input)

        # 每天发送用户数输入框
        self.send_message_label = QLabel("需要发送信息:")
        self.send_message_input = QTextEdit()
        layout.addWidget(self.send_message_label)
        layout.addWidget(self.send_message_input)

        # 发送速度输入框
        self.send_group_label = QLabel("发送到群组:")
        self.send_group_input = QLineEdit()
        self.send_group_input.setText('@test')
        self.send_group_input.setReadOnly(True)
        layout.addWidget(self.send_group_label)
        layout.addWidget(self.send_group_input)

        # 确定按钮
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(self.save_monitor_key_words)
        layout.addWidget(confirm_button)

        # 显示模态窗口
        self.watchEditDialog.exec_()

    def save_monitor_key_words(self):

        key_word = self.key_word_input.text()
        send_message = self.key_word_input.text()
        send_group = self.send_group_input.text()
        self.monitorKeyWords.insert(self.current_item.item['id'], self.current_item.item['user_id'], key_word, send_message, send_group, datetime.now())

        print(self.current_item.item['user_id'])
        self.watchEditDialog.accept()
        self.open_watch_message_list_modal_window()

    
    def tool_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()

        # 创建文件菜单
        file_menu = menu_bar.addMenu("文件")

        new_socket = QAction("导入代理", self)
        new_socket.triggered.connect(partial(self.import_file_dialog, 'proxy'))
        file_menu.addAction(new_socket)

        file_menu.addSeparator()

        # 添加文件菜单项
        new_action = QAction("导入session", self)
        new_action.triggered.connect(partial(self.import_file_dialog, 'session'))
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


    def import_file_dialog(self, fileType):
        print('测试')
        folder_dialog = QFileDialog(self)
        folder_dialog.setWindowTitle("选择要导入的文件夹")
        folder_path = folder_dialog.getExistingDirectory()
        if folder_path:
            if fileType == 'session':
                self.import_session(folder_path)
            elif fileType == 'proxy':
                 print("proxy")
                 self.import_proxy(folder_path)


    def finish_login(self):
        # time.sleep(3)
        print(343423432)
        self.init_account_list()


    # 导入登陆的session
    def import_session(self, folder_path):
        try:
            phones_sessions = []
            proxy_list = self.proxys.get_all()
            print(proxy_list)
            index = 0
            # self.text_edit.clear()
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:
                    if file_name.endswith(".session"):  # 指定要导入的文件后缀
                        print(f'proxy代理index：{index % len(proxy_list)}, proxy_list 长度为：{len(proxy_list)}')
                        proxy = proxy_list[index % len(proxy_list)]
                        index += 1
                        phone = re.sub('.session', '', file_name)
                        file_path = os.path.join(root, file_name)
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                            project_directory = sys.path[0]
                            dir = f"{project_directory}/assets/sessions"
                            shutil.copy(file_path, dir)
                            session = (f'{dir}/{file_name}', phone, proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'])
                            phones_sessions.append(session)
            self.worker = Worker(self.manager, phones_sessions)
            self.worker.login_done.connect(self.finish_login)
            self.worker.start()
                            
            # await self.manager.start_sessions()

        except Exception as e:
            print(f"导入文件夹失败：{e}")


    # 导入登陆用的代理proxy
    def import_proxy(self, folder_path):
        try:
            # self.text_edit.clear()
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:
                    if file_name.endswith(".proxy"):  # 指定要导入的文件后缀
                        print(file_name)
                        file_path = os.path.join(root, file_name)
                        with open(file_path, 'r') as file:
                            # 逐行读取文件内容
                            for line in file:
                                try:
                                    if line.strip().count(":") == 3:
                                        proxy_arr = line.strip().split(":")
                                        self.proxys.insert(proxy_arr[0], proxy_arr[1], proxy_arr[2], proxy_arr[3])
                                except Exception as e:
                                    print(f"导入代理失败：{e}")
                                    continue
        except Exception as e:
            print(f"导入代理失败：{e}")
