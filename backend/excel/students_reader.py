import pandas as pd

from ..database import Student, StudentClass


class ExcelStudentsReader:
    def __init__(self, filename: str, iti_id: int):
        self.filename = filename
        self.iti_id = iti_id
    
    def compare_students(self, old_student: dict, new_student: dict) -> str:
        ans = 'Обновили информацию о школьнике {}, обновления: '.format(old_student['id'])
        for key in old_student.keys():
            if old_student[key] != new_student[key]:
                ans += "<font style='color: blue'>{}:</font> '{}' &rarr; '{}'".format(key, old_student[key], new_student[key])
        return ans

    def read(self):
        sheets = pd.read_excel(self.filename, sheet_name=None, engine="openpyxl")
        sheet = sheets[Student.__tablename__]
        answer = []
        for _, row in sheet.iterrows():
            name_1, name_2, name_3, gender, other_id, class_number, class_latter, school_id = row
            students = Student.select_by_other_id(other_id)
            new_student = Student.build(None, name_1, name_2, name_3, gender, other_id)
            if len(students) == 0:
                txt = "<font style='color: green'>Новый школьник id={}:</font> {}".format('REP_ID', new_student.json())
                student_id = Student.insert(new_student, return_id=True)
                answer.append(txt.replace('REP_ID', str(student_id)))
            elif len(students) > 1:
                answer.append("<font style='color: red'>Нашлось много</font> школьников для нового: {}, школьник пропущен".format(new_student.json()))
                continue
            else:
                old_student = students[0]
                new_student = old_student ^ new_student
                if new_student.json() != old_student.json():
                    Student.update(new_student)
                    answer.append(self.compare_students(old_student.json(), new_student.json()))
                student_id = new_student.id
            sc = StudentClass.build(student_id, self.iti_id, class_number, class_latter, school_id)
            StudentClass.delete(sc)
            StudentClass.insert(sc)
        return '<br>\n'.join(answer)
