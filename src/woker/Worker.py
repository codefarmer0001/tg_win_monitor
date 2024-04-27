from config import CONFIG
from PySide6.QtCore import QThread, Signal, Slot, QTimer
import asyncio
from dao import Accounts
import os


class Worker(QThread):
    login_done = Signal(str)

    def __init__(self, manager):
        super().__init__()
        # self.phones_sessions = phones_sessions
        self.manager = manager
        self.stopped = False  # 新增一个标志位来表示线程是否应该停止
        

    async def run_async(self):
        try:

            for session_path, phone, hostname, port, user_name, password, type, proxy_id in self.phones_sessions:
                print(f'{session_path}, {phone}, {hostname}, {port}, {user_name}, {password}, {type}, {proxy_id}')
                try:
                    await self.manager.add_session(session_path, phone, hostname, port, user_name, password, type, proxy_id)
                except Exception as e:
                    print(e)
                    if 'The user has been deleted/deactivated' in str(e):

                        # print('The user has been deleted/deactivated' in str(e))
                        # print(f'手机号为：{phone}， session文件为：{session_path} 的账号已被telegram官方删除')
                        self.accounts = Accounts()
                        self.accounts.delete_account_by_phoen(phone)
                    elif 'The authorization key (session file) was used under two different IP addresses simultaneously' in str(e):
                        print(f'手机号为：{phone}， session文件为：{session_path} 的账号同一个session被不同ip登录')
                    elif 'Server closed the connection: [WinError 64]' in str(e):
                        print(f'手机账号')
                    continue
                
                self.login_done.emit(f"登录成功")
                print(f'手机号：{phone}登录完整')
            
            

            await self.manager.run()
        except Exception as e:
            print(e)

    
    def run(self):
        asyncio.run(self.run_async())


    def set_sessions(self, phones_sessions):
        self.phones_sessions = phones_sessions

    def re_login(self):
        self.manager.stop_connect()