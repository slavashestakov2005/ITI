"""Тесты на весь пайплайн вместе."""

import pytest

from pipeline import Engine, Object, Row, Table
from pipeline.engine import not_found_callback
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
    - merge_ind
  output:
    type: row
    columns:
      sum_math: int
      sum_ind: int
"""


def test_pipeline_engine_callback_type() -> None:
    """Сигнатура колбека должна быть правильной."""

    @Engine.callback  # type: ignore[arg-type]
    def some_test_callback() -> None:
        raise ValueError("Unreachable")


def test_pipeline_engine_invalid_callback() -> None:
    """Нет колбеков."""
    Engine.clear()

    with pytest.raises(ValueError, match="Callback was empty in yaml, but called"):
        not_found_callback(Row())

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
    with pytest.raises(KeyError, match="Callback 'in_test_read_math' not registered"):
        engine = Engine.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
        engine.run("sum")
    with pytest.raises(KeyError, match="Callback 'in_test_calc_sums' not registered"):

        @Engine.callback
        def in_test_read_math(inp: Object) -> Object:
            return Row(student=1, res=1)

        engine = Engine.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
        engine.run("sum")


def test_pipeline_engine_core_ok() -> None:
    """Правильный пайплайн."""
    Engine.clear()

    @Engine.callback
    def in_test_read_math(inp: Object) -> Object:
        table = Table()
        table.append(Row(student=1, res=5))
        table.append(Row(student=2, res=27))
        table.append(Row(student=3, res=1))
        table.append(Row(student=4, res=17))
        return table

    @Engine.callback
    def in_test_calc_sums(inp: Object) -> Object:
        sum_math, sum_ind = 0, 0
        for elem in inp.math:  # type: ignore[union-attr]
            sum_math += elem.res  # type: ignore[union-attr]
        for elem in inp.merge_ind.math:  # type: ignore[union-attr]
            sum_ind += elem.res  # type: ignore[union-attr]
        return Row(sum_math=sum_math, sum_ind=sum_ind)

    engine = Engine.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
    assert engine.run("sum").sum_math == 50  # type: ignore[union-attr]
    assert engine.run("sum").sum_ind == 50  # type: ignore[union-attr]
