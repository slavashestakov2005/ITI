from backend.database import Row, Table, Query


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
        return '.'.join(self.file.split('.')[2:-1])[1:]


class SubjectsFilesTable(Table):
    table = "subjects_files"
    row = SubjectFile
    create = '''(
        year	INT NOT NULL,
        subject	INT NOT NULL,
        file	VARCHAR(256) NOT NULL,
        PRIMARY KEY(subject,file,year)
        );'''

    @staticmethod
    def select_by_subject(year: int, subject: int) -> list:
        return Query.select_list(SubjectsFilesTable.table, SubjectFile, 'year', year, 'subject', subject)

    @staticmethod
    def select(subject_file: SubjectFile) -> SubjectFile:
        return Query.select_one(SubjectsFilesTable.table, SubjectFile, 'year', subject_file.year,
                                'subject', subject_file.subject, 'file', subject_file.file)

    @staticmethod
    def delete(subject_file: SubjectFile) -> None:
        return Query.delete(SubjectsFilesTable.table, 'year', subject_file.year, 'subject', subject_file.subject,
                            'file', subject_file.file)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Query.delete(SubjectsFilesTable.table, 'year', year)
