"""
This module sets up the logging configuration for the application and loads environment variables using dotenv.
It is primarily responsible for initializing the logger and retrieving the Telegram bot token from environment
variables.

The module configures the logger to record messages in a specified format with timestamps, logging levels,
and message details.
It writes these logs to a file named 'logs.log'. The logging level is set to INFO, meaning it captures all messages
of level INFO and above.

Additionally, the module uses the dotenv library to load environment variables from a '.env' file. This approach is
used to securely manage sensitive data, such as the Telegram bot token, which is retrieved from these environment
variables.

If the required 'BOT_TOKEN' environment variable is not found, the module logs a critical error message and raises
a KeyError, indicating a failure in the token retrieval process. This behavior is essential to ensure the bot does
not run without the necessary authentication token.

Imports:
    - logging: Standard Python library for logging events.
    - os: Standard Python library to interact with the operating system.
    - load_dotenv: Function from the dotenv library to load environment variables from a .env file.

Variables:
    - TOKEN: The Telegram bot token retrieved from the environment variables.

Exceptions:
    - KeyError: Raised if the 'BOT_TOKEN' environment variable is not found.
"""


import logging
import os

from dotenv import load_dotenv

logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

try:
    TOKEN = os.environ['BOT_TOKEN']
except KeyError as err:
    logging.critical(f"Can't read token from environment variable. Message: {err}")
    raise KeyError(err)
