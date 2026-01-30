"""Классы для передачи по пайплайну."""

from dataclasses import dataclass
from typing import Any, Callable, Iterator, Optional

from utils import YAML, sorted_dict_keys


class Row:
    """Класс для описания объекта (например строки таблицы) ."""

    def __init__(self, **kwargs: Any):  # noqa: ANN401
        """Сохраняем словарь как есть."""
        self._fields = kwargs

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Получение полей через точку."""
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError(f"Field {name} not found in Row")

    def __repr__(self) -> str:
        """Вывод объекта."""
        return f"Row({self._fields})"

    def validate(self, scheme: Optional["ObjectConstraint"]) -> None:
        """Валидация объекта."""
        if scheme is None:
            return
        our_attrs = sorted_dict_keys(self._fields)
        expected_attrs = sorted_dict_keys(scheme.columns)
        if our_attrs != expected_attrs:
            raise AttributeError(f"Expected attributes {expected_attrs} got {our_attrs}")
        for key, typ in scheme.columns.items():
            our_type = type(self._fields[key])
            if our_type != typ:
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

    def validate(self, scheme: Optional["ObjectConstraint"]) -> None:
        """Валидация объекта."""
        if scheme is None:
            return
        for row in self._rows:
            row.validate(scheme)


PrimitiveType = type[str] | type[int] | type[float]
Object = Row | Table
ObjectType = type[Row] | type[Table]
Callback = Callable[[Object], Object]


def primitive_type(name: str) -> PrimitiveType:
    """Возвращает примитивный тип по строке."""
    match name:
        case "str":
            return str
        case "int":
            return int
        case "float":
            return float
        case _:
            raise ValueError(f"Unknown value for PrimitiveType: {name}")


def object_type(name: str) -> ObjectType:
    """Возвращает тип объекта пайплайна по строке."""
    match name:
        case "row":
            return Row
        case "table":
            return Table
        case _:
            raise ValueError(f"Unknown value for ObjectType: {name}")


@dataclass
class ObjectConstraint:
    """Ограничение на передаваемый объект - строка/таблица + типы полей."""

    columns: dict[str, PrimitiveType]
    type: ObjectType

    def validate(self) -> None:
        """Валидирует объект."""
        assert len(self.columns) > 0, "ObjectConstraint.columns cannot be empty"

    @classmethod
    def from_raw_cfg(cls, raw_cfg: YAML) -> Optional["ObjectConstraint"]:
        """Создаёт объект из словаря."""
        if raw_cfg is None:
            return None
        assert isinstance(raw_cfg, dict), "Raw config for ObjectConstraint need be dict"
        columns = raw_cfg.get("columns", {})
        constraint = cls(
            type=object_type(raw_cfg["type"]),
            columns={col: primitive_type(typ) for col, typ in columns.items()},
        )
        constraint.validate()
        return constraint
