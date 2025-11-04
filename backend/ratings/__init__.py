"""Генерация рейтингов из сырых результатов."""

from ratings.score_generator import (
    MiddleSchoolIndividualScoreGenerator,
    PrimarySchoolIndividualScoreGenerator,
    ScoreGenerator,
)

__all__ = [
    "MiddleSchoolIndividualScoreGenerator",
    "PrimarySchoolIndividualScoreGenerator",
    "ScoreGenerator",
]
