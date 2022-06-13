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


class DatabaseNotFound(Exception):
    """The file path specified does not match an existent sqlite database archive"""
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

    def get_table_index(self, table_name: str) -> int:
        """Gets the index of a table in the table list by searching with its exact table_name"""
        for index, table in enumerate(self.table_list):
            if table_name == table.table_name:
                return index

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

        # print(f'CREATE TABLE {table.table_name} {table_tuple_string};')
        cursor.execute(f'CREATE TABLE {table.table_name} {table_tuple_string};')

        connection.commit()
        connection.close()

    def get_table_fieldnames(self, table_index: int) -> List[str]:
        """Recieves a table index and returns a list of strings with all the fieldnames in the table"""
        return [field.name for field in self.table_list[table_index].fields]

    def insert_one_tuple(self, table_index: int, tuple_data: dict) -> bool:
        """Selects a table by its index and inserts a tuple (or line) of data in it.
        The tuple must be a dictionary following the model {field_name: field_value}.
        You can get all the fieldnames of a table with the get_table_fieldnames() method.
        This method returns True if the database operation went OK and False if something went wrong."""
        tablename = self.table_list[table_index].table_name
        keys = values = '('
        for key, value in tuple_data.items():
            keys += f'"{key}", '
            values += f'"{value}", '

        keys = keys[:-2]
        values = values[:-2]
        keys += ')'
        values += ')'

        sql_string = f'Insert into {tablename} {keys} values {values};'
        connection = sqlite.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql_string)
            connection.commit()
            connection.close()
            return True
        except:
            connection.rollback()
            connection.close()
            return False

    def get_one_tuple(self, table_index: int, tuple_id: int) -> dict:
        """Gets a tuple (or a line) of data from a table by its primary key id and returns
        a dictionary containing all the info in the format {column_name: column_value}"""
        table_name = self.table_list[table_index].table_name

        connection = sqlite.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(f'PRAGMA table_info({table_name})')
        tuples_info = cursor.fetchall()

        primary_key_field = ''
        keys = []
        for info in tuples_info:
            keys.append(info[1])
            if bool(info[-1]):
                primary_key_field = info[1]

        cursor.execute(f'SELECT * FROM "{table_name}" WHERE "{primary_key_field}" = "{tuple_id}";')

        table_tuple = {}
        for idx, value in enumerate(cursor.fetchone()):
            table_tuple[keys[idx]] = value

        return table_tuple

    def get_all_tuples(self, table_index: int) -> List[dict]:
        """Returns all tuples (lines) contained in a table, each line following the format {column_name: column_value}"""
        table_name = self.table_list[table_index].table_name

        connection = sqlite.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(f'PRAGMA table_info({table_name})')
        tuples_info = cursor.fetchall()

        keys = []
        for info in tuples_info:
            keys.append(info[1])

        cursor.execute(f'SELECT * FROM {table_name};')

        all_tuples = []
        table_tuple = {}
        raw_tuples = cursor.fetchall()
        for tup in raw_tuples:
            for idx, value in enumerate(tup):
                table_tuple[keys[idx]] = value
            all_tuples.append(table_tuple.copy())
            table_tuple.clear()

        return all_tuples

    def update_one_tuple(self, table_index: int, tuple_id: int, new_tuple_value: dict) -> bool:
        """Recieves a table index to identify the table, a tuple id (primary key) to identify the line of the table
        to be changed and a new tuple value that will update it. The new_tuple_value variable needs to follow the
        model {column_name: field_value}. YOU ONLY NEED TO PASS THE VALUES THAT YOU WANT TO CHANGE IN THE DICT.
        To get all the column names of a table, you can use the get_table_fieldnames() method.
        Returns true if everything went OK, false otherwise."""
        table_name = self.table_list[table_index].table_name
        connection = sqlite.connect(self.db_path)
        try:
            cursor = connection.cursor()

            cursor.execute(f'PRAGMA table_info({table_name})')
            tuples_info = cursor.fetchall()

            primary_key_field = ''
            for info in tuples_info:
                if bool(info[-1]):
                    primary_key_field = info[1]

            for key, value in new_tuple_value.items():
                cursor.execute(f'UPDATE {table_name} set {key} = {value} where {primary_key_field} = {tuple_id};')

            connection.commit()
            connection.close()
            return True
        except sqlite.Error as err:
            print(f"Failed to update {table_name}. Error:", err)
            connection.rollback()
            return False
        except:
            print("Unknown error ocurred...")
            connection.rollback()
            return False

    def delete_one_tuple(self, table_index: int, tuple_id: int) -> bool:
        """Takes a table index and a tuple id (primary key) as an argument and deletes it from the table.
        Returns True if everything went OK, otherwise False."""
        table_name = self.table_list[table_index].table_name
        connection = sqlite.connect(self.db_path)

        try:
            cursor = connection.cursor()

            cursor.execute(f'PRAGMA table_info({table_name})')
            tuples_info = cursor.fetchall()

            primary_key_field = ''
            for info in tuples_info:
                if bool(info[-1]):
                    primary_key_field = info[1]

            cursor.execute(f'DELETE FROM {table_name} WHERE {primary_key_field} = {tuple_id};')

            connection.commit()
            connection.close()
            return True
        except sqlite.Error as err:
            print(f"Failed to update {table_name}. Error:", err)
            connection.rollback()
            return False
        except:
            print("Unknown error ocurred...")
            connection.rollback()
            return False


def connect(db_path: str) -> Database:
    """Connects the database class with an existing sqlite archive and map all its tables.
    Return a Database instance that lets you interact with it."""
    if not os.path.exists(db_path):
        raise DatabaseNotFound("The file path specified does not match an existent sqlite database archive")

    connection = sqlite.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('SELECT name from sqlite_master where type= "table";')
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]

    table_list = []

    for table_name in table_names:
        cursor.execute(f'PRAGMA table_info({table_name})')
        field_info_tuples = cursor.fetchall()

        fields = []
        for field_info in field_info_tuples:
            fieldtype = maxl = ''
            helper_list = field_info[2].split(' ')
            if len(helper_list) > 1:
                fieldtype = helper_list[0]
                maxl = helper_list[1]
            else:
                fieldtype = helper_list[0]

            fields.append(Field(field_name=field_info[1],
                                field_type=fieldtype,
                                field_max_length=maxl,
                                is_primary_key=bool(field_info[-1])))

        table_list.append(Table(table_name=table_name, fields=fields))

    new_db = Database(db_path, table_list)
    new_db.db_path = db_path
    return new_db
