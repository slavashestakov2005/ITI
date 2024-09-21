from .__parent_writer__ import ExcelParentWriter
from ..database import *


class ExcelItiWriter(ExcelParentWriter):
    def __init__(self, filename: str, iti_id: int):
        self.filename = filename
        self.iti_id = iti_id

    def __gen_sheet__(self, worksheet, head, data):
        self.__head__(worksheet, *head)
        self.__write__(worksheet, data)

    def parse_data(self, table, data):
        sheet = []
        for row in data:
            line = []
            for field in table.fields:
                line.append(getattr(row, field))
            sheet.append(line)
        self.__gen_sheet__(self.workbook.add_worksheet(table.__tablename__), table.fields, sheet)

    def write(self):
        self.__styles__(self.filename)
        iti_subject_score, result, subject_student, subject_roles = [], [], [], []
        group_result, team_student = [], []
        for iti_subject in ItiSubject.select_by_iti(self.iti_id):
            iti_subject_score.extend(ItiSubjectScore.select_by_iti_subject(iti_subject.id))
            result.extend(Result.select_by_iti_subject(iti_subject.id))
            subject_student.extend(SubjectStudent.select_by_iti_subject(iti_subject.id))
            subject_roles.extend(RoleItiSubject.select_by_iti_subject(iti_subject.id))
        for team in Team.select_by_iti(self.iti_id):
            group_result.extend(GroupResult.select_by_team(team.id))
            team_student.extend(TeamStudent.select_by_team(team.id))

        self.parse_data(Barcode, Barcode.select_by_iti(self.iti_id))
        self.parse_data(Code, Code.select_by_iti(self.iti_id))
        self.parse_data(GroupResult, group_result)
        self.parse_data(IndDayStudent, IndDayStudent.select_by_iti(self.iti_id))
        self.parse_data(Iti, [Iti.select(self.iti_id)])
        self.parse_data(ItiSubject, ItiSubject.select_by_iti(self.iti_id))
        self.parse_data(ItiSubjectScore, iti_subject_score)
        self.parse_data(Message, Message.select_by_iti(self.iti_id))
        self.parse_data(Result, result)
        self.parse_data(RoleIti, RoleIti.select_by_iti(self.iti_id))
        self.parse_data(RoleItiSubject, subject_roles)
        self.parse_data(School, School.select_all())
        self.parse_data(Student, Student.select_all())
        self.parse_data(StudentClass, StudentClass.select_by_iti(self.iti_id))
        self.parse_data(Subject, Subject.select_all())
        self.parse_data(SubjectStudent, subject_student)
        self.parse_data(Team, Team.select_by_iti(self.iti_id))
        self.parse_data(TeamConsent, TeamConsent.select_by_iti(self.iti_id))
        self.parse_data(TeamStudent, team_student)
        self.parse_data(User, User.select_all())
        self.workbook.close()
