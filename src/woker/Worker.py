from config import CONFIG
from PySide6.QtCore import QThread, Signal, Slot
# from telegram import TgClient
import asyncio
# from cache import TgClientCache



class Worker(QThread):
    login_done = Signal(str)
    # finished_signal = Signal()

    def __init__(self, manager, phones_sessions):
        super().__init__()
        self.phones_sessions = phones_sessions
        self.manager = manager

    async def run_async(self):
        # print(self.phones_sessions)
        # clients = []
        # tgClient = TgClient()

        for phone, session_path, hostname, port, user_name, password in self.phones_sessions:
            await self.manager.add_session(phone, session_path, hostname, port, user_name, password)

        await self.manager.run()

        # tasks = [tgClient.login_and_run(phone, session_path, hostname, port, user_name, password) for phone, session_path, hostname, port, user_name, password in self.phones_sessions]
        # await asyncio.gather(*tasks)
        # print(222222)
        self.login_done.emit(f"登录成功")


        # for phone, session_path in self.phones_sessions:
        #     try:
        #         # print(session_path)
                
        #         await tgClient.login()


        #         tasks = [tgClient.login_and_run(phone, session_path) for phone, session_path in phones_sessions]
        #         await asyncio.gather(*tasks)

        #         # tgClientCache = TgClientCache()
        #         # tgClientCache.set_data(phone, tgClient)
        #         # print(tgClientCache.get_all_data())

        #         # 登录逻辑，这里假设登录成功后返回用户名
        #         await tgClient.run()
        #         self.login_done.emit(f"{phone} 登录成功，用户名：{phone}")  # 发送登录成功信号

        #         await asyncio.gather(*tasks)

        #     except Exception as e:
        #         self.login_done.emit(f"{phone} 登录失败：{e}")  # 发送登录失败信号
        #         continue
        # self.finished_signal.emit()

    
    def run(self):
        asyncio.run(self.run_async())