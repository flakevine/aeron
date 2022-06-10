from dataclasses import dataclass
from typing import List, Literal
import sqlite3 as sqlite
import os
import re


class Field:
    """A Field model used to define fields in a Table model.
    Can also be called a column"""
    def __init__(self,
                 field_name: str,
                 field_type: Literal["INTEGER", "TEXT"],
                 field_max_length: int = '',
                 is_primary_key: bool = False):
        self.name = field_name
        self.type = field_type
        self.max_length = f'({field_max_length})' if field_max_length != '' else ''
        self.primary_key = 'PRIMARY KEY AUTOINCREMENT' if is_primary_key else 'NOT NULL'

    def __str__(self):
        sql_string = f'{self.name} {self.type} {self.max_length} {self.primary_key}'
        return re.sub(' +', ' ', sql_string)


@dataclass
class Table:
    """A Table model used to create your sqlite database tables"""
    table_name: str
    fields: List[Field]


class ZeroTablesError(Exception):
    """You need to create at least one table to scaffold your Database"""
    pass


class Database:
    """A database model that will be used to create a sqlite database archive"""
    def __init__(self,
                 db_path: str = os.getcwd(),
                 tables: List[Table] = [],
                 insta_scaffold: bool = False):
        # if tables is None:
        #     tables = []
        # if db_path is None:
        #     db_path = os.getcwd()

        self.table_list = tables
        self.db_path = f'{db_path}/database.sqlite'
        if insta_scaffold:
            self.scaffold()

    def insert_table(self, table: Table):
        """Inserts a table in the table list"""
        self.table_list.append(table)

    def remove_table_by_index(self, index: int):
        """Removes a table from the database by its index on the table list"""
        self.table_list.pop(index)

    def scaffold(self):
        """A helper method that creates your sqlite archive and structure it
        with all the tables that the Database instance contains in its table list"""
        if len(self.table_list) == 0:
            raise ZeroTablesError("You need to create at least one table to scaffold your Database")

        for table in self.table_list:
            self.__scaffold_table(table)

    def __scaffold_table(self, table: Table):
        """Private method that scaffolds individual tables.
        THIS SHOULD NOT BE USED OUTSIDE THE DATABASE CLASS DEFINITION."""
        connection = sqlite.connect(self.db_path)
        cursor = connection.cursor()

        table_tuple_string = '('
        for field in table.fields:
            # The Field class has a special __str__ method that translates it to SQL
            table_tuple_string += f'{str(field)},'
        table_tuple_string = table_tuple_string[:-1]
        table_tuple_string += ' )'

        print(f'CREATE TABLE {table.table_name} {table_tuple_string};')
        cursor.execute(f'CREATE TABLE {table.table_name} {table_tuple_string};')

        connection.commit()
        connection.close()
