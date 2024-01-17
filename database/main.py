"""
This module contains the DatabaseManager class for managing SQLite database operations asynchronously.
"""

import aiosqlite


class DatabaseManager:
    """
       A class for managing SQLite database operations asynchronously.
    """
    def __init__(self, db_name):
        """
            Initialize the DatabaseManager with the given database name.

            Args:
                db_name (str): The name of the SQLite database file.
        """
        self.db_name = db_name

    async def __aenter__(self):
        """
            Async enter method for using the database as a context manager.
            Opens a connection to the database and returns self.

            Returns:
                DatabaseManager: The DatabaseManager instance.
        """
        self.conn = await aiosqlite.connect(self.db_name)
        self.cursor = await self.conn.cursor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
            Async exit method for using the database as a context manager.
            Commits changes and closes the connection.

            Args:
                exc_type: Exception type.
                exc_val: Exception value.
                exc_tb: Exception traceback.
        """
        await self.conn.commit()
        await self.conn.close()

    async def create_tables(self):
        """
            Creates all necessary tables in the database if they don't already exist.
        """
        await self.cursor.execute('''
                               CREATE TABLE IF NOT EXISTS all_users (
                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   telegram_id INTEGER UNIQUE NOT NULL,
                                   chosen_language TEXT
                                                                       )
                                ''')

        await self.cursor.execute('''
                               CREATE TABLE IF NOT EXISTS accounts (
                                   personal_account TEXT PRIMARY KEY,
                                   telegram_id INTEGER,
                                   address TEXT,
                                   last_date INTEGER,
                                   last_indicator INTEGER,
                                   FOREIGN KEY (telegram_id) REFERENCES all_users(telegram_id)
                                                                     )
                                ''')

        await self.cursor.execute('''
                                     CREATE TABLE IF NOT EXISTS all_accounts (
                                           personal_account TEXT PRIMARY KEY,
                                           address TEXT,
                                           last_indicator INTEGER,
                                           last_date TEXT
                                                        )
                                        ''')

    async def insert_data(self, table_name: str, data: dict):
        """
            Inserts data into the specified table.

            Args:
                table_name (str): The name of the table to insert data into.
                data (dict): A dictionary representing the columns and values to be inserted.
        """
        placeholders = ', '.join(['?'] * (len(data.values())))
        columns = ', '.join(data.keys())
        values = tuple(list(data.values()))

        await self.cursor.execute(f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
        """, values)

    async def update_data(self, table_name: str, data: dict, identifier: dict):
        """
            Updates data in the specified table based on the given identifier.

            Args:
                table_name (str): The name of the table to update.
                data (dict): A dictionary representing the columns and values to be updated.
                identifier (dict): A dictionary specifying the column and value for identifying the rows to be updated.
        """
        where_column = list(identifier.keys())[0]
        where_value = identifier[where_column]
        set_values = ', '.join([f'{key} = ?' for key in data.keys()])
        values = tuple(list(data.values()) + [where_value])

        query = f"""
                    UPDATE {table_name}
                    SET {set_values}
                    WHERE {where_column} = ?
                 """

        await self.cursor.execute(query, values)

    async def check_data(self, table_name: str, parameters: dict):
        """
            Checks for data in the specified table based on the given parameters.

            Args:
                table_name (str): The name of the table to check.
                parameters (dict): A dictionary specifying the column and value for the check.

            Returns:
                list|bool: A list of dictionaries representing the rows found, or False if no data is found.
        """

        column = parameters["column"]
        value = parameters["value"]
        query = f"SELECT * FROM {table_name} WHERE {column} = ?"

        await self.cursor.execute(query, (value, ))
        result = await self.cursor.fetchall()
        if result:
            columns = [description[0] for description in self.cursor.description]
            results_list = []

            for row in result:
                result_dict = {columns[i]: row[i] for i in range(len(columns))}
                results_list.append(result_dict)

            return results_list
        else:
            return False

    async def delete_from_db(self, table_name: str, parameters: dict):
        """
            Deletes rows from the specified table based on the given parameters.

            Args:
                table_name (str): The name of the table to delete from.
                parameters (dict): A dictionary specifying the column and value for identifying the rows to delete.
        """
        column = parameters["column"]
        value = parameters["value"]
        query = f"DELETE FROM {table_name} WHERE {column} = ?"

        await self.cursor.execute(query, (value, ))

    async def get_all_data_from_table(self, table_name: str):
        """
            Retrieves all data from the specified table.

            Args:
                table_name (str): The name of the table to retrieve data from.

            Returns:
                list: A list of dictionaries representing the rows in the table.
        """
        query = f"SELECT * FROM {table_name}"

        await self.cursor.execute(query)

        result = await self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]

        data = []

        for record in result:
            record_dict = dict(zip(columns, record))
            data.append(record_dict)

        return data
