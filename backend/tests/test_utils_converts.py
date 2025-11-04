"""Тесты на функции конвертации."""

from utils import math_round


def test_math_round() -> None:
    """Проверяем что math_round округляет правильно."""
    assert math_round(3.49) == 3
    assert math_round(3.50) == 4
    assert math_round(3.51) == 4
    assert math_round(4.49) == 4
    assert math_round(4.50) == 5
    assert math_round(4.51) == 5
