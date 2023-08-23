import pandas as pd
from ..database import Result
from backend.queries.results_raw import save_result_


class ExcelResultsReader:
    def __init__(self, filename: str, iti_id: int, subject_id: int):
        self.filename = filename
        self.iti_id = iti_id
        self.subject_id = subject_id

    def __gen_results__(self, user):
        ans = {}
        for i, row in self.result.iterrows():
            try:
                student_code = int(row[0])
                result = float(row[1])
            except Exception:
                student_code = None
                result = None
            if student_code is None or result is None:
                if 0 not in ans:
                    ans[0] = []
                ans[0].append(str(i + 1))
            else:
                answer = save_result_(user, self.iti_id, self.subject_id, student_code, str(result))
                if answer:
                    if answer not in ans:
                        ans[answer] = []
                    ans[answer].append(str(i + 1))
        decode = {-1: 'Вам запрещено редактирование',
                  0: 'Несуществующий шифр в строках: ' + (','.join(ans[0]) if 0 in ans else ''),
                  1: 'Пустые ячеёки в строках: ' + (','.join(ans[1]) if 1 in ans else ''),
                  3: ('Такого предмета нет в этом году',),
                  4: 'Повтор кодов в строках: ' + (','.join(ans[4]) if 4 in ans else ''),
                  5: 'Неправильный формат для результата в строках: ' + (','.join(ans[5]) if 5 in ans else '')}
        txt = [decode[key] for key in decode if key in ans]
        return txt

    def read(self, user):
        sheets = pd.read_excel(self.filename, sheet_name=None, engine="openpyxl")
        self.result = sheets[Result.__tablename__]
        return self.__gen_results__(user)
