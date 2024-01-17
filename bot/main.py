"""
This module initializes the core components necessary for the operation of an Aiogram-based Telegram bot.
It sets up the bot with the provided API token, configures the parsing mode for messages, and initializes
the dispatcher with memory storage for managing the state of conversations.

The Aiogram library is utilized here to create the bot and dispatcher objects. The bot token is sourced
from the 'bot.settings' module. Additionally, the module configures the bot to parse messages in HTML format,
allowing for rich text messages including bold, italic, links, etc.

Imports:
    - Aiogram: A library for Telegram Bot API.
    - TOKEN: A variable containing the bot's API token.
    - ParseMode: Enum to specify the message parsing mode.
    - MemoryStorage: A storage class for maintaining the state in memory.

Variables:
    - storage: An instance of MemoryStorage to store user state and data.
    - bot: The bot instance created with the TOKEN and HTML parsing mode.
    - dp: The Dispatcher instance, linked with the bot and the storage for handling updates.
"""


from aiogram import Bot, Dispatcher
from bot.settings import TOKEN
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)
