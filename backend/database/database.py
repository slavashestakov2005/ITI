import sqlite3
from typing import Tuple


class DataBase:
    @staticmethod
    def execute(sql: str, params=()) -> list:
        print("SQL : " + sql + ", params = " + str(params))
        connection = sqlite3.connect('backend/database.db')
        cursor = connection.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        connection.commit()
        connection.close()
        return result

    @staticmethod
    def execute_one(sql: str, params=()) -> Tuple:
        result = DataBase.execute(sql, params)
        if not result or len(result) == 0:
            return ()
        return result[0]


class Row:
    def __init__(self, cls, row):
        if len(row) == 0:
            self.__is_none__ = True
            return
        self.__is_none__ = False
        position = 0
        self.cls = cls
        for field in cls.fields:
            self.__setattr__(field, row[position])
            position += 1

    def __repr__(self):
        if self.__is_none__:
            return "{None}"
        data = {}
        for field in self.cls.fields:
            data[field] = self.__getattribute__(field)
        return str(data)

    def update_string(self):
        if self.__is_none__:
            raise ValueError("Updates row is {None}")
        text = ""
        params = []
        for field in self.cls.fields:
            text += ", " + field + " = ?"
            params.append(getattr(self, field))
        return text[2:], params


class Table:
    @staticmethod
    def select_all(table_name: str, cls) -> list:
        return [cls(_) for _ in DataBase.execute("SELECT * FROM " + table_name)]

    @staticmethod
    def select_by_field(table_name: str, field: str, value, cls):
        return cls(DataBase.execute_one("SELECT * FROM " + table_name + " WHERE " + field + " = ?", (value,)))

    @staticmethod
    def select_list_by_field(table_name: str, field: str, value, cls) -> list:
        return [cls(_) for _ in DataBase.execute("SELECT * FROM " + table_name + " WHERE " + field + " = ?", (value,))]

    @staticmethod
    def update_by_field(table_name: str, field: str, value):
        params = value.update_string()
        params[1].append(getattr(value, field))
        return DataBase.execute("UPDATE " + table_name + " SET " + params[0] + " WHERE " + field + " = ?", params[1])

    @staticmethod
    def insert(table_name: str, value, fields: list):
        if value.__is_none__:
            raise ValueError("Insert row is {None}")
        text = "INSERT INTO " + table_name + "("
        text2 = ") VALUES ("
        params = []
        for field in fields:
            text += field + ", "
            text2 += "?, "
            params.append(getattr(value, field))
        return DataBase.execute(text[:-2] + text2[:-2] + ")", params)

    @staticmethod
    def insert_all_columns(table_name: str, value):
        return Table.insert(table_name, value, value.cls.field)

    @staticmethod
    def delete(table_name: str, value):
        return DataBase.execute("DELETE FROM " + table_name + " WHERE id = ?", (value.id,))

    @staticmethod
    def delete_by_field(table_name: str, field: str, value):
        return DataBase.execute("DELETE FROM " + table_name + " WHERE " + field + " = ?", (value,))
