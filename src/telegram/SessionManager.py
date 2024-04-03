from telethon.sync import TelegramClient
from telethon import events
from config import CONFIG
import asyncio
import socks
from datetime import datetime
from dao import Accounts
from cache import ContactCache

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.contactCache = ContactCache()

    async def add_session(self, session_name, phone_number=None, hostname = None, port = None, user_name = None, password = None):
        # print(phone_number)
        # print(session_name)
        if not hostname:
            proxy = (socks.SOCKS5 ,hostname, port, True, user_name, password)
            client = TelegramClient(session_name, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0', proxy=proxy)
            if phone_number:
                await self.insert_accounts(client, phone_number, session_name)
                await self.get_dialogs(client, phone_number, session_name)
            client.add_event_handler(self.handle_new_message, events.NewMessage)
            self.sessions[session_name] = client
        else:
            client = TelegramClient(session_name, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0')
            if phone_number:
                await self.insert_accounts(client, phone_number, session_name)
                await self.get_dialogs(client, phone_number, session_name)
            client.add_event_handler(self.handle_new_message, events.NewMessage)
            self.sessions[session_name] = client
        return self.sessions[session_name]
    
    
    async def get_dialogs(self, client, phone_number, session_name):
        if client:
            dialogs = await client.get_dialogs(limit=None)
            if dialogs:
                self.contactCache.set_data(phone_number, dialogs)

    
    async def insert_accounts(self, client, phone_number, session_name):

        await client.connect()
        me = await client.get_me()

        if me:
            columns = ['user_id']
            values = [me.id]

            accounts = Accounts()
            result = accounts.get_data(columns=columns, values= values)
            if not result:
                accounts.insert(me.id, me.username, f'{me.first_name} {me.last_name}', phone_number, session_name, 1, 0, datetime.now())
            


    async def handle_new_message(self, event):
        # 处理接收到的新消息
        print(f"Received message from {event.message}")


    async def start_sessions(self, client):
        print(12345)
        await client.start()
        await client.connect()
        await client.run_until_disconnected()

    async def run(self):
        await asyncio.gather(*[self.start_sessions(client) for client in self.sessions.values()])
