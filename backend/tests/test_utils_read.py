"""Проверяет утилиты чтения."""

from utils import read_from_yaml_str


def test_read_from_yaml_str() -> None:
    """Проверяем чтение ямла в объект."""
    parsed = read_from_yaml_str(
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
    )
    assert parsed == {
        "type": "db_read",
        "callback": "select_subjects_info_for_iti",
        "input": ["iti_id"],
        "output": {
            "type": "table",
            "columns": {
                "subject_id": "int",
                "about": "str",
            },
        },
    }
