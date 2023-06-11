from backend import app
from ..database import Student, Subject, SubjectStudent, Team, TeamStudent, YearSubject, User
from .help import check_status, check_block_year, is_in_team, compare
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


def teams_page_params(user: User, year: int):
    try:
        teams, res, subjects, team_tour = user.teams_list(year), [], [], None
        subjects.append(Subject.build(-1, 'Инд. 1', 'Инд. 1', 'g', 'diploma', 'msg'))
        subjects.append(Subject.build(-2, 'Инд. 2', 'Инд. 2', 'g', 'diploma', 'msg'))
        subjects.append(Subject.build(-3, 'Инд. 3', 'Инд. 3', 'g', 'diploma', 'msg'))
        subjects.append(Subject.build(-4, 'Инд. 4', 'Инд. 4', 'g', 'diploma', 'msg'))
        for x in YearSubject.select_by_year(year):
            subject = Subject.select(x.subject)
            if subject.type == 'g':
                subjects.append(subject)
            if subject.type == 'a':
                team_tour = subject
        if team_tour:
            subjects.append(team_tour)
        teams = sorted(list(teams), key=compare(lambda x: -x // abs(x), lambda x: x, field=True))
        for now in teams:
            if now < 0:
                team, t = Team.build(now, 'Отказ', None, None), []
            else:
                team, t = Team.select(now), []
            peoples = TeamStudent.select_by_team(team.id)
            for x in peoples:
                people = Student.select(x.student)
                subjects_for_people = set([_.subject for _ in SubjectStudent.select_by_student(year, people.id)])
                p = [[None, people.class_name()], [None, people.name_1], [None, people.name_2]]
                for subject in subjects:
                    p.append([subject.id, people.id, subject.id in subjects_for_people])
                t.append(p)
            t.sort(key=compare(lambda x: x[0][1], lambda x: x[1][1], lambda x: x[2][1], field=True))
            res.append([team.name, t])
        return {'year': abs(year), 'teams': res, 'subjects': [_.short_name for _ in subjects]}
    except Exception:
        return {}


@app.route("/<year:year>/save_teams", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def save_teams(year: int):
    t = set(request.form.getlist('t'))
    ot = set(request.form.getlist('ot'))
    cl = request.form['cl']
    if 'part' in request.form:
        kw = {'error' + str(ord(request.form['part'])): 'Сохранено'}
        url = '{}/rating_{}.html'.format(year, cl)
    else:
        kw = {'error' + cl: 'Сохранено'}
        url = '{}/rating.html'.format(year)
    different = set(_[:-2] for _ in t.symmetric_difference(ot))
    for x in different:
        cnt = (x + '_0' in t) + (x + '_1' in t) + (x + '_2' in t)
        if cnt != 1:
            return render_template(url, **teams_page_params(current_user, year), error='Некорректные данные')
    pl, mn = is_in_team(year)
    for x in different:
        st = int(x)
        if x + '_0' in ot:
            TeamStudent.delete(TeamStudent.build(mn, st))
        if x + '_2' in ot:
            TeamStudent.delete(TeamStudent.build(pl, st))
        if x + '_0' in t:
            TeamStudent.insert(TeamStudent.build(mn, st))
        if x + '_2' in t:
            TeamStudent.insert(TeamStudent.build(pl, st))
    Generator.gen_ratings(year)
    return render_template(url, **teams_page_params(current_user, year), **kw)


@app.route("/<year:year>/team_edit")
@cross_origin()
@login_required
@check_block_year()
def team_edit(year: int):
    return render_template(str(year) + '/teams_for_year.html', **teams_page_params(current_user, year))


@app.route("/<year:year>/automatic_division", methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def automatic_division(year: int):
    args = teams_page_params(current_user, year)
    good = Generator.gen_automatic_division(year)
    Generator.gen_teams(year)
    Generator.gen_teams_students(year)
    if not good:
        return render_template(str(year) + '/teams_for_year.html', **args, error9='Остались свободные места')
    message_teams_public(year)
    return render_template(str(year) + '/teams_for_year.html', **args, error9='Участники распределены')
