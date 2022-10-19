from .database import Row, Table, Query


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


class GroupResultsTable(Table):
    table = "group_results"
    row = GroupResult
    create = '''(
        team	INT NOT NULL,
        subject	INT NOT NULL,
        result	INT NOT NULL,
        PRIMARY KEY(team,subject)
        );'''

    @staticmethod
    def select_by_team(team: int) -> list:
        return Query.select_list(GroupResultsTable.table, GroupResult, 'team', team)

    @staticmethod
    def select_by_subject(subject: int) -> list:
        return Query.select_list(GroupResultsTable.table, GroupResult, 'subject', subject)

    @staticmethod
    def select_by_team_and_subject(team: int, subject: int) -> GroupResult:
        return Query.select_one(GroupResultsTable.table, GroupResult, 'team', team, 'subject', subject)

    @staticmethod
    def update(group_result: GroupResult) -> None:
        return Query.update(GroupResultsTable.table, group_result, 'team', 'subject')

    @staticmethod
    def delete_by_team(team: int) -> None:
        return Query.delete(GroupResultsTable.table, 'team', team)
