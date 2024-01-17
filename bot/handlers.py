"""
This module contains all the handlers for the bot, defining how it responds to various messages and states.
It includes functions for language selection, handling the main menu, adding and deleting accounts,
inputting indicators, confirming actions, and handling initial greetings.
The module also includes a function to execute the bot, initializing and starting the bot's operations.
"""

import re
import bot.texts as texts
import logging

from aiogram.types import Message
from bot.main import dp, bot
from aiogram.fsm.context import FSMContext
from bot.states import UserState
from bot.keyboards import (get_languages_kb, get_main_menu_kb, get_accounts_kb, get_back_button, get_address_check_kb,
                           get_single_account_kb, get_confirmation_kb, get_photo_buttons)
from database.main import DatabaseManager
from google_spreadsheets.functions import save_data_to_sheet, save_photo
from datetime import datetime


logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@dp.message(UserState.language_choosing)
async def handle_language(message: Message, state: FSMContext):
    """Handles choosing language for user"""
    try:
        if "First language" or "Second language" in message.text:
            if "First language" in message.text:
                user_language = "en"
            else:
                user_language = "ua"

            async with DatabaseManager("test.db") as db:
                parameters = {"column": "telegram_id",
                              "value": message.from_user.id}
                user_existence = await db.check_data(table_name="all_users", parameters=parameters)

                if not user_existence:
                    data = {"telegram_id": message.from_user.id,
                            "chosen_language": user_language}
                    await db.insert_data(table_name="all_users", data=data)

                else:
                    data = {"chosen_language": user_language}
                    identifier = {"telegram_id": message.from_user.id}
                    await db.update_data(table_name="all_users", data=data, identifier=identifier)

            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

        else:
            async with DatabaseManager("test.db") as db:
                parameters = {"column": "telegram_id",
                              "value": message.from_user.id}
                user_data = await db.check_data(table_name="all_users", parameters=parameters)

            user_language = user_data[0]["chosen_language"]
            kb = await get_languages_kb()
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)

    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.main_menu)
async def handle_main_menu(message: Message, state: FSMContext):
    """Handles all main menu actions"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)
            user_accounts = await db.check_data(table_name="accounts", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        buttons_texts = texts.main_menu_buttons_text[user_language]

        if message.text == buttons_texts["my_accounts"]:
            if user_accounts:
                accounts_data = [f"{account['personal_account']}, {account['address']}" for account in user_accounts]
                kb = await get_accounts_kb(user_language=user_language, user_accounts=accounts_data)
                await state.set_state(UserState.accounts_menu)
                await message.answer(text=texts.accounts_menu_text[user_language]["account_exists"],
                                     reply_markup=kb)

            else:
                kb = await get_back_button(user_language=user_language)
                await state.set_state(UserState.adding_account)
                await message.answer(text=texts.accounts_menu_text[user_language]["no_account"],
                                     reply_markup=kb)

        elif message.text == buttons_texts["input_indicator"]:
            if not user_accounts:
                kb = await get_main_menu_kb(user_language=user_language)
                await message.answer(text=texts.general_texts[user_language]["no_accounts_to_add_indicator"],
                                     reply_markup=kb)
                await state.clear()
                await state.set_state(UserState.main_menu)

            else:
                if len(user_accounts) == 1:
                    kb = await get_back_button(user_language=user_language)
                    user_account = f"{user_accounts[0]['personal_account']}, {user_accounts[0]['address']}"
                    last_indicator = round(float(user_accounts[0]["last_indicator"]), 2)
                    await state.update_data(account_data=user_account,
                                            last_indicator=last_indicator)
                    text = texts.general_texts[user_language]["input_indicator"].format(user_account, last_indicator)
                    await message.answer(text=text,
                                         reply_markup=kb)
                    await state.set_state(UserState.adding_indicator)

                else:
                    accounts_data = [f"{account['personal_account']}, {account['address']}" for account in user_accounts]
                    kb = await get_accounts_kb(user_language=user_language, user_accounts=accounts_data, indicator=True)
                    await message.answer(text=texts.general_texts[user_language]["choose_account"],
                                         reply_markup=kb)
                    await state.set_state(UserState.choosing_account)

        elif message.text == buttons_texts["change_language"]:
            kb = await get_languages_kb()
            await message.answer(text=texts.language_choosing,
                                 reply_markup=kb)
            await state.set_state(UserState.language_choosing)

        else:
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)
    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.choosing_account)
async def handle_account_indicator_choosing(message: Message, state: FSMContext):
    """Handles user's action when user have to choose account to input indicator"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)
            user_accounts = await db.check_data(table_name="accounts", parameters=parameters)

        accounts_data = [f"{account['personal_account']}, {account['address']}" for account in user_accounts]

        user_language = user_data[0]["chosen_language"]

        if message.text in accounts_data:
            account_number = message.text.split(",")[0]
            filtered_account = filter(lambda item: item['personal_account'] == account_number, user_accounts)
            account = next(filtered_account)
            last_indicator = round(float(account["last_indicator"]), 2)
            await state.update_data(account_data=message.text,
                                    last_indicator=last_indicator)
            kb = await get_back_button(user_language=user_language)
            text = texts.general_texts[user_language]["input_indicator"].format(message.text, last_indicator)
            await message.answer(text=text,
                                 reply_markup=kb)
            await state.set_state(UserState.adding_indicator)

        elif message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

        else:
            kb = await get_accounts_kb(user_language=user_language, user_accounts=accounts_data, indicator=True)
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)

    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.accounts_menu)
