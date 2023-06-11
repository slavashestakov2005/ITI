from .help import SplitFile, all_templates, tr_format, compare, class_min, class_max, team_cnt, is_in_team, \
    individual_days_count, class_cnt, html_render
from backend.excel.excel_writer import ExcelSubjectWriter, ExcelCodesWriter, ExcelClassesWriter, ExcelDiplomaWriter
from ..database import GroupResult, Result, Student, StudentCode, Subject, SubjectStudent, Team, TeamStudent, User, Year, YearSubject
from backend.config import Config
import glob
#TODO: убрать повторы коды в генерации результатов
'''
    class Generator             Заменяет комментарии специального вида на код.
        gen_years_lists()                   Изменяет списки годов.
        gen_subjects_lists()                Изменяет глобальные списки предметов.
        gen_years_subjects_list(year)       Изменяет списки предметов для одного года.
        gen_students_list(class_n)          Изменяет таблицу учеников класса class_n.
        gen_codes(year)                     Генерирует страницу с кодами участников.

        get_net_score(...)                  Генерирует балл в рейтинг.
        get_inv_codes(year)                 student : [code1, code2] для НШ / student : [code] для ОШ.
        get_codes(year)                     Для всех дней: code : student
        get_students(year)                  student.id : student
        get_teams(year)                     team.id : team
        get_subjects_days(year)             subject.id : subject.day
        get_results(year, subject)          Получает все результаты по указанному предмету.
        get_student_team(year)              student.id : team.id.
        get_all_data_from_results(year)     student_result, class_results, team_results, all_students_results, diploma

        gen_results(year, sub, file)        Генерирует таблицу результатов по предмету sub.
        gen_group_results(year, sub, file)  Генерирует таблицу групповых результатов по предмету sub.
        gen_ratings(year)                   Генерирует рейтинговые таблицы года year.
        gen_teams(year)                     Генерирует списки команд года year.
        gen_teams_students(year)            Генерирует списки участников команд года year.
        gen_timetable(year)                 Генерирует расписание предметов года year.
        gen_files_list(year, sub, path)     Генерирует список предметных файлов.
        gen_users_list()                    Генерирует список пользователей.
        gen_rules()                         Генерирует страницу для правил группового тура.
        gen_automatic_division()            Генерирует автоматическое распределение по командам.
'''


