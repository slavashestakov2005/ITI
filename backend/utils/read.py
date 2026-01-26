"""Функции для чтения разных форматов."""

from typing import Any

import yaml


def read_from_yaml_str(yaml_str: str) -> Any:
    """Читает yaml из строки."""
    return yaml.safe_load(yaml_str)


def read_from_yaml_file(file_path: str) -> Any:
    """Читает yaml из файла."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
