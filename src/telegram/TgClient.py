from telethon.sync import TelegramClient, connection
from telethon.tl.types import InputMessagesFilterVideo
from telethon.network import ConnectionTcpMTProxyAbridged
from telethon import events
from config import CONFIG
from dao import Accounts
from datetime import datetime
import asyncio
import socks

class TgClient:

    def __init__(self) -> None:
        # self.proxy = ('116.162.172.48', 25266, '7gj6WL86hV9OM8iCiIwVh5FhenVyZS5taWNyb3NvZnQuY29t')
        self.accounts = Accounts()
        self.client = None

    async def handle_new_message(self, event):
        # Handle incoming messages
        print(f"Received message from {event.message}")

    async def login_and_run(self, phone_number, session_path, hostname, port, user_name, password):
        try:
            proxy = (socks.SOCKS5 ,hostname, port, True, user_name, password)
            # 创建 MTProxy 连接
            # connection = ConnectionTcpMTProxyAbridged(*proxy_info, loggers=None)
            self.client = TelegramClient(session_path, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0')
            await self.client.start(phone=phone_number)

            await self.client.connect()
 
            self.client.add_event_handler(self.handle_new_message, events.NewMessage)

            me = await self.client.get_me()

            if me:
                columns = ['user_id']
                values = [me.id]
                print(f'Logged in as: {me}')

                result = self.accounts.get_data(columns=columns, values= values)
                print(result)
                if not result:
                    print(result)
                    self.accounts.insert(me.id, me.username, f'{me.first_name} {me.last_name}', phone_number, session_path, 1, 0, datetime.now())

            await self.client.run_until_disconnected()
        except Exception as e:
            print(e)
            


    async def get_dialogs(self):
        if self.client:
            dialogs = await self.client.get_dialogs(limit=None)
            if not dialogs:
                for dialog in dialogs:
                    print(dialog.name)
                return dialogs
        else:
            print("TelegramClient is not initialized.")

    async def run(self):
        if self.client:
            await self.client.run_until_disconnected()
        else:
            print("TelegramClient is not initialized.")
