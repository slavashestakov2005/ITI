"""Тесты на классы пайплайна."""

import pytest

from pipeline import (
    PipelineNodeSpec,
    PipelineNodeType,
    PipelineObjectPrimitiveType,
    PipelineObjectType,
    PipelineObjectTypeConstraint,
)
from utils import read_from_yaml_str


def test_pipeline_object_primitive_type() -> None:
    """PipelineObjectPrimitiveType конструируется из строки."""
    assert PipelineObjectPrimitiveType.from_string("str") == PipelineObjectPrimitiveType.STR
    assert PipelineObjectPrimitiveType.STR.py_type() == str
    assert PipelineObjectPrimitiveType.from_string("int") == PipelineObjectPrimitiveType.INT
    assert PipelineObjectPrimitiveType.INT.py_type() == int
    assert PipelineObjectPrimitiveType.from_string("float") == PipelineObjectPrimitiveType.FLOAT
    assert PipelineObjectPrimitiveType.FLOAT.py_type() == float
    with pytest.raises(ValueError, match="Unknown value for PipelineObjectPrimitiveType: dict"):
        PipelineObjectPrimitiveType.from_string("dict")
    with pytest.raises(ValueError, match="Unknown value for PipelineObjectPrimitiveType: "):
        PipelineObjectPrimitiveType.from_string("")


def test_pipeline_object_type() -> None:
    """PipelineObjectType конструируется из строки."""
    assert PipelineObjectType.from_string("row") == PipelineObjectType.ROW
    assert PipelineObjectType.from_string("table") == PipelineObjectType.TABLE
    with pytest.raises(ValueError, match="Unknown value for PipelineObjectType: other"):
        PipelineObjectType.from_string("other")


def test_pipeline_object_type_constraint() -> None:
    """PipelineObjectType конструируется из словарей и валидируется."""
    with pytest.raises(AssertionError, match="Raw config for PipelineObjectTypeConstraint need be dict"):
        PipelineObjectTypeConstraint.from_raw_cfg("hahaha")
    with pytest.raises(ValueError, match="Unknown value for PipelineObjectType: no"):
        PipelineObjectTypeConstraint.from_raw_cfg({"type": "no"})
    with pytest.raises(AssertionError, match="PipelineObjectTypeConstraint.columns cannot be empty"):
        PipelineObjectTypeConstraint.from_raw_cfg({"type": "table"})
    with pytest.raises(AttributeError, match="'list' object has no attribute 'items'"):
        PipelineObjectTypeConstraint.from_raw_cfg({"type": "table", "columns": []})
    with pytest.raises(ValueError, match="Unknown value for PipelineObjectPrimitiveType: no"):
        PipelineObjectTypeConstraint.from_raw_cfg({"type": "table", "columns": {"col1": "no"}})
    constraint = PipelineObjectTypeConstraint.from_raw_cfg(
        {"type": "table", "columns": {"col1": "int", "col2": "str", "col3": "float"}}
    )
    assert constraint is not None
    assert constraint.type == PipelineObjectType.TABLE
    assert constraint.columns == {
        "col1": PipelineObjectPrimitiveType.INT,
        "col2": PipelineObjectPrimitiveType.STR,
        "col3": PipelineObjectPrimitiveType.FLOAT,
    }


def test_pipeline_node_type() -> None:
    """PipelineNodeType конструируется из строки."""
    assert PipelineNodeType.from_string("db_read") == PipelineNodeType.DB_READ
    assert PipelineNodeType.from_string("merger") == PipelineNodeType.MERGER
    assert PipelineNodeType.from_string("agg") == PipelineNodeType.AGGREGATOR
    with pytest.raises(ValueError, match="Unknown value for PipelineNodeType: do"):
        PipelineNodeType.from_string("do")
    with pytest.raises(ValueError, match="Unknown value for PipelineNodeType: "):
        PipelineNodeType.from_string("")


def test_pipeline_node_spec_ok() -> None:  # noqa: CFQ001
    """PipelineNodeSpec конструируется из словарей правильно."""
    spec = PipelineNodeSpec.from_raw_cfg(
        "db_iti_subjects",
        read_from_yaml_str(
            """
type: db_read
callback: select_subjects_info_for_iti
input:
  - iti_id
output:
  type: table
  columns:
    subject_id: int
    about: str
"""
        ),
    )
    assert spec.name == "db_iti_subjects"
    assert spec.type == PipelineNodeType.DB_READ
    assert spec.callback == "select_subjects_info_for_iti"
    assert spec.input == ["iti_id"]
    assert spec.output == PipelineObjectTypeConstraint(
        type=PipelineObjectType.TABLE,
        columns={
            "subject_id": PipelineObjectPrimitiveType.INT,
            "about": PipelineObjectPrimitiveType.STR,
        },
    )

    spec = PipelineNodeSpec.from_raw_cfg(
        "all_ind_res",
        read_from_yaml_str(
            """
type: merger
input:
  - math
  - rus
  - eng
"""
        ),
    )
    assert spec.name == "all_ind_res"
    assert spec.type == PipelineNodeType.MERGER
    assert spec.callback == ""
    assert spec.input == ["math", "rus", "eng"]
    assert spec.output is None

    spec = PipelineNodeSpec.from_raw_cfg(
        "ind_agg",
        read_from_yaml_str(
            """
type: agg
callback: ind_agg_calc
input: [all_ind_res, db_iti_subjects]
output:
  type: table
  columns:
    student_id: int
    place: int
    total_score: float
"""
        ),
    )
    assert spec.name == "ind_agg"
    assert spec.type == PipelineNodeType.AGGREGATOR
    assert spec.callback == "ind_agg_calc"
    assert spec.input == ["all_ind_res", "db_iti_subjects"]
    assert spec.output == PipelineObjectTypeConstraint(
        type=PipelineObjectType.TABLE,
        columns={
            "student_id": PipelineObjectPrimitiveType.INT,
            "place": PipelineObjectPrimitiveType.INT,
            "total_score": PipelineObjectPrimitiveType.FLOAT,
        },
    )
