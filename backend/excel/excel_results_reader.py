import pandas as pd
from backend.queries.results_raw import save_result_


def find(titles, exists, not_exists=None):
    i = 0
    for x in titles:
        t = x.lower()
        if exists in t and (not not_exists or not_exists not in t):
            return i
        i += 1
    return -1


class ExcelResultsReader:
    RES = ['code', 'result']

    def __init__(self, file: str, year: int, subject: int):
        self.file = file
        self.year = year
        self.subject = subject

    def __frames__(self):
        sheet_name = list(self.sheet.keys())
        self.sheet = list(self.sheet.values())
        result = find(sheet_name, 'результаты')
        self.result = self.sheet[result]

    def __get_result_cols__(self):
        columns = self.result.columns
        code, result = find(columns, 'шифр'), find(columns, 'балл')
        frame = pd.DataFrame(self.result, columns=[columns[code], columns[result]])
        frame.columns = self.RES
        self.result = frame[frame[self.RES[0]].notna() & frame[self.RES[1]].notna()]

    def __gen_results__(self, user):
        ans = {}
        for i, row in self.result.iterrows():
            try:
                student_code = int(row[0])
            except Exception:
                student_code = None
            if not student_code or str(row[1]) == 'nan':
                if 0 not in ans:
                    ans[0] = []
                ans[0].append(str(i + 1))
            else:
                answer = save_result_(user, self.year, self.subject, student_code, str(row[1]))
                if answer:
                    if answer not in ans:
                        ans[answer] = []
                    ans[answer].append(str(i + 1))
        txt = []
        if -1 in ans:
            txt.append('Вам запрещено редактирование')
        if 3 in ans:
            txt.append('Такого предмета нет в этом году')
        if 0 in ans:
            txt.append('Несуществующий шифр в строках: ' + ','.join(ans[0]))
        if 5 in ans:
            txt.append('Неправильный формат для результата в строках: ' + ','.join(ans[5]))
        if 1 in ans:
            txt.append('Пустые ячеёки в строках: ' + ','.join(ans[1]))
        if 2 in ans:
            txt.append('Неверные коды в строках: ' + ','.join(ans[2]))
        if 4 in ans:
            txt.append('Повтор кодов в строках: ' + ','.join(ans[4]))
        return txt

    def read(self, user):
        self.sheet = pd.read_excel(self.file, sheet_name=None, engine="openpyxl")
        self.__frames__()
        self.__get_result_cols__()
        return self.__gen_results__(user)
