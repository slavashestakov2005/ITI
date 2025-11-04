"""Тесты на генерацию результатов из сырых баллов."""

import pytest

from ratings import MiddleSchoolIndividualScoreGenerator, PrimarySchoolIndividualScoreGenerator, ScoreGenerator


def test_base_score_generator() -> None:
    """ScoreGenerator абстрактный класс, нельзя создать его объект."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class ScoreGenerator"):
        ScoreGenerator([])  # type: ignore[abstract,misc,arg-type]


def test_middle_school_ind_score_generator_no_args() -> None:
    """В MiddleSchoolIndividualScoreGenerator нужно передавать аргументы."""
    with pytest.raises(
        TypeError, match="missing 2 required keyword-only arguments: 'all_results' and 'theoretical_maximum'"
    ):
        MiddleSchoolIndividualScoreGenerator()  # type: ignore[call-arg]


def test_middle_school_ind_score_generator_no_key_args() -> None:
    """Аргументы в MiddleSchoolIndividualScoreGenerator должны быть именованными."""
    with pytest.raises(TypeError, match="takes 1 positional argument but 3 were give"):
        MiddleSchoolIndividualScoreGenerator((7.0, 4.0, 5.0), 10)  # type: ignore[misc]


def test_middle_school_ind_score_generator_normalization_by_participant() -> None:
    """MiddleSchoolIndividualScoreGenerator нормирует по лучшему участнику."""
    generator = MiddleSchoolIndividualScoreGenerator(all_results=(4.0, 8.0, 1.0, 7.0), theoretical_maximum=10)
    assert generator.compute() == (50, 100, 13, 88)
    generator = MiddleSchoolIndividualScoreGenerator(
        all_results=(0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0), theoretical_maximum=10
    )
    assert generator.compute() == (0, 14, 29, 43, 57, 71, 86, 100)
    generator = MiddleSchoolIndividualScoreGenerator(all_results=(5.0,), theoretical_maximum=10)
    assert generator.compute() == (100,)


def test_middle_school_ind_score_generator_normalization_by_theoretical_maximum() -> None:
    """MiddleSchoolIndividualScoreGenerator нормирует по теоретическому максимуму."""
    generator = MiddleSchoolIndividualScoreGenerator(all_results=(4.0, 8.0, 1.0, 7.0), theoretical_maximum=100)
    assert generator.compute() == (8, 16, 2, 14)


def test_primary_school_ind_score_generator() -> None:
    """PrimarySchoolIndividualScoreGenerator оставляет результаты как есть."""
    generator = PrimarySchoolIndividualScoreGenerator(all_results=(1.0, 7.0, 3.0, 9.0))
    assert generator.compute() == (1, 7, 3, 9)
