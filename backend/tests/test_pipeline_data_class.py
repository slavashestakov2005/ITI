"""Тесты на классы пайплайна."""

import re

import pytest

from pipeline import PipelineRow, PipelineTable


def test_pipeline_row_validation() -> None:
    """В PipelineRow типы полей должны проходить валидацию."""
    with pytest.raises(AttributeError, match="Expected type <class 'float'> for key num got <class 'int'>"):
        row = PipelineRow(text="text", num=5)
        row.validate({"text": str, "num": float})
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['text'] got ['num', 'text']")):
        row = PipelineRow(text="text", num=5)
        row.validate({"text": str})
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['num', 'text'] got ['text']")):
        row = PipelineRow(text="text")
        row.validate({"text": str, "num": float})


def test_pipeline_row_attributes() -> None:
    """В PipelineRow обращение к полям через точку."""
    row = PipelineRow(text="text", num=5, num2=3.14)
    row.validate({"text": str, "num": int, "num2": float})
    assert row.text == "text"
    assert row.num == 5
    assert row.num2 == 3.14
    with pytest.raises(AttributeError, match="Field field not found in PipelineRow"):
        row.field
    assert repr(row) == "PipelineRow({'text': 'text', 'num': 5, 'num2': 3.14})"


def test_pipeline_table_validation() -> None:
    """В PipelineTable валидируются все строки."""
    table = PipelineTable()
    with pytest.raises(TypeError, match="Expected PipelineRow in PipelineTable.append, got <class 'int'>"):
        table.append(5)  # type: ignore[arg-type]
    table.append(PipelineRow(text="text"))
    table.append(PipelineRow(text="text", num=5))
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['text'] got ['num', 'text']")):
        table.validate({"text": str})


def test_pipeline_table_attributes() -> None:
    """В PipelineTable есть доступ к отдельным элементам."""
    table = PipelineTable()
    table.append(PipelineRow(num=1, text="one"))
    table.append(PipelineRow(num=2, text="two"))
    table.append(PipelineRow(num=3, text="three"))
    table.validate({"num": int, "text": str})
    assert len(table) == 3
    assert repr(table) == (
        "PipelineTable([PipelineRow({'num': 1, 'text': 'one'}), "
        "PipelineRow({'num': 2, 'text': 'two'}), "
        "PipelineRow({'num': 3, 'text': 'three'})])"
    )
    for pos, row in enumerate(table, start=1):
        assert row.num == pos
        assert row.text == ["one", "two", "three"][pos - 1]
