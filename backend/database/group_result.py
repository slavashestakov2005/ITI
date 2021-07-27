from backend.database import DataBase, Table, Row


class GroupResult(Row):
    """
        Строка таблицы GroupResultsTable
        team        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
        result      INT     NOT NULL
    """
    fields = ['team', 'subject', 'result']

    def __init__(self, row):
        Row.__init__(self, GroupResult, row)

    @staticmethod
    def sort_by_result(result):
        return -result.result


class GroupResultsTable:
    table = "group_results"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + GroupResultsTable.table + '''" (
        "team"	INTEGER NOT NULL,
        "subject"	INTEGER NOT NULL,
        "result"	INTEGER NOT NULL,
        PRIMARY KEY("team","subject")
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(GroupResultsTable.table, GroupResult)

    @staticmethod
    def select_by_team_and_subject(team: int, subject: int) -> GroupResult:
        return Table.select_by_fields(GroupResultsTable.table, GroupResult, 'team', team, 'subject', subject)

    @staticmethod
    def update(group_result: GroupResult):
        return Table.update_by_fields(GroupResultsTable.table, group_result, 'team', group_result.team, 'subject',
                                      group_result.subject)

    @staticmethod
    def insert(group_result: GroupResult) -> None:
        return Table.insert(GroupResultsTable.table, group_result, group_result.fields)
