from backend.config import Config
from backend.excel.diploma_writer import ExcelDiplomaWriter
from .help import html_render
from ..database import decode_result, GroupResult, IndDayStudent, Iti, ItiSubject, ItiSubjectScore, Result, School,\
    Student, Subject, SubjectStudent, Team, TeamConsent, TeamStudent, User
from ..help import FileNames

'''
    class Generator             Генерирует данные для html страниц и сами страницы.
        gen_iti_lists()                                     Изменяет списки ИТИ.
        gen_subjects_lists()                                Изменяет глобальные списки предметов.
        gen_iti_subjects_list(iti_id)                       Изменяет списки предметов для одного ИТИ.
        gen_iti_block_page(iti)                             Изменяет страницы блокировки ИТИ.
        gen_students_list(iti_id, class_n)                  Изменяет таблицу учеников класса class_n.
        gen_teams(iti_id)                                   Генерирует списки команд года year.
        gen_timetable(iti_id)                               Генерирует расписание предметов года year.
        gen_users_list()                                    Генерирует список пользователей.
        gen_iti_users_list(iti_id)                          Генерирует список ролей ИТИ для пользователей.
        gen_rules(subject)                                  Генерирует страницу для правил группового тура.

        __get_net_score(...)                                Генерирует балл в рейтинг.
        __get_students(iti)                                 student.id : student
        __get_teams(iti_id)                                 team.id : team
        __get_subjects_days(iti_id)                         subject.id : day
        __get_subject_possible_max_score(iti_subject_id)    class_n : possible_max
        __get_ind_day_student(iti_id, students)             student.id : list[day]
        __get_team_students(iti_id)                         team.id : list[student.id]
        __get_team_students_group_subject_raw(...)          team.id : list[student.id]
        __get_team_students_group_subject(...)              team.id : team, team.id : list[student.id], student.id: student
        __get_iti_subject(iti_id)                           iti_subject_id: dict[Subject]

        __get_results_individual_subject(iti, ys_id)        list[Result]
        get_results_individual_subject(iti, sub_id)         ItiSubject, list[Result]
        get_results_individual_iti(iti)                     subject.id: list[Result]
        get_results_group_subject(...)                      team.id: dict[GroupResult]
        get_results_group_iti(iti, subjects)                subject.id: {team.id: dict[GroupResult]}

        __gen_individual_results_table(...)                 Генерирует данные для таблицы по индивидуальному предмету.
        gen_individual_results(iti, sub_id, file)           Генерирует таблицу результатов по индивидуальному предмету.
        __gen_group_results_table(...)                      Генерирует данные для таблицы по групповому предмету.
        gen_group_results(iti, sub_id, file)                Генерирует таблицу результатов по групповому предмету.

        gen_diplomas_and_super_champion(...)                list[DiplomaRow], student.id: [int, int, int]
        gen_ratings(iti)                                    Генерирует рейтинговые таблицы ИТИ.
        gen_automatic_division(iti)                         Генерирует автоматическое распределение по командам.
'''


class IndividualResultNumerator:
    def __init__(self, prize_policy: int):
        self.__last_result = None
        self.__prize_policy = prize_policy
        self.__cur_place = 0
        self.__peoples_with_cur_result = 1

    def get_place(self, result: float) -> int:
        if self.__last_result != result:
            if self.__prize_policy == 0:
                self.__cur_place += self.__peoples_with_cur_result
            elif self.__prize_policy == 1:
                if self.__cur_place <= 3:
                    self.__cur_place += 1
                else:
                    self.__cur_place += self.__peoples_with_cur_result
            else:
                raise ValueError('Неверная политика призовых мест за индивидуальные дни')
            self.__last_result = result
            self.__peoples_with_cur_result = 1
        else:
            self.__peoples_with_cur_result += 1
        return self.__cur_place


class GroupResultNumerator:
    def __init__(self):
        self.__last_result = None
        self.__cur_place = 0
        self.__peoples_with_cur_result = 1

    def get_place(self, result: int) -> int:
        if self.__last_result != result:
            self.__cur_place += self.__peoples_with_cur_result
            self.__last_result = result
            self.__peoples_with_cur_result = 1
        else:
            self.__peoples_with_cur_result += 1
        return self.__cur_place


class Generator:
    @staticmethod
    def gen_iti_lists() -> None:
        html_render('all/years_edit.html', 'years_edit.html', itis=Iti.select_all())

    @staticmethod
    def gen_subjects_lists() -> None:
        subjects = Subject.select_all()
        html_render('all/subjects_edit.html', 'subjects_edit.html', subjects=sorted(subjects, key=Subject.sort_by_type))

    @staticmethod
    def gen_iti_subjects_list(iti_id: int) -> None:
        years_subjects_0 = ItiSubject.select_by_iti(iti_id)
        years_subjects = set([x.subject_id for x in years_subjects_0])
        subjects = Subject.select_all()
        html_render('iti/subjects_for_year.html', str(iti_id) + '/subjects_for_year.html', subjects=subjects,
                    iti_subject=years_subjects)

    @staticmethod
    def gen_iti_block_page(iti: Iti) -> None:
        html_render('iti/year_block.html', str(iti.id) + '/year_block.html', blocked=iti.block)

    @staticmethod
    def gen_students_list(iti_id: int, class_n: int) -> None:
        schools = School.select_id_dict()
        students = Student.select_by_class_n(iti_id, class_n)
        students = sorted(students, key=lambda x: (Student.sort_by_class(x), x.name_1, x.name_2))
        html_render('iti/students_table.html', str(iti_id) + '/students_' + str(class_n) + '.html', class_number=class_n,
                    students=students, schools=schools)

    @staticmethod
    def gen_teams(iti_id: int) -> None:
        teams = Team.select_by_iti(iti_id)
        html_render('iti/add_result.html', str(iti_id) + '/add_result.html', teams=teams)

    @staticmethod
    def gen_timetable(iti_id: int) -> None:
        iti_subjects = [_ for _ in ItiSubject.select_by_iti(iti_id) if _.start or _.end or _.place]
        iti_subjects.sort(key=ItiSubject.sort_by_start)
        subjects = {subject.id: subject for subject in Subject.select_all()}
        html_render('iti/timetable.html', str(iti_id) + '/timetable.html', iti_subjects=iti_subjects, subjects=subjects)

    @staticmethod
    def gen_users_list() -> None:
        users = User.select_all()
        subjects = {_.id: _.short_name for _ in Subject.select_all()}
        html_render('all/user_edit.html', 'user_edit.html', users=users, subjects=subjects)

    @staticmethod
    def gen_iti_users_list(iti_id: int) -> None:
        iti = Iti.select(iti_id)
        users = User.select_all()
        subjects = Subject.select_all()
        iti_subjects = {sub.id: Subject.select(sub.subject_id) for sub in ItiSubject.select_by_iti(iti_id)}
        html_render('iti/roles_edit.html', str(iti_id) + '/roles_edit.html', iti=iti, users=users,
                    iti_subjects=iti_subjects, subjects=subjects)

    @staticmethod
    def gen_rules(subject: Subject) -> None:
        html_render('all/rules.html', 'Info/{}.html'.format(subject.id), subject=subject)


    @staticmethod
    def __get_net_score(maximum: int, best_score: float, score: float, net_score_formula: int) -> int | float:
        if net_score_formula == 0:
            if 2 * best_score >= maximum:
                return int(0.5 + score * 100 / best_score)
            return int(0.5 + score * 200 / maximum)
        elif net_score_formula == 1:
            return score
        else:
            raise ValueError('Неверная формула вычисления балла за индивидуальный тур')

    @staticmethod
    def __get_students(iti: Iti) -> dict[int, Student]:
        return {_.id: _ for _ in Student.select_by_iti(iti)}

    @staticmethod
    def __get_teams(iti_id: int) -> dict[int, Team]:
        return {_.id: _ for _ in Team.select_by_iti(iti_id)}

    @staticmethod
    def __get_subjects_days(iti_id: int) -> dict[int, int]:
        return {_.subject_id: _.n_d for _ in ItiSubject.select_by_iti(iti_id)}

    @staticmethod
    def __get_subject_possible_max_score(iti_subject_id: int) -> dict[int, int]:
        return {x.class_n: x.max_value for x in ItiSubjectScore.select_by_iti_subject(iti_subject_id)}
    
    @staticmethod
    def __get_ind_day_student(iti_id: int, students: list[int]) -> dict[int, list[int]]:
        return {student_id: [day.n_d for day in IndDayStudent.select_by_iti_and_student(iti_id, student_id)] for student_id in students}

    @staticmethod
    def __get_team_students(iti_id: int) -> dict[int, list[int]]:
        teams = Team.select_by_iti(iti_id)
        return {team.id: [ts.student_id for ts in TeamStudent.select_by_team(team.id)] for team in teams}

    @staticmethod
    def __get_team_students_group_subject_raw(iti_subject_id: int, teams: set[int]) \
        -> dict[int, list[int]]:
        data = {team: [] for team in teams}
        for subject_student in SubjectStudent.select_by_iti_subject(iti_subject_id):
            student_id = subject_student.student_id
            student_teams = set([ts.team_id for ts in TeamStudent.select_by_student(student_id)])
            team = list(student_teams.intersection(teams))
            if len(team) != 1:
                raise ValueError('Школьник участвовал в групповом туре, но состоит не в одной команде.')
            data[team[0]].append(student_id)
        return data            

    @staticmethod
    def __get_team_students_group_subject(iti_id: int, iti_subject_id: int) \
        -> tuple[dict[int, Team], dict[int, list[int]], dict[int, Student]]:
        teams = Generator.__get_teams(iti_id)
        team_ids_set = set(teams.keys())
        students = {}
        team_students = {team_id: [] for team_id in teams}
        for subject_student in SubjectStudent.select_by_iti_subject(iti_subject_id):
            student_id = subject_student.student_id
            student_teams = set([ts.team_id for ts in TeamStudent.select_by_student(student_id)])
            student_teams = list(student_teams.intersection(team_ids_set))
            if len(student_teams) != 1:
                raise ValueError('Школьник участвовал в групповом туре, но состоит не в одной команде.')
            student = Student.select(student_id)
            student.load_class(iti_id)
            team_students[student_teams[0]].append(student_id)
            students[student_id] = student
        return teams, team_students, students

    @staticmethod
    def __get_iti_subject(iti_id: int) -> dict[int, dict]:
        data = {}
        for ys in ItiSubject.select_by_iti(iti_id):
            subject = Subject.select(ys.subject_id)
            data[ys.id] = {'id': subject.id, 'name': subject.name, 'short_name': subject.short_name, 'type': subject.type,
                           'priority': subject.type_priority(), 'diploma': subject.diploma, 'day': ys.n_d}
        return data


    @staticmethod
    def __get_results_individual_subject(iti: Iti, ys_id: int) -> list[Result]:
        results = Result.select_by_iti_subject(ys_id)
        for result in results:
            if not result.student_id:
                decoded_student = decode_result(iti, result.student_code)
                if decoded_student:
                    Result.update(result ^ Result.build(ys_id, result.student_code, decoded_student.student_id, None,
                                                        None, None, allow_empty=True))
        return [result for result in Result.select_by_iti_subject(ys_id) if result.student_id != 0]

    @staticmethod
    def get_results_individual_subject(iti: Iti, subject_id: int) -> tuple[ItiSubject, list[Result]]:
        ys = ItiSubject.select(iti.id, subject_id)
        return ys, Generator.__get_results_individual_subject(iti, ys.id)

    @staticmethod
    def get_results_individual_iti(iti: Iti) -> dict[int, list[Result]]:
        data = {}
        for ys in ItiSubject.select_by_iti(iti.id):
            data[ys.subject_id] = Generator.__get_results_individual_subject(iti, ys.id)
        return data

    @staticmethod
    def get_results_group_subject(iti: Iti, ys_id: int, subject_id: int, teams: dict[int, Team] | None = None) \
        -> dict[int, dict]:
        if teams is None:
            teams = Generator.__get_teams(iti.id)
        teams_students = Generator.__get_team_students_group_subject_raw(ys_id, set(teams.keys()))
        data = {}
        for team_id in teams:
            result = GroupResult.select_by_team_and_subject(team_id, subject_id)
            students = teams_students[team_id]
            ind_multiply, gr_multiply = iti.sum_gr_to_ind_policy, len(students) if iti.sum_gr_to_ind_policy else 1
            if result is not None:
                data[team_id] = {'score_ind': ind_multiply * result.result, 'score_gr': gr_multiply * result.result,
                                 'result': result.result, 'position': result.position, 'students': students}
            else:
                data[team_id] = {'score_ind': 0, 'score_gr': 0, 'result': 0, 'position': 4, 'students': []}
        return data

    @staticmethod
    def get_results_group_iti(iti: Iti, subjects: dict[int, dict]) -> dict[int, dict[int, dict]]:
        teams = Generator.__get_teams(iti.id)
        data = {}
        for ys_id, info in subjects.items():
            if info['type'] != 'i':
                res = Generator.get_results_group_subject(iti, ys_id, info['id'], teams)
                if res is not None:
                    data[info['id']] = res
        return data


    @staticmethod
    def __gen_individual_results_table(results: list[Result], students: dict[int, Student], possible_maximum: int,
                                       net_score_formula: int, ind_prize_policy: int,
                                       schools: dict[int, School]) -> list[list[int, str, str, str, str, float, float]]:
        if len(results) == 0:
            return []
        numerator = IndividualResultNumerator(ind_prize_policy)
        data = []
        max_result = results[0].result
        for result in results:
            if result.result > possible_maximum:
                raise ValueError('Сохранены некорректные результаты (есть участник с количеством '
                                 'баллов большим максимального)')
            people = students[result.student_id]
            result.net_score = Generator.__get_net_score(possible_maximum, max_result, result.result, net_score_formula)
            result.position = numerator.get_place(result.net_score)
            row = [result.position, people.name_1, people.name_2, people.school_name(schools), people.class_name(),
                result.result, result.net_score]
            data.append(row)
            Result.update(result)
        return data

    @staticmethod
    def gen_individual_results(iti: Iti, subject_id: int, file_name: str) -> None:
        subject = Subject.select(subject_id)
        year_subject, results = Generator.get_results_individual_subject(iti, subject_id)
        possible_max_scores = Generator.__get_subject_possible_max_score(year_subject.id)
        students = Generator.__get_students(iti)
        sorted_results = {cls: [] for cls in iti.classes_list()}
        for r in results:
            if r.student_id not in students:
                raise ValueError('Неизвестный школьник code: {}, id: {}'.format(r.student_code, r.student_id))
            sorted_results[students[r.student_id].class_n].append(r)
        for cls in sorted_results:
            sorted_results[cls].sort(key=lambda x: (Result.sort_by_result(x), students[x.student_id].class_latter(), 
                                                    Student.sort_by_name(students[x.student_id])))
        data = {}
        schools = School.select_id_dict()
        for cls in iti.classes_list():
            data[cls] = Generator.__gen_individual_results_table(sorted_results[cls], students, possible_max_scores[cls],
                                                    iti.net_score_formula, iti.ind_prize_policy, schools)
        html_render('iti/subject_ind.html', file_name, subject_name=subject.name, results=data,
                    scores=possible_max_scores, iti=iti)

    @staticmethod
    def __gen_group_results_table(subject_id: int, results: list[tuple[int, dict]], teams: dict[int, Team],
                                  students: dict[int, Student], team_students: dict[int, list[int]], 
                                  is_team: bool) -> list[list]:
        if len(results) == 0:
            return []
        numerator = GroupResultNumerator()
        data = []
        for team_id, result in results:
            result['position'] = numerator.get_place(result['score_gr'])
            GroupResult.update(GroupResult.build(team_id, subject_id, result['result'], result['position']))
            cur_students = []
            for student_id in team_students[team_id]:
                student = students[student_id]
                cur_students.append(student.name_1 + ' ' + student.name_2 + ' ' + student.class_name())
            row = [result['position'], teams[team_id].name, result['score_gr']]
            if not is_team:
                row.extend(cur_students)
            data.append(row)
        return data

    @staticmethod
    def gen_group_results(iti: Iti, subject_id: int, file_name: str) -> None:
        subject = Subject.select(subject_id)
        iti_subject = ItiSubject.select(iti.id, subject.id)
        is_team = (subject.type == 'a')
        teams, team_students, students = Generator.__get_team_students_group_subject(iti.id, iti_subject.id)
        if len(teams) == 0:
            return None
        results = Generator.get_results_group_subject(iti, iti_subject.id, subject.id, teams)
        if None in results.values():
            return None
        results = sorted(results.items(), key=lambda x: (-x[1]['score_gr'], Team.sort_by_latter(teams[x[0]])))
        for team_id in team_students:
            team_students[team_id].sort(key=lambda x: (Student.sort_by_class(students[x]), Student.sort_by_name(students[x])))
        teams_size = max((len(team_students[team_id]) for team_id in team_students), default=0)
        if is_team:
            teams_size = 0
        data = Generator.__gen_group_results_table(subject_id, results, teams, students, team_students, is_team)
        html_render('iti/subject_group.html', file_name, results=data, subject_name=subject.name, teams_size=teams_size)

    @staticmethod
    def gen_diplomas_and_super_champion(iti: Iti, ind_results: dict[int, dict[int, dict]],
                                        group_results: dict[int, dict[int, dict]]) \
                                        -> tuple[list[list[int, int, int]], dict[int, list[int, int, int]]]:
        diplomas = []
        super_rating = {}
        for subject_id in ind_results:
            for student_id in ind_results[subject_id]:
                result = ind_results[subject_id][student_id]
                if result['position'] < 4:
                    diplomas.append([student_id, subject_id, result['position']])
                    if student_id not in super_rating:
                        super_rating[student_id] = [0, 0, 0]
                    super_rating[student_id][result['position'] - 1] += 1
        for subject_id in group_results:
            for team_id in group_results[subject_id]:
                result = group_results[subject_id][team_id]
                for student_id in result['students']:
                    if result['position'] < 4:
                        diplomas.append([student_id, subject_id, result['position']])
                        if iti.sum_gr_to_super:
                            if student_id not in super_rating:
                                super_rating[student_id] = [0, 0, 0]
                            super_rating[student_id][result['position'] - 1] += 1
        return diplomas, super_rating

    @staticmethod
    def gen_ratings(iti: Iti):
        schools = School.select_id_dict()
        students = Generator.__get_students(iti)
        students = {_id: {'name1': student.name_1, 'name2': student.name_2, 'school': student.school_name(schools),
                          'class': student.class_name(), 'class_n': student.class_n, 'class_latter': student.class_latter(),
                          'name_all': student.name(), 'gender': student.gender} for _id, student in students.items()}
        classes = {(student['school'], student['class']) for _id, student in students.items()}
        team_consent = {_.student_id: _.status for _ in TeamConsent.select_by_iti(iti.id)}
        teams = {team_id: {'name': team.name} for team_id, team in Generator.__get_teams(iti.id).items()}
        team_students = Generator.__get_team_students(iti.id)
        students_in_teams = set()
        for team_id in team_students:
            students_in_teams = students_in_teams.union(team_students[team_id])
        ind_day_students = Generator.__get_ind_day_student(iti.id, students_in_teams)

        iti_subjects = Generator.__get_iti_subject(iti.id)
        ind_subjects = {ys_id: info for ys_id, info in iti_subjects.items() if info['type'] == 'i'}
        group_subjects = {info['id']: info for ys_id, info in iti_subjects.items() if info['type'] != 'i'}
        info_subjects = {info['id']: info for ys_id, info in iti_subjects.items()}
        if iti.sum_ind_to_team:
            for day in range(1, 1 + iti.ind_days):
                name = 'Инд.&nbsp;{}'.format(day)
                group_subjects['ind_' + str(day)] = {'id': 'ind_' + str(day), 'name': name, 'short_name': name, 
                                                     'type': 'is', 'priority': -1, 'diploma': '', 'day': day}        
        ind_subjects_sorted = sorted(ind_subjects.items(), key=lambda x: (x[1]['priority'], x[1]['id']))
        group_subjects_sorted = sorted(group_subjects.items(), key=lambda x: (x[1]['priority'], x[1]['id']))

        ind_results = {}
        for subject_id, results in Generator.get_results_individual_iti(iti).items():
            ind_results[subject_id] = {result.student_id: {'position': result.position, 'score': result.net_score}
                                       for result in results}
        group_results, group_results_for_student = {}, {}
        for subject_id, results in Generator.get_results_group_iti(iti, iti_subjects).items():
            group_results[subject_id] = {}
            for team_id, result in results.items():
                group_results[subject_id][team_id] = {'position': result['position'], 'students': result['students'],
                                                      'score': result['score_gr']}
                for student_id in result['students']:
                    if student_id not in group_results_for_student:
                        group_results_for_student[student_id] = {}
                    group_results_for_student[student_id][subject_id] = {'score': result['score_ind'], 'position': result['position']}
        diplomas, super_rating = Generator.gen_diplomas_and_super_champion(iti, ind_results, group_results)
        html_render('iti/rating_students.html', str(iti.id) + '/rating_students.html', students=students,
                    classes=classes, ind_results=ind_results, group_results=group_results_for_student, ind_subjects=ind_subjects_sorted, iti=iti, group_subjects=group_subjects)
        html_render('iti/rating_students_check.html', str(iti.id) + '/rating_students_check.html', students=students,
                    classes=classes, ind_results=ind_results, ind_subjects=ind_subjects_sorted, iti=iti,
                    check_marks=team_consent, group_results=group_results_for_student, group_subjects=group_subjects)
        html_render('iti/rating_classes.html', str(iti.id) + '/rating_classes.html', students=students, ind_subjects=ind_subjects,
                    ind_results=ind_results, group_results=group_results_for_student, group_subjects=group_subjects,
                    iti=iti, classes=classes)
        html_render('iti/rating_teams.html', str(iti.id) + '/rating_teams.html', team_results=group_results,
                    ind_subjects=ind_subjects_sorted, team_subjects=group_subjects_sorted, students=students, teams=teams,
                    ind_results=ind_results, iti=iti, team_student=team_students, ind_day_students=ind_day_students)
        html_render('iti/rating.html', str(iti.id) + '/rating.html', results=super_rating, students=students)
        ExcelDiplomaWriter().write(Config.DATA_FOLDER + '/' + FileNames.diploma_excel(iti)[0], diplomas, info_subjects, students)


    @staticmethod
    def gen_automatic_division_1(codes: list, pos: int, teams: list, ts: set, cls: int):
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
        schools = School.select_id_dict()
        for vertical in teams_names:
            if '#sch-' in vertical:
                team_name = schools[int(vertical.replace('#sch-', ''))].short_name
            else:
                team_name = 'Вертикаль {}'.format(vertical)
            Team.insert(Team.build(None, team_name, iti.id, vertical))
        results, students = Generator.get_results_individual_iti(iti), Generator.__get_students(iti)
        res_for_ord = {}
        student_result = {}
        t0 = [_.id for _ in Team.select_by_iti(iti.id)]
        ys = Generator.__get_subjects_days(iti.id)
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
                res_for_ord[student_id].result += sum(student_result[student_id][day][:iti.ind_res_per_day])
        if iti.automatic_division == 2:
            res_for_ord = sorted(res_for_ord.items(), key=lambda x: (-x[1].result, Student.sort_by_name(x[1])))
            used_classes = {}
            for res in res_for_ord:
                stud = res[1]
                class_name = stud.school_class(schools)
                team_name = stud.class_l if stud.class_l else '#sch-{}'.format(stud.school_id)
                if class_name not in used_classes:
                    used_classes[class_name] = 0
                if stud.id in ts and used_classes[class_name] < iti.students_in_team:
                    TeamStudent.insert(TeamStudent.build(t0[teams_names.index(team_name)], stud.id))
                    used_classes[class_name] += 1
            return min(used_classes.values()) == iti.students_in_team
        res_for_ord = sorted(res_for_ord.items(),
                             key=lambda x: (x[1].class_n, -x[1].result, x[1].class_latter(), Student.sort_by_name(x[1])))

        pos, good = 0, True
        iti_classes = iti.classes_list()
        for i in range(len(iti_classes)):
            teams = Generator.gen_automatic_division_list(i, iti.students_in_team * len(teams_names), len(teams_names),
                                                          len(iti_classes), t0)
            pos, g = Generator.gen_automatic_division_1(res_for_ord, pos, teams, ts, iti_classes[i])
            good = good and g
        return good
