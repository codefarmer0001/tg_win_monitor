from config import CONFIG
from PySide6.QtCore import QThread, Signal, Slot, QTimer
import asyncio
from dao import Accounts


class Worker(QThread):
    login_done = Signal(str)

    def __init__(self, manager, phones_sessions):
        super().__init__()
        self.phones_sessions = phones_sessions
        self.manager = manager
        self.stopped = False  # 新增一个标志位来表示线程是否应该停止
        

    async def run_async(self):
        try:

            for session_path, phone, hostname, port, user_name, password, type in self.phones_sessions:
                try:
                    await self.manager.add_session(session_path, phone, hostname, port, user_name, password, type)
                except Exception as e:
                    # print('\n\n\n')
                    # print(phone)
                    # print(session_path)
                    # print(hostname)
                    # print(port)
                    # print(user_name)
                    # print(password)
                    # print(f'登陆失败，手机号为：{phone}')
                    print(e)
                    print('The user has been deleted/deactivated' in str(e))
                    if 'The user has been deleted/deactivated' in str(e):
                        print(f'手机号为：{phone}， session文件为：{session_path} 的账号已被telegram官方删除')
                    elif 'The authorization key (session file) was used under two different IP addresses simultaneously' in str(e):
                        print(f'手机号为：{phone}， session文件为：{session_path} 的账号同一个session被不同ip登录')
                    elif 'Server closed the connection: [WinError 64]' in str(e):
                        print(f'手机账号')
                    self.accounts = Accounts()
                    self.accounts.delete_account_by_phoen(phone)
                    # print(f'删除数据：{phone}')
                    # print('\n\n\n')
                    continue
                    

            # if self.stop:
            #     return
            
            self.login_done.emit(f"登录成功")
            print('登陆数据完成')
            # QTimer.singleShot(0, lambda: self.login_done.emit("登录成功"))

            await self.manager.run()
        except Exception as e:
            print(e)


    # def stop(self):
    #     self.stopped = True  # 设置停止标志位
    
    def run(self):
        asyncio.run(self.run_async())