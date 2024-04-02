from telethon.sync import TelegramClient
from telethon import events
from config import CONFIG
import asyncio
import socks
from datetime import datetime
from dao import Accounts

class SessionManager:
    def __init__(self):
        self.accounts = Accounts()
        self.sessions = {}

    async def add_session(self, phone_number, session_name, hostname = None, port = None, user_name = None, password = None):
        print(phone_number)
        print(session_name)
        if not hostname:
            proxy = (socks.SOCKS5 ,hostname, port, True, user_name, password)
            client = TelegramClient(session_name, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0', proxy=proxy)
            # print(client)
            await self.insert_accounts(client, phone_number, session_name)
            client.add_event_handler(self.handle_new_message, events.NewMessage)
            self.sessions[session_name] = client
        else:
            client = TelegramClient(session_name, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0')
            # print(client)
            await self.insert_accounts(client, phone_number, session_name)
            client.add_event_handler(self.handle_new_message, events.NewMessage)
            self.sessions[session_name] = client
        return self.sessions[session_name]
    
    
    async def insert_accounts(self, client, phone_number, session_name):

        await client.connect()
        me = await client.get_me()
        print(me)
        
        columns = ['user_id']
        values = [me.id]
        print(f'Logged in as: {me}')

        result = self.accounts.get_data(columns=columns, values= values)
        print(result)
        if not result:
            print(result)
            self.accounts.insert(me.id, me.username, f'{me.first_name} {me.last_name}', phone_number, session_name, 1, 0, datetime.now())


    async def handle_new_message(self, event):
        # 处理接收到的新消息
        print(f"Received message from {event.message}")


    async def start_sessions(self, client):
        print(12345)
        await client.start()
        await client.connect()
        # me = await client.get_me()
        # print(me)
        await client.run_until_disconnected()
        # await asyncio.gather(*[client.run_until_disconnected() for client in self.sessions.values()])

    async def run(self):
        await asyncio.gather(*[self.start_sessions(client) for client in self.sessions.values()])
