from telethon.sync import TelegramClient
from telethon.tl.types import InputMessagesFilterVideo
from telethon import events
from config import CONFIG
from dao import Accounts
from datetime import datetime

class TgClient:
    _instances = {}  # Dictionary to store instances based on phone number

    def __new__(cls, phone_number, session_path):
        if phone_number not in cls._instances:
            cls._instances[phone_number] = super().__new__(cls)
            cls._instances[phone_number].phone_number = phone_number
            cls._instances[phone_number].session_path = session_path
            cls._instances[phone_number].client = None  # Initialize client attribute
        return cls._instances[phone_number]

    async def handle_new_message(self, event):
        # Handle incoming messages
        print(f"Received message from {event.message}")

    async def login(self):
        if not self.client:
            # Initialize TelegramClient only if it's not already initialized
            self.client = TelegramClient(
                self.session_path,
                CONFIG.APP_ID,
                CONFIG.API_HASH,
                device_model='Android',
                system_version='10',
                app_version='1.0.0'
            )
            await self.client.start(phone=self.phone_number)
            await self.client.connect()
            print(f"Session file: {self.session_path}, Phone number: {self.phone_number}")
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.phone_number)
                await self.client.sign_in(self.phone_number, input('Enter the code: '))
            self.client.add_event_handler(self.handle_new_message, events.NewMessage)

            me = await self.client.get_me()

            columns = ['user_id']
            values = [me.id]
            print(f'Logged in as: {me}')

            self.accounts = Accounts()
            result = self.accounts.get_data(columns=columns, values= values)
            print(result)
            if not result:
                print(result)
                self.accounts.insert(me.id, me.username, f'{me.first_name} {me.last_name}', self.phone_number, self.session_path, 1, 0, datetime.now())

    async def get_dialogs(self):
        if self.client:
            dialogs = await self.client.get_dialogs(limit=None)
            if not dialogs:
                for dialog in dialogs:
                    print(dialog.name)
                # callback(dialogs)
                return dialogs
        else:
            print("TelegramClient is not initialized.")

    async def run(self):
        if self.client:
            await self.client.run_until_disconnected()
        else:
            print("TelegramClient is not initialized.")
