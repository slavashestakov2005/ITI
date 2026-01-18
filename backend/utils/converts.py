"""Функции для конвертации между типами."""

from typing import Any


def math_round(number: float) -> int:
    """Округляет число математически правильно."""
    return int(number + 0.5)


def sorted_dict_keys(storage: dict[str, Any]) -> list[str]:
    """Сортирует ключи словаря."""
    return sorted(storage.keys())
