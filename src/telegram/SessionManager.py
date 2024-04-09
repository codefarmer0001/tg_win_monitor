from telethon.sync import TelegramClient
from telethon.network import ConnectionTcpMTProxyRandomizedIntermediate, TcpMTProxy
from telethon.tl.types import InputPeerUser, PeerUser, PeerChat
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon import events, connection
from config import CONFIG
import asyncio
import socks
from datetime import datetime
from dao import Accounts, MonitorKeyWords
from cache import ContactCache, DialogsCache, MonitorKeyWordsCache, AccountCache
import random
import os
from python_socks import ProxyType

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.cacheUserSession = {}
        self.contactCache = ContactCache()
        self.dialogsCache = DialogsCache()
        self.monitorKeyWordsCache = MonitorKeyWordsCache()
        self.accountCache = AccountCache()
        self.is_run_until = {}

    async def add_session(self, session_name, phone_number=None, hostname = None, port = None, user_name = None, password = None, type = None):
        print(session_name)
        print(f'\n\n\n {hostname} \n\n\n')
        if hostname:
            print(222222)
            client = None
            print(f'type的值为：{type}')
            if type and type == 0:
                proxy = (hostname, port, password)
                client = TelegramClient(session_name, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0', connection=ConnectionTcpMTProxyRandomizedIntermediate, proxy=proxytelethon, timeout=30)
            elif type and type == 1:

                my_proxy = {
                    'proxy_type': ProxyType.SOCKS5,
                    'addr': hostname,
                    'port': port,
                    'username': user_name,
                    'password': password,
                    'rdns': True
                }

                # print('\n\n\n')
                # print(my_proxy)
                # print('\n\n')
                client = TelegramClient(session_name, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0', proxy=my_proxy, timeout=30)
            # print(client)
            if phone_number:
                # print(phone_number)
                # print(44444)
                await self.insert_accounts(client, phone_number, session_name)
                await self.get_dialogs(client, phone_number, session_name)
            client.add_event_handler(self.handle_new_message, events.NewMessage)
            self.sessions[session_name] = client
        else:
            # print(session_name)
            client = TelegramClient(session_name, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0', timeout=30)
            # print(client)
            if phone_number:
                # print(phone_number)
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
        # print(phone_number)
        result = await client.connect()
        # print(result)
        me = await client.get_me()
        # print(me)

        if me:
            self.cacheUserSession[me.id] = client
            # print(self.cacheUserSession)
            columns = ['user_id']
            values = [me.id]
            
            print(phone_number)

            accounts = Accounts()
            result = accounts.get_data(columns=columns, values= values)
            print(result)
            if not result:
                accounts.insert(me.id, me.username, f'{me.first_name} {me.last_name}', phone_number, session_name, 1, 0, datetime.now())
                # account.db.close()
            


    async def handle_new_message(self, event):
        userId = -1

        for user_id, sendMessageClient in self.cacheUserSession.items():
            if event.client is sendMessageClient:
                userId = user_id

        # me = await event.client.get_me()

        # data = self.monitorKeyWordsCache.get_data(me.id)
        print(userId)
        data = self.monitorKeyWordsCache.get_data(userId)
        # print('\n\n\n')
        # print(data)
        if not data:
            self.monitorKeyWords = MonitorKeyWords()
            list = self.monitorKeyWords.get_all()
            # print('\n\n\n')
            # print(list)

            map = {}

            for row, item in enumerate(list):
                # user_id = item['user_id']
                if self.monitorKeyWordsCache.has_key(userId):
                    array = self.monitorKeyWordsCache.get_data(userId)
                    array.append(item)
                    self.monitorKeyWordsCache.set_data(userId, array)
                else:
                    array = [item]
                    self.monitorKeyWordsCache.set_data(userId, array)

            data = self.monitorKeyWordsCache.get_data(userId)

        account = self.accountCache.get_data(userId)
        if not account:
            columns = ['user_id']
            # values = [me.id]
            values = [userId]
            accounts = Accounts()
            account = accounts.get_data(columns=columns, values= values)
            # self.accountCache.set_data(me.id, account)
            self.accountCache.set_data(userId, account)

        await self.send_or_forward_message(event, account, data, 0, True)
        
            

    async def send_or_forward_message(self, event, account, data, flag, forward, max_attempts=10):
        if account['type'] == 1:
            if data:
                print('监控账号')
                for item in data:
                    keywords = item['keyword']
                    if keywords in event.message.message and len(event.message.message) < 20:

                        print(f"Received message from {event.message}")
                        sender = await event.get_sender()

                        if flag == 0:
                            current_working_directory = os.getcwd()
                            print("当前工作目录：", current_working_directory)
                            file_path = f'{current_working_directory}/watch_message.txt'
                            if not os.path.exists(file_path):
                                with open(file_path, 'w+', encoding='utf-8') as file:
                                    file.write(f'@{sender.username}-{sender.id} \n')
                            else:
                                with open(file_path, 'a', encoding='utf-8') as file:
                                    file.write(f'@{sender.username}-{sender.id} \n')

                        # print(item['send_to_group'])
                        try:
                            if forward:
                                forward_result = await event.client.forward_messages(item['send_to_group'], event.message)
                                print('\n\n消息转发结果：\n')
                                print(forward_result)
                                if forward_result:
                                    forward = False
                        except Exception as e:
                            print(e)
                            forward = False
                        
                        forward = False
                        
                        # print(forward_result)
                        try:
                            currtClient = self.get_client(10)
                            send_result = await currtClient.send_message(sender.username, item['send_message'])
                            print('\n\n消息发送：\n')
                            print(send_result)
                            currUser = await currtClient.get_me()
                            currAccount = self.accountCache.get_data(currUser.id)
                            await self.get_dialogs(currtClient, currAccount['phone'], currAccount['session_path'])
                        except Exception as e:
                            print(e)
                            if max_attempts > 0:
                                # return self.get_client(max_attempts - 1)
                                await self.send_or_forward_message(event, account, data, 1, forward, max_attempts - 1)
            else:
                print(f"{account['user_nickname']} 监听账号的监控词为空，请添加监控词")


    def get_client(self, max_attempts=10):
        array = []
        for user_id, sendMessageClient in self.cacheUserSession.items():
            currAccount = self.accountCache.get_data(user_id)
            if currAccount['type'] == 0:
                array.append(sendMessageClient)

        size = len(array)
        if size < 1:
            return None

        random_int = random.randint(0, size - 1)

        client = array[random_int]
        if client.is_connected():
            return client
        elif max_attempts > 0:
            return self.get_client(max_attempts - 1)
        else:
            return None


    async def start_sessions(self, client):
        # print(12345)
        await client.start()
        # await client.connect()
        await client.run_until_disconnected()
        # if userId not in self.is_run_until:
        #     self.is_run_until[userId] = client

    async def run(self):
        await asyncio.gather(*[self.start_sessions(client) for client in self.sessions.values()])
