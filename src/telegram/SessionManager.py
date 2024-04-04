from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, PeerUser, PeerChat
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon import events
from config import CONFIG
import asyncio
import socks
from datetime import datetime
from dao import Accounts
from cache import ContactCache, DialogsCache, MonitorKeyWordsCache, AccountCache

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.cacheUserSession = {}
        self.contactCache = ContactCache()
        self.dialogsCache = DialogsCache()
        self.monitorKeyWordsCache = MonitorKeyWordsCache()
        self.accountCache = AccountCache()

    async def add_session(self, session_name, phone_number=None, hostname = None, port = None, user_name = None, password = None):
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
            self.cacheUserSession[me.id] = client
            # print(self.cacheUserSession)
            columns = ['user_id']
            values = [me.id]
            

            accounts = Accounts()
            result = accounts.get_data(columns=columns, values= values)
            if not result:
                accounts.insert(me.id, me.username, f'{me.first_name} {me.last_name}', phone_number, session_name, 1, 0, datetime.now())
            


    async def handle_new_message(self, event):
        me = await event.client.get_me()
        # print(f'接受者ID：{me.id}')
        # print(self.monitorKeyWordsCache.get_all_data())
        # 处理接收到的新消息
        print(f"Received message from {event.message}")
        # peer_id = event.message.peer_id

        data = self.monitorKeyWordsCache.get_data(me.id)
        # print(data)
        account = self.accountCache.get_data(me.id)
        # print(account)
        if account['type'] == 1:
            print('监控账号')
            for item in data:
                keywords = item['keyword']
                if keywords in event.message.message:
                    # 构造要发送的消息内容
                    # message = f"Hello! This is a reply message from ."
                    # print(item['send_to_group'])
                    # print(message)
                    # 使用 event.client 发送消息
                    # 获取消息发送者的用户 ID
                    print(event.message)
                    sender_id = event.message.from_id.user_id
                    sender = await event.get_sender()
                    print(sender)
                    # print(sender_id)
                    # print(sender.id)
                    # 构造要转发的消息 ID 列表
                    message_ids = [event.message.id]
                    # await event.client.forward_messages(me.id, message_ids, from_peer=sender_id)
                    # print(sendMessageClient.is_connected())

                    await event.client.forward_messages(item['send_to_group'], event.message)
                    for user_id, sendMessageClient in self.cacheUserSession.items():
                        # print(user_id)
                        # currentMe = await sendMessageClient.get_me()
                        # print(currentMe)
                        # print(sendMessageClient)
                        try:
                            currAccount = self.accountCache.get_data(user_id)
                            if currAccount['type'] == 0:
            
                                if sender.username:
                                    await sendMessageClient.send_message(sender.username, item['send_message'])
                                    break
                        except Exception as e:
                            print(e)
                            continue

        # print(f'接受者ID：{me.id}')


    async def start_sessions(self, client):
        # print(12345)
        await client.start()
        await client.connect()
        await client.run_until_disconnected()

    async def run(self):
        await asyncio.gather(*[self.start_sessions(client) for client in self.sessions.values()])
