"""Классы для передачи по пайплайну."""

from typing import Any, Callable, Iterator, Optional

from pipeline.node import PipelineObjectTypeConstraint
from utils import sorted_dict_keys


class Row:
    """Класс для описания объекта (например строки таблицы) ."""

    def __init__(self, **kwargs: Any):
        """Сохраняем словарь как есть."""
        self._fields = kwargs

    def __getattr__(self, name: str) -> Any:
        """Получение полей через точку."""
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError(f"Field {name} not found in Row")

    def __repr__(self) -> str:
        """Вывод объекта."""
        return f"Row({self._fields})"

    def validate(self, scheme: Optional[PipelineObjectTypeConstraint]) -> None:
        """Валидация объекта."""
        if scheme is None:
            return
        our_attrs = sorted_dict_keys(self._fields)
        expected_attrs = sorted_dict_keys(scheme.columns)
        if our_attrs != expected_attrs:
            raise AttributeError(f"Expected attributes {expected_attrs} got {our_attrs}")
        for key, typ in scheme.columns.items():
            our_type = type(self._fields[key])
            if our_type != typ.py_type():
                raise AttributeError(f"Expected type {typ} for key {key} got {our_type}")


class Table:
    """Класс для описания таблицы объектов."""

    def __init__(self):
        """В начале таблица пустая."""
        self._rows = []

    def append(self, row: Row) -> None:
        """Добавляем строку в таблицу."""
        if not isinstance(row, Row):
            raise TypeError(f"Expected Row in Table.append, got {type(row)}")
        self._rows.append(row)

    def __repr__(self) -> str:
        """Вывод объекта."""
        return f"Table({self._rows})"

    def __iter__(self) -> Iterator[Row]:
        """Итерация по строкам таблицы."""
        return iter(self._rows)

    def __len__(self) -> int:
        """Число строк таблицы."""
        return len(self._rows)

    def validate(self, scheme: Optional[PipelineObjectTypeConstraint]) -> None:
        """Валидация объекта."""
        if scheme is None:
            return
        for row in self._rows:
            row.validate(scheme)


Object = Row | Table
Callback = Callable[[Object], Object]