async def handle_accounts_menu_actions(message: Message, state: FSMContext):
    """Handles all actions when user in accounts menu"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)
            user_accounts = await db.check_data(table_name="accounts", parameters=parameters)

        user_language = user_data[0]["chosen_language"]
        accounts_data = [f"{account['personal_account']}, {account['address']}" for account in user_accounts]

        if message.text == texts.accounts_buttons_text[user_language]["add"]:
            kb = await get_back_button(user_language=user_language)
            await state.set_state(UserState.adding_account)
            await message.answer(text=texts.general_texts[user_language]["input_personal_account"],
                                 reply_markup=kb)

        elif message.text == texts.accounts_buttons_text[user_language]["delete"]:
            if len(user_accounts) == 1:
                user_account = accounts_data[0]
                await state.update_data(account_data=user_account)
                kb = await get_confirmation_kb(user_language)
                await message.answer(text=texts.general_texts[user_language]["confirm_deleting"].format(user_account),
                                     reply_markup=kb)
                await state.set_state(UserState.delete_confirmation)

            else:
                kb = await get_accounts_kb(user_language=user_language, user_accounts=accounts_data, indicator=True)
                await message.answer(text=texts.general_texts[user_language]["choose_account_to_delete"],
                                     reply_markup=kb)
                await state.set_state(UserState.deleting_account)

        elif message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

        elif message.text in accounts_data:
            await state.set_state(UserState.single_account)
            user_account = message.text
            account_number = user_account.split(",")[0]
            async with DatabaseManager("test.db") as db:
                parameters = {"column": "personal_account",
                              "value": account_number}
                account_data = await db.check_data(table_name="accounts", parameters=parameters)

            last_indicator = round(float(account_data[0]["last_indicator"]), 2)
            last_date = account_data[0]["last_date"]
            await state.update_data(last_indicator=last_indicator,
                                    account_data=user_account)

            kb = await get_single_account_kb(user_language)
            text = texts.general_texts[user_language]["choose_action_with_account"].format(user_account,
                                                                                           last_date,
                                                                                           last_indicator)
            await message.answer(text=text,
                                 reply_markup=kb)

        else:
            if not user_accounts:
                kb = await get_accounts_kb(user_language=user_language)
                await message.answer(text=texts.accounts_menu_text[user_language]["no_account"],
                                     reply_markup=kb)
                await state.clear()
                await state.set_state(UserState.adding_account)

            else:
                kb = await get_accounts_kb(user_language=user_language, user_accounts=accounts_data)
                await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                     reply_markup=kb)

    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.single_account)
async def handle_single_account_actions(message: Message, state: FSMContext):
    """Handles actions when user interacts with single account"""
    try:
        state_data = await state.get_data()
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        if message.text == texts.main_menu_buttons_text[user_language]["input_indicator"]:
            kb = await get_back_button(user_language=user_language)
            user_account = state_data["account_data"]
            account_number = user_account.split(",")[0]
            async with DatabaseManager("test.db") as db:
                parameters = {"column": "personal_account",
                              "value": account_number}
                account_data = await db.check_data(table_name="accounts", parameters=parameters)

            last_indicator = round(float(account_data[0]["last_indicator"]), 2)
            await state.update_data(last_indicator=last_indicator)
            text = texts.general_texts[user_language]["input_indicator"].format(user_account, last_indicator)
            await message.answer(text=text,
                                 reply_markup=kb)
            await state.set_state(UserState.adding_indicator)

        elif message.text == texts.accounts_buttons_text[user_language]["delete"]:
            user_account = state_data["account_data"]
            kb = await get_confirmation_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["confirm_deleting"].format(user_account),
                                 reply_markup=kb)
            await state.set_state(UserState.delete_confirmation)

        elif message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

        else:
            kb = await get_single_account_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)

    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.deleting_account)
async def handle_account_deleting(message: Message, state: FSMContext):
    """Handles process of account deleting"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)
            user_accounts = await db.check_data(table_name="accounts", parameters=parameters)

        user_language = user_data[0]["chosen_language"]
        accounts_data = [f"{account['personal_account']}, {account['address']}" for account in user_accounts]

        if message.text in accounts_data:
            await state.update_data(account_data=message.text)
            kb = await get_confirmation_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["confirm_deleting"].format(message.text),
                                 reply_markup=kb)
            await state.set_state(UserState.delete_confirmation)

        elif message.text == texts.back_button_text[user_language]:
            kb = await get_accounts_kb(user_language=user_language, user_accounts=accounts_data)
            await state.set_state(UserState.accounts_menu)
            await message.answer(text=texts.accounts_menu_text[user_language]["account_exists"],
                                 reply_markup=kb)

        else:
            kb = await get_accounts_kb(user_language=user_language, user_accounts=accounts_data, indicator=True)
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)
    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.delete_confirmation)
