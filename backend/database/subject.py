from backend.database import DataBase


class Subject:
    pass


class SubjectsTable:
    name = "subject"

    @staticmethod
    def create_table() -> None:
        DataBase.execute("""CREATE TABLE "constants" (
            "name"	TEXT NOT NULL UNIQUE,
            "value"	TEXT NOT NULL,
            PRIMARY KEY("name"));""")




