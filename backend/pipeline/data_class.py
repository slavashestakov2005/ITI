"""Классы для передачи по пайплайну."""

from typing import Any, Callable, Iterator

from utils import sorted_dict_keys


class PipelineRow:
    """Класс для описания объекта (например строки таблицы) ."""

    def __init__(self, **kwargs: Any):
        """Сохраняем словарь как есть."""
        self._fields = kwargs

    def __getattr__(self, name: str) -> Any:
        """Получение полей через точку."""
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError(f"Field {name} not found in PipelineRow")

    def __repr__(self) -> str:
        """Вывод объекта."""
        return f"PipelineRow({self._fields})"

    def validate(self, expected: dict[str, type]) -> None:
        """Валидация объекта."""
        our_attrs = sorted_dict_keys(self._fields)
        expected_attrs = sorted_dict_keys(expected)
        if our_attrs != expected_attrs:
            raise AttributeError(f"Expected attributes {expected_attrs} got {our_attrs}")
        for key, typ in expected.items():
            our_type = type(self._fields[key])
            if our_type != typ:
                raise AttributeError(f"Expected type {typ} for key {key} got {our_type}")


class PipelineTable:
    """Класс для описания таблицы объектов."""

    def __init__(self):
        """В начале таблица пустая."""
        self._rows = []

    def append(self, row: PipelineRow) -> None:
        """Добавляем строку в таблицу."""
        if not isinstance(row, PipelineRow):
            raise TypeError(f"Expected PipelineRow in PipelineTable.append, got {type(row)}")
        self._rows.append(row)

    def __repr__(self) -> str:
        """Вывод объекта."""
        return f"PipelineTable({self._rows})"

    def __iter__(self) -> Iterator[PipelineRow]:
        """Итерация по строкам таблицы."""
        return iter(self._rows)

    def __len__(self) -> int:
        """Число строк таблицы."""
        return len(self._rows)

    def validate(self, expected: dict[str, type]) -> None:
        """Валидация объекта."""
        for row in self._rows:
            row.validate(expected)


PipelineBaseObject = PipelineRow | PipelineTable
PipelineCallback = Callable[[PipelineBaseObject], PipelineBaseObject]
