from typing import Tuple, List
import sqlite3
from sqlite3 import Error


class SQLiteConnector:
    """
    A class to handle SQLite database connections and operations.

    Attributes:
        db_file (str): The path to the SQLite database file.
        connection (sqlite3.Connection): The connection object to the SQLite database.

    Example of usage:
        >>> db_connector = SQLiteConnector('example.db')
        >>> status_code, status_message = db_connector.connect()
        >>> if status_code == 0:
        ...     print("Connection established.")
        ... else:
        ...     print(f"Connection failed with error: {status_message}")

        >>> # Example of inserting a new object
        >>> query = "insert into users (id, name) values (?, ?);"
        >>> params = (1, 'John Doe')
        >>> status_code, status_message = db_connector.execute_query(query, params)
        >>> if status_code == 0:
        ...     print("User added successfully.")
        ... else:
        ...     print(f"Failed to add user with error: {status_message}")

        >>> # Example of selecting objects
        >>> query = "select * from users where name = ?;"
        >>> params = ('John Doe',)
        >>> status_code, status_message, results = db_connector.execute_read_query(query, params)
        >>> if status_code == 0:
        ...     print("Query executed successfully.")
        ...     for row in results:
        ...         print(row)
        ... else:
        ...     print(f"Query execution failed with error: {status_message}")

        >>> db_connector.close()
    """

    def __init__(self, db_file: str):
        """
        Initialize the SQLiteConnector with the path to the database file.

        Args:
            db_file (str): The path to the SQLite database file.
        """
        self.db_file = db_file
        self.connection = None

    def connect(self) -> Tuple[int, str]:
        """
        Establish a connection to the SQLite database.

        Returns:
            Tuple[int, str]: A tuple containing a status code and a message.
                             (0, 'OK') if successful, (1, 'error message') if an error occurs.
        """
        try:
            self.connection = sqlite3.connect(self.db_file)
        except Error as e:
            return 1, f'Error "{e}" occurred during database connection.'

        return 0, 'OK'

    def close(self):
        """
        Close the connection to the SQLite database.
        """
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: Tuple = None) -> Tuple[int, str]:
        """
        Execute a modification query against the SQLite database.

        Args:
            query (str): The SQL query to execute.
            params (Tuple, optional): Parameters to bind to the SQL query.

        Returns:
            Tuple[int, str]: A tuple containing a status code and a message.
                             (0, 'OK') if successful, (1, 'error message') if an error occurs.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
        except Error as e:
            return 1, f'The error "{e}" occurred'

        return 0, 'OK'

    def execute_read_query(self, query: str, params: Tuple = None) -> Tuple[int, str, List]:
        """
        Execute a read query against the SQLite database and fetch results.

        Args:
            query (str): The SQL query to execute.
            params (Tuple, optional): Parameters to bind to the SQL query.

        Returns:
            Tuple[int, str, List]: A tuple containing a status code, fetched results, and a message.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()

            return 0, 'OK', result
        except Error as e:
            return 1, f'The error "{e}" occurred', []
