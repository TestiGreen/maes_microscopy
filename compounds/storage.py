import sqlite3
from sqlalchemy import create_engine
import pandas as pd

DATABASE_DIRECTORY = './data/chembl'

class DB_Storer:
    COMPOUND_DB = "compounds"
    ASSAYS_DB = "assays"
    ACTIVITY_DB = "activities"

    def __init__(self, data_directory: str=DATABASE_DIRECTORY):
        self.base_database_url = f'sqlite:///{data_directory}/{{}}.db'
        self.data_directory = data_directory

    def store_compounds(self, df: pd.DataFrame):
        database_url = self.base_database_url.format(DB_Storer.COMPOUND_DB)
        sql_engine = create_engine(database_url)
        df.to_sql('compounds', con=sql_engine, if_exists='replace', index=False)

    def store_activities(self, df: pd.DataFrame, new_db: bool=False):
        database_url = self.base_database_url.format(DB_Storer.ACTIVITY_DB)
        sql_engine = create_engine(database_url)
        df.to_sql('activities', con=sql_engine, if_exists='replace' if new_db else 'append', index=False)

if not 'db_storer' in globals():
    globals()['db_storer'] = DB_Storer()

db_storer = DB_Storer()