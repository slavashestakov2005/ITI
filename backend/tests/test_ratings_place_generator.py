"""Тесты на генерацию результатов из сырых баллов."""

import pytest

from ratings import MiddleSchoolIndividualPlaceGenerator, PlaceGenerator, PrimarySchoolIndividualPlaceGenerator


def test_base_place_generator() -> None:
    """PlaceGenerator абстрактный класс, нельзя создать его объект."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class PlaceGenerator"):
        PlaceGenerator([])  # type: ignore[abstract,misc,arg-type]


def test_middle_school_sorting_in_place_generator() -> None:
    """Результаты должны быть отсортированы от больших к меньшим."""
    with pytest.raises(AssertionError, match="Results not sorted"):
        MiddleSchoolIndividualPlaceGenerator(raw_scores=(4.0, 8.0, 1.0, 7.0))
    with pytest.raises(AssertionError, match="Results not sorted"):
        MiddleSchoolIndividualPlaceGenerator(raw_scores=(1.0, 4.0, 7.0, 8.0))


def test_middle_school_ind_place_generator() -> None:
    """MiddleSchoolIndividualPlaceGenerator выдаёт места в естественном порядке."""
    generator = MiddleSchoolIndividualPlaceGenerator(raw_scores=(8.0, 7.0, 4.0, 1.0))
    assert generator.compute() == (1, 2, 3, 4)
    generator = MiddleSchoolIndividualPlaceGenerator(raw_scores=(8.0, 8.0, 8.0, 8.0, 7.0))
    assert generator.compute() == (1, 1, 1, 1, 5)
    generator = MiddleSchoolIndividualPlaceGenerator(raw_scores=(8.0, 7.0, 7.0, 7.0, 1.0))
    assert generator.compute() == (1, 2, 2, 2, 5)
    generator = MiddleSchoolIndividualPlaceGenerator(raw_scores=(8.0, 7.0, 6.0, 6.0, 1.0))
    assert generator.compute() == (1, 2, 3, 3, 5)
    generator = MiddleSchoolIndividualPlaceGenerator(raw_scores=(8.0, 8.0, 7.0, 7.0, 6.0, 6.0, 1.0))
    assert generator.compute() == (1, 1, 3, 3, 5, 5, 7)


def test_primary_school_ind_place_generator() -> None:
    """PrimarySchoolIndividualPlaceGenerator выдаёт все призовые места."""
    generator = PrimarySchoolIndividualPlaceGenerator(raw_scores=(8.0, 7.0, 4.0, 1.0))
    assert generator.compute() == (1, 2, 3, 4)
    generator = PrimarySchoolIndividualPlaceGenerator(raw_scores=(8.0, 7.0, 7.0, 6.0, 5.0, 4.0))
    assert generator.compute() == (1, 2, 2, 3, 4, 5)
    generator = PrimarySchoolIndividualPlaceGenerator(raw_scores=(8.0, 7.0, 6.0, 6.0, 5.0, 4.0))
    assert generator.compute() == (1, 2, 3, 3, 4, 5)
    generator = PrimarySchoolIndividualPlaceGenerator(raw_scores=(8.0, 7.0, 7.0, 6.0, 6.0, 5.0, 4.0))
    assert generator.compute() == (1, 2, 2, 3, 3, 4, 5)
    generator = PrimarySchoolIndividualPlaceGenerator(raw_scores=(8.0, 8.0, 7.0, 7.0, 6.0, 6.0, 5.0, 5.0, 4.0))
    assert generator.compute() == (1, 1, 2, 2, 3, 3, 4, 4, 6)
