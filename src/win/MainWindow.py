import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QMenu, QDialog, QLineEdit, QFileDialog, QTextEdit, QTableWidget, QTableWidgetItem, QWidget
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
from cache import ContactCache, AccountCache, MonitorKeyWordsCache
from datetime import datetime
from utils import ProxyCheck
import time
import threading

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        # self.accounts = Accounts()
        self.proxys = Proxys()
        self.contactCache = ContactCache()
        self.manager = SessionManager()
        self.accountCache = AccountCache()
        self.monitorKeyWords = MonitorKeyWords()
        self.monitorKeyWordsCache = MonitorKeyWordsCache()
        self.proxyCheck = ProxyCheck()

        self.worker = Worker(self.manager)

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
        # self.load_init_data()

        self.load_keyword_data()
        # asyncio.run(self.checkout_proxy())

    # 检车代理是否正常
    def checkout_proxy(self):
    #     while True:
        proxy_list = self.proxys.get_all()
        if len(proxy_list) > 0:
            for proxy in proxy_list:
                connect_time = True
                if proxy['type'] == 0:
                    connect_time = self.proxyCheck.check_mt_proxy(proxy['hostname'], proxy['port'], proxy['password'])
                else:
                    connect_time = self.proxyCheck.check_socket_proxy(proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'])
                if connect_time > 0:
                    self.proxys.update_proxy_status(proxy['id'], 1, f"{connect_time:.3g}")
                else:
                    self.proxys.update_proxy_status(proxy['id'], 0, -1)

        
        self.load_proxy.accept()
        self.import_proxy_loading('proxy')
                # if not flag:
                #     self.proxys.delete_by_id(proxy['id'])
    #         time.sleep(60)

    # 加载左侧账号的数据
    def load_init_data(self):
        accounts = Accounts()
        list = accounts.get_all()
        phones_sessions = []
        if list:
            proxy_list = self.proxys.get_all()
            index = 0
            for data in list:
                proxy = {}
                proxy['hostname'] = None
                proxy['port'] = None
                proxy['user_name'] = None
                proxy['password'] = None
                proxy['type'] = None
                # session = (data['session_path'], data['phone'], proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'])
                if data['type'] == 1:
                    session = (data['session_path'], data['phone'], None, None, None, None, None)
                else:
                    if len(proxy_list) > 0:
                        print(f'proxy代理index：{index % len(proxy_list)}, proxy_list 长度为：{len(proxy_list)}')
                        proxy = proxy_list[index % len(proxy_list)]
                        index += 1
                    session = (data['session_path'], data['phone'], proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'], proxy['type'])
                phones_sessions.append(session)

            
            self.worker.set_sessions(phones_sessions)
            self.worker.login_done.connect(self.finish_login)
            self.worker.start()


    def load_keyword_data(self):
        list = self.monitorKeyWords.get_all()

        map = {}

        for row, item in enumerate(list):
            user_id = item['user_id']
            if self.monitorKeyWordsCache.has_key(user_id):
                array = self.monitorKeyWordsCache.get_data(user_id)
                array.append(item)
                self.monitorKeyWordsCache.set_data(user_id, array)
            else:
                array = [item]
                self.monitorKeyWordsCache.set_data(user_id, array)
        # print("adfafadf")
        # print(self.monitorKeyWordsCache.get_all_data())
        # print("adfafadf")
        # pass

        

    def init_account_list(self):
        accounts = Accounts()
        list = accounts.get_all()
        print(list)
        self.lift_list_widget.clear()
        if list:
            for data in list:
                self.accountCache.set_data(data['user_id'], data)
                custom_item = CustomItem(data, '监控账号' if data['type'] == 1 else '消息账号', data['online'])
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
        # if self.current_item and self.current_item.item['type'] == 0:
        #     action3 = menu.addAction("发送策略")
        if self.current_item and self.current_item.item['type'] == 1:
            action4 = menu.addAction("监听设定")
        action5 = menu.addAction("删除")

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
        elif action5 and action == action5:
            print("执行 Action 5")
            accounts = Accounts()
            accounts.delete_by_id(self.current_item.item['id'])
            self.init_account_list()

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

        self.setLayout(None)
        self.watchListDialog = QDialog(self)
        self.watchListDialog.resize(650, 500)

        # 创建垂直布局，并将表格添加到布局中
        self.watchListDialogLayout = QVBoxLayout(self.watchListDialog)


        # 创建一个空的QWidget对象
        buttons_container = QWidget()
        self.watchBottonsLayout = QHBoxLayout(buttons_container)

        # 确定按钮
        add_button = QPushButton("新增")
        add_button.setFixedSize(100, 40)
        add_button.clicked.connect(self.open_watch_message_modal_window)
        self.watchBottonsLayout.addWidget(add_button)

        import_button = QPushButton("导入")
        import_button.setFixedSize(100, 40)
        import_button.clicked.connect(self.import_key_words)
        self.watchBottonsLayout.addWidget(import_button)

        export_button = QPushButton("导出")
        export_button.setFixedSize(100, 40)
        export_button.clicked.connect(self.export_key_words)
        self.watchBottonsLayout.addWidget(export_button)

        self.watchListDialogLayout.addWidget(buttons_container)

        # 设置对话框的主布局
        # self.setLayout(self.watchListDialogLayout)

        columns = ['user_id']
        values = [self.current_item.item['user_id']]

        list = self.monitorKeyWords.get_data(columns=columns, values=values)
        if not list:
            list = []
        # if len(list) == 1:
        #     list = [list]
        print(list)
        self.monitorKeyWordsCache.set_data(self.current_item.item['user_id'], list)


        # 创建一个 QTableWidget 实例，并设置行列数
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(list))
        self.tableWidget.setColumnCount(4)
        self.watchListDialogLayout.addWidget(self.tableWidget)

        # Set column width and row height
        self.tableWidget.setColumnWidth(2, 150)  # Set column 0 width
        self.tableWidget.setColumnWidth(3, 200)  # Set column 1 width

        # 设置表头标签
        self.tableWidget.setHorizontalHeaderLabels(['关键词', '发送信息', '发送到群组', '操作'])

        # 添加数据到表格中
        for row, item in enumerate(list):
            
            self.tableWidget.setRowHeight(row, 50)

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


            menuitem = QTableWidgetItem()

            widget = MultiButtonWidget(self, item)
            
            menuitem.setFlags(menuitem.flags() ^ Qt.ItemIsEditable)  # 设置值为只读

            self.tableWidget.setItem(row, 3, menuitem)
            self.tableWidget.setCellWidget(row, 3, widget)

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
        print(data)
        if data:
            self.key_word_input.setText(data['keyword'])
        layout.addWidget(self.key_word_label)
        layout.addWidget(self.key_word_input)

        # 每天发送用户数输入框
        self.send_message_label = QLabel("需要发送信息:")
        self.send_message_input = QTextEdit()
        if data:
            self.send_message_input.setText(data['send_message'])
        layout.addWidget(self.send_message_label)
        layout.addWidget(self.send_message_input)

        # 发送速度输入框
        self.send_group_label = QLabel("发送到群组:")
        self.send_group_input = QLineEdit()
        if data:
            self.send_group_input.setText(data['send_to_group'])
        layout.addWidget(self.send_group_label)
        layout.addWidget(self.send_group_input)

        # 确定按钮
        confirm_button = QPushButton("确定")
        if not data:
            confirm_button.clicked.connect(self.save_monitor_key_words)
        else:
            confirm_button.clicked.connect(partial(self.update_monitor_key_words, data['id']))
        layout.addWidget(confirm_button)

        # 显示模态窗口
        self.watchEditDialog.exec_()

    def save_monitor_key_words(self):

        key_word = self.key_word_input.text()
        send_message = self.send_message_input.toPlainText()
        send_group = self.send_group_input.text()
        self.monitorKeyWords.insert(self.current_item.item['user_id'], self.current_item.item['id'], key_word, send_message, send_group, datetime.now())

        print(self.current_item.item['user_id'])
        self.watchEditDialog.accept()
        self.open_watch_message_list_modal_window()


    def update_monitor_key_words(self, id):
        key_word = self.key_word_input.text()
        send_message = self.send_message_input.toPlainText()
        send_group = self.send_group_input.text()
        self.monitorKeyWords.update_by_id(id, key_word, send_message, send_group)

        print(self.current_item.item['user_id'])
        self.watchEditDialog.accept()
        self.open_watch_message_list_modal_window()

    def delete_monitor_key_words(self, id):
        self.monitorKeyWords.delete_by_id(id)
        self.watchListDialog.accept()
        self.open_watch_message_list_modal_window()

    
    def tool_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()

        # 创建文件菜单
        file_menu = menu_bar.addMenu("文件")

        new_socket = QAction("导入代理", self)
        # self.import_proxy_loading()
        new_socket.triggered.connect(partial(self.import_proxy_loading, 'proxy'))
        file_menu.addAction(new_socket)

        # file_menu.addSeparator()

        # # 添加文件菜单项
        # new_action = QAction("导入session", self)
        # new_action.triggered.connect(partial(self.import_file_dialog, 'session'))
        # file_menu.addAction(new_action)

        # open_action = QAction("导出session", self)
        # file_menu.addAction(open_action)

        # 添加分隔符
        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # # 创建编辑菜单
        edit_menu = menu_bar.addMenu("账号")

        # # 添加编辑菜单项
        cut_action = QAction("登录", self)
        cut_action.triggered.connect(self.login_session)
        edit_menu.addAction(cut_action)

        # copy_action = QAction("复制", self)
        # edit_menu.addAction(copy_action)

        # paste_action = QAction("粘贴", self)
        # edit_menu.addAction(paste_action)

    def login_session(self):
        accounts = Accounts()
        accounts.update_account_online()
        self.worker.re_login()
        self.init_account_list()
        current_working_directory = os.getcwd()
        print("当前工作目录：", current_working_directory)
        file_path = f'{current_working_directory}\session'
        print(file_path)
        self.import_session(file_path)
        # pass


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
                #  asyncio.run(self.import_proxy_loading())
                
                asyncio.run(self.import_proxy(folder_path))


    def finish_login(self):
        # time.sleep(3)
        print(343423432)
        self.init_account_list()


    # 导入登陆的session
    def import_session(self, folder_path):
        print(folder_path)
        # try:
        if 1 == 1:
            sessionMap = {}
            phones_sessions = []
            columns = ['status']
            values = [1]
            proxy_list = self.proxys.get_all_by_status(columns, values)
            print(proxy_list)
            proxyMap = {}
        
            for proxy_item in proxy_list:
                proxyMap[proxy_item['id']] = proxy_item

            index = 0
            
            accounts = Accounts()
            list = accounts.get_all()
            if list:
                proxy_list = self.proxys.get_all()
                index = 0
                for data in list:
                    proxy = {}
                    proxy['hostname'] = None
                    proxy['port'] = None
                    proxy['user_name'] = None
                    proxy['password'] = None
                    proxy['type'] = None
                    proxy['id'] = -1
                    if data['status'] == 1:
                        if not data['proxy_id']:
                            # print(data['proxy_id'])
                            proxy = proxyMap[data['proxy_id']]
                            print(f'1\n\n\n')
                            print(f"代理id：{data['proxy_id']}")
                            print(proxy)
                            print(f'1\n\n\n')
                        elif len(proxy_list) > 0:
                            print(f'proxy代理index：{index % len(proxy_list)}, proxy_list 长度为：{len(proxy_list)}')
                            proxy = proxy_list[index % len(proxy_list)]
                            index += 1
                        sessionMap[data['session_path']] = data['session_path']
                        session = (data['session_path'], data['phone'], proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'], proxy['type'], proxy['id'])
                        phones_sessions.append(session)


            
            # self.text_edit.clear()
            for root, dirs, files in os.walk(folder_path):
                print(111111111)
                for file_name in files:
                    print(file_name)
                    if file_name.endswith(".session") and file_name not in sessionMap:  # 指定要导入的文件后缀
                        proxy = {}
                        proxy['hostname'] = None
                        proxy['port'] = None
                        proxy['user_name'] = None
                        proxy['password'] = None
                        proxy['type'] = None
                        proxy['id'] = -1
                        # print()
                        if len(proxy_list) > 0:
                            print(f'proxy代理index：{index % len(proxy_list)}, proxy_list 长度为：{len(proxy_list)}')
                            proxy = proxy_list[index % len(proxy_list)]
                            index += 1
                        phone = re.sub('.session', '', file_name)

                        print(proxy)
                        
                        print(f'{root}\{file_name}')

                        session = (f'{root}\{file_name}', phone, proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'], proxy['type'], proxy['id'])
                        phones_sessions.append(session)
                        print(phones_sessions)
                        # file_path = os.path.join(root, file_name)
                        # with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                        #     # project_directory = sys.path[0]
                        #     # dir = f"{project_directory}\\assets\\sessions"
                        #     # dir = f"{project_directory}"
                        #     project_directory = user_home_dir = os.path.expanduser("~")
                        #     # project_directory = "C:\\Users\\walle\\AppData\\Local\\tgmonitor"
                        #     project_directory = f"{project_directory}\\AppData\\Local\\tgmonitor"
                        #     dir = project_directory
                        #     # print(dir)
                        #     # print(not os.path.exists(dir))
                        #     if not os.path.exists(dir):
                        #         print(f'create folder "{dir}" ')
                        #         os.makedirs(dir, exist_ok=True)
                        #         print(f"Folder '{dir}' created successfully.")
                        #     else:
                        #         print(f"Folder '{dir}' already exists.")
                        #     shutil.copy(file_path, dir)
                        #     # session = (f'{dir}/{file_name}', phone, proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'])
                        #     session = (f'{dir}/{file_name}', phone, proxy['hostname'], proxy['port'], proxy['user_name'], proxy['password'], proxy['type'])
                        #     phones_sessions.append(session)
            # self.worker = Worker(self.manager, phones_sessions)


            
            self.worker.set_sessions(phones_sessions)
            self.worker.login_done.connect(self.finish_login)
            self.worker.start()
                            
            # await self.manager.start_sessions()

        # except Exception as e:
        #     print(f"导入文件夹失败：{e}")


    def import_proxy_loading(self, fileType):
        print('测试')
        self.load_proxy = QDialog(self)
        self.load_proxy.resize(650, 400)

        layout = QVBoxLayout(self.load_proxy)


        # 创建一个空的QWidget对象
        buttons_container = QWidget()
        self.importProxyBottonsLayout = QHBoxLayout(buttons_container)

        # # 确定按钮
        # add_button = QPushButton("新增")
        # add_button.setFixedSize(100, 40)
        # add_button.clicked.connect(self.open_watch_message_modal_window)
        # self.importProxyBottonsLayout.addWidget(add_button)

        import_button = QPushButton("导入")
        import_button.setFixedSize(100, 40)
        # import_file_dialog
        import_button.clicked.connect(partial(self.import_file_dialog, 'proxy'))
        self.importProxyBottonsLayout.addWidget(import_button)

        export_button = QPushButton("网络检测")
        export_button.setFixedSize(100, 40)
        export_button.clicked.connect(self.checkout_proxy)
        self.importProxyBottonsLayout.addWidget(export_button)

        layout.addWidget(buttons_container)


        list = self.proxys.get_all()
        if not list:
            list = []
        print(list)

        # 创建一个 QTableWidget 实例，并设置行列数
        self.proxyTableWidget = QTableWidget()
        self.proxyTableWidget.setRowCount(len(list))
        self.proxyTableWidget.setColumnCount(7)

        self.proxyTableWidget.setHorizontalHeaderLabels(['代理host', '端口号', '账号', '密码', '连接时长', '状态', '操作'])

        # 添加数据到表格中
        for row, item in enumerate(list):
            keywordValue = item['hostname']  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.proxyTableWidget.setItem(row, 0, keywordValue_item)

            keywordValue = item['port']  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.proxyTableWidget.setItem(row, 1, keywordValue_item)

            keywordValue = item['user_name']  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.proxyTableWidget.setItem(row, 2, keywordValue_item)

            keywordValue = item['password']  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.proxyTableWidget.setItem(row, 3, keywordValue_item)

            keywordValue = item['connect_time']  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.proxyTableWidget.setItem(row, 4, keywordValue_item)

            
            keywordValue = '正常' if item['status'] == 1 else '异常'  # 获取值（value）
            keywordValue_item = QTableWidgetItem(str(keywordValue))
            keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读
            self.proxyTableWidget.setItem(row, 5, keywordValue_item)


            # # 创建按钮和按钮所在的布局
            # button = QPushButton("Click me")
            # layout = QHBoxLayout()
            # layout.addWidget(button)
            # layout.setAlignment(button, Qt.AlignCenter)

            # # 创建 QWidget 作为单元格的容器，并将布局设置给它
            # cellWidget = QWidget()
            # cellWidget.setLayout(layout)

            
            # keywordValue = item['password']  # 获取值（value）
            # keywordValue_item = QTableWidgetItem()
            # keywordValue_item.setData(0, button)
            # keywordValue_item.setFlags(keywordValue_item.flags() ^ Qt.ItemIsEditable)  # 设置值为只读

            menuitem = QTableWidgetItem()

            widget = ButtonWidget(self, item['id'])
            
            menuitem.setFlags(menuitem.flags() ^ Qt.ItemIsEditable)  # 设置值为只读

            self.proxyTableWidget.setItem(row, 6, menuitem)
            self.proxyTableWidget.setCellWidget(row, 6, widget)

            

            # self.proxyTableWidget.setItem(row, 6, cellWidget)

        layout.addWidget(self.proxyTableWidget)

        # 设置对话框的主布局
        self.setLayout(layout)

        self.load_proxy.exec_()

    def delete_proxy_by_id(self, id):
        proxys = Proxys()
        proxys.delete_by_id(id)
        self.load_proxy.accept()
        self.import_proxy_loading('proxy')


    # 导入登陆用的代理proxy
    async def import_proxy(self, folder_path):
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
                                    if line and line.strip().startswith("tg://proxy?"):
                                        url_arry = line.split('?')
                                        print(url_arry)
                                        if url_arry[1]:
                                            params_arry = url_arry[1].split('&')
                                            hostname = ''
                                            port = ''
                                            password = ''
                                            for param in params_arry:
                                                if param:
                                                    data_arry = param.split('=')
                                                    if data_arry[0] == 'server':
                                                        hostname = data_arry[1]
                                                    if data_arry[0] == 'port':
                                                        port = data_arry[1]
                                                    if data_arry[0] == 'secret':
                                                        password = data_arry[1]
                                            self.proxys.insert(hostname, port, '', password, 0)
                                    if line.strip().count(":") == 3:
                                        proxy_arr = line.strip().split(":")
                                        self.proxys.insert(proxy_arr[0], proxy_arr[1], proxy_arr[2], proxy_arr[3], 1)
                                    if line and line.strip().startswith("https://t.me/socks"):
                                        url_arry = line.split('?')
                                        print(url_arry)
                                        if url_arry[1]:
                                            params_arry = url_arry[1].split('&')
                                            hostname = ''
                                            port = ''
                                            user_name = ''
                                            password = ''
                                            for param in params_arry:
                                                if param:
                                                    data_arry = param.split('=')
                                                    if data_arry[0] == 'server':
                                                        hostname = data_arry[1]
                                                    if data_arry[0] == 'port':
                                                        port = data_arry[1]
                                                    if data_arry[0] == 'user':
                                                        user_name = data_arry[1]
                                                    if data_arry[0] == 'pass':
                                                        password = data_arry[1]
                                            self.proxys.insert(hostname, port, user_name, password, 1)
                                except Exception as e:
                                    print(e)
                                # try:
                                #     if line.strip().count(":") == 3:
                                #         proxy_arr = line.strip().split(":")
                                #         self.proxys.insert(proxy_arr[0], proxy_arr[1], proxy_arr[2], proxy_arr[3])
                                # except Exception as e:
                                #     print(f"导入代理失败：{e}")
                                #     continue
            self.checkout_proxy()
            print('123123123')
            # self.load_proxy
        except Exception as e:
            print(f"导入代理失败：{e}")


    def import_key_words(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("选择要导入的文件")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Text files (*.txt)")

        file_path, _ = file_dialog.getOpenFileName()

        if file_path:
            # 处理选定的文件路径
            print("选择的文件路径:", file_path)
            # 在这里可以调用处理文件的函数，比如导入文件的操作
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        # 处理每一行的内容，例如打印到控制台
                        print(line.strip())  # 使用 strip() 方法去除行尾的换行符或空格
                        txt = line.strip()
                        array = txt.split("#¥#")
                        print(array)
                        if len(array) == 3:
                            keyword = array[0]
                            sendMsg = array[1]
                            forward_group = array[2]
                            self.monitorKeyWords = MonitorKeyWords()
                            columns = ['user_id', 'keyword']
                            values = [self.current_item.item['user_id'], keyword]
                            result = self.monitorKeyWords.get_data(columns, values)
                            if not result:
                                self.monitorKeyWords.insert(self.current_item.item['user_id'], self.current_item.item['id'], keyword, sendMsg, forward_group, datetime.now())
                self.watchListDialog.accept()
                self.open_watch_message_list_modal_window()
            except FileNotFoundError:
                print(f"File '{file_path}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("未选择文件")

    def export_key_words(self):
        # 创建文件保存对话框
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setWindowTitle("选择文件夹")

        self.monitorKeyWords = MonitorKeyWords()
        columns = ['user_id']
        values = [self.current_item.item['user_id']]
        result = self.monitorKeyWords.get_data(columns, values)

        # 获取选择的文件夹路径
        folder_path = file_dialog.getExistingDirectory()
        if folder_path and result:
            userId = self.current_item.item['user_id']
            # 打开文件并写入内容
            file_path = f"{folder_path}/{userId}.txt"
            with open(file_path, "w", encoding='utf-8') as file:
                # file.write("这是要导出的文件内容。")
                for item in result:
                    file.write(f"{item['keyword']}#¥#{item['send_message']}#¥#{item['send_to_group']}\n")
                    
            print(f"文件已导出到：{file_path}")        


class MultiButtonWidget(QWidget):
    def __init__(self, mainWindow, data, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.button1 = QPushButton("修改")
        self.button1.clicked.connect(partial(mainWindow.open_watch_message_modal_window, data))
        self.button1.setFixedSize(80, 36)
        self.button2 = QPushButton("删除")
        self.button2.clicked.connect(partial(mainWindow.delete_monitor_key_words, data['id']))
        self.button2.setFixedSize(80, 36)
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.setLayout(self.layout)


class ButtonWidget(QWidget):
    def __init__(self, mainWindow, data, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.button = QPushButton('删除')
        self.button.clicked.connect(partial(mainWindow.delete_proxy_by_id, data))
        layout.addWidget(self.button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)