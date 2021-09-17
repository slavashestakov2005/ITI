from backend.database import Table, Row


class Subject(Row):
    """
        Строка таблицы SubjectsTable
        id      INT     NOT NULL    PK  AI  UNIQUE
        name    TEXT    NOT NULL            UNIQUE
        type    TEXT    NOT NULL    ('i' / 'g' / 'a')
    """
    fields = ['id', 'name', 'type']

    def __init__(self, row):
        Row.__init__(self, Subject, row)

    def type_str(self):
        if self.type == 'i':
            return 'individual'
        elif self.type == 'g':
            return 'group'
        return 'team'


class SubjectsTable:
    table = "subject"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(SubjectsTable.table, '''(
        "id"	SERIAL NOT NULL UNIQUE,
        "name"	TEXT NOT NULL UNIQUE,
        "type"	TEXT NOT NULL,
        PRIMARY KEY("id")
        )''')
        SubjectsTable.insert(Subject([None, 'Командный тур', 'a']))
        SubjectsTable.insert(Subject([None, 'История', 'i']))
        SubjectsTable.insert(Subject([None, 'Английский язык', 'i']))
        SubjectsTable.insert(Subject([None, 'Русский язык', 'i']))
        SubjectsTable.insert(Subject([None, 'Информатика', 'i']))
        SubjectsTable.insert(Subject([None, 'ИЦН', 'i']))
        SubjectsTable.insert(Subject([None, 'Математика', 'i']))
        SubjectsTable.insert(Subject([None, 'Обществознание', 'i']))
        SubjectsTable.insert(Subject([None, 'Естествознание', 'i']))
        SubjectsTable.insert(Subject([None, 'Литература', 'i']))
        SubjectsTable.insert(Subject([None, 'Исскуство', 'i']))
        SubjectsTable.insert(Subject([None, 'Карусель', 'g']))
        SubjectsTable.insert(Subject([None, 'Естественно-научные бои', 'g']))
        SubjectsTable.insert(Subject([None, 'Коммуникативные бои', 'g']))
        SubjectsTable.insert(Subject([None, 'Литература (групповая)', 'g']))
        SubjectsTable.insert(Subject([None, 'Английский язык (групповой)', 'g']))
        SubjectsTable.insert(Subject([None, 'Театр', 'g']))
        SubjectsTable.insert(Subject([None, 'Изобретательство', 'g']))

    @staticmethod
    def select_all() -> list:
        return Table.select_list(SubjectsTable.table, Subject)

    @staticmethod
    def select_by_name(name: str) -> Subject:
        return Table.select_one(SubjectsTable.table, Subject, 'name', name)

    @staticmethod
    def select_by_id(id: int) -> Subject:
        return Table.select_one(SubjectsTable.table, Subject, 'id', id)

    @staticmethod
    def insert(subject: Subject) -> None:
        return Table.insert(SubjectsTable.table, subject)

    @staticmethod
    def update_by_id(subject: Subject) -> None:
        return Table.update(SubjectsTable.table, subject)

    @staticmethod
    def delete(subject: Subject) -> None:
        return Table.delete(SubjectsTable.table, subject)
