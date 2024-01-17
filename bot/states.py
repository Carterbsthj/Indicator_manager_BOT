"""
This module defines the finite state machine (FSM) states for user interactions in the Telegram bot.
It utilizes the aiogram library to create states and state groups for handling different stages of user interaction.

The module employs the concept of states to manage the flow of conversation with the bot,
ensuring that responses and actions are contextually relevant to the user's current interaction stage.

The UserState class, as a subclass of StatesGroup, encapsulates various states representing different interaction phases of the user.
Each state corresponds to a specific step in the user's journey, allowing the bot to maintain context and provide appropriate responses or actions.

Imported Libraries:
    - aiogram.fsm.state: Provides State and StatesGroup classes for creating FSM states.

Usage:
    This module is used throughout the bot to manage and transition between different states based on user interactions.
"""

from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """
        Represents the various states a user can be in during their interaction with the Telegram bot.
        This class is a subclass of StatesGroup and is used to define different stages of user engagement with the bot.

        Each state in this class corresponds to a specific part of the bot's conversation flow.
        The states are used to track and manage the user's progress through the bot's functionalities, ensuring a structured and coherent interaction.

        States:
            - language_choosing: State where the user selects their preferred language.
            - main_menu: State representing the user's interaction with the main menu of the bot.
            - accounts_menu: State for navigating and interacting with the accounts menu.
            - adding_account: State for the process where the user adds a new account.
            - adding_indicator: State where the user is in the process of adding a new indicator to their account.
            - choosing_account: State that allows the user to select an account for further actions.
            - address_check: State for confirming the address associated with a user's account.
            - deleting_account: State during which the user can delete an existing account.
            - single_account: State for managing and interacting with a single account.
            - confirming_indicator: State for confirming the indicators added by the user.
            - uploading_photo: State in which the user can upload a photo related to their account.
            - delete_confirmation: State for confirming the deletion of an account.

        Usage:
            This class is utilized in the bot's logic to track the user's current state and to provide appropriate responses
            and actions based on the context of the interaction. It helps in making the bot's conversation flow more manageable and user-friendly.
    """
    language_choosing = State()
    main_menu = State()
    accounts_menu = State()
    adding_account = State()
    adding_indicator = State()
    choosing_account = State()
    address_check = State()
    deleting_account = State()
    single_account = State()
    confirming_indicator = State()
    uploading_photo = State()
    delete_confirmation = State()
