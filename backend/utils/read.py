"""Функции для чтения разных форматов."""

from typing import Any

import yaml


def read_from_yaml_str(yaml_str: str) -> Any:
    """Читает yaml из строки."""
    return yaml.safe_load(yaml_str)
