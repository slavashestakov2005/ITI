"""Генерация рейтингов из сырых результатов."""

from ratings.place_generator import (
    MiddleSchoolIndividualPlaceGenerator,
    PlaceGenerator,
    PrimarySchoolIndividualPlaceGenerator,
)
from ratings.score_generator import (
    MiddleSchoolIndividualScoreGenerator,
    PrimarySchoolIndividualScoreGenerator,
    ScoreGenerator,
)

__all__ = [
    "MiddleSchoolIndividualPlaceGenerator",
    "PrimarySchoolIndividualPlaceGenerator",
    "PlaceGenerator",
    "MiddleSchoolIndividualScoreGenerator",
    "PrimarySchoolIndividualScoreGenerator",
    "ScoreGenerator",
]
