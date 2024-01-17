"""
This module contains functions for Google API integration, including saving photos and interacting with Google Sheets and Google Drive.
"""


import os
import asyncio

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from bot.main import bot


# Define your service account file path and other constants
SERVICE_ACCOUNT_FILE = ''  # add path to you auth json file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
all_users_info_spreadsheet_id = ''  # spreadsheet ID for historical data storage
users_input_spreadsheet_id = ''  # spreadsheet ID for user's inputs
photo_folder_id = ''  # folder ID for user's photo storage


async def save_photo(file_name, message):
    """
        Save a photo from a message to Google Drive.

        Args:
            file_name (str): The name to be used for the saved file.
            message: The message containing the photo.

        Returns:
            str: The web link to the saved photo on Google Drive.
    """
    photo_file = message.photo[-1].file_id
    file = await bot.get_file(photo_file)
    file_path = file.file_path
    local_path = f"{file_name}.jpeg"
    await bot.download_file(file_path, destination=local_path)

    media = MediaFileUpload(local_path, mimetype='image/jpeg')
    file_metadata = {
        'name': f'{file_name}.jpeg',
        'parents': [photo_folder_id]
    }
    loop = asyncio.get_event_loop()
    file_drive = await loop.run_in_executor(None,
                                            lambda: drive_service.files().create(body=file_metadata,
                                                                                 media_body=media,
                                                                                 fields='id, webViewLink').execute())

    file_link = file_drive.get('webViewLink')
    os.remove(local_path)

    return file_link


async def save_data_to_sheet(data: list):
    """
        Save data to a Google Sheet.

        Args:
            data (list): A list of data to be saved in the sheet.
    """
    values = [data]
    range_ = 'A:E'
    value_input_option = 'USER_ENTERED'
    body = {'values': values}

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None,
                               lambda: sheets_service.spreadsheets().values().append(
                                   spreadsheetId=users_input_spreadsheet_id,
                                   range=range_,
                                   valueInputOption=value_input_option,
                                   body=body).execute())


async def get_data_from_sheet(user_input: bool = False):
    """
        Retrieve data from a Google Sheet.

        Args:
            user_input (bool): Whether to retrieve user input data.

        Returns:
            list: A list of retrieved data from the sheet.
    """
    if user_input:
        range_ = 'A:F'
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: sheets_service.spreadsheets().values().get(
            spreadsheetId=users_input_spreadsheet_id, range=range_).execute())

    else:
        range_ = 'A:J'
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: sheets_service.spreadsheets().values().get(
            spreadsheetId=all_users_info_spreadsheet_id, range=range_).execute())

    values = result.get('values', [])

    return values[1:]