async def handle_delete_confirmation(message: Message, state: FSMContext):
    """Handles confirmation of deleting account"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)
            user_accounts = await db.check_data(table_name="accounts", parameters=parameters)

        user_language = user_data[0]["chosen_language"]
        state_data = await state.get_data()
        account_number = state_data["account_data"].split(",")[0]

        if message.text == texts.confirming_buttons[user_language]["yes"]:
            async with DatabaseManager("test.db") as db:
                parameters = {"column": "personal_account",
                              "value": account_number}
                await db.delete_from_db(table_name="accounts", parameters=parameters)

            kb = await get_main_menu_kb(user_language)
            text = (f"{texts.general_texts[user_language]['account_deleted']}\n\n"
                    f"{texts.general_texts[user_language]['main_menu']}")
            await message.answer(text=text,
                                 reply_markup=kb)
            await state.clear()
            await state.set_state(UserState.main_menu)

        elif message.text == texts.confirming_buttons[user_language]["no"]:
            accounts_data = [f"{account['personal_account']}, {account['address']}" for account in user_accounts]
            kb = await get_accounts_kb(user_language=user_language, user_accounts=accounts_data)
            await state.set_state(UserState.accounts_menu)
            await message.answer(text=texts.accounts_menu_text[user_language]["account_exists"],
                                 reply_markup=kb)

        elif message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

        else:
            kb = await get_confirmation_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)
    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.adding_indicator)
async def handle_indicator_adding(message: Message, state: FSMContext):
    """Handles indicator adding process"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]
        indicator_pattern = "^\d+(\.\d{1,2})?$"
        if message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

        elif re.match(indicator_pattern, message.text):
            current_indicator = round(float(message.text), 2)
            await state.update_data(current_indicator=current_indicator)
            state_data = await state.get_data()
            account_data = state_data["account_data"]
            last_indicator = state_data["last_indicator"]

            kb = await get_confirmation_kb(user_language)
            if current_indicator < last_indicator:
                text = (f"{texts.general_texts[user_language]['confirmation_indicator'].format(current_indicator, account_data)}\n"
                        f"\n"
                        f"{texts.general_texts[user_language]['indicator_less']}")
            else:
                text = texts.general_texts[user_language]['confirmation_indicator'].format(current_indicator,
                                                                                           account_data)
            await message.answer(text=text,
                                 reply_markup=kb)
            await state.set_state(UserState.confirming_indicator)

        elif not re.match(indicator_pattern, message.text):
            kb = await get_back_button(user_language=user_language)
            await message.answer(text=texts.general_texts[user_language]["incorrect_format_of_indicator"],
                                 reply_markup=kb)

        else:
            kb = await get_back_button(user_language=user_language)
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)

    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.confirming_indicator)
async def handle_indicator_confirmation(message: Message, state: FSMContext):
    """Handles confirming indicator value"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        if message.text == texts.confirming_buttons[user_language]["yes"]:
            state_data = await state.get_data()
            account_data = state_data["account_data"]

            current_indicator = state_data["current_indicator"]
            await state.update_data(current_indicator=current_indicator)
            kb = await get_photo_buttons(user_language)
            await message.answer(text=texts.general_texts[user_language]["upload_photo"].format(account_data),
                                 reply_markup=kb)
            await state.set_state(UserState.uploading_photo)

        elif message.text == texts.confirming_buttons[user_language]["no"]:
            state_data = await state.get_data()
            account_data = state_data["account_data"]
            last_indicator = state_data["last_indicator"]
            text = texts.general_texts[user_language]["input_indicator"].format(account_data, last_indicator)
            kb = await get_back_button(user_language=user_language)
            await message.answer(text=text,
                                 reply_markup=kb)
            await state.set_state(UserState.adding_indicator)

        elif message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)
        else:
            kb = await get_back_button(user_language=user_language)
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)
    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.uploading_photo)
async def handle_photo(message: Message, state: FSMContext):
    """Handles photo uploading"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        if message.photo or message.text == texts.skip_text[user_language]:
            state_data = await state.get_data()
            account_data = state_data["account_data"]
            account_number = account_data.split(",")[0]
            account_address = account_data[1:]
            time_of_indicator = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_indicator = state_data["current_indicator"]

            file_name = f"{account_number}_{time_of_indicator}"
            if message.photo:
                photo_link = await save_photo(file_name=file_name, message=message)
            else:
                photo_link = "None"

            data_to_sheet = [current_indicator,
                             f"'{account_number}",
                             account_address,
                             message.from_user.id,
                             time_of_indicator,
                             photo_link]
            await save_data_to_sheet(data=data_to_sheet)
            async with DatabaseManager("test.db") as db:
                identifier = {"personal_account": account_number}
                data = {"last_date": time_of_indicator,
                        "last_indicator": current_indicator}
                await db.update_data(table_name="accounts", data=data, identifier=identifier)

            kb = await get_main_menu_kb(user_language)
            text = (f"{texts.general_texts[user_language]['indicator_added']}\n\n"
                    f"{texts.general_texts[user_language]['main_menu']}")
            await message.answer(text=text,
                                 reply_markup=kb)
            await state.clear()
            await state.set_state(UserState.main_menu)

        elif message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

        else:
            state_data = await state.get_data()
            account_data = state_data["account_data"]

            kb = await get_back_button(user_language)
            await message.answer(text=texts.general_texts[user_language]["upload_photo"].format(account_data),
                                 reply_markup=kb)

    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.adding_account)
async def handle_account_adding(message: Message, state: FSMContext):
    """Handles account adding"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)
            all_accounts = await db.get_all_data_from_table(table_name="all_accounts")

        all_accounts_numbers = [record["personal_account"] for record in all_accounts]
        user_language = user_data[0]["chosen_language"]

        account_number_pattern = "^\d{7}$"

        if message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

        elif re.match(account_number_pattern, message.text):
            if message.text in all_accounts_numbers:
                async with DatabaseManager("test.db") as db:
                    parameters = {"column": "personal_account",
                                  "value": message.text}
                    already_exists = await db.check_data(table_name="accounts", parameters=parameters)
                    if already_exists:
                        await db.delete_from_db(table_name="accounts", parameters=parameters)

                kb = await get_address_check_kb(user_language)
                filtered_account = filter(lambda item: item['personal_account'] == message.text, all_accounts)
                account = next(filtered_account)
                address = account["address"]
                last_indicator = account["last_indicator"]
                last_date = account["last_date"]
                text = texts.general_texts[user_language]["check_address"].format(address)
                await state.update_data(account_number=message.text,
                                        address=address,
                                        last_indicator=last_indicator,
                                        last_date=last_date)

                await message.answer(text=text,
                                     reply_markup=kb)
                await state.set_state(UserState.address_check)

            else:
                kb = await get_back_button(user_language)
                await message.answer(text=texts.general_texts[user_language]["incorrect_account_data"],
                                     reply_markup=kb)

        elif not re.match(account_number_pattern, message.text):
            kb = await get_back_button(user_language)
            await message.answer(text=texts.general_texts[user_language]["incorrect_format_of_account"],
                                 reply_markup=kb)

        elif message.text == texts.back_button_text[user_language]:
            await state.clear()
            await state.set_state(UserState.main_menu)
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["main_menu"],
                                 reply_markup=kb)

    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message(UserState.address_check)
async def address_check_handler(message: Message, state: FSMContext):
    """Handles actions with address check"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        if message.text == texts.address_verification_buttons_text[user_language]:
            user_state_data = await state.get_data()
            async with DatabaseManager("test.db") as db:
                data = {"telegram_id": message.from_user.id,
                        "personal_account": user_state_data["account_number"],
                        "address": user_state_data["address"],
                        "last_indicator": user_state_data["last_indicator"],
                        "last_date": user_state_data["last_date"]}

                await db.insert_data(table_name="accounts", data=data)

            text = (f"{texts.general_texts[user_language]['account_added']}\n\n"
                    f"{texts.general_texts[user_language]['main_menu']}")
            kb = await get_main_menu_kb(user_language)
            await message.answer(text=text,
                                 reply_markup=kb)
            await state.clear()
            await state.set_state(UserState.main_menu)

        elif message.text == texts.back_button_text[user_language]:
            text = texts.general_texts[user_language]['main_menu']

            kb = await get_main_menu_kb(user_language)
            await message.answer(text=text,
                                 reply_markup=kb)
            await state.clear()
            await state.set_state(UserState.main_menu)

        else:
            kb = await get_address_check_kb(user_language)
            await message.answer(text=texts.general_texts[user_language]["choose_action_from_menu"],
                                 reply_markup=kb)

    except Exception as e:
        logging.error(msg=f"An error occurred: {e}")
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            user_data = await db.check_data(table_name="all_users", parameters=parameters)

        user_language = user_data[0]["chosen_language"]

        await state.clear()
        await state.set_state(UserState.main_menu)
        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.error_text[user_language],
                             reply_markup=kb)


@dp.message()
async def handle_greeting(message: Message, state: FSMContext):
    """General handler for initial message"""
    async with DatabaseManager("test.db") as db:
        parameters = {"column": "telegram_id",
                      "value": message.from_user.id}
        user_data = await db.check_data(table_name="all_users", parameters=parameters)

    if user_data:
        user_language = user_data[0]["chosen_language"]

        kb = await get_main_menu_kb(user_language)
        await message.answer(text=texts.general_texts[user_language]['main_menu'],
                             reply_markup=kb)
        await state.clear()
        await state.set_state(UserState.main_menu)

    else:
        kb = await get_languages_kb()
        await message.answer(text=texts.language_choosing,
                             reply_markup=kb)
        await state.set_state(UserState.language_choosing)


async def exe_bot():
    """
        Initializes and starts the bot. It ensures the necessary tables are created in the database
        and starts the bot's polling mechanism.
    """
    async with DatabaseManager("test.db") as db:
        await db.create_tables()

    logging.info(msg="BOT started")
    print("BOT started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
