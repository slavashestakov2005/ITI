import pandas as pd
from ..database import Student, StudentClass


class ExcelStudentsReader:
    def __init__(self, filename: str, iti_id: int):
        self.filename = filename
        self.iti_id = iti_id

    def read(self):
        sheets = pd.read_excel(self.filename, sheet_name=None, engine="openpyxl")
        sheet = sheets[Student.__tablename__]
        for _, row in sheet.iterrows():
            name_1, name_2, name_3, gender, other_id, class_number, class_latter, school_id = row
            student = Student.select_by_other_id(other_id)
            if not student:
                student_id = Student.insert(Student.build(None, name_1, name_2, name_3, gender, other_id), return_id=True)
            else:
                student_id = student.id
            sc = StudentClass.build(student_id, self.iti_id, class_number, class_latter, school_id)
            StudentClass.delete(sc)
            StudentClass.insert(sc)
