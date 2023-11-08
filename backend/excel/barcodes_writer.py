from .__parent_writer__ import ExcelParentWriter


class ExcelBarcodesWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list):
        self.__head__(worksheet, 'Штрих-код')
        self.__write__(worksheet, data, cols_cnt=0)

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Штрих-коды'), data)
        self.workbook.close()
