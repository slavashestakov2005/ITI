# from functools import wraps
# from flask import request
# from ..database import Table, Row
# from ..help import empty_checker
#
#
# def __form_args(fields, types):
#     n, data, not_empty = len(fields), [], []
#     try:
#         for i in range(n):
#             field, typ = fields[i], types[i]
#             if typ == Row.NONE:
#                 data.append(None)
#             elif typ == Row.STR:
#                 data.append(request.form[field])
#             elif typ == Row.NE_STR:
#                 data.append(request.form[field])
#                 not_empty.append(data[-1])
#             elif typ == Row.INT:
#                 data.append(int(request.form[field]) if request.form[field] else None)
#             elif typ == Row.NE_INT:
#                 data.append(int(request.form[field]))
#             elif typ == Row.FILE:
#                 data.append('')
#             elif typ == Row.DATETIME:
#                 d, t = request.form[field + '_date'], request.form[field + '_time']
#                 date = [int(_) for _ in d.split('-')] if d else None
#                 time = [int(_) for _ in t.split(':')] if t else None
#                 data.append((date, time))
#             elif typ == Row.NE_DATETIME:
#                 date = [int(_) for _ in request.form[field + '_date'].split('-')]
#                 time = [int(_) for _ in request.form[field + '_time'].split(':')]
#                 data.append((date, time))
#         empty_checker(*not_empty)
#     except Exception:
#         data = []
#     return data
#
#
# def form_add(table: Table, form_fields='add_form'):
#     def my_decorator(function_to_decorate):
#
#         @wraps(function_to_decorate)
#         def wrapped(*args, **kwargs):
#             cls = table.row
#             row = cls(__form_args(cls.fields, getattr(cls, form_fields)))
#             return function_to_decorate(*args, row=row, **kwargs)
#
#         return wrapped
#
#     return my_decorator
#
#
# def form_edit(table: Table, form_fields='edit_form'):
#     def my_decorator(function_to_decorate):
#
#         @wraps(function_to_decorate)
#         def wrapped(*args, **kwargs):
#             cls = table.row
#             new_row = cls(__form_args(cls.fields, getattr(cls, form_fields)))
#             if new_row.__is_none__:
#                 return function_to_decorate(*args, new_row=new_row, old_row=cls([]), **kwargs)
#             old_row = table.select(getattr(new_row, table.id_field))
#             return function_to_decorate(*args, new_row=new_row, old_row=old_row, **kwargs)
#
#         return wrapped
#
#     return my_decorator
#
#
# def form_delete(table: Table):
#     def my_decorator(function_to_decorate):
#
#         @wraps(function_to_decorate)
#         def wrapped(*args, **kwargs):
#             try:
#                 row = table.select(int(request.form[table.id_field]))
#             except Exception:
#                 row = table.row([])
#             return function_to_decorate(*args, row=row, **kwargs)
#
#         return wrapped
#
#     return my_decorator
#
#
# def copy_fields(new_row, old_row):
#     fields = old_row.__class__.fields
#     for field in fields:
#         new_value, old_value = getattr(new_row, field), getattr(old_row, field)
#         if not new_value:
#             new_row.__setattr__(field, old_value)
#     return new_row
