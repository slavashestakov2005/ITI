import pandas as pd

from .__parent_writer__ import ExcelParentWriter
from ..database import *


class ExcelFullReader:
    def __init__(self, filename: str):
        self.filename = filename

    def read(self, on_iti=None):    # TODO: now on_iti not working
        sheets = pd.read_excel(self.filename, sheet_name=None, engine="openpyxl")
        if on_iti is not None:
            for iti_id in sheets[Iti.__tablename__]:
                on_iti(iti_id)
        for table in Table.__subclasses__():
            sheet = sheets[table.__tablename__]
            for _, row in sheet.iterrows():
                val = table.build(*(col.replace(r'_x000D_', '') if type(col) == str else col for col in row))
                table.insert(val)
        return [iti['id'] for _, iti in sheets[Iti.__tablename__].iterrows()]


class ExcelFullWriter(ExcelParentWriter):
    def __init__(self, filename: str):
        self.filename = filename

    def __gen_sheet__(self, worksheet, head, data):
        self.__head__(worksheet, *head)
        self.__write__(worksheet, data)

    def write(self):
        self.__styles__(self.filename)
        for table in Table.__subclasses__():
            sheet = []
            for row in table.select_all():
                line = []
                for field in table.fields:
                    line.append(getattr(row, field))
                sheet.append(line)
            self.__gen_sheet__(self.workbook.add_worksheet(table.__tablename__), table.fields, sheet)
        self.workbook.close()
