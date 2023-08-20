from backend import app
from ..database import Student, Subject, SubjectStudent, Team, TeamStudent, ItiSubject, User, TeamConsent, Iti,\
    IndDayStudent
from .help import check_status, compare, check_block_iti
from .auto_generator import Generator
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .messages_help import message_teams_public
'''
    teams_page_params(user, year)                               Параметры для страницы 'teams_for_year.html'
    /<year>/save_teams              save_teams()                Список согласных / несогласных играть у команде.
    /<year>/team_edit               team_edit()                 redirect с параметрами на страницу редактирования.
    /<year>/automatic_division      automatic_division()        Генерирует автоматическое распределение школьников.
'''


def teams_page_params(user: User, iti: Iti):
    try:
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
                for part in SubjectStudent.select_by_subject(x.id):
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
                p = [[None, people.class_name()], [None, people.name_1], [None, people.name_2]]
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
        return {'teams': res, 'subjects': [_.short_name for _ in subjects], 'rejection': rejection}
    except Exception:
        return {}


@app.route("/<int:iti_id>/save_teams", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def save_teams(iti: Iti):
    t = set(request.form.getlist('t'))
    ot = set(request.form.getlist('ot'))
    different = set(_[:-2] for _ in t.symmetric_difference(ot))
    for x in different:
        cnt = (x + '_0' in t) + (x + '_1' in t) + (x + '_2' in t)
        if cnt != 1:
            return render_template(url, **teams_page_params(current_user, iti), error='Некорректные данные')
    for x in different:
        st = int(x)
        if x + '_0' in ot:
            TeamConsent.delete(iti.id, st)
        if x + '_2' in ot:
            TeamConsent.delete(iti.id, st)
        if x + '_0' in t:
            TeamConsent.insert(TeamConsent.build(iti.id, st, -1))
        if x + '_2' in t:
            TeamConsent.insert(TeamConsent.build(iti.id, st, 1))
    Generator.gen_ratings(iti)
    return render_template(str(iti.id) + '/rating_students_check.html')


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
