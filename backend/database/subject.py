from backend.database import Table, Row


class Subject(Row):
    """
        Строка таблицы SubjectsTable
        id          INT     NOT NULL    PK  AI  UNIQUE
        name        TEXT    NOT NULL            UNIQUE
        short_name  TEXT    NOT NULL
        type        TEXT    NOT NULL    ('i' / 'g' / 'a')
    """
    fields = ['id', 'name', 'short_name', 'type']

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
        id          INT         NOT NULL UNIQUE KEY AUTO_INCREMENT,
        name	    VARCHAR(30) NOT NULL UNIQUE,
        short_name	TEXT        NOT NULL,
        type	    TEXT        NOT NULL,
        PRIMARY KEY(id)
        )''')
        SubjectsTable.insert(Subject([None, 'Командный тур', 'Команд.', 'a']))
        SubjectsTable.insert(Subject([None, 'История', 'Ист.', 'i']))
        SubjectsTable.insert(Subject([None, 'Английский язык', 'Анг.', 'i']))
        SubjectsTable.insert(Subject([None, 'Русский язык', 'Рус.', 'i']))
        SubjectsTable.insert(Subject([None, 'Информатика', 'Инф.', 'i']))
        SubjectsTable.insert(Subject([None, 'ИЦН', 'ИЦН', 'i']))
        SubjectsTable.insert(Subject([None, 'Математика', 'Мат.', 'i']))
        SubjectsTable.insert(Subject([None, 'Обществознание', 'Общ.', 'i']))
        SubjectsTable.insert(Subject([None, 'Естествознание', 'Ест.', 'i']))
        SubjectsTable.insert(Subject([None, 'Литература', 'Лит.', 'i']))
        SubjectsTable.insert(Subject([None, 'Искусство', 'Иск.', 'i']))
        SubjectsTable.insert(Subject([None, 'Карусель', 'Карус.', 'g']))
        SubjectsTable.insert(Subject([None, 'Естественно-научные бои', 'Е-н. бои', 'g']))
        SubjectsTable.insert(Subject([None, 'Коммуникативные бои', 'Ком. бои', 'g']))
        SubjectsTable.insert(Subject([None, ' Литература', 'Пар. лит.', 'g']))
        SubjectsTable.insert(Subject([None, ' Английский язык', 'Пар. анг.', 'g']))
        SubjectsTable.insert(Subject([None, 'Театр', 'Театр', 'g']))
        SubjectsTable.insert(Subject([None, 'Изобретательство', 'Изобр.', 'g']))
        SubjectsTable.insert(Subject([None, ' Информатика', 'Пар. инф.', 'g']))

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
