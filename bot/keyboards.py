"""
This module contains functions to generate various keyboards (sets of buttons) for the bot interface.
Each function returns a specific type of keyboard layout to be used in different contexts within the bot,
such as selecting languages, navigating the main menu, managing accounts, and confirming actions.
"""


from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup
from bot.texts import (first_language, second_language, main_menu_buttons_text, accounts_buttons_text, back_button_text,
                       address_verification_buttons_text, confirming_buttons, skip_text)


async def get_languages_kb():
    """
    Generates a keyboard with language selection buttons.

    Returns:
        ReplyKeyboardMarkup: A keyboard markup with buttons for each available language.
    """
    language_buttons = [[KeyboardButton(text=first_language)],
                        [KeyboardButton(text=second_language)]]

    kb = ReplyKeyboardMarkup(keyboard=language_buttons, is_persistent=True, resize_keyboard=True)

    return kb


async def get_main_menu_kb(user_language: str):
    """
     Generates the main menu keyboard based on the user's selected language.

     Args:
         user_language (str): The language selected by the user.

     Returns:
         ReplyKeyboardMarkup: A keyboard markup for the main menu.
     """
    buttons = []

    buttons_texts = main_menu_buttons_text[user_language]

    first_row = [KeyboardButton(text=buttons_texts["my_accounts"]),
                 KeyboardButton(text=buttons_texts["input_indicator"])]

    second_row = [KeyboardButton(text=buttons_texts["change_language"])]

    buttons.append(first_row)
    buttons.append(second_row)

    kb = ReplyKeyboardMarkup(keyboard=buttons, is_persistent=True, resize_keyboard=True)

    return kb


async def get_accounts_kb(user_language: str, user_accounts: list = None, indicator: bool = False):
    """
    Generates a keyboard for account management, including options for adding, deleting, and selecting accounts.

    Args:
        user_language (str): The language selected by the user.
        user_accounts (list, optional): A list of user accounts. Defaults to None.
        indicator (bool, optional): Flag to indicate if the keyboard is for indicator input. Defaults to False.

    Returns:
        ReplyKeyboardMarkup: A keyboard markup for account management.
    """
    buttons = []

    back_button = [KeyboardButton(text=back_button_text[user_language])]
    add_button = KeyboardButton(text=accounts_buttons_text[user_language]["add"])
    delete_button = KeyboardButton(text=accounts_buttons_text[user_language]["delete"])

    if user_accounts:
        for account in user_accounts:
            buttons.append([KeyboardButton(text=f"{account}")])
    if not indicator:
        if not user_accounts:
            add_delete_buttons = [add_button]

        elif len(user_accounts) < 5:
            add_delete_buttons = [add_button, delete_button]

        else:
            add_delete_buttons = [delete_button]

        buttons.append(add_delete_buttons)

    buttons.append(back_button)

    kb = ReplyKeyboardMarkup(keyboard=buttons, is_persistent=True, resize_keyboard=True)

    return kb


async def get_back_button(user_language: str):
    """
    Generates a keyboard with a 'Back' button in the user's selected language.

    Args:
        user_language (str): The language selected by the user.

    Returns:
        ReplyKeyboardMarkup: A keyboard markup with a 'Back' button.
    """
    back_button = [KeyboardButton(text=back_button_text[user_language])]

    kb = ReplyKeyboardMarkup(keyboard=[back_button], is_persistent=True, resize_keyboard=True)

    return kb


async def get_address_check_kb(user_language: str):
    """
    Generates a keyboard for address verification with confirmation buttons.

    Args:
        user_language (str): The language selected by the user.

    Returns:
        ReplyKeyboardMarkup: A keyboard markup for address verification.
    """
    buttons = []

    back_button = [KeyboardButton(text=back_button_text[user_language])]
    confirm_button = [KeyboardButton(text=address_verification_buttons_text[user_language])]

    buttons.append(confirm_button)
    buttons.append(back_button)

    kb = ReplyKeyboardMarkup(keyboard=buttons, is_persistent=True, resize_keyboard=True)

    return kb


async def get_single_account_kb(user_language: str):
    """
    Generates a keyboard for single account actions like inputting indicators or deleting the account.

    Args:
        user_language (str): The language selected by the user.

    Returns:
        ReplyKeyboardMarkup: A keyboard markup for single account actions.
    """
    buttons = []

    back_button = [KeyboardButton(text=back_button_text[user_language])]

    indicator_delete_button = [KeyboardButton(text=main_menu_buttons_text[user_language]["input_indicator"]),
                               KeyboardButton(text=accounts_buttons_text[user_language]["delete"])]

    buttons.append(indicator_delete_button)
    buttons.append(back_button)

    kb = ReplyKeyboardMarkup(keyboard=buttons, is_persistent=True, resize_keyboard=True)

    return kb


async def get_confirmation_kb(user_language: str):
    """
    Generates a confirmation keyboard with 'Yes' and 'No' options in the user's selected language.

    Args:
        user_language (str): The language selected by the user.

    Returns:
        ReplyKeyboardMarkup: A keyboard markup for confirmation actions.
    """
    buttons = []

    back_button = [KeyboardButton(text=back_button_text[user_language])]

    yes_no_buttons = [KeyboardButton(text=confirming_buttons[user_language]["yes"]),
                      KeyboardButton(text=confirming_buttons[user_language]["no"])]

    buttons.append(yes_no_buttons)
    buttons.append(back_button)

    kb = ReplyKeyboardMarkup(keyboard=buttons, is_persistent=True, resize_keyboard=True)

    return kb


async def get_photo_buttons(user_language: str):
    """
        Generates a keyboard for handling photo uploads, offering options to skip or return to the main menu.

        Args:
            user_language (str): The language selected by the user.

        Returns:
            ReplyKeyboardMarkup: A keyboard markup with options for handling photo uploads,
            including skipping the upload or returning to the main menu.
    """
    buttons = []

    back_button = [KeyboardButton(text=back_button_text[user_language])]
    skip_button = [KeyboardButton(text=skip_text[user_language])]

    buttons.append(skip_button)
    buttons.append(back_button)

    kb = ReplyKeyboardMarkup(keyboard=buttons, is_persistent=True, resize_keyboard=True)

    return kb
