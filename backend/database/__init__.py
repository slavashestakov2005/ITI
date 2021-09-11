from .database import *
from .subject import *
from .user import *
from .year import *
from .year_subject import *
from .result import *
from .student import *
from .team import *
from .student_code import *
from .team_student import *
from .group_result import *
from .appeal import *
from .file import *
from ..config import Config


def create_tables():
    if Config.DROP_DB:
        SubjectsTable.create_table()
        UsersTable.create_table()
        YearsTable.create_table()
        YearsSubjectsTable.create_table()
        ResultsTable.create_table()
        StudentsTable.create_table()
        TeamsTable.create_table()
        StudentsCodesTable.create_table()
        TeamsStudentsTable.create_table()
        GroupResultsTable.create_table()
        AppealsTable.create_table()
        FilesTable.create_table()
