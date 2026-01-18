"""Тесты на классы пайплайна."""

import re

import pytest
from pipeline import PipelineBaseObject, PipelineObject, PipelineTable


def test_pipeline_base_object() -> None:
    """PipelineBaseObject абстрактный класс, нельзя создать его объект."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class PipelineBaseObject"):
        PipelineBaseObject()  # type: ignore[abstract,misc,arg-type]


def test_pipeline_object_validation() -> None:
    """В PipelineBaseObject типы полей должны проходить валидацию."""
    with pytest.raises(AttributeError, match="Expected type <class 'float'> for key num got <class 'int'>"):
        obj = PipelineObject(text="text", num=5)
        obj.validate({"text": str, "num": float})
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['text'] got ['num', 'text']")):
        obj = PipelineObject(text="text", num=5)
        obj.validate({"text": str})
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['num', 'text'] got ['text']")):
        obj = PipelineObject(text="text")
        obj.validate({"text": str, "num": float})
    obj = PipelineObject(text="text", num=5, num2=3.14)
    obj.validate({"text": str, "num": int, "num2": float})


def test_pipeline_object_attributes() -> None:
    obj = PipelineObject(text="text", num=5, num2=3.14)
    assert obj.text == "text"
    assert obj.num == 5
    assert obj.num2 == 3.14
    with pytest.raises(AttributeError, match="Field field not found in PipelineObject"):
        obj.field
    assert repr(obj) == "PipelineRow({'text': 'text', 'num': 5, 'num2': 3.14})"


def test_pipeline_table_validation() -> None:
    table = PipelineTable()
    with pytest.raises(TypeError, match="Expected PipelineObject in PipelineTable.append, got <class 'int'>"):
        table.append(5)
    table.append(PipelineObject(text="text"))
    table.append(PipelineObject(text="text", num=5))
    with pytest.raises(AttributeError, match=re.escape("Expected attributes ['text'] got ['num', 'text']")):
        table.validate({"text": str})


def test_pipeline_table_attributes() -> None:
    table = PipelineTable()
    table.append(PipelineObject(num=1, text="one"))
    table.append(PipelineObject(num=2, text="two"))
    table.append(PipelineObject(num=3, text="three"))
    table.validate({"num": int, "text": str})
    assert len(table) == 3
    assert (
        repr(table)
        == "PipelineTable([PipelineRow({'num': 1, 'text': 'one'}), PipelineRow({'num': 2, 'text': 'two'}), PipelineRow({'num': 3, 'text': 'three'})])"
    )
    for i, obj in enumerate(table, start=1):
        assert obj.num == i
        assert obj.text == ["one", "two", "three"][i - 1]
