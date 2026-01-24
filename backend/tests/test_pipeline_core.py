"""Тесты на весь пайплайн вместе."""

import pytest

from pipeline import Engine, PipelineBaseObject, PipelineRow, PipelineTable
from utils import read_from_yaml_str


def test_pipeline_engine_invalid_yaml() -> None:
    """Не верный полный ямл."""
    with pytest.raises(ValueError, match="Top-level pipeline config must be a mapping: node_name -> node_cfg"):
        Engine.from_raw_cfg("expect_dict_here")
    with pytest.raises(ValueError, match="node_name in pipeline must be a string"):
        Engine.from_raw_cfg(
            read_from_yaml_str(
                """
node1:
  type: merger
  input:
    - math
2:
  type: merger
  input:
    - math
"""
            )
        )


test_yaml_pipeline = """
math:
  type: db_read
  callback: in_test_read_math
  output:
    type: table
    columns:
      student: int
      res: int
merge_ind:
  type: merger
  input: [math]
sum:
  type: agg
  callback: in_test_calc_sums
  input:
    - math
  output:
    type: row
    columns:
      sum: int
"""


def test_pipeline_engine_callback_type() -> None:
    """Сигнатура колбека должна быть правильной."""

    @Engine.callback  # type: ignore[arg-type]
    def some_test_callback() -> None:
        raise ValueError("Unreachable")


def test_pipeline_engine_invalid_callback() -> None:
    """Нет колбеков."""
    with pytest.raises(KeyError, match="Unknown node 'math'"):
        engine = Engine.from_raw_cfg(
            read_from_yaml_str(
                """
node1:
  type: merger
  input:
    - math
"""
            )
        )
        engine.run("node1")
    with pytest.raises(KeyError, match="Callback 'in_test_calc_sums' not registered"):
        engine = Engine.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
        engine.run("sum")
    with pytest.raises(KeyError, match="Callback 'in_test_read_math' not registered"):

        @Engine.callback  # type: ignore[arg-type]
        def in_test_calc_sums() -> None:
            raise ValueError("Unreachable")

        engine = Engine.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
        engine.run("sum")


def test_pipeline_engine_core_ok() -> None:
    """Правильный пайплайн."""
    called = False

    @Engine.callback
    def in_test_read_math(inp: PipelineBaseObject) -> PipelineBaseObject:
        nonlocal called
        if called:
            raise ValueError("Expected only one function call, use cache")
        called = True
        table = PipelineTable()
        table.append(PipelineRow(student=1, res=5))
        table.append(PipelineRow(student=2, res=27))
        table.append(PipelineRow(student=3, res=1))
        table.append(PipelineRow(student=4, res=17))
        return table

    @Engine.callback
    def in_test_calc_sums(inp: PipelineBaseObject) -> PipelineBaseObject:
        all_sum = 0
        for elem in inp.math:  # type: ignore[union-attr]
            all_sum += elem.res  # type: ignore[union-attr]
        return PipelineRow(sum=all_sum)

    engine = Engine.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
    assert engine.run("sum").sum == 50  # type: ignore[union-attr]
    with pytest.raises(ValueError, match="Expected only one function call, use cache"):
        engine.run("sum")