class Generator:
    @staticmethod
    def gen_years_lists():
        years = Year.select_all()
        type1 = type2 = type3 = type4 = '\n'
        type_1 = type_2 = type_3 = type_4 = '\n'
        for year in years:
            if year.year > 0:
                type1 += '\t' * 7 + '<a class="dropdown-item" href="{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
                type2 += '\t' * 7 + '<a class="dropdown-item" href="../{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
                type3 += '\t' * 7 + '<a class="dropdown-item" href="../../{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
                type4 += '\t' * 7 + '<a class="dropdown-item" href="../../../{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
            else:
                year.year = abs(year.year)
                type_1 += '\t' * 7 + '<a class="dropdown-item" href="-{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
                type_2 += '\t' * 7 + '<a class="dropdown-item" href="../-{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
                type_3 += '\t' * 7 + '<a class="dropdown-item" href="../../-{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
                type_4 += '\t' * 7 + '<a class="dropdown-item" href="../../../-{0}/main.html">ИТИ-{0}</a>\n'.format(year.year)
        for file_name in all_templates():
            data = SplitFile(file_name)
            data.insert_after_comment(' list of years (1) ', type1 + '\t' * 7)
            data.insert_after_comment(' list of years (2) ', type2 + '\t' * 7)
            data.insert_after_comment(' list of years (3) ', type3 + '\t' * 7)
            data.insert_after_comment(' list of years (4) ', type4 + '\t' * 7)
            data.insert_after_comment(' list of years (-1) ', type_1 + '\t' * 7)
            data.insert_after_comment(' list of years (-2) ', type_2 + '\t' * 7)
            data.insert_after_comment(' list of years (-3) ', type_3 + '\t' * 7)
            data.insert_after_comment(' list of years (-4) ', type_4 + '\t' * 7)
            data.save_file()

    @staticmethod
    def gen_subjects_lists():
        subjects = Subject.select_all()
        type1 = type2 = type3 = type4 = type5 = type6 = '\n'
        for subject in subjects:
            text1 = ' ' * 16 + '<p><input type="checkbox" name="status" value="{0}">{1}</p>\n'.format(subject.id, subject.name)
            text2 = ' ' * 12 + '<p>[ {0} ] {1} ({2}) — {3} — {4}</p>\n'.format(subject.id, subject.name, subject.short_name,
                                                                               subject.diplomas_br(), subject.msg_br())
            if subject.type == 'i':
                type1 += text1
                type4 += text2
            elif subject.type == 'g':
                type2 += text1
                type5 += text2
            else:
                type3 += text1
                type6 += text2
        for file_name in all_templates():
            data = SplitFile(file_name)
            data.insert_after_comment(' list of individual tours (1) ', type1 + ' ' * 12)
            data.insert_after_comment(' list of group tours (1) ', type2 + ' ' * 12)
            data.insert_after_comment(' list of another tours (1) ', type3 + ' ' * 12)
            data.insert_after_comment(' list of individual tours (2) ', type4 + ' ' * 8)
            data.insert_after_comment(' list of group tours (2) ', type5 + ' ' * 8)
            data.insert_after_comment(' list of another tours (2) ', type6 + ' ' * 8)
            data.save_file()
        html_render('subjects_and_years.html', 'subjects_and_years.html',
                    subjects=sorted(subjects, key=Subject.sort_by_type))

    @staticmethod
    def gen_years_subjects_list(year: int):
        years_subjects_0 = YearSubject.select_by_year(year)
        years_subjects = set([x.subject for x in years_subjects_0])
        subject_n_d = {_.subject: _.n_d for _ in years_subjects_0}
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
            data.insert_after_comment(' list of year_individual tour (main page) ', text4)
            data.insert_after_comment(' list of year_group tour (main page) ', text5)
            data.save_file()

    @staticmethod
    def gen_students_list(class_n: int):
        students = Student.select_by_class_n(class_n)
        students = sorted(students, key=compare(lambda x: Student.sort_by_class(x), lambda x: x.name_1,
                                                lambda x: x.name_2, field=True))
        length = len(students)
        m1 = length - length * 2 // 3
        m2 = length - length // 3
        html_render('students_table.html', 'students_' + str(class_n) + '.html', class_number=class_n,
                    students1=students[:m1], students2=students[m1:m2], students3=students[m2:])

    @staticmethod
    def gen_codes(year: int):
        students = Generator.get_inv_codes(year)
        students = sorted(students.items(), key=compare(lambda x: Student.sort_by_class(x[0]),
                                                        lambda x: Student.sort_by_name(x[0]), field=True))
        length = len(students)
        m1 = length - length * 2 // 3
        m2 = length - length // 3
        html_render('codes_table.html', str(year) + "/codes.html", codes1=students[:m1], codes2=students[m1:m2],
                    codes3=students[m2:])
        arr = [[s[0].name_1, s[0].name_2, s[0].class_name(), *s[1]] for s in students]
        ExcelCodesWriter(year).write(Config.DATA_FOLDER + '/codes_{}.xlsx'.format(year), arr)

    @staticmethod
    def get_net_score(maximum: int, best_score: int, score: int, year: int) -> int:
        if year > 0:
            if 2 * best_score >= maximum:
                return int(0.5 + score * 100 / best_score)
            return int(0.5 + score * 200 / maximum)
        return score  # НШ хочет баллы [0;30], у максимума не 100%

    @staticmethod
    def get_inv_codes(year):
        students = Generator.get_students(year)
        all_codes = StudentCode.select_by_year(year)
        codes = {}
        for code in all_codes:
            # [code.code1, code.code2] if year < 0 else
            codes[students[code.student]] = [code.code1]
        return codes

    @staticmethod
    def get_codes(year):
        students = Generator.get_students(year)
        all_codes = StudentCode.select_by_year(year)
        codes1, codes2 = {}, {}
        for code in all_codes:
            codes1[code.code1] = students[code.student]
            codes2[code.code2] = students[code.student]
        return {1: codes1, 2: codes2, 3: codes2, 4: codes2, 5: codes2}

    @staticmethod
    def get_students(year):
        return {_.id: _ for _ in Student.select_all(year)}

    @staticmethod
    def get_teams(year):
        return {_.id: _ for _ in Team.select_by_year(year)}

    @staticmethod
    def get_subjects_days(year):
        return {_.subject: _.n_d for _ in YearSubject.select_by_year(year)}

    @staticmethod
    def get_results(year: int, subject: int = None):
        if not subject:
            return Result.select_by_year(year)
        return Result.select_by_year_and_subject(year, subject)

    @staticmethod
    def get_student_team(year):
        teams = Team.select_by_year(year)
        ans = {}
        for team in teams:
            students = TeamStudent.select_by_team(team.id)
            for student in students:
                ans[student.student] = student.team
        return ans

    @staticmethod
    def get_all_data_from_results(year: int):
        results = Generator.get_results(year)
        decode = Generator.get_codes(year)
        student_team = Generator.get_student_team(year)
        ys = Generator.get_subjects_days(year)
        students = Generator.get_students(year)
        subjects = {_.id: _ for _ in Subject.select_all()}
        subjects_students_0, subjects_students = SubjectStudent.select_by_year(year), {}
        for s in subjects_students_0:
            if s.student not in subjects_students:
                subjects_students[s.student] = []
            subjects_students[s.student].append(s.subject)
        temp_results, all_students_results, diploma = {}, {}, []
        class_results, team_results, student_result = {}, {_.id: {1: 0, 2: 0, 3: 0, 4: 0} for _ in Team.select_by_year(year)}, {}
        for day in decode:
            for code in decode[day]:
                class_results[decode[day][code].class_name()] = 0

        for r in results:
            day = ys[r.subject]
            student = decode[day][r.user]
            if student.id not in temp_results:
                temp_results[student.id] = {}
            if day not in temp_results[student.id]:
                temp_results[student.id][day] = []
            temp_results[student.id][day].append(r.net_score)
            if student.id not in all_students_results:
                all_students_results[student.id] = {}
            if r.subject not in all_students_results[student.id]:
                all_students_results[student.id][r.subject] = r.net_score, r.position
            if r.position < 4:
                diploma.append([student, r.position, subjects[r.subject]])

        for student in temp_results:
            student_info = students[student]
            student_sum, stud_res = 0, {1: 0, 2: 0, 3: 0, 4: 0}
            for day in temp_results[student]:
                temp_results[student][day].sort(reverse=True)
                current_sum = sum(temp_results[student][day][:2])
                student_sum += current_sum
                stud_res[day] = current_sum
            student_result[student] = student_sum
            class_results[student_info.class_name()] += student_sum
            if student in student_team:
                if student not in subjects_students or -1 not in subjects_students[student]:
                    stud_res[1] = 0
                if student not in subjects_students or -2 not in subjects_students[student]:
                    stud_res[2] = 0
                if student not in subjects_students or -3 not in subjects_students[student]:
                    stud_res[3] = 0
                team_results[student_team[student]][1] += stud_res[1]
                team_results[student_team[student]][2] += stud_res[2]
                team_results[student_team[student]][3] += stud_res[3]
                team_results[student_team[student]][4] += stud_res[4]
        return student_result, class_results, team_results, all_students_results, diploma

    @staticmethod
    def gen_results_main(results: list, codes: map, maximum: int, year: int):
        if len(results) == 0:
            return None
        text = '''
        <table width="100%" border="1">
            <tr>
                <td width="10%">Место</td>
                <td width="30%">Фамилия</td>
                <td width="30%">Имя</td>
                <td width="10%">Класс</td>
                <td width="10%">Балл</td>
                <td width="10%">Балл в рейтинг</td>
            </tr>\n'''
        cnt, last_pos, last_result = 1, 0, None
        for result in results:
            if result.result > maximum:
                raise ValueError("Bad results are saved")
            people = codes[result.user]
            result.net_score = Generator.get_net_score(maximum, results[0].result, result.result, year)
            # if cnt < 20: # на сайте захотели все результаты
            if last_result != result.result:
                last_pos, last_result = cnt, result.result
            result.position = last_pos
            text += tr_format(result.position, people.name_1, people.name_2, people.class_name(), result.result,
                              result.net_score, color=last_pos, tabs=3)
            Result.update(result)
            cnt += 1
        text += ' ' * 8 + '</table>'
        return text

    @staticmethod
    def gen_results_protocol(results: list, codes: map, file_name: str, args: map):
        arr = []
        txt = '''
        <table border="1" class="td-1">
            <tr>
                <td width="5%">Место</td>
                <td width="15%">Фамилия</td>
                <td width="15%">Имя</td>
                <td width="10%">Класс</td>'''
        r_split = []
        ln = len(results)
        tasks_cnt = 0
        for result in results:
            r_split.append(result.text_result.split())
            tasks_cnt = max(tasks_cnt, len(r_split[-1]))
        for i in range(tasks_cnt):
            txt += '\n' + ' ' * 16 + '<td width="5%">№ {0}</td>'.format(i + 1)
        txt += '''
                <td width="5%">Балл</td>
                <td width="5%">Балл в рейтинг</td>
            </tr>\n'''
        last_pos, last_result = 0, None
        for i in range(ln):
            people = codes[results[i].user]
            if last_result != results[i].result:
                last_pos, last_result = i + 1, results[i].result
            row = [last_pos, people.name_1, people.name_2, people.class_name()]
            for x in range(tasks_cnt):
                if x < len(r_split[i]):
                    row.append(r_split[i][x])
                else:
                    row.append('—')
            txt += tr_format(*row, results[i].result, results[i].net_score, color=last_pos, tabs=3)
            arr.append([last_pos, people.name_1, people.name_2, people.class_name(), results[i].result, results[i].net_score])
        txt += ' ' * 8 + '</table>\n' + ' ' * 4
        data = SplitFile(Config.HTML_FOLDER + "/protocol.html")
        data.insert_after_comment(' results table ', txt)
        for arg in args:
            data.replace_comment(arg, args[arg])
        data.save_file(file_name)
        return arr

    @staticmethod
    def gen_results_2(results: list, codes: map, class_n: int, maximum: int, file_name: str, args: map, year: int):
        txt, arr = Generator.gen_results_main(results, codes, maximum, year), None
        if txt:
            txt = '''    <div class="col t-3">
        <center>
            <h3>{0} класс</h3>
            <p>(Максимум: {1} баллов)</p>
        </center>{2}
    </div>\n'''.format(class_n, maximum, txt)
            args[' {class} '] = str(class_n)
            arr = Generator.gen_results_protocol(results, codes, file_name, args)
        return txt, arr

    @staticmethod
    def gen_results(year: int, subject: int, file_name: str):
        results = Generator.get_results(year, subject)
        year_subject = YearSubject.select(year, subject)
        codes = Generator.get_codes(year)[year_subject.n_d]
        sorted_results = [[] for _ in range(class_cnt(year))]
        for r in results:
            sorted_results[codes[r.user].class_n - class_min(year)].append(r)
        for lst in sorted_results:
            lst.sort(key=compare(lambda x: Result.sort_by_result(x), lambda x: codes[x.user].class_l,
                                 lambda x: Student.sort_by_name(codes[x.user]), field=True))
        pth = Config.TEMPLATES_FOLDER + '/' + str(year) + '/' + str(subject) + '/protocol'
        params = {' {year} ': str(abs(year)), ' {subject_id} ': str(subject),
                  ' {subject} ': Subject.select(subject).name}
        if year > 0:
            txt5, arr5 = Generator.gen_results_2(sorted_results[0], codes, 5, year_subject.score_5, pth + '_5.html', params, year)
            txt6, arr6 = Generator.gen_results_2(sorted_results[1], codes, 6, year_subject.score_6, pth + '_6.html', params, year)
            txt7, arr7 = Generator.gen_results_2(sorted_results[2], codes, 7, year_subject.score_7, pth + '_7.html', params, year)
            txt8, arr8 = Generator.gen_results_2(sorted_results[3], codes, 8, year_subject.score_8, pth + '_8.html', params, year)
            txt9, arr9 = Generator.gen_results_2(sorted_results[4], codes, 9, year_subject.score_9, pth + '_9.html', params, year)
        else:
            txt2, arr2 = Generator.gen_results_2(sorted_results[0], codes, 2, year_subject.score_5, pth + '_2.html', params, year)
            txt3, arr3 = Generator.gen_results_2(sorted_results[1], codes, 3, year_subject.score_6, pth + '_3.html', params, year)
            txt4, arr4 = Generator.gen_results_2(sorted_results[2], codes, 4, year_subject.score_7, pth + '_4.html', params, year)
        txt = '\n<center><h2>Результаты</h2></center>\n<div class="row col-12 justify-content-center">\n'
        protocols = '<center><h2>Протоколы</h2></center>\n'
        prot_start = '<p><a href="{0}/protocol_'.format(subject)
        if year > 0:
            protocols += prot_start + '5.html">5 класс</a></p>\n' if txt5 else ''
            protocols += prot_start + '6.html">6 класс</a></p>\n' if txt6 else ''
            protocols += prot_start + '7.html">7 класс</a></p>\n' if txt7 else ''
            protocols += prot_start + '8.html">8 класс</a></p>\n' if txt8 else ''
            protocols += prot_start + '9.html">9 класс</a></p>\n' if txt9 else ''
            txt += txt5 if txt5 else ''
            txt += txt6 if txt6 else ''
            txt += txt7 if txt7 else ''
            txt += txt8 if txt8 else ''
            txt += txt9 if txt9 else ''
        else:
            protocols += prot_start + '2.html">2 класс</a></p>\n' if txt2 else ''
            protocols += prot_start + '3.html">3 класс</a></p>\n' if txt3 else ''
            protocols += prot_start + '4.html">4 класс</a></p>\n' if txt4 else ''
            txt += txt2 if txt2 else ''
            txt += txt3 if txt3 else ''
            txt += txt4 if txt4 else ''
        txt += '</div>\n' + protocols
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + file_name)
        data.insert_after_comment(' results table ', txt)
        data.save_file()
        ExcelSubjectWriter(Subject.select(subject).name, year).write(
            Config.DATA_FOLDER + '/data_{}_{}.xlsx'.format(year, subject),
            [arr5, arr6, arr7, arr8, arr9] if year > 0 else [arr2, arr3, arr4])

    @staticmethod
    def gen_group_results(year: int, subject: int, file_name: str):
        is_team = (Subject.select(subject).type == 'a')
        teams = Team.select_by_year(year)
        teams_set = set([_.id for _ in teams])
        if len(teams) == 0:
            return None
        results = {_: GroupResult.select_by_team_and_subject(_.id, subject) for _ in teams}
        results = sorted(results.items(), key=compare(GroupResult.sort_by_result, lambda x: x[1],
                                                      Team.sort_by_later, lambda x: x[0]))
        students = [_.student for _ in SubjectStudent.select_by_subject(year, subject)]
        teams_student, students_count = {}, 0
        for now in students:
            ts = list(set([_.team for _ in TeamStudent.select_by_student(now)]).intersection(teams_set))
            if len(ts) != 1:
                raise ValueError
            if ts[0] not in teams_student:
                teams_student[ts[0]] = []
            teams_student[ts[0]].append(Student.select(now))
        for x in teams_student:
            students_count = max(students_count, len(teams_student[x]))
            teams_student[x].sort(key=compare(Student.sort_by_class, Student.sort_by_name, field=True))
        txt = '''
    <center>
        <h2>Результаты</h2>
        <div class="row col-12 justify-content-center">
            <div class="col {0}">
                <table border="1">
                    <tr>
                        <td width="5%">Место</td>
                        <td width="15%">Команда</td>
                        <td width="10%">Балл в рейтинг</td>'''.format('td-1' if not is_team else 't-3')
        txt += '\n' + ' ' * 20 + '<td width="60%" colspan="{0}"><center>Участники</center></td>'.format(students_count) \
            if not is_team else ''
        txt += '''
                    </tr>\n'''.format(students_count)
        i, last_pos, last_result = 1, 1, None
        for result in results:
            if result[1].result != last_result:
                last_pos, last_result = i, result[1].result
            txt += tr_format(last_pos, result[0].name, result[1].result,
                             *([_.name_1 + ' ' + _.name_2 + ' ' + _.class_name() for _ in teams_student[result[0].id]]
                               if not is_team and result[0].id in teams_student else []), color=last_pos, tabs=5)
            i += 1
        txt += ' ' * 16 + '</table>\n' + ' ' * 12 + '</div>\n' + ' ' * 8 + '</div>\n' + ' ' * 4 + '</center>\n'
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + file_name)
        data.insert_after_comment(' results table ', txt)
        data.save_file()

    @staticmethod
    def gen_ratings_parallel(results: list, index: int, start: int, tpl: set, tmn: set):
        radio = '''
    {{% if adm %}}<td>
        <input type="checkbox" name="t" value="{3}_0" id="{3}_0" {0}>-<input type="checkbox" name="ot" value="{3}_0" {0} hidden>
        <input type="checkbox" name="t" value="{3}_1" id="{3}_1" {1}>?<input type="checkbox" name="ot" value="{3}_1" {1} hidden>
        <input type="checkbox" name="t" value="{3}_2" id="{3}_2" {2}>+<input type="checkbox" name="ot" value="{3}_2" {2} hidden>
    </td>{{% endif %}}'''
        txt = '\n'
        last_pos, last_result = 0, None
        pl_cnt, mn_cnt = 0, 0
        for i in range(min(40, len(results) - index)):
            s = results[index + i][1]
            if s.class_n != start:
                break
            if last_result != s.result:
                last_result, last_pos = s.result, i
            mn_cnt += s.id in tmn
            pl_cnt += s.id in tpl
            rad = radio.format('checked' if s.id in tmn else '',
                               'checked' if s.id not in tmn and s.id not in tpl else '',
                               'checked' if s.id in tpl else '', s.id)
            txt += tr_format(last_pos + 1, s.class_name(), s.name_1, s.name_2, s.result, rad, color=last_pos + 1, skip_end=True)
        while index < len(results) and results[index][1].class_n == start:
            index += 1
        return txt, index, '<p>Итого: + {} штук, - {} штук.</p>'.format(pl_cnt, mn_cnt)

    @staticmethod
    def gen_ratings_best_class(results: list):
        txt = '\n'
        i, last_pos, last_result = 0, 0, None
        for x in results:
            if x[1] != last_result:
                last_pos, last_result = i, x[1]
            txt += tr_format(last_pos + 1, x[0], x[1], color=last_pos + 1)
            i += 1
            if i == 20:
                break
        return txt

    # Пока будем учитывать индивидуальные туры для НШ
    @staticmethod
    def gen_ratings_best_team(year: int, results: map):
        subjects = []
        team = None
        new_results = []
        ind_days = individual_days_count(year)
        txt = '''
    <table width="90%" border="1">
        <tr>
            <td width="5%">Место</td>
            <td width="15%">Команда</td>\n'''
        if ind_days > 0:
            txt += '''            <td width="8%">Инд. 1</td>
            <td width="8%">Инд. 2</td>
            <td width="8%">Инд. 3</td>
            <td width="8%">Инд. 4</td>
            '''
        for x in YearSubject.select_by_year(year):
            subject = Subject.select(x.subject)
            if subject.type == 'g':
                subjects.append(subject)
                txt += ' ' * 12 + '<td width="8%">{0}</td>\n'.format(subject.short_name)
            elif subject.type == 'a':
                team = subject
        if team:
            subjects.append(team)
            txt += ' ' * 12 + '<td width="8%">{}</td>\n'.format(team.short_name)
        txt += ' ' * 12 + '<td width="8%">Сумма</td>\n' + ' ' * 8 + '</tr>\n'
        subject_ids = [_ for _ in range(-1, -ind_days - 1, -1)] + [_.id for _ in subjects]
        cols_result = [[] for _ in range(len(subject_ids) + 1)]
        returned_data, teams_ids = {}, []
        for x in results:
            summ = results[x][1] + results[x][2] + results[x][3] + results[x][4] if ind_days > 0 else 0
            team_info = Team.select(x)
            row = [team_info.id, team_info.name]
            if ind_days > 0:
                cols_result[0].append(results[x][1])
                cols_result[1].append(results[x][2])
                cols_result[2].append(results[x][3])
                cols_result[3].append(results[x][4])
                row.append(results[x][1])
                row.append(results[x][2])
                row.append(results[x][3])
                row.append(results[x][4])
            res = GroupResult.select_by_team(team_info.id)
            res = {_.subject: _.result for _ in res} if res else {}
            pos = ind_days
            for subject in subject_ids[ind_days:]:
                r = res[subject] if subject in res else 0
                row.append(r)
                summ += r
                cols_result[pos].append(r)
                pos += 1
            row.append(summ)
            new_results.append([row, summ])
            cols_result[-1].append(summ)
        new_results.sort(key=compare(lambda x: -x[1], lambda x: x[0][0], field=True))
        teams_ids = [_[0][0] for _ in new_results]
        new_results = [[_[0][1:], _[1]] for _ in new_results]
        cols_result = [sorted(_, reverse=True) for _ in cols_result]
        i, last_pos, last_result = 1, 1, None
        for x in new_results:
            if x[1] != last_result:
                last_pos, last_result = i, x[1]
            colors = [4, 4]
            colors.extend([cols_result[i - 1].index(x[0][i]) + 1 for i in range(1, len(x[0]))])
            txt += tr_format(last_pos, *x[0], tabs=2, color=colors)
            i += 1

            for j in range(1 + ind_days, len(x[0]) - 1):
                team_id = teams_ids[i - 2]
                subject_id = subject_ids[j - 1]
                if team_id not in returned_data:
                    returned_data[team_id] = {}
                returned_data[team_id][subject_id] = cols_result[j - 1].index(x[0][j]) + 1
        return txt + ' ' * 4 + '</table>\n', returned_data

    # Добавили результаты по классам
    @staticmethod
    def gen_ratings_in_class(codes: map, class_n: int, filename: str, year: int, results: list, tpl: set, tmn: set, team_info: map):
        class_results, class_sums = {}, {}
        for x in codes:
            student = x[1]
            if student.class_n == class_n:
                if student.class_l not in class_results:
                    class_results[student.class_l] = []
                    class_sums[student.class_l] = 0
                class_results[student.class_l].append(student)
                class_sums[student.class_l] += student.result
        subjects_map = {}
        subjects, txt = [], ''
        template = '''
        <div class="col t-2">
            {{% if adm %}}
                <form action="save_teams" method="post">
                <input type="text" name="cl" value="2" hidden>
                <input type="text" name="part" value="{1}" hidden>
            {{% endif %}}
            <center><h3>{0}</h3></center>
            <table width="100%" border="1">
                <tr>
                    <td width="5%">Место</td>
                    <td width="30%">Фамилия</td>
                    <td width="30%">Имя</td>\n'''
        for x in YearSubject.select_by_year(year):
            subject = Subject.select(x.subject)
            subjects_map[subject.id] = subject
            if subject.type == 'i':
                subjects.append(subject)
                template += ' ' * 20 + '<td width="5%">{}</td>\n'.format(subject.short_name)
        template += '''                    <td width="5%">Сумма</td>
                    <td width="11$">Другие</td>
                    {{% if adm %}}
                    <td width="11%">Команда</td>
                    {{% endif %}}
                </tr>\n'''
        radio = '''
                    {{% if adm %}}<td>
                        <input type="checkbox" name="t" value="{3}_0" id="{3}_0" {0}>-<input type="checkbox" name="ot" value="{3}_0" {0} hidden>
                        <input type="checkbox" name="t" value="{3}_1" id="{3}_1" {1}>?<input type="checkbox" name="ot" value="{3}_1" {1} hidden>
                        <input type="checkbox" name="t" value="{3}_2" id="{3}_2" {2}>+<input type="checkbox" name="ot" value="{3}_2" {2} hidden>
                    </td>{{% endif %}}'''
        class_sums = sorted(class_sums.items(), key=lambda x: -x[1])
        classes_text = '''
        <div class="col t-4">
            <center><h3>Классы</h3></center>
            <table width="100%" border="1">
                <tr>
                    <td width="10%">Место</td>
                    <td width="40%">Класс</td>
                    <td width="40%">Сумма</td>
                    <td width="10%">Не 0</td>
                </tr>\n'''
        all_pos, all_res, gun_zero, gsum = 0, None, 0, 0
        ret_data = []
        teams = set([_.id for _ in Team.select_by_year(year)])

        for r in class_sums:
            if all_res != r[1]:
                all_pos += 1
                all_res = r[1]
            sub_sums = {_.id: 0 for _ in subjects}
            txt += template.format(str(class_n) + r[0], r[0])
            position, last_pos, last_result, un_zero = 1, 1, None, 0
            for x in class_results[r[0]]:
                # TODO: починить строку ниже
                x_team = list(set([_.team for _ in TeamStudent.select_by_student(x.id)]).intersection(teams))
                x_subjects = SubjectStudent.select_by_student(year, x.id)
                if len(x_subjects) and len(x_team) != 1:
                    raise ValueError()
                other_subjects_text = ''
                for sub in x_subjects:
                    if sub.subject < 0:
                        continue
                    gres = team_info[x_team[0]][sub.subject]
                    other_subjects_text += subjects_map[sub.subject].name + ' ({})'.format(gres)

                if x.result != last_result:
                    last_pos, last_result = position, x.result
                row = [last_pos, x.name_1, x.name_2]
                for subject in subjects:
                    if x.id in results and subject.id in results[x.id]:
                        row.append('{} ({})'.format(*results[x.id][subject.id]))
                        sub_sums[subject.id] += results[x.id][subject.id][0]
                    else:
                        row.append('—')
                rad = radio.format('checked' if x.id in tmn else '',
                                   'checked' if x.id not in tmn and x.id not in tpl else '',
                                   'checked' if x.id in tpl else '', x.id)
                txt += tr_format(*row, str(x.result) + ' ', other_subjects_text, rad, color=last_pos, tabs=4, skip_end=True)
                if x.result > 0:
                    un_zero += 1
                position += 1
            ret_data.append([all_pos, str(class_n) + r[0], r[1], un_zero])
            classes_text += tr_format(all_pos, str(class_n) + r[0], r[1], un_zero, color=all_pos, tabs=4)
            sub_sums = sub_sums.values()
            txt += ' ' * 16 + '<tr><td colspan="3"><center>Сумма</center></td>' + tr_format(*sub_sums, r[1],
                                                                                            tr=False) + '</tr>\n'
            error_idx = str(ord(r[0])) if r[0] else '0'
            txt += '''            </table>
            {% if adm %}
                <center>
                    {% if error''' + error_idx + ''' %} <p><font color="red">[ {{ error''' + error_idx + ''' }} ]</font></p>{% endif %}
                    <p><input type="submit" value="Сохранить"></p>
                </center></form>
            {% endif %}
        </div>'''
            gun_zero += un_zero
            gsum += r[1]
        txt += '\n    '
        classes_text += ' ' * 16 + '<tr><td colspan="2"><center>Итого</center></td>' + tr_format(gsum, gun_zero, tr=False) + '</tr>\n'
        classes_text += ' ' * 12 + '</table>\n' + ' ' * 8 + '</div>\n' + ' ' * 4
        data = SplitFile(filename)
        data.insert_after_comment(' results ', txt)
        data.insert_after_comment(' classes ', classes_text)
        data.save_file()
        return ret_data

    @staticmethod
    def gen_ratings_5_i(year: int, subject: int, decode: map, sp: map):
        r = Result.select_by_year_and_subject(year, subject)
        r.sort(key=compare(lambda x: decode[x.user].class_n, lambda x: Result.sort_by_result(x), field=True))
        last_result, last_pos, last_class, i = None, 0, 0, 1
        for x in r:
            user = decode[x.user]
            if last_class != user.class_n:
                last_result, last_pos, last_class, i = None, 0, user.class_n, 1
            if last_result != x.result:
                last_result, last_pos = x.result, i
            if last_pos < 4:
                if user.id not in sp:
                    sp[user.id] = [0, 0, 0]
                sp[user.id][last_pos - 1] += 1
            i += 1
        return sp

    @staticmethod
    def gen_ratings_5_g(year: int, subject: int, teams: map, sp: map):
        ts, diploma = set(teams.keys()), []
        peoples = set([_.student for _ in SubjectStudent.select_by_subject(year, subject)])
        r = [_ for _ in GroupResult.select_by_subject(subject) if _.team in ts]
        r.sort(key=GroupResult.sort_by_result)
        last_result, last_pos, i = None, 0, 1
        for x in r:
            if last_result != x.result:
                last_result, last_pos = x.result, i
            if last_pos > 3:
                break
            for user in peoples.intersection(set([_.student for _ in TeamStudent.select_by_team(x.team)])):
                if user not in sp:
                    sp[user] = [0, 0, 0]
                sp[user][last_pos - 1] += 1
                diploma.append([user, last_pos])
            i += 1
        return sp, diploma

    @staticmethod
    def gen_ratings_5_a(year: int, subject: int, teams: map, sp: map):
        ts, diploma = set(teams.keys()), []
        r = [_ for _ in GroupResult.select_by_subject(subject) if _.team in ts]
        peoples = set([_.student for _ in SubjectStudent.select_by_subject(year, subject)])
        r.sort(key=GroupResult.sort_by_result)
        last_result, last_pos, i = None, 0, 1
        for x in r:
            if last_result != x.result:
                last_result, last_pos = x.result, i
            if last_pos > 3:
                break
            for user in TeamStudent.select_by_team(x.team):
                if user.student in peoples:
                    if user.student not in sp:
                        sp[user.student] = [0, 0, 0]
                    sp[user.student][last_pos - 1] += 1
                    diploma.append([user.student, last_pos])
            i += 1
        return sp, diploma

    @staticmethod
    def gen_ratings_best_student(year: int, codes: map):
        decode = Generator.get_codes(year)
        teams = Generator.get_teams(year)
        codes = {_[0]: _[1] for _ in codes}
        codes = {_.id: _ for _ in codes.values()}
        subjects = YearSubject.select_by_year(year)
        res, group_diploma, team_diploma = {}, [], []
        for subject in subjects:
            day = subject.n_d
            subject = Subject.select(subject.subject)
            if subject.type == 'i':
                res = Generator.gen_ratings_5_i(year, subject.id, decode[day], res)
            elif subject.type == 'g':
                res, diploma = Generator.gen_ratings_5_g(year, subject.id, teams, res)
                for d in diploma:
                    group_diploma.append([codes[d[0]], d[1], subject])
            else:
                res, diploma = Generator.gen_ratings_5_a(year, subject.id, teams, res)
                for d in diploma:
                    team_diploma.append([codes[d[0]], d[1], subject])
        res = sorted(res.items(), key=compare(lambda x: -x[1][0], lambda x: -x[1][1], lambda x: -x[1][2],
                                              lambda x: Student.sort_by_class(codes[x[0]]),
                                              lambda x: codes[x[0]].name_1, lambda x: codes[x[0]].name_2, field=True))
        txt, last_result, last_pos, i = '\n', None, 0, 1
        for r in res:
            user = codes[r[0]]
            if last_result != r[1]:
                last_result, last_pos = r[1], i
            txt += tr_format(last_pos, user.class_name(), user.name_1, user.name_2, *r[1], color=last_pos)
            if i == 20:
                break
            i += 1
        return txt, group_diploma, team_diploma

    @staticmethod
    def gen_ratings(year: int):
        student_results, class_results, team_results, all_res, dip1 = Generator.get_all_data_from_results(year)
        codes = Generator.get_students(year)
        for _ in student_results:
            codes[_].result = student_results[_]
        codes = sorted(codes.items(), key=compare(lambda x: -x[1].class_n, lambda x: -x[1].result,
                                                  lambda x: x[1].class_l, lambda x: Student.sort_by_name(x[1]),
                                                  field=True))
        class_results = sorted(class_results.items(), key=compare(lambda x: -x[1], lambda x: x[0], field=True))
        index = 0
        tpl, tmn = is_in_team(year)
        tpl = set(_.student for _ in TeamStudent.select_by_team(tpl))
        tmn = set(_.student for _ in TeamStudent.select_by_team(tmn))
        if year > 0:
            best_9, index, best_sum_9 = Generator.gen_ratings_parallel(codes, index, 9, tpl, tmn)
            best_8, index, best_sum_8 = Generator.gen_ratings_parallel(codes, index, 8, tpl, tmn)
            best_7, index, best_sum_7 = Generator.gen_ratings_parallel(codes, index, 7, tpl, tmn)
            best_6, index, best_sum_6 = Generator.gen_ratings_parallel(codes, index, 6, tpl, tmn)
            best_5, index, best_sum_5 = Generator.gen_ratings_parallel(codes, index, 5, tpl, tmn)
        else:
            best_4, index, best_sum_4 = Generator.gen_ratings_parallel(codes, index, 4, tpl, tmn)
            best_3, index, best_sum_3 = Generator.gen_ratings_parallel(codes, index, 3, tpl, tmn)
            best_2, index, best_sum_2 = Generator.gen_ratings_parallel(codes, index, 2, tpl, tmn)
        best_class = Generator.gen_ratings_best_class(class_results)
        best_team, tems_info = Generator.gen_ratings_best_team(year, team_results)
        best_student, dip2, dip3 = Generator.gen_ratings_best_student(year, codes)
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + '/rating.html')
        data.insert_after_comment(' rating_teams ', best_team)
        data.insert_after_comment(' rating_class ', best_class)
        data.insert_after_comment(' rating_student ', best_student)
        if year > 0:
            data.insert_after_comment(' rating_parallel_5 ', best_5)
            data.insert_after_comment(' rating_parallel_6 ', best_6)
            data.insert_after_comment(' rating_parallel_7 ', best_7)
            data.insert_after_comment(' rating_parallel_8 ', best_8)
            data.insert_after_comment(' rating_parallel_9 ', best_9)
            data.insert_after_comment(' rating_parallel_sum_5 ', best_sum_5)
            data.insert_after_comment(' rating_parallel_sum_6 ', best_sum_6)
            data.insert_after_comment(' rating_parallel_sum_7 ', best_sum_7)
            data.insert_after_comment(' rating_parallel_sum_8 ', best_sum_8)
            data.insert_after_comment(' rating_parallel_sum_9 ', best_sum_9)
        else:
            data.insert_after_comment(' rating_parallel_2 ', best_2)
            data.insert_after_comment(' rating_parallel_3 ', best_3)
            data.insert_after_comment(' rating_parallel_4 ', best_4)
            data.insert_after_comment(' rating_parallel_sum_2 ', best_sum_2)
            data.insert_after_comment(' rating_parallel_sum_3 ', best_sum_3)
            data.insert_after_comment(' rating_parallel_sum_4 ', best_sum_4)
        data.save_file()
        arr, arr_a = [], []
        for i in range(class_min(year), class_max(year)):
            filename = Config.TEMPLATES_FOLDER + "/" + str(year) + '/rating_' + str(i) + '.html'
            now = Generator.gen_ratings_in_class(codes, i, filename, year, all_res, tpl, tmn, tems_info)
            arr.append([[y for y in x] for x in now])
            arr_a.extend(now)
        arr_a.sort(key=lambda x: -x[2])
        arr_a[0][0] = 1
        for i in range(1, len(arr_a)):
            if arr_a[i][2] == arr_a[i - 1][2]:
                arr_a[i][0] = arr_a[i - 1][0]
            else:
                arr_a[i][0] = i + 1
        ExcelClassesWriter(year).write(Config.DATA_FOLDER + '/classes_{}.xlsx'.format(year), arr, arr_a)
        ExcelDiplomaWriter(year).write(Config.DATA_FOLDER + '/diploma_{}.xlsx'.format(year), dip1, dip2, dip3)

    @staticmethod
    def gen_teams(year: int):
        teams = Team.select_by_year(year)
        text1, text2, text3 = '\n', '\n', '\n'
        for team in teams:
            row = [team.later, team.name]
            text1 += tr_format(team.id, *row, tabs=4)
            text2 += tr_format(*row, tabs=3)
            text3 += ' ' * 16 + '<p>{0}: <input type="text" name="score_{1}" value="{{{{ t{1} }}}}"></p>\n'. \
                format(team.name, team.id)
        text1 += ' ' * 12
        text2 += ' ' * 8
        text3 += ' ' * 12
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/teams_for_year.html")
        data.insert_after_comment(' list of teams (full) ', text1)
        data.save_file()
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/teams.html")
        data.insert_after_comment(' list of teams ', text2)
        data.save_file()
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/add_result.html")
        data.insert_after_comment(' teams list for saving group results ', text3)
        data.save_file()

    @staticmethod
    def gen_teams_students(year: int):
        codes = Generator.get_students(year)
        decode = Generator.get_codes(year)
        result = Generator.get_results(year)
        subjects0, subjects, ys = YearSubject.select_by_year(year), [], {}
        for x in subjects0:
            subject = Subject.select(x.subject)
            if subject.type == 'i':
                subjects.append(subject)
                ys[subject.id] = x.n_d
        student_result = {}
        for r in result:
            day = ys[r.subject]
            student = decode[day][r.user]
            if student.id not in student_result:
                student_result[student.id] = {}
            if day not in student_result[student.id]:
                student_result[student.id][day] = {}
            student_result[student.id][day][r.subject] = r.net_score
        teams = Team.select_by_year(year)
        teams.sort(key=Team.sort_by_later)
        template = '''
        <div class="col t-2"><center><h2>{0}</h2></center>
            <table width="100%" border="1">
                <tr>
                    <td width="10%">Класс</td>
                    <td width="45%">Фамилия</td>
                    <td width="45%">Имя</td>\n'''
        for subject in subjects:
            template += ' ' * 20 + '<td width="5%">{0}</td>\n'.format(subject.short_name)
        template += ' ' * 20 + '<td width="5%">Сумма</td>\n' + ' ' * 16 + '</tr>\n'
        txt = ''
        for team in teams:
            students = TeamStudent.select_by_team(team.id)
            students = [codes[_.student] for _ in students]
            students.sort(key=compare(lambda x: x.class_name(), lambda x: x.name_1, lambda x: x.name_2, field=True))
            sub_sums = {_.id: 0 for _ in subjects}
            sum_of_sums = 0
            if len(students) == 0:
                continue
            txt += template.format(team.name)
            for student in students:
                row = [student.class_name(), student.name_1, student.name_2]
                for subject in subjects:
                    if student.id in student_result and ys[subject.id] in student_result[student.id] \
                            and subject.id in student_result[student.id][ys[subject.id]]:
                        row.append(student_result[student.id][ys[subject.id]][subject.id])
                        sub_sums[subject.id] += row[-1]
                    else:
                        row.append('—')
                summ = 0
                if student.id in student_result:
                    for day in student_result[student.id]:
                        summ += sum(sorted(student_result[student.id][day].values(), reverse=True)[:2])
                txt += tr_format(*row, summ, tabs=4)
                sum_of_sums += summ
            sub_sums = sub_sums.values()
            txt += ' ' * 16 + '<tr><td colspan="3"><center>Сумма</center></td>' + tr_format(*sub_sums, sum_of_sums,
                                                                                            tr=False) + '</tr>\n'
            txt += ' ' * 12 + '</table>\n' + ' ' * 8 + '</div>\n'
        txt += ' ' * 4
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/teams.html")
        data.insert_after_comment(' list of students_in_team ', txt)
        data.save_file()

    @staticmethod
    def gen_timetable(year: int):
        subjects = [_ for _ in YearSubject.select_by_year(year) if _.start or _.end or _.place]
        subjects.sort(key=YearSubject.sort_by_start)
        txt = '\n'
        for subject in subjects:
            txt += tr_format(subject.n_d, subject.date_str(), Subject.select(subject.subject).name,
                             subject.classes, subject.start_str(), subject.end_str(), subject.place, tabs=3)
        data = SplitFile(Config.TEMPLATES_FOLDER + "/" + str(year) + "/timetable.html")
        data.insert_after_comment(' timetable ', txt + ' ' * 8)
        data.save_file()

    @staticmethod
    def gen_files_list(year: int, subject: int, path: str):
        data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(year) + '/' + path)
        # files = SubjectsFilesTable.select_by_subject(year, subject)
        files = []
        txt = '\n    <center><h2>Файлы</h2></center>\n' if len(files) != 0 else '\n'
        # for file in files:
        #     txt += '    <p><a href="/' + file.file + '">' + file.just_filename() + '</a></p>\n'
        data.insert_after_comment(' files ', txt)
        data.save_file()

    @staticmethod
    def gen_users_list():
        txt, users = '\n', User.select_all()
        subjects = {_.id: _.short_name for _ in Subject.select_all()}
        for user in users:
            if user.can_do(-2):
                continue
            txt += tr_format(user.id, user.login, user.subjects_str(subjects), tabs=4)
        data = SplitFile(Config.TEMPLATES_FOLDER + '/user_edit.html')
        data.insert_after_comment(' list of users ', txt + ' ' * 12)
        data.save_file()

    @staticmethod
    def gen_rules(subject):
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
    def gen_automatic_division(year: int):
        teams_l = 'АБВГДЕЖЗИМ'
        teams = Team.select_by_year(year)
        for team in teams:
            TeamStudent.delete_by_team(team.id)
        Team.delete_by_year(year)
        for i in range(1, team_cnt(year) + 1):
            if year > 0:
                Team.insert(Team.build(None, 'Команда {}'.format(i), year, '{}'.format(i)))
            else:
                Team.insert(Team.build(None, 'Команда {}'.format(teams_l[i - 1]), year, teams_l[i - 1]))
        results = Generator.get_results(year)
        decode, res_for_ord = Generator.get_codes(year), {}
        for day in decode:
            for code in decode[day]:
                res_for_ord[decode[day][code].id] = decode[day][code]
                res_for_ord[decode[day][code].id].result = 0
        student_result = {}
        t0 = [_.id for _ in Team.select_by_year(year)]
        ys = Generator.get_subjects_days(year)
        ts = set((_.student for _ in TeamStudent.select_by_team(is_in_team(year)[0])))
        for r in results:
            day = ys[r.subject]
            if r.user not in student_result:
                student_result[r.user] = {}
            if day not in student_result[r.user]:
                student_result[r.user][day] = []
            student_result[r.user][day].append(r.net_score)
        for code in student_result:
            for day in student_result[code]:
                student_result[code][day].sort(reverse=True)
                res_for_ord[decode[day][code].id].result += sum(student_result[code][day][:2])
        if year < 0:
            res_for_ord = sorted(res_for_ord.items(), key=compare(lambda x: x[1].class_name(), lambda x: -x[1].result,
                                                                  lambda x: Student.sort_by_name(x[1]), field=True))
            used_classes = {'.': 4}
            for res in res_for_ord:
                stud = res[1]
                class_name = stud.class_name()
                if class_name not in used_classes:
                    used_classes[class_name] = 0
                if stud.id in ts and used_classes[class_name] < 4:
                    TeamStudent.insert(TeamStudent.build(t0[teams_l.find(stud.class_l)], stud.id))
                    used_classes[class_name] += 1
            return min(used_classes.values()) == 4
        res_for_ord = sorted(res_for_ord.items(), key=compare(lambda x: x[1].class_n, lambda x: -x[1].result,
                                                              lambda x: x[1].class_l, lambda x: Student.sort_by_name(x[1]),
                                                              field=True))

        pos, good = 0, True
        for i in range(class_cnt(year)):
            teams = Generator.gen_automatic_division_list(i, 4 * team_cnt(year), team_cnt(year), class_cnt(year), t0)
            pos, g = Generator.gen_automatic_division_1(res_for_ord, pos, teams, ts, class_min(year) + i)
            good = good and g
        return good
