"""Тесты на классы пайплайна."""

import re
from typing import Optional

import pytest

from pipeline import Row, Table
from pipeline.object import ObjectConstraint


def make_validator(row_or_table: str, columns: dict[str, str]) -> Optional[ObjectConstraint]:
    """Создаёт ограничение на типы."""
    return ObjectConstraint.from_raw_cfg({"type": row_or_table, "columns": columns})


def test_pipeline_row_validation() -> None:
    """В Row типы полей должны проходить валидацию."""
    with pytest.raises(AttributeError, match="Expected type <class 'float'> for key num got <class 'int'>"):
        row = Row(text="text", num=5)
        row.validate(make_validator("row", {"text": "str", "num": "float"}))
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['text'] got ['num', 'text']")):
        row = Row(text="text", num=5)
        row.validate(make_validator("row", {"text": "str"}))
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['num', 'text'] got ['text']")):
        row = Row(text="text")
        row.validate(make_validator("row", {"text": "str", "num": "float"}))


def test_pipeline_row_attributes() -> None:
    """В Row обращение к полям через точку."""
    row = Row(text="text", num=5, num2=3.14)
    row.validate(None)
    row.validate(make_validator("row", {"text": "str", "num": "int", "num2": "float"}))
    assert row.text == "text"
    assert row.num == 5
    assert row.num2 == 3.14
    with pytest.raises(AttributeError, match="Field field not found in Row"):
        row.field
    assert repr(row) == "Row({'text': 'text', 'num': 5, 'num2': 3.14})"


def test_pipeline_table_validation() -> None:
    """В Table валидируются все строки."""
    table = Table()
    with pytest.raises(TypeError, match="Expected Row in Table.append, got <class 'int'>"):
        table.append(5)  # type: ignore[arg-type]
    table.append(Row(text="text"))
    table.append(Row(text="text", num=5))
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['text'] got ['num', 'text']")):
        table.validate(make_validator("row", {"text": "str"}))


def test_pipeline_table_attributes() -> None:
    """В Table есть доступ к отдельным элементам."""
    table = Table()
    table.append(Row(num=1, text="one"))
    table.append(Row(num=2, text="two"))
    table.append(Row(num=3, text="three"))
    table.validate(None)
    table.validate(make_validator("table", {"num": "int", "text": "str"}))
    assert len(table) == 3
    assert repr(table) == (
        "Table([Row({'num': 1, 'text': 'one'}), "
        "Row({'num': 2, 'text': 'two'}), "
        "Row({'num': 3, 'text': 'three'})])"
    )
    for pos, row in enumerate(table, start=1):
        assert row.num == pos
        assert row.text == ["one", "two", "three"][pos - 1]
