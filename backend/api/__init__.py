from flask_restful import Api
from backend import app
from .__help__ import *
from . import group_result, iti, iti_subject, message, result, school, student, student_class, subject,\
    subject_student, team, team_student, user


api = Api(app)
api.add_resource(group_result.GroupResultListResource, '/api/v1/group_result')
api.add_resource(iti.ItiListResource, '/api/v1/iti')
api.add_resource(iti.ItiResource, '/api/v1/iti/<int:item_id>')
api.add_resource(iti_subject.ItiSubjectListResource, '/api/v1/iti_subject')
api.add_resource(iti_subject.ItiSubjectResource, '/api/v1/iti_subject/<int:iti_id>/<int:subject_id>')
api.add_resource(message.MessageListResource, '/api/v1/message')
api.add_resource(message.MessageResource, '/api/v1/message/<int:item_id>')
api.add_resource(result.ResultListResource, '/api/v1/result')
api.add_resource(school.SchoolListResource, '/api/v1/school')
api.add_resource(school.SchoolResource, '/api/v1/school/<int:item_id>')
api.add_resource(student.StudentListResource, '/api/v1/student')
api.add_resource(student.StudentResource, '/api/v1/student/<int:item_id>')
api.add_resource(student_class.StudentClassResource, '/api/v1/student_class/<int:iti_id>/<int:student_id>')
api.add_resource(subject.SubjectListResource, '/api/v1/subject')
api.add_resource(subject.SubjectResource, '/api/v1/subject/<int:item_id>')
api.add_resource(subject_student.SubjectStudentListResource, '/api/v1/subject_student')
api.add_resource(team.TeamListResource, '/api/v1/team')
api.add_resource(team.TeamResource, '/api/v1/team/<int:item_id>')
api.add_resource(team_student.TeamStudentListResource, '/api/v1/team_student')
api.add_resource(user.UserListResource, '/api/v1/user')
api.add_resource(user.UserResource, '/api/v1/user/<int:item_id>')
