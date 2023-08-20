import pandas as pd
from ..database import *
from .excel_parent import ExcelParentWriter


class ExcelFullReader:
    def __init__(self, filename: str):
        self.filename = filename

    def read(self):
        sheets = pd.read_excel(self.filename, sheet_name=None, engine="openpyxl")
        for table in Table.__subclasses__():
            sheet = sheets[table.__tablename__]
            for _, row in sheet.iterrows():
                val = table.build(*row)
                table.insert(val)


class ExcelFullWriter(ExcelParentWriter):
    def __init__(self, filename: str):
        self.filename = filename

    def __gen_sheet__(self, worksheet, head, data):
        self.__head__(worksheet, *head)
        self.__write__(worksheet, data)

    def write(self):
        self.__styles__(self.filename)
        for table in Table.__subclasses__():
            sheet = [table.fields]
            for row in table.select_all():
                line = []
                for field in table.fields:
                    line.append(getattr(row, field))
                sheet.append(line)
            self.__gen_sheet__(self.workbook.add_worksheet(table.__tablename__), table.fields, sheet)
        self.workbook.close()


class ExcelItiWriter(ExcelParentWriter):
    def __init__(self, filename: str, iti_id: int):
        self.filename = filename
        self.iti_id = iti_id

    def __gen_sheet__(self, worksheet, head, data):
        self.__head__(worksheet, *head)
        self.__write__(worksheet, data)

    def write(self):
        self.__styles__(self.filename)
        # for table in self.tables:
        #     sheet = [table.fields]
        #     for row in table.select_by():
        #         line = []
        #         for field in table.fields:
        #             line.append(getattr(row, field))
        #         sheet.append(line)
        #     self.__gen_sheet__(self.workbook.add_worksheet(table.__tablename__), table.fields, sheet)
        self.workbook.close()
