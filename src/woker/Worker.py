from config import CONFIG
from PySide6.QtCore import QThread, Signal, Slot
from telegram import TgClient
import asyncio
from cache import TgClientCache


class Worker(QThread):
    login_done = Signal(str)
    

    def __init__(self, phones_sessions):
        super().__init__()
        self.phones_sessions = phones_sessions

    async def run_async(self):
        # print(self.phones_sessions)
        for phone, session_path in self.phones_sessions:
            try:
                print(session_path)
                tgClient = TgClient(phone, session_path)
                await tgClient.login()

                # tgClientCache = TgClientCache()
                # tgClientCache.set_data(phone, tgClient)
                # print(tgClientCache.get_all_data())

                # 登录逻辑，这里假设登录成功后返回用户名
                await tgClient.run()
                self.login_done.emit(f"{phone} 登录成功，用户名：{phone}")  # 发送登录成功信号

            except Exception as e:
                self.login_done.emit(f"{phone} 登录失败：{e}")  # 发送登录失败信号
                continue
        self.finished.emit()

    
    def run(self):
        asyncio.run(self.run_async())