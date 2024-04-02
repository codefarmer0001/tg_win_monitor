from config import CONFIG
from PySide6.QtCore import QThread, Signal, Slot, QTimer
import asyncio



class Worker(QThread):
    login_done = Signal(str)

    def __init__(self, manager, phones_sessions):
        super().__init__()
        self.phones_sessions = phones_sessions
        self.manager = manager
        self.stopped = False  # 新增一个标志位来表示线程是否应该停止

    async def run_async(self):
        try:

            for phone, session_path, hostname, port, user_name, password in self.phones_sessions:
                await self.manager.add_session(phone, session_path, hostname, port, user_name, password)

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