"""Module for Bot Operations and Database Management.

This module contains various asynchronous functions essential for bot operations
and database management. It includes routines to update the database with new account
data, send notifications to users, and initiate the main program execution.
It utilizes asyncio for asynchronous programming, integrates with Google Sheets
for data retrieval, and manages SQLite database interactions.

Functions:
    make_db_updates(): Asynchronously updates the database with new accounts data from Google Sheets.
    make_notifications(): Sends notifications to all users at a specified hour, 3 days before the end of each month.
    start_program(): Initializes and starts the execution of the bot, database updates, and notification system.
"""


import time
import asyncio
import calendar
import logging

from google_spreadsheets.functions import get_data_from_sheet
from datetime import datetime
from bot.main import bot
from bot import texts
from database.main import DatabaseManager
from bot.handlers import exe_bot


logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


async def make_db_updates():
    """
        Continuously updates the database with new account data.

        This function fetches data from a Google Sheet, processes it, and updates the
        database accordingly. It handles exceptions during data processing and logs errors.
        The function runs in an infinite loop with a delay between each iteration.

        Raises:
            Exception: If any error occurs during data processing.
    """

    while True:
        start = time.time()
        data = await get_data_from_sheet()
        clear_data = []
        for record in data:
            try:
                account_number = record[7]
                address = f"{record[1]}, {record[2]}, {record[3]}, {record[4]}/{record[5]}"
                last_indicator = float(record[8].replace("\xa0", ""))
                last_date = record[9]
                account_data = {"personal_account": account_number,
                                "address": address,
                                "last_indicator": last_indicator,
                                "last_date": last_date}

                clear_data.append(account_data)
            except Exception as e:
                logging.error(msg=f"{e} with {record}")

        provided_indicators = {}
        for user_input in await get_data_from_sheet(user_input=True):
            provided_indicators.update({user_input[1]: user_input[0]})

        async with DatabaseManager("test.db") as db:
            existing_accounts = [user["personal_account"] for user in
                                 await db.get_all_data_from_table(table_name="accounts")]

            for clear_record in clear_data:
                if clear_record["personal_account"] in provided_indicators.keys():
                    clear_record["last_indicator"] = provided_indicators.get(clear_record["personal_account"])
                    user_data_to_update = {"last_indicator": clear_record["last_indicator"]}
                    user_identifier = {"personal_account": clear_record["personal_account"]}
                    await db.update_data(table_name="accounts", data=user_data_to_update, identifier=user_identifier)

                if clear_record["personal_account"] in existing_accounts:
                    user_data_to_update = {"last_indicator": clear_record["last_indicator"]}
                    user_identifier = {"personal_account": clear_record["personal_account"]}
                    await db.update_data(table_name="accounts", data=user_data_to_update, identifier=user_identifier)

                data_to_update = {"last_indicator": clear_record["last_indicator"],
                                  "last_date": clear_record["last_date"]}
                identifier = {"personal_account": clear_record["personal_account"]}

                await db.update_data(table_name="all_accounts", data=data_to_update, identifier=identifier)

                parameters = {"column": "personal_account",
                              "value": clear_record["personal_account"]}

                if not await db.check_data(table_name="all_accounts", parameters=parameters):
                    await db.insert_data(table_name="all_accounts", data=clear_record)

        finish = time.time()
        logging.info(msg=f"Update done in {round(float(finish - start), 2)} seconds")

        await asyncio.sleep(600)


async def make_notifications():
    """
        Sends notifications to all users at a specified hour, three days before the end of each month.

        This function calculates the date three days before the end of the current month and
        sends notifications to all users at the target hour on that day. It ensures notifications
        are sent only once by sleeping for an hour after sending the notifications.
    """
    target_hour = 19

    while True:
        current_date = datetime.now()
        year = current_date.year
        current_month = current_date.month

        cal = calendar.Calendar()
        initial_month = cal.monthdatescalendar(year, current_month)

        all_month_days = []

        for week in initial_month:
            for day in week:
                if day.month == current_month:
                    all_month_days.append(day)

        target_day = all_month_days[-3]

        if current_date.date() == target_day:
            logging.info(msg="Today is notification day!")
            while True:
                current_minutes = datetime.now().time().hour
                if current_minutes == target_hour:
                    logging.info(msg="It's notification time!")
                    async with DatabaseManager("test.db") as db:
                        all_users_data = await db.get_all_data_from_table(table_name="all_users")

                    for user in all_users_data:
                        await bot.send_message(chat_id=user["telegram_id"],
                                               text=texts.notification_text[user['chosen_language']])
                    await asyncio.sleep(3700)
                    break
                else:
                    break

        await asyncio.sleep(600)


async def start_program():
    """
        Initializes and starts the main execution of the bot program.

        This function concurrently runs the bot execution, database updates, and notification
        system using asyncio's gather method. It is the entry point for starting all major
        asynchronous tasks in the application.
    """
    await asyncio.gather(exe_bot(), make_db_updates(), make_notifications())
