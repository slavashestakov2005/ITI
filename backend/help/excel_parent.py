import xlsxwriter


class ExcelParentWriter:
    def __add_row__(self, worksheet, idx, *args, style=None):
        if not style:
            style = self.normal_style
        i = 0
        for arg in args:
            worksheet.write(idx, i, arg, style)
            i += 1

    def __write__(self, worksheet, data, row_idx=0, cols_cnt=0):
        start = row_idx
        row_idx += 1
        if not cols_cnt and len(data):
            cols_cnt = len(data[0]) - 1
        for row in data:
            self.__add_row__(worksheet, row_idx, *row)
            row_idx += 1
        worksheet.autofilter(start, 0, row_idx-1, cols_cnt)

    def __head__(self, worksheet, *cols, title=None, widths=None):
        cols_cnt = 1 if not title else 3
        worksheet.freeze_panes(cols_cnt, 0)
        if title:
            worksheet.merge_range('A1:{}1'.format(chr(ord('A') + len(cols) - 1)), title, self.caps_style)
        idx = 0
        for col in cols:
            worksheet.write(cols_cnt - 1, idx, col, self.head_style)
            if widths:
                worksheet.set_column(idx, idx, widths[idx])
            idx += 1
        if not widths:
            worksheet.set_column(0, idx-1, 15)

    def __footer__(self, worksheet, cols: list, widths: list, styles: list, row: int):
        while len(widths) < len(cols):
            widths.append(1)
        while len(styles) < len(cols):
            styles.append(self.normal_style)
        col = 0
        for i in range(len(cols)):
            if widths[i] > 1:
                worksheet.merge_range('{1}{0}:{2}{0}'.format(row + 1, chr(ord('A') + col),
                                                             chr(ord('A') + col + widths[i] - 1)), cols[i], styles[i])
            else:
                worksheet.write(row, col, cols[i], styles[i])
            col += widths[i]

    def __styles__(self, filename: str):
        self.workbook = xlsxwriter.Workbook(filename)
        self.center_style = self.workbook.add_format({'bold': True, 'border': 1, 'text_wrap': True, 'align': 'center'})
        self.center_style.set_font_size(14)
        self.head_style = self.workbook.add_format({'bold': True, 'border': 1, 'text_wrap': True})
        self.head_style.set_font_size(14)
        self.caps_style = self.workbook.add_format({'bold': True, 'align': 'center'})
        self.caps_style.set_font_size(20)
        self.normal_style = self.workbook.add_format({'border': 1})
        self.normal_style.set_font_size(14)
