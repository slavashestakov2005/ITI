"""Генерирует балл в рейтинг по сырым результатам."""

import abc

from utils import math_round


class ScoreGenerator(abc.ABC):
    """Базовый класс для генерации балла в рейтинг по сырым результатам."""

    def __init__(self, *, raw_scores: tuple[float, ...]):
        """Базовый конструктор."""
        self._raw_scores = raw_scores

    def compute(self) -> tuple[float, ...]:
        """Вычисляет результаты для всех участников предмета."""
        return tuple([self._compute_score(score) for score in self._raw_scores])

    @abc.abstractmethod
    def _compute_score(self, score: float) -> float:
        """Возвращает по сырому результату балл в рейтинг."""
        raise NotImplementedError


class MiddleSchoolIndividualScoreGenerator(ScoreGenerator):
    """Класс для результатов индивидуальных предметов в ОШ."""

    def __init__(self, *, raw_scores: tuple[float, ...], theoretical_maximum: float):
        """Сохраняем максимальный результат по предмету."""
        super().__init__(raw_scores=raw_scores)
        max_raw_score = max(raw_scores)
        self._normalization_maximum = max(max_raw_score, theoretical_maximum / 2)

    def _compute_score(self, score: float) -> float:
        return math_round(score / self._normalization_maximum * 100)


class PrimarySchoolIndividualScoreGenerator(ScoreGenerator):
    """Класс для результатов индивидуальных предметов в НШ."""

    def _compute_score(self, score: float) -> float:
        return score
