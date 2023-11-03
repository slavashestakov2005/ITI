from backend import app
from ..database import Student, Subject, SubjectStudent, Team, TeamStudent, ItiSubject, User, TeamConsent, Iti,\
    IndDayStudent, School
from .help import check_status, compare, check_block_iti
from .auto_generator import Generator
from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .messages_help import message_teams_public
'''
    /<iti_id>/team_edit                     Redirect с параметрами на страницу редактирования (admin).
    /<iti_id>/automatic_division            Генерирует автоматическое распределение школьников (admin).
'''


def teams_page_params(user: User, iti: Iti):
    try:
        schools = School.select_id_dict()
        teams, res, subjects = user.teams_list(iti.id), [], []
        if iti.sum_ind_to_team:
            for day in range(1, 1 + iti.ind_days):
                name = 'Инд. {}'.format(day)
                subjects.append(Subject.build(-day, name, name, 'q', 'diploma', 'msg'))
        participants = set()
        for x in ItiSubject.select_by_iti(iti.id):
            subject = Subject.select(x.subject_id)
            if subject.type == 'g' or subject.type == 'a':
                subjects.append(subject)
                for part in SubjectStudent.select_by_iti_subject(x.id):
                    participants.add('{} {}'.format(subject.id, part.student_id))
        for val in IndDayStudent.select_by_iti(iti.id):
            participants.add('{} {}'.format(-val.n_d, val.student_id))
        subjects = sorted(subjects, key=Subject.sort_by_type)
        teams = sorted(list(teams))
        for now in teams:
            team, t = Team.select(now), []
            peoples = TeamStudent.select_by_team(team.id)
            for x in peoples:
                people = Student.select(x.student_id)
                people.load_class(iti.id)
                p = [[None, people.school_name(schools)], [None, people.class_name()], [None, people.name_1], [None, people.name_2]]
                for subject in subjects:
                    p.append([subject.id, people.id, '{} {}'.format(subject.id, people.id) in participants])
                t.append(p)
            t.sort(key=compare(lambda x: x[0][1], lambda x: x[1][1], lambda x: x[2][1], field=True))
            res.append([team, t])
        rejection = []
        for tc in TeamConsent.select_rejection_by_iti(iti.id):
            people = Student.select(tc.student_id)
            people.load_class(iti.id)
            rejection.append(people)
        rejection.sort(key=Student.sort_by_all)
        return {'teams': res, 'subjects': [_.short_name for _ in subjects], 'rejection': rejection, 'schools': schools}
    except Exception:
        return {}


@app.route("/<int:iti_id>/team_edit")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def team_edit(iti: Iti):
    return render_template(str(iti.id) + '/teams_for_year.html', **teams_page_params(current_user, iti))


@app.route("/<int:iti_id>/automatic_division", methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def automatic_division(iti: Iti):
    args = teams_page_params(current_user, iti)
    if iti.automatic_division == 0:
        return render_template(str(iti.id) + '/teams_for_year.html', **args,
                               error9='Автоматическое распределение отключено в настройках ИТИ')
    if iti.automatic_division not in [1, 2]:
        return render_template(str(iti.id) + '/teams_for_year.html', **args,
                               error9='Задан неверный вариант автоматического распределения в настройках ИТИ')
    good = Generator.gen_automatic_division(iti)
    Generator.gen_teams(iti.id)
    if not good:
        return render_template(str(iti.id) + '/teams_for_year.html', **args, error9='Остались свободные места')
    message_teams_public(iti.id)
    return render_template(str(iti.id) + '/teams_for_year.html', **args, error9='Участники распределены')
