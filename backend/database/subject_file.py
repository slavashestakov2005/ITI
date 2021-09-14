from backend.database import Table, Row


class SubjectFile(Row):
    """
        Строка таблицы SubjectsFilesTable
        year        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
        file        TEXT    NOT NULL    PK
    """
    fields = ['year', 'subject', 'file']

    def __init__(self, row):
        Row.__init__(self, SubjectFile, row)

    def just_filename(self):
        return self.file.rsplit('.', 2)[1][1:]


class SubjectsFilesTable:
    table = "subjects_files"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(SubjectsFilesTable.table, '''(
        "year"	INTEGER NOT NULL,
        "subject"	INTEGER NOT NULL,
        "file"	TEXT NOT NULL,
        PRIMARY KEY("subject","file","year")
        )''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(SubjectsFilesTable.table, SubjectFile)

    @staticmethod
    def select_by_subject(year: int, subject: int) -> list:
        return Table.select_list(SubjectsFilesTable.table, SubjectFile, 'year', year, 'subject', subject)

    @staticmethod
    def select(subject_file: SubjectFile) -> SubjectFile:
        return Table.select_one(SubjectsFilesTable.table, SubjectFile, 'year', subject_file.year,
                                'subject', subject_file.subject, 'file', subject_file.file)

    @staticmethod
    def insert(subject_file: SubjectFile) -> None:
        return Table.insert(SubjectsFilesTable.table, subject_file)

    @staticmethod
    def delete(subject_file: SubjectFile) -> None:
        return Table.delete(SubjectsFilesTable.table, 'year', subject_file.year, 'subject', subject_file.subject,
                            'file', subject_file.file)
