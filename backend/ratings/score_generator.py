"""Генерирует балл в рейтинг по сырым результатам."""

import abc

from utils import math_round


class ScoreGenerator(abc.ABC):
    """Класс генерирует балл в рейтинг по сырым результатам."""

    def __init__(self, *, all_results: tuple[float, ...]):
        """Базовый конструктор."""
        self.__all_results = all_results

    @abc.abstractmethod
    def _compute_score(self, result: float) -> float:
        """Возвращает по сырому результату балл в рейтинг."""
        pass

    def compute(self) -> tuple[float, ...]:
        """Вычисляет результаты для всех участников предмета."""
        return tuple([self._compute_score(result) for result in self.__all_results])


class MiddleSchoolIndividualScoreGenerator(ScoreGenerator):
    """Класс для результатов индивидуальных предметов в ОШ."""

    def __init__(self, *, all_results: tuple[float, ...], theoretical_maximum: float):
        """Сохраняем максимальный результат по предмету."""
        super().__init__(all_results=all_results)
        max_result = max(all_results)
        self.__normalization_maximum = max(max_result, theoretical_maximum / 2)

    def _compute_score(self, result: float) -> float:
        return math_round(result / self.__normalization_maximum * 100)


class PrimarySchoolIndividualScoreGenerator(ScoreGenerator):
    """Класс для результатов индивидуальных предметов в НШ."""

    def _compute_score(self, result: float) -> float:
        return result
