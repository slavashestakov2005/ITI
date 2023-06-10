from ..database import Message


def page_args(year: int):
    return {'year': abs(year), 'messages': Message.select_by_year(year)}
