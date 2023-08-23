from .help import SplitFile, all_templates, compare, html_render
from backend.excel.diploma_writer import ExcelDiplomaWriter
from ..database import Barcode, GroupResult, Result, Student, Subject, SubjectStudent, Team, TeamStudent, User, Iti,\
    ItiSubject, ItiSubjectScore, School, TeamConsent, IndDayStudent
from backend.config import Config
import glob


'''
    class Generator             Заменяет комментарии специального вида на код.
        gen_iti_lists()                             Изменяет списки ИТИ.
        gen_subjects_lists()                        Изменяет глобальные списки предметов.
        gen_iti_subjects_list(iti_id)               Изменяет списки предметов для одного ИТИ.
        gen_students_list(iti_id, class_n)          Изменяет таблицу учеников класса class_n.

        get_net_score(...)                          Генерирует балл в рейтинг.
        get_students(iti)                           student.id : student
        get_teams(iti_id)                           team.id : team
        get_subjects_days(iti_id)                   subject.id : subject.day
        get_results(iti_id, subject_id)             Получает все результаты по указанному предмету.
        get_student_team(iti_id)                    student.id : team.id.
        get_all_data_from_results(iti)              student_result, class_results, team_results, all_students_results, diploma

        gen_results(iti, sub_id, file)              Генерирует таблицу результатов по предмету sub.
        gen_group_results(iti_id, sub_id, file)     Генерирует таблицу групповых результатов по предмету sub.
        gen_ratings(iti)                            Генерирует рейтинговые таблицы года year.
        gen_teams(iti_id)                           Генерирует списки команд года year.
        gen_timetable(iti_id)                       Генерирует расписание предметов года year.
        gen_users_list()                            Генерирует список пользователей.
        gen_rules(subject)                          Генерирует страницу для правил группового тура.
        gen_automatic_division(iti)                 Генерирует автоматическое распределение по командам.
'''


