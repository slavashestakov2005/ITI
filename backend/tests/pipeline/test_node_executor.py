"""Тесты на весь пайплайн вместе."""

import pytest

from pipeline import NodeExecutor, Object, Row, Table
from pipeline.node_executor import not_found_callback
from utils import read_from_yaml_str


def test_pipeline_node_executor_invalid_yaml() -> None:
    """Не верный полный ямл."""
    with pytest.raises(ValueError, match="Top-level pipeline config must be a mapping: node_name -> node_cfg"):
        NodeExecutor.from_raw_cfg("expect_dict_here")
    with pytest.raises(ValueError, match="node_name in pipeline must be a string"):
        NodeExecutor.from_raw_cfg(read_from_yaml_str("""
node1:
  type: merge
  input:
    - math
2:
  type: merge
  input:
    - math
"""))


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
  type: merge
  input: [math]
sum:
  type: func
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


def test_pipeline_node_executor_callback_type() -> None:
    """Сигнатура колбека должна быть правильной."""

    @NodeExecutor.callback  # type: ignore[arg-type]
    def some_test_callback() -> None:
        raise ValueError("Unreachable")


def test_pipeline_node_executor_invalid_callback() -> None:
    """Нет колбеков."""
    NodeExecutor.clear()

    with pytest.raises(ValueError, match="Callback was empty in yaml, but called"):
        not_found_callback(Row())

    with pytest.raises(KeyError, match="Unknown node 'math'"):
        node_executor = NodeExecutor.from_raw_cfg(read_from_yaml_str("""
node1:
  type: merge
  input:
    - math
"""))
        node_executor.run("node1")
    with pytest.raises(KeyError, match="Callback 'in_test_read_math' not registered"):
        node_executor = NodeExecutor.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
        node_executor.run("sum")
    with pytest.raises(KeyError, match="Callback 'in_test_calc_sums' not registered"):

        @NodeExecutor.callback
        def in_test_read_math(inp: Object) -> Object:
            return Row(student=1, res=1)

        node_executor = NodeExecutor.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
        node_executor.run("sum")


def test_pipeline_node_executor_core_ok() -> None:
    """Правильный пайплайн."""
    NodeExecutor.clear()

    @NodeExecutor.callback
    def in_test_read_math(inp: Object) -> Object:
        table = Table()
        table.append(Row(student=1, res=5))
        table.append(Row(student=2, res=27))
        table.append(Row(student=3, res=1))
        table.append(Row(student=4, res=17))
        return table

    @NodeExecutor.callback
    def in_test_calc_sums(inp: Object) -> Object:
        sum_math, sum_ind = 0, 0
        for elem in inp.math:  # type: ignore[union-attr]
            sum_math += elem.res  # type: ignore[union-attr]
        for elem in inp.merge_ind.math:  # type: ignore[union-attr]
            sum_ind += elem.res  # type: ignore[union-attr]
        return Row(sum_math=sum_math, sum_ind=sum_ind)

    node_executor = NodeExecutor.from_raw_cfg(read_from_yaml_str(test_yaml_pipeline))
    assert node_executor.run("sum").sum_math == 50  # type: ignore[union-attr]
    assert node_executor.run("sum").sum_ind == 50  # type: ignore[union-attr]


def test_real_pipeline() -> None:
    """Пример реального пайплайна."""
    NodeExecutor.clear()
    pipeline = """
math:
  type: db_read
  callback: in_test_read_math
  output:
    type: table
    columns:
      student: int
      res: int
students:
  type: db_read
  callback: in_test_read_students
  output:
    type: table
    columns:
      id: int
      name: str
decode_math:
  type: func
  callback: in_test_decode_math
  input:
    - math
    - students
  output:
    type: table
    columns:
      name: str
      score: int
"""
    node_executor = NodeExecutor.from_raw_cfg(read_from_yaml_str(pipeline))

    @NodeExecutor.callback
    def in_test_read_math(inp: Object) -> Object:
        table = Table()
        table.append(Row(student=1, res=5))
        table.append(Row(student=2, res=27))
        table.append(Row(student=123, res=10))
        return table

    @NodeExecutor.callback
    def in_test_read_students(inp: Object) -> Object:
        table = Table()
        table.append(Row(id=1, name="Slava"))
        table.append(Row(id=2, name="Dima"))
        table.append(Row(id=3, name="Dan"))
        return table

    @NodeExecutor.callback
    def in_test_decode_math(inp: Object) -> Object:
        decode = {stud.id: stud.name for stud in inp.students}  # type: ignore[union-attr]
        table = Table()
        for res in inp.math:  # type: ignore[union-attr]
            name = decode.get(res.student)  # type: ignore[union-attr]
            if name is not None:
                table.append(Row(name=decode[res.student], score=res.res))  # type: ignore[union-attr]
        return table

    res = node_executor.run("decode_math")
    assert repr(res) == "Table([Row({'name': 'Slava', 'score': 5}), Row({'name': 'Dima', 'score': 27})])"
