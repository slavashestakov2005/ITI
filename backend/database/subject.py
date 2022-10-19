from backend.database import Row, Table, Query


class Subject(Row):
    """
        Строка таблицы SubjectsTable
        id          INT     NOT NULL    PK  AI  UNIQUE
        name        TEXT    NOT NULL            UNIQUE
        short_name  TEXT    NOT NULL
        type        TEXT    NOT NULL    ('i' / 'g' / 'a')
        diploma     TEXT    NOT NULL
    """
    fields = ['id', 'name', 'short_name', 'type', 'diploma']

    def __init__(self, row):
        Row.__init__(self, Subject, row)

    def type_str(self):
        if self.type == 'i':
            return 'individual'
        elif self.type == 'g':
            return 'group'
        return 'team'

    def diplomas_br(self):
        return self.diploma.replace('\n', '<br>')


class SubjectsTable(Table):
    table = "subject"
    row = Subject
    create = '''(
        id          INT         NOT NULL UNIQUE KEY AUTO_INCREMENT,
        name	    VARCHAR(30) NOT NULL UNIQUE,
        short_name	TEXT        NOT NULL,
        type	    TEXT        NOT NULL,
        diploma     TEXT        NOT NULL,
        PRIMARY KEY(id)
        );'''

    @staticmethod
    def create_table() -> None:
        super().create_table()
        SubjectsTable.insert(Subject([None, 'Командный тур', 'Команд.', 'a', 'в командном туре']))
        SubjectsTable.insert(Subject([None, 'История', 'Ист.', 'i', 'в индивидуальном туре\nпо истории']))
        SubjectsTable.insert(Subject([None, 'Английский язык', 'Анг.', 'i', 'в индивидуальном туре\nпо английскому языку']))
        SubjectsTable.insert(Subject([None, 'Русский язык', 'Рус.', 'i', 'в индивидуальном туре\nпо русскому языку']))
        SubjectsTable.insert(Subject([None, 'Информатика', 'Инф.', 'i', 'в индивидуальном туре\nпо информатике']))
        SubjectsTable.insert(Subject([None, 'ИЦН', 'ИЦН', 'i', 'в индивидуальном туре\nпо ИЦН']))
        SubjectsTable.insert(Subject([None, 'Математика', 'Мат.', 'i', 'в индивидуальном туре\nпо математике']))
        SubjectsTable.insert(Subject([None, 'Обществознание', 'Общ.', 'i', 'в индивидуальном туре\nпо обществознанию']))
        SubjectsTable.insert(Subject([None, 'Естествознание', 'Ест.', 'i', 'в индивидуальном туре\nпо естествознанию']))
        SubjectsTable.insert(Subject([None, 'Литература', 'Лит.', 'i', 'в индивидуальном туре\nпо литературе']))
        SubjectsTable.insert(Subject([None, 'Искусство', 'Иск.', 'i', 'в индивидуальном туре\nпо искусству']))
        SubjectsTable.insert(Subject([None, 'Карусель', 'Карус.', 'g', 'в карусели']))
        SubjectsTable.insert(Subject([None, 'Естественно-научные бои', 'Е-н. бои', 'g', 'в естественно-научных боях']))
        SubjectsTable.insert(Subject([None, 'Коммуникативные бои', 'Ком. бои', 'g', 'в коммуникативных боях']))
        SubjectsTable.insert(Subject([None, ' Литература', 'Пар. лит.', 'g', 'в групповом туре\nпо литературе']))
        SubjectsTable.insert(Subject([None, ' Английский язык', 'Пар. анг.', 'g', 'в групповом туре\nпо английскому языку']))
        SubjectsTable.insert(Subject([None, 'Театр', 'Театр', 'g', 'в театре']))
        SubjectsTable.insert(Subject([None, 'Изобретательство', 'Изобр.', 'g', 'в изобретательстве']))
        SubjectsTable.insert(Subject([None, ' Информатика', 'Пар. инф.', 'g', 'в групповом туре\nпо информатике']))
        SubjectsTable.insert(Subject([None, 'Окружающий мир', 'Окр. мир', 'i', 'в индивидуальном туре\nпо окружающему миру']))

    @staticmethod
    def select_by_name(name: str) -> Subject:
        return Query.select_one(SubjectsTable.table, Subject, 'name', name)
