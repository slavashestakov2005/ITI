from typing import Tuple
from ..config import Config
if Config.HEROKU:
    import psycopg2 as db
else:
    import sqlite3 as db


class DataBase:
    @staticmethod
    def prepare_sql(sql: str, params=()) -> str:
        print("SQL : " + sql + ", params = " + str(params))
        return sql if not Config.HEROKU else sql.replace('?', '%s')

    @staticmethod
    def just_execute(sql: str, params=()) -> None:
        sql = DataBase.prepare_sql(sql, params)
        connection = db.connect(Config.DB)
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
        connection.close()

    @staticmethod
    def execute(sql: str, params=()) -> list:
        sql = DataBase.prepare_sql(sql, params)
        connection = db.connect(Config.DB)
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
            text += ", " + Config.DB_COLS_PREFIX + field + " = ?"
            params.append(getattr(self, field))
        return text[2:], params


class Table:
    @staticmethod
    def correct_table_name(table_name: str):
        return Config.DB_TABLE_PREFIX + table_name

    @staticmethod
    def conditional_query(args):
        if not args or not len(args):
            return '', []
        text = ' WHERE '
        params = []
        for i in range(0, len(args), 2):
            if i > 0:
                text += ' AND '
            text += Config.DB_COLS_PREFIX + args[i] + ' = ?'
            params.append(args[i + 1])
        return text, params

    @staticmethod
    def drop_and_create(table_name: str, create: str) -> None:
        table_name = Table.correct_table_name(table_name)
        try:
            DataBase.just_execute('DROP TABLE ' + table_name)
        except Exception as ex:
            print('Exception: ', ex)
        try:
            new_create = create.split('"')
            create = new_create[0]
            for i in range(1, len(create), 2):
                create += '"' + Config.DB_COLS_PREFIX + new_create[i] + '"' + new_create[i + 1]
            DataBase.just_execute('CREATE TABLE "{0}" {1};'.format(table_name, create))
        except Exception as ex:
            print('Exception: ', ex)

    @staticmethod
    def select_one(table_name: str, cls, *args) -> Row:
        table_name = Table.correct_table_name(table_name)
        if not len(args):
            raise ValueError("Cannot select one row without parameters")
        x = Table.conditional_query(args)
        return cls(DataBase.execute_one("SELECT * FROM " + table_name + x[0], x[1]))

    @staticmethod
    def select_list(table_name: str, cls, *args) -> list:
        table_name = Table.correct_table_name(table_name)
        x = Table.conditional_query(args)
        return [cls(_) for _ in DataBase.execute("SELECT * FROM " + table_name + x[0], x[1])]

    @staticmethod
    def select_list_with_where(table_name: str, cls, field: str, start: int, end: int) -> list:
        table_name = Table.correct_table_name(table_name)
        field = Config.DB_COLS_PREFIX + field
        return [cls(_) for _ in DataBase.execute("SELECT * FROM {0} WHERE {1} < {2} AND {2} < {3}"
                                                 .format(table_name, start, field, end))]

    @staticmethod
    def update(table_name: str, value, *args) -> None:
        table_name = Table.correct_table_name(table_name)
        if not args or not len(args):
            args = ['id']
        new_args = []
        for arg in args:
            new_args.append(arg)
            new_args.append(getattr(value, arg))
        value = value.update_string()
        x = Table.conditional_query(new_args)
        return DataBase.just_execute("UPDATE " + table_name + " SET " + value[0] + x[0], value[1] + x[1])

    @staticmethod
    def update_col(table_name: str, field: str, value: str, op: str = '+') -> None:
        table_name = Table.correct_table_name(table_name)
        sql = 'UPDATE {0} SET {1} = {1} {2} {3}'.format(table_name, Config.DB_COLS_PREFIX + field, op, value)
        return DataBase.just_execute(sql)

    @staticmethod
    def insert_query(table_name: str, fields: list):
        text = "INSERT INTO " + table_name + " ("
        for field in fields:
            text += Config.DB_COLS_PREFIX + field + ", "
        return text[:-2] + ") VALUES"

    @staticmethod
    def insert_value(value, fields):
        params = []
        text = '('
        for field in fields:
            text += "?, "
            params.append(getattr(value, field))
        return text[:-2] + ')', params

    @staticmethod
    def insert(table_name: str, rows) -> None:
        table_name = Table.correct_table_name(table_name)
        if issubclass(type(rows), Row):
            rows = [rows]
        if rows is None or len(rows) == 0:
            raise ValueError("Insert empty list of rows")
        fields = rows[0].cls.fields
        new_fields = []
        for x in fields:
            if x != 'id':
                new_fields.append(x)
        fields = new_fields
        text = Table.insert_query(table_name, fields)
        params = []
        for row in rows:
            if row is None or row.__is_none__:
                raise ValueError("Insert row is {None}")
            t, p = Table.insert_value(row, fields)
            text += t + ', '
            params.extend(p)
        return DataBase.just_execute(text[:-2], params)

    @staticmethod
    def delete(table_name: str, *args) -> None:
        table_name = Table.correct_table_name(table_name)
        if len(args) == 1:
            args = ['id', args[0].id]
        x = Table.conditional_query(args)
        return DataBase.just_execute("DELETE FROM " + table_name + x[0], x[1])
