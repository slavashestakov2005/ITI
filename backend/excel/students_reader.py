import pandas as pd
from ..database import Student, StudentClass


class ExcelStudentsReader:
    def __init__(self, filename: str, iti_id: int):
        self.filename = filename
        self.iti_id = iti_id

    def read(self):
        sheets = pd.read_excel(self.filename, sheet_name=None, engine="openpyxl")
        sheet = sheets[Student.__tablename__]
        answer = []
        for _, row in sheet.iterrows():
            name_1, name_2, name_3, gender, other_id, class_number, class_latter, school_id = row
            student = Student.select_by_other_id(other_id)
            new_student = Student.build(None, name_1, name_2, name_3, gender, other_id)
            if not student:
                answer.append('Новый школьник: "{}", "{}", "{}", "{}", "{}", "{}", "{}"')
                student_id = Student.insert(new_student, return_id=True)
            else:
                student_id = student.id
                new_v = [new_student.name_1, new_student.name_2, new_student.name_3, new_student.gender]
                old_v = [student.name_1, student.name_2, student.name_3, student.gender]
                if new_v != old_v:
                    answer.append('Хотели поменять данные школьника, сохранены старые данные. Было: "{}", "{}", "{}", "{}". Хотели сделать: "{}", "{}", "{}", "{}".'
                                  .format(*old_v, *new_v))
            sc = StudentClass.build(student_id, self.iti_id, class_number, class_latter, school_id)
            StudentClass.delete(sc)
            StudentClass.insert(sc)
        return '<br>\n'.join(answer)
