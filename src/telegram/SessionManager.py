from telethon.sync import TelegramClient
from telethon.network import ConnectionTcpMTProxyRandomizedIntermediate, TcpMTProxy
from telethon.tl.types import InputPeerUser, PeerUser, PeerChat, ChannelParticipantsAdmins, PeerChannel
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon import events, connection
from telethon.sessions import SQLiteSession
from config import CONFIG
import asyncio
import socks
from datetime import datetime
from dao import Accounts, MonitorKeyWords, SearchRecords, GroupAdmins
from cache import ContactCache, DialogsCache, MonitorKeyWordsCache, AccountCache, GroupSAdminCache
import random
import os
from python_socks import ProxyType
from datetime import datetime, timezone


class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.cacheUserSession = {}
        self.contactCache = ContactCache()
        self.dialogsCache = DialogsCache()
        self.monitorKeyWordsCache = MonitorKeyWordsCache()
        self.accountCache = AccountCache()
        self.filters = []
        self.groupSAdminCache = GroupSAdminCache()

    async def add_session(self, session_name, phone_number=None, hostname = None, port = None, user_name = None, password = None, type = None, proxy_id = None):
        # print(f'{session_name}, {phone_number}, {hostname}, {port}, {user_name}, {password}, {type}')
        # print(session_name)
        # print(f'\n\n\n {hostname} \n\n\n')
        session_account = SQLiteSession(session_name)
        if hostname:
            print(222222)
            client = None
            aaaaa = (type and type == 0)
            print(f'type的值为：{aaaaa}')
            print(type == 0)
            if type and type == 0:
                proxy = (hostname, port, password)
                print(proxy)
                client = TelegramClient(session_account, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0', connection=ConnectionTcpMTProxyRandomizedIntermediate, proxy=proxy, timeout=30)
            elif type and type == 1:

                my_proxy = {
                    'proxy_type': ProxyType.SOCKS5,
                    'addr': hostname,
                    'port': port,
                    'username': user_name,
                    'password': password,
                    'rdns': True
                }

                client = TelegramClient(session_account, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0', proxy=my_proxy, timeout=30)
            else:
                print(not type)
            if phone_number:
                await self.insert_accounts(client, phone_number, session_name, proxy_id)
                await self.get_dialogs(client, phone_number, session_name)
            print(client)
            client.add_event_handler(self.handle_new_message, events.NewMessage)
            self.sessions[session_name] = client
        else:
            client = TelegramClient(session_account, CONFIG.APP_ID, CONFIG.API_HASH, device_model='Android', system_version='10', app_version='1.0.0', timeout=30)
            if phone_number:
                await self.insert_accounts(client, phone_number, session_name, proxy_id)
                await self.get_dialogs(client, phone_number, session_name)
            client.add_event_handler(self.handle_new_message, events.NewMessage)
            self.sessions[session_name] = client
        return self.sessions[session_name]
    
    
    async def get_dialogs(self, client, phone_number, session_name):
        if client:
            dialogs = await client.get_dialogs(limit=None)
            if dialogs:
                self.contactCache.set_data(phone_number, dialogs)


    async def get_group_name(self, client, user_id, group_id):
        dialogs = self.contactCache.get_data(user_id)
        # print(dialogs)
        title = ""
        flag = True
        if dialogs:
            for dialog in dialogs:
                print(f'群组id：{dialog.id}，{group_id}，{str(group_id) in str(dialog.id)}')
                if str(group_id) in str(dialog.id):
                    title = dialog.name
                    print(f'本地缓存的标题：{title}')
                    flag = False
                    break
                    
        print(f"本地是否有列表：{flag}")
        if flag:
            dialogs = await client.get_dialogs(limit=None)
            if dialogs:
                self.contactCache.set_data(user_id, dialogs)
                print(f'获取远程的标题：{title}')
            title = await self.get_group_name(client, user_id, group_id)

        return title

    
                
    
    async def insert_accounts(self, client, phone_number, session_name, proxy_id):
        result = await client.connect()
        me = await client.get_me()

        if me:
            self.cacheUserSession[me.id] = client
            columns = ['user_id']
            values = [me.id]
            
            print(phone_number)

            accounts = Accounts()
            result = accounts.get_data(columns=columns, values= values)
            
            if result:
                # print('\n\n\n')
                print(result)
                # print('\n\n\n')
                if not proxy_id:
                    proxy_id = -1
                accounts.update_account_proxy(result['id'], proxy_id, 1)
            else:
                if not proxy_id:
                    proxy_id = -1
                accounts.insert(me.id, me.username, f'{me.first_name} {me.last_name}', phone_number, session_name, 1, 0, proxy_id, datetime.now())
                # account.db.close()
        

    async def update_filters_groups(self, client):
        self.monitorKeyWords = MonitorKeyWords()
        list = self.monitorKeyWords.get_all_no_group_id()
        # print(f'数据长度为：len(list)')
        flag = False
        if len(list) > 0:
            # for item in list
            item = list[0]
            if item['send_to_group']:
                try:
                    entity = await client.get_entity(item['send_to_group'])
                    print(f'群组的id为：{entity.id},{item["send_to_group"]}')
                    self.monitorKeyWords.update_group_id(f'-100{entity.id}', item['send_to_group'])
                except Exception as e:
                    self.monitorKeyWords.update_group_id(-1, item['send_to_group'])
                    flag = True
            else:
                self.monitorKeyWords.update_group_id(-1, item['send_to_group'])
                flag = True
        if len(list) > 0:
            flag = await self.update_filters_groups(client)
        return flag


    async def handle_new_message(self, event):
        userId = -1

        # print(f'消息时间{event.message.date}')

        time_str2 = '2024-09-30 03:10:29'

        # 将时间字符串转换为 datetime 对象
        time1 = datetime.strptime(str(event.message.date), '%Y-%m-%d %H:%M:%S%z')  # 带有时区信息的时间字符串

        # 转换 time_str2 为带有时区信息的 datetime 对象
        time2 = datetime.strptime(time_str2, '%Y-%m-%d %H:%M:%S')
        time2 = time2.replace(tzinfo=timezone.utc)  # 设置为 UTC 时区

        # 比较两个 datetime 对象的大小
        if time1 > time2:
            # print(f"时间1 晚于 时间2")
            # pass
            return
        elif time1 < time2:
            pass
            # return
            # print(f"时间1 早于 时间2")


        flag = await self.update_filters_groups(event.client)
        if flag:
            self.cacheUserSession.clean_all_data()
            await self.get_filter()
        if len(self.filters) == 0:
            await self.get_filter()

        # print(f'是否是管理员：{flag}')

        for user_id, sendMessageClient in self.cacheUserSession.items():
            if event.client is sendMessageClient:
                userId = user_id

        # print(userId)
        data = self.monitorKeyWordsCache.get_data(userId)
        if not data:
            self.monitorKeyWords = MonitorKeyWords()
            list = self.monitorKeyWords.get_all()

            map = {}

            for row, item in enumerate(list):
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
            values = [userId]
            accounts = Accounts()
            account = accounts.get_data(columns=columns, values= values)
            self.accountCache.set_data(userId, account)

        await self.send_or_forward_message(event, account, data, 0, True)
        
    async def get_filter(self):
        self.monitorKeyWords = MonitorKeyWords()
        list = self.monitorKeyWords.get_all()
        for row, item in enumerate(list):
            if str(item['group_id']) not in self.filters:
                self.filters.append(str(item['group_id']))

    async def add_search_records(self, keyword, user_id):
        self.search_records = SearchRecords()
        self.search_records.insert(user_id, keyword)


    async def get_user_is_admin(self, client, group_id, user_id):
        print(f'群组id：{group_id},用户id：{user_id}')
        admins = self.groupSAdminCache.get_data(str(group_id))
        if admins:
            print(f'内存中有缓存管理员id')
            return str(user_id) in admins
        else:
            groupAdmins = GroupAdmins()
            columns = ['group_id']
            values = [group_id]
            admins = groupAdmins.get_data(columns=columns, values= values)
            print(admins)
            if admins:
                print(f'数据库中有缓存管理员id')
                admin_array = []
                for admin in admins:
                    admin_array.append(str(admin['user_id']))
                self.groupSAdminCache.set_data(str(group_id), admin_array)
                return str(user_id) in admin_array
            else:
                admin_array = []
                async for user in client.iter_participants(group_id, filter=ChannelParticipantsAdmins):
                    print(f'获取线上的管理员id')
                    print(f'Admin: {user.first_name} {user.last_name}')
                    admin_user_id = user.id
                    admin_array.append(str(admin_user_id))
                    groupAdmins = GroupAdmins()
                    groupAdmins.insert(group_id, admin_user_id)
                    self.groupSAdminCache.set_data(str(group_id), admin_array)
                    return str(user_id) in admin_array


    async def send_or_forward_message(self, event, account, data, flag, forward, max_attempts=10):
        if event.message.message and len(event.message.message) > 15:
            return

        if account['type'] == 1:
            # print('\n\n\n\n')
            sender = await event.get_sender()
            print(f'群组id：{event.message.peer_id}')
            print(f'发送者id：{sender.id}')
            group_id = -1
            # 假设 message 是您接收到的消息对象
            if isinstance(event.message.peer_id, PeerChat):  # 如果是群组消息
                group_id = event.message.peer_id.chat_id
                # print(f"群组ID：{group_id}")
            elif isinstance(event.message.peer_id, PeerChannel):  # 如果是频道消息
                group_id = event.message.peer_id.channel_id
                # print(f"频道ID：{group_id}")
            else:
                print("不是群组或频道消息")

            # print(f'匹配的数据：-100{group_id}，列表数据：{self.filters}, 字符串是否在数据中：')
            if str(f'-100{group_id}') in self.filters:
            # if str(group_id) in self.filters:
                print('条件匹配')
                return

            if data:
                # print('监控账号')
                for item in data:
                    keywords = item['keyword']
                    # if keywords in event.message.message:
                    #     print('\n\n\n\n')
                    #     print(f'匹配到关键词：{keywords in event.message.message}，消息长度{len(event.message.message)}')
                    #     print(f'消息：{event.message.message}')
                    if keywords in event.message.message and len(event.message.message) < 20:

                        # print(f"Received message from {event.message}")
                        

                        is_admin = await self.get_user_is_admin(event.client, group_id, sender.id)
                        print(f'是否为管理员：{is_admin}')
                        if is_admin:
                            return

                        columns = ['user_id', 'keyword']
                        values = [sender.id, keywords]
                        print(f'参数为:{columns},参数为:{values}')
                        self.search_records = SearchRecords()
                        result = self.search_records.get_data(columns=columns, values= values)
                        print(f'查询结果：{result}')
                        if result:
                            return

                        # if flag == 0:
                        #     current_working_directory = os.getcwd()
                        #     print("当前工作目录：", current_working_directory)
                        #     file_path = f'{current_working_directory}/watch_message.txt'
                        #     if not os.path.exists(file_path):
                        #         with open(file_path, 'w+', encoding='utf-8') as file:
                        #             file.write(f'@{sender.username}-{sender.id} \n')
                        #     else:
                        #         with open(file_path, 'a', encoding='utf-8') as file:
                        #             file.write(f'@{sender.username}-{sender.id} \n')

                        # print('\n\n\n')
                        print(f'是否转发消息：{forward}')
                        try:
                            if forward:
                                # print(f'\n\n\n收到的消息：')
                                # print(event.message)
                                # message = event.message
                                # message.message = "哈哈哈哈"
                                forward_result = await event.client.forward_messages(item['send_to_group'], event.message)
                                print(f'\n\n\n发送完的消息：')
                                print(forward_result)


                                await self.add_search_records(keywords, sender.id)
                                
                                print(group_id)
                                group_name = await self.get_group_name(event.client, event.sender.id, group_id)
                                print(group_name)
                                # 发送新消息并添加文本内容
                                await event.client.send_message(
                                    item['send_to_group'],  # 目标聊天的用户名或 ID
                                    f'群组： {group_name}\n用户： @{event.sender.username}',  # 要发送的文本内容
                                    reply_to=forward_result,  # 回复刚刚转发的消息
                                )
                                print('\n\n消息转发结果：\n')
                                print(forward_result)
                                if forward_result:
                                    forward = False
                        except Exception as e:
                            print(e)
                            forward = False
                        
                        forward = False
                        
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

    def stop_connect(self):
        print('停止客户端连接')
        for client in self.sessions.values():
            # client.disconnect()
            print('2\n\n\n')
            print(client.is_connected())
            print('2\n\n\n')
            if(client.is_connected()) :
                client.disconnect()


    async def start_sessions(self, client):
        await client.start()
        await client.connect()
        await client.run_until_disconnected()


    async def run(self):
        await asyncio.gather(*[self.start_sessions(client) for client in self.sessions.values()])
