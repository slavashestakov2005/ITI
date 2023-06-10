from flask_restful import Api
from backend import app
from .__help__ import *
from . import group_result, message, result, student, subject, subject_student, team, team_student, user, year, year_subject


api = Api(app)
api.add_resource(group_result.GroupResultListResource, '/api/v1/group_result')
api.add_resource(message.MessageListResource, '/api/v1/message')
api.add_resource(message.MessageResource, '/api/v1/message/<int:item_id>')
api.add_resource(result.ResultListResource, '/api/v1/result')
api.add_resource(student.StudentListResource, '/api/v1/student')
api.add_resource(student.StudentResource, '/api/v1/student/<int:item_id>')
api.add_resource(subject.SubjectListResource, '/api/v1/subject')
api.add_resource(subject.SubjectResource, '/api/v1/subject/<int:item_id>')
api.add_resource(subject_student.SubjectStudentListResource, '/api/v1/subject_student')
api.add_resource(team.TeamListResource, '/api/v1/team')
api.add_resource(team.TeamResource, '/api/v1/team/<int:item_id>')
api.add_resource(team_student.TeamStudentListResource, '/api/v1/team_student')
api.add_resource(user.UserListResource, '/api/v1/user')
api.add_resource(user.UserResource, '/api/v1/user/<int:item_id>')
api.add_resource(year.YearListResource, '/api/v1/year')
api.add_resource(year.YearResource, '/api/v1/year/<int:item_id>')
api.add_resource(year_subject.YearSubjectListResource, '/api/v1/year_subject')
api.add_resource(year_subject.YearSubjectResource, '/api/v1/year_subject/<int:year>/<int:subject>')
