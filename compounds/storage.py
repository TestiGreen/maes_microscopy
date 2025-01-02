import sqlite3
from sqlalchemy import create_engine
import pandas as pd

DATABASE_DIRECTORY = './data/chembl'

class DB_Storer:
    """
    Handles the storage of compound, assay, and activity data into SQLite databases.

    DB_Storer provides an interface to store different types of data into SQLite
    databases located in a specified directory. It manages compound data, assay
    data, and activity data by creating or appending to corresponding tables
    within the structured database files.

    :ivar base_database_url: Base URL for the database connections, formatted
        with `data_directory`.
    :type base_database_url: str
    :ivar data_directory: Directory where SQLite database files are located or
        will be created.
    :type data_directory: str
    """
    COMPOUND_DB = "compounds"
    ASSAYS_DB = "assays"
    ACTIVITY_DB = "activities"

    def __init__(self, data_directory: str=DATABASE_DIRECTORY):
        """
        Initializes the class with a base database URL and a data directory. The
        database URL is automatically formatted based on the provided data directory.

        :param data_directory: The directory where database files are stored.
        :type data_directory: str
        """
        self.base_database_url = f'sqlite:///{data_directory}/{{}}.db'
        self.data_directory = data_directory

    def store_compounds(self, df: pd.DataFrame):
        """
        Stores compound data into a specified database.

        This method takes a pandas DataFrame containing compound data and stores it
        in a pre-configured database. The data is saved in the 'compounds' table,
        replacing any existing data in the table.

        :param df: The DataFrame containing the compound data to be stored.
        :type df: pd.DataFrame
        """
        database_url = self.base_database_url.format(DB_Storer.COMPOUND_DB)
        sql_engine = create_engine(database_url)
        df.to_sql('compounds', con=sql_engine, if_exists='replace', index=False)

    def store_activities(self, df: pd.DataFrame, new_db: bool=False):
        """
        Stores activity data into a database.

        This function saves the given DataFrame into a database table named 'activities'.
        It accepts an option to either create a new database or append to an existing one.
        The data will be stored using the database URL constructed based on the activity
        database's configuration.

        :param df: DataFrame containing the data to be stored in the database.
        :type df: pd.DataFrame
        :param new_db: Specifies whether to create a new database ('replace') or append
            to an existing one ('append'). Defaults to False.
        :type new_db: bool
        :return: None
        """
        database_url = self.base_database_url.format(DB_Storer.ACTIVITY_DB)
        sql_engine = create_engine(database_url)
        df.to_sql('activities', con=sql_engine, if_exists='replace' if new_db else 'append', index=False)


# Use a single instance of the DB_Storer classes.  The first time this module is loaded a new instance will be made
# and stored in the global namespace.  Later the same instance will be retrieved from the global scope.
if not 'db_storer' in globals():
    globals()['db_storer'] = DB_Storer()

db_storer = globals()['db_storer']