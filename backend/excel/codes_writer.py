from .__parent_writer__ import ExcelParentWriter


class ExcelCodesWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list):
        self.__head__(worksheet, 'Фамилия', 'Имя', 'Отчество', 'Школа', 'Класс', 'Код')
        self.__write__(worksheet, data, cols_cnt=5)

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Кодировка'), data)
        self.workbook.close()