class Generator:
    @staticmethod
    def gen_iti_lists():
        html_render('years_edit.html', 'years_edit.html', itis=Iti.select_all())

    @staticmethod
    def gen_subjects_lists():
        subjects = Subject.select_all()
        type1 = type2 = type3 = '\n'
        for subject in subjects:
            text1 = ' ' * 16 + '<p><input type="checkbox" name="status" value="{0}">{1}</p>\n'.format(subject.id, subject.name)
            if subject.type == 'i':
                type1 += text1
            elif subject.type == 'g':
                type2 += text1
            else:
                type3 += text1
        for file_name in all_templates():
            data = SplitFile(file_name)
            data.insert_after_comment(' list of individual tours (1) ', type1 + ' ' * 12)
            data.insert_after_comment(' list of group tours (1) ', type2 + ' ' * 12)
            data.insert_after_comment(' list of another tours (1) ', type3 + ' ' * 12)
            data.save_file()
        html_render('subjects_edit.html', 'subjects_edit.html', subjects=sorted(subjects, key=Subject.sort_by_type))

    @staticmethod
    def gen_iti_subjects_list(year: int):
        years_subjects_0 = ItiSubject.select_by_iti(year)
        years_subjects = set([x.subject_id for x in years_subjects_0])
        subject_n_d = {_.subject_id: _.n_d for _ in years_subjects_0}
        subjects = Subject.select_all()
        text1 = text2 = text3 = text4 = text5 = '\n'
        t4 = []
        for subject in subjects:
            checked = ''
            if subject.id in years_subjects:
                checked = ' checked'
                if subject.type == 'i':
                    t4.append(['<p><a href="individual/{0}.html">{1}</a></p>\n'.format(subject.id, subject.name),
                               subject_n_d[subject.id]])
                elif subject.type == 'g':
                    text5 += '<p><a href="group/{0}.html">{1}</a></p>\n'.format(subject.id, subject.name)
            text = '<p><input type="checkbox" name="subject" value="{0}"{1}>[ {0} ] {2}</p>\n'. \
                format(subject.id, checked, subject.name, tabs=7)
            if subject.type == 'i':
                text1 += text
            elif subject.type == 'g':
                text2 += text
            else:
                text3 += text
        t4 = sorted(t4, key=compare(lambda x: x[1], field=True))
        ld = None
        for x in t4:
            if x[1] != ld:
                text4 += '<h3>День {}</h3>\n'.format(x[1])
                ld = x[1]
            text4 += ' ' * 4 + x[0]
        for file_name in glob.glob(Config.TEMPLATES_FOLDER + '/' + str(year) + '/**/*.html', recursive=True):
            data = SplitFile(file_name)
            data.insert_after_comment(' list of year_individual tours ', text1 + ' ' * 24)
            data.insert_after_comment(' list of year_group tours ', text2 + ' ' * 24)
            data.insert_after_comment(' list of year_another tours ', text3 + ' ' * 24)
            data.save_file()

    @staticmethod
    def gen_students_list(year: int, class_n: int):
        schools = {_.id: _ for _ in School.select_all()}
        students = Student.select_by_class_n(year, class_n)
        students = sorted(students, key=compare(lambda x: Student.sort_by_class(x), lambda x: x.name_1,
                                                lambda x: x.name_2, field=True))
        length = len(students)
        m1 = length - length // 2
        html_render('students_table.html', str(year) + '/students_' + str(class_n) + '.html', class_number=class_n,
                    students1=students[:m1], students2=students[m1:], schools=schools)

    @staticmethod
    def get_net_score(maximum: int, best_score: float, score: float, net_score_formula: int) -> int:
        if net_score_formula == 0:
            if 2 * best_score >= maximum:
                return int(0.5 + score * 100 / best_score)
            return int(0.5 + score * 200 / maximum)
        elif net_score_formula == 1:
            return score
        else:
            raise ValueError('Неверная формула вычисления балла за индивидуальный тур')

    @staticmethod
    def get_students(iti: Iti):
        return {_.id: _ for _ in Student.select_by_iti(iti)}

    @staticmethod
    def get_teams(year):
        return {_.id: _ for _ in Team.select_by_iti(year)}

    @staticmethod
    def get_subjects_days(year):
        return {_.subject_id: _.n_d for _ in ItiSubject.select_by_iti(year)}

    @staticmethod
    def get_results_0(year: int, ys_id: int):
        results = Result.select_by_iti_subject(ys_id)
        for result in results:
            if not result.student_id:
                barcode = Barcode.select(year, result.student_code)
                if barcode:
                    Result.update(result ^ Result.build(ys_id, barcode.code, barcode.student_id, None, None, None,
                                                        allow_empty=True))
        return Result.select_by_iti_subject(ys_id)

    @staticmethod
    def get_results(year: int, subject: int = None):
        if not subject:
            data = {}
            for ys in ItiSubject.select_by_iti(year):
                data[ys.subject_id] = Generator.get_results_0(year, ys.id)
            return data
        ys = ItiSubject.select(year, subject)
        return ys, Generator.get_results_0(year, ys.id)

    @staticmethod
    def get_student_team(year):
        teams = Team.select_by_iti(year)
        ans = {}
        for team in teams:
            students = TeamStudent.select_by_team(team.id)
            for student in students:
                ans[student.student_id] = student.team_id
        return ans

    @staticmethod
    def get_all_data_from_results(iti: Iti):
        year = iti.id
        zeros = {day: 0 for day in range(1, iti.ind_days + 1)}
        results = Generator.get_results(year)
        student_team = Generator.get_student_team(year)
        ys = {_.id: _ for _ in ItiSubject.select_by_iti(year)}
        students = Generator.get_students(iti)
        subjects = {_.id: _ for _ in Subject.select_all()}
        subjects_students_0, subjects_students = [], {}
        for y in ys:
            subjects_students_0.extend(SubjectStudent.select_by_iti_subject(y))
        for s in subjects_students_0:
            if s.student_id not in subjects_students:
                subjects_students[s.student_id] = []
            subjects_students[s.student_id].append(ys[s.iti_subject_id].subject_id)
        temp_results, all_students_results, diploma = {}, {}, []
        class_results, team_results, student_result = {}, {_.id: zeros.copy() for _ in Team.select_by_iti(year)}, {}
        for subject_id in results:
            for r in results[subject_id]:
                day = ys[r.iti_subject_id].n_d
                student = students[r.student_id]
                if student.id not in temp_results:
                    temp_results[student.id] = {}
                if day not in temp_results[student.id]:
                    temp_results[student.id][day] = []
                temp_results[student.id][day].append(r.net_score)
                if student.id not in all_students_results:
                    all_students_results[student.id] = {}
                if ys[r.iti_subject_id].id not in all_students_results[student.id]:
                    all_students_results[student.id][ys[r.iti_subject_id].id] = r.net_score, r.position
                if r.position < 4:
                    diploma.append([student, r.position, subjects[subject_id]])

        for student in temp_results:
            student_info = students[student]
            student_sum, stud_res = 0, zeros.copy()
            for day in temp_results[student]:
                temp_results[student][day].sort(reverse=True)
                current_sum = sum(temp_results[student][day][:2])
                student_sum += current_sum
                stud_res[day] = current_sum
            student_result[student] = student_sum
            if student_info.class_name() not in class_results:
                class_results[student_info.class_name()] = [0, 0]
            class_results[student_info.class_name()][0] += student_sum
            if student_sum:
                class_results[student_info.class_name()][1] += 1
            if student in student_team and iti.sum_ind_to_team:
                sum_days = {_.n_d for _ in IndDayStudent.select_by_iti_and_student(iti.id, student)}
                for day in range(1, iti.ind_days + 1):
                    if day not in sum_days:
                        continue
                    if day not in stud_res:
                        stud_res[day] = 0
                    team_results[student_team[student]][day] += stud_res[day]
        return student_result, class_results, team_results, all_students_results, diploma

    @staticmethod
    def gen_results_row(result: Result, people: Student):
        return [result.position, people.name_1, people.name_2, people.class_name(), result.result, result.net_score]

    @staticmethod
    def gen_results_table(results: list, students: map, maximum: int, net_score_formula: int):
        if len(results) == 0:
            return []
        cnt, last_pos, last_result = 1, 0, None
        data = []
        for result in results:
            if result.result > maximum:
                raise ValueError('Сохранены некорректные результаты (есть участник с количеством '
                                 'баллов большим максимального)')
            people = students[result.student_id]
            result.net_score = Generator.get_net_score(maximum, results[0].result, result.result, net_score_formula)
            if last_result != result.result:
                last_pos, last_result = cnt, result.result
            result.position = last_pos
            row = Generator.gen_results_row(result, people)
            data.append(row)
            Result.update(result)
            cnt += 1
        return data

    @staticmethod
    def gen_results(iti: Iti, subject: int, file_name: str):
        subject_info = Subject.select(subject)
        year_subject, results = Generator.get_results(iti.id, subject)
        scores = {x.class_n: x.max_value for x in ItiSubjectScore.select_by_iti_subject(year_subject.id)}
        students = Generator.get_students(iti)
        sorted_results = {cls: [] for cls in iti.classes_list()}
        for r in results:
            if r.student_id not in students:
                raise ValueError('Неизвестный школьник code: {}, id: {}'.format(r.student_code, r.student_id))
            sorted_results[students[r.student_id].class_n].append(r)
        for cls in sorted_results:
            sorted_results[cls].sort(key=compare(lambda x: Result.sort_by_result(x), lambda x: students[x.student_id].class_l,
                                 lambda x: Student.sort_by_name(students[x.student_id]), field=True))
        data = {}
        for cls in iti.classes_list():
            data[cls] = Generator.gen_results_table(sorted_results[cls], students, scores[cls], iti.net_score_formula)
        html_render('subject_ind.html', file_name, subject_name=subject_info.name, results=data, scores=scores, iti=iti)

    @staticmethod
    def gen_group_results(year: int, subject: int, file_name: str):
        ys = ItiSubject.select(year, subject)
        subject_info = Subject.select(subject)
        is_team = (subject_info.type == 'a')
        teams = Team.select_by_iti(year)
        teams_set = set([_.id for _ in teams])
        if len(teams) == 0:
            return None
        results = {_: GroupResult.select_by_team_and_subject(_.id, subject) for _ in teams}
        results = sorted(results.items(), key=compare(GroupResult.sort_by_result, lambda x: x[1],
                                                      Team.sort_by_latter, lambda x: x[0]))
        students = [_.student_id for _ in SubjectStudent.select_by_iti_subject(ys.id)]
        teams_student, students_count = {}, 0
        for now in students:
            ts = list(set([_.team_id for _ in TeamStudent.select_by_student(now)]).intersection(teams_set))
            if len(ts) != 1:
                raise ValueError
            if ts[0] not in teams_student:
                teams_student[ts[0]] = []
            student = Student.select(now)
            student.load_class(year)
            teams_student[ts[0]].append(student)
        for x in teams_student:
            students_count = max(students_count, len(teams_student[x]))
            teams_student[x].sort(key=compare(Student.sort_by_class, Student.sort_by_name, field=True))
        i, last_pos, last_result = 1, 1, None
        rows = []
        for result in results:
            if result[1].result != last_result:
                last_pos, last_result = i, result[1].result
            rows.append([last_pos, result[0].name, result[1].result,
                         *([_.name_1 + ' ' + _.name_2 + ' ' + _.class_name() for _ in teams_student[result[0].id]]
                           if not is_team and result[0].id in teams_student else [])])
            i += 1
        html_render('subject_group.html', file_name, results=rows, subject_name=subject_info.name)

    @staticmethod
    def get_grouped_group_results(team_results):
        subj_res, cop = {}, {}
        for team_id, team_res in team_results.items():
            for subject_id, result in team_res.items():
                if subject_id > 0:
                    if subject_id not in subj_res:
                        subj_res[subject_id] = []
                    subj_res[subject_id].append(result)
        for subject_id, results in subj_res.items():
            cop[subject_id] = sorted(set(results), reverse=True)
        return cop

    @staticmethod
    def gen_super_champion(year: int, team_results, student_results, ys_index_2_subject):
        diplomas = []
        rating = {}
        for student_id in student_results:
            if student_id not in rating:
                rating[student_id] = [0, 0, 0]
            for subject, result in student_results[student_id].items():
                if result[1] < 4:
                    diplomas.append([student_id, ys_index_2_subject[subject], result[1]])
                    rating[student_id][result[1] - 1] += 1
        grouped_team_results = Generator.get_grouped_group_results(team_results)
        for team_id in team_results:
            students = [ts.student_id for ts in TeamStudent.select_by_team(team_id)]
            for subject_id, result in team_results[team_id].items():
                if subject_id > 0:
                    place = grouped_team_results[subject_id].index(result)
                    if place < 3:
                        for student_id in students:
                            ys = ItiSubject.select(year, subject_id)
                            if SubjectStudent.select_by_all(ys.id, student_id):
                                if student_id not in rating:
                                    rating[student_id] = [0, 0, 0]
                                diplomas.append([student_id, subject_id, place + 1])
                                rating[student_id][place] += 1
        return rating, diplomas

    @staticmethod
    def get_teams_results(team_results):
        results = {}
        for team in team_results:
            results[team] = {}
            for r in team_results[team]:
                results[team][-r] = team_results[team][r]
            for r in GroupResult.select_by_team(team):
                results[team][r.subject_id] = r.result
        return results

    @staticmethod
    def gen_ratings(iti: Iti):
        student_results, class_results, team_results, all_res, dip1 = Generator.get_all_data_from_results(iti)
        students_raw = {_.id: _ for _ in Student.select_by_iti(iti)}
        students = {_.id: [_.name_1, _.name_2, _.class_name()] for _id, _ in students_raw.items()}
        subjects_raw = {_.id: _ for _ in Subject.select_all()}
        subjects = {ys.id: Subject.select(ys.subject_id) for ys in ItiSubject.select_by_iti(iti.id)}
        ind_subjects = {ys: s.short_name for ys, s in subjects.items() if s.type == 'i'}
        group_subjects = {s.id: s.short_name for ys, s in subjects.items() if s.type != 'i'}
        subject_priority = {s.id: Subject.sort_by_type(s) for ys, s in subjects.items()}
        if iti.sum_ind_to_team:
            for day in range(1, 1 + iti.ind_days):
                group_subjects[-day] = 'Инд.&nbsp;{}'.format(day)
                subject_priority[-day] = -1, day
        ind_subjects = sorted(ind_subjects.items(), key=lambda x: subject_priority[subjects[x[0]].id])
        group_subjects = sorted(group_subjects.items(), key=lambda x: subject_priority[x[0]])
        all_team_results = Generator.get_teams_results(team_results)
        teams = {_.id: _.name for _ in Team.select_by_iti(iti.id)}
        team_student = {team: [ts.student_id for ts in TeamStudent.select_by_team(team)] for team in teams}
        ys_index_2_subject = {ys.id: Subject.select(ys.subject_id).id for ys in ItiSubject.select_by_iti(iti.id)}
        rating, diplomas = Generator.gen_super_champion(iti.id, all_team_results, all_res, ys_index_2_subject)
        html_render('rating_students.html', str(iti.id) + '/rating_students.html', results=all_res, students=students,
                    subjects=ind_subjects, classes=class_results.keys())
        html_render('rating_students_check.html', str(iti.id) + '/rating_students_check.html', results=all_res,
                    students=students, subjects=ind_subjects, classes=class_results.keys(),
                    check_marks={_.student_id: _.status for _ in TeamConsent.select_by_iti(iti.id)})
        html_render('rating_classes.html', str(iti.id) + '/rating_classes.html', classes=class_results.keys(),
                    results=[(_[0], *_[1]) for _ in class_results.items()], year=iti.id)
        html_render('rating_teams.html', str(iti.id) + '/rating_teams.html', team_results=all_team_results,
                    ind_subjects=ind_subjects, team_subjects=group_subjects, team_student=team_student,
                    teams=teams, students=students, student_results=all_res)
        html_render('rating.html', str(iti.id) + '/rating.html', results=rating, students=students)
        ExcelDiplomaWriter().write(Config.DATA_FOLDER + '/diploma_{}.xlsx'.format(iti.id), diplomas, subjects_raw,
                                         students_raw)

    @staticmethod
    def gen_teams(year: int):
        teams = Team.select_by_iti(year)
        text3 = '\n'
        for team in teams:
            text3 += ' ' * 16 + '<p>{0}: <input type="text" name="score_{1}" value="{{{{ t{1} }}}}"></p>\n'. \
                format(team.name, team.id)
        text3 += ' ' * 12
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/add_result.html")
        data.insert_after_comment(' teams list for saving group results ', text3)
        data.save_file()

    @staticmethod
    def gen_timetable(year: int):
        iti_subjects = [_ for _ in ItiSubject.select_by_iti(year) if _.start or _.end or _.place]
        iti_subjects.sort(key=ItiSubject.sort_by_start)
        subjects = {subject.id: subject for subject in Subject.select_all()}
        html_render('timetable.html', str(year) + '/timetable.html', iti_subjects=iti_subjects, subjects=subjects)

    @staticmethod
    def gen_users_list():
        users = User.select_all()
        subjects = {_.id: _.short_name for _ in Subject.select_all()}
        html_render('user_edit.html', 'user_edit.html', users=users, subjects=subjects)

    @staticmethod
    def gen_rules(subject: Subject):
        href = '<li><p><a href="{0}.html">{1}</a></p></li>\n'.format(subject.id, subject.name) + ' ' * 12
        data = SplitFile(Config.TEMPLATES_FOLDER + '/Info/rules.html')
        data.insert_after_comment(' tours rules ', href, append=True)
        data.save_file()
        data = SplitFile(Config.HTML_FOLDER + '/rules.html')
        data.replace_comment(' {name} ', subject.name)
        data.save_file(Config.TEMPLATES_FOLDER + '/Info/{}.html'.format(subject.id))

    @staticmethod
    def gen_automatic_division_1(codes: map, pos: int, teams: list, ts: set, cls: int):
        ln, t = len(codes), list(teams)
        t.reverse()
        while pos < ln and codes[pos][1].class_n == cls and len(t):
            if codes[pos][1].id in ts:
                TeamStudent.insert(TeamStudent.build(t[-1], codes[pos][1].id))
                t.pop()
            pos += 1
        while pos < ln and codes[pos][1].class_n == cls:
            pos += 1
        return pos, len(t) == 0

    @staticmethod
    def gen_automatic_division_list(start, peoples_in_team_count, teams_count, cls_cnt, t0):
        teams, now = [], start
        for i in range(peoples_in_team_count):
            teams.append(t0[now])
            now = (now + cls_cnt) % teams_count
        return teams

    # Изменили распределение по командам
    @staticmethod
    def gen_automatic_division(iti: Iti):
        teams_names = iti.auto_teams_list()
        teams = Team.select_by_iti(iti.id)
        for team in teams:
            TeamStudent.delete_by_team(team.id)
        Team.delete_by_iti(iti.id)
        for vertical in teams_names:
            Team.insert(Team.build(None, 'Команда {}'.format(vertical), iti.id, vertical))
        results, students = Generator.get_results(iti.id), Generator.get_students(iti)
        res_for_ord = {}
        student_result = {}
        t0 = [_.id for _ in Team.select_by_iti(iti.id)]
        ys = Generator.get_subjects_days(iti.id)
        ts = set((_.student_id for _ in TeamConsent.select_approval_by_iti(iti.id)))
        for subject_id in results:
            for r in results[subject_id]:
                day = ys[subject_id]
                if r.student_id not in student_result:
                    student_result[r.student_id] = {}
                if day not in student_result[r.student_id]:
                    student_result[r.student_id][day] = []
                student_result[r.student_id][day].append(r.net_score)
        for student_id in student_result:
            res_for_ord[student_id] = students[student_id]
            res_for_ord[student_id].result = 0
            for day in student_result[student_id]:
                student_result[student_id][day].sort(reverse=True)
                res_for_ord[student_id].result += sum(student_result[student_id][day][:iti.sum_ind_to_rating])
        if iti.automatic_division == 2:
            res_for_ord = sorted(res_for_ord.items(), key=compare(lambda x: x[1].class_name(), lambda x: -x[1].result,
                                                                  lambda x: Student.sort_by_name(x[1]), field=True))
            used_classes = {'.': 4}
            for res in res_for_ord:
                stud = res[1]
                class_name = stud.class_name()
                if class_name not in used_classes:
                    used_classes[class_name] = 0
                if stud.id in ts and used_classes[class_name] < 4:
                    TeamStudent.insert(TeamStudent.build(t0[teams_names.index(stud.class_l)], stud.id))
                    used_classes[class_name] += 1
            return min(used_classes.values()) == 4
        res_for_ord = sorted(res_for_ord.items(), key=compare(lambda x: x[1].class_n, lambda x: -x[1].result,
                                                              lambda x: x[1].class_l, lambda x: Student.sort_by_name(x[1]),
                                                              field=True))

        pos, good = 0, True
        iti_classes = iti.classes_list()
        for i in range(len(iti_classes)):
            teams = Generator.gen_automatic_division_list(i, iti.students_in_team * len(teams_names), len(teams_names),
                                                          len(iti_classes), t0)
            pos, g = Generator.gen_automatic_division_1(res_for_ord, pos, teams, ts, iti_classes[i])
            good = good and g
        return good
