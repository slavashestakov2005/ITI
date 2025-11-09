"""Генерирует место в рейтинге по сырым результатам."""

import abc


class PlaceGenerator(abc.ABC):
    """Базовый класс для генерации места в рейтинге по сырым результатам."""

    def __init__(self, *, raw_scores: tuple[float, ...]):
        """Базовый конструктор."""
        self._raw_scores = raw_scores
        last = raw_scores[0]
        for score in raw_scores:
            assert last >= score, "Results not sorted"
            last = score

    def compute(self) -> tuple[int, ...]:
        """Вычисляет места для всех участников предмета."""
        places = []
        last = None
        peoples = 0
        for score in self._raw_scores:
            if last is None:
                places.append(self._compute_first_place())
                peoples = 1
                last = score
            elif last == score:
                places.append(places[-1])
                peoples += 1
            else:
                places.append(self._compute_next_place(places[-1], peoples))
                peoples = 1
                last = score
        return tuple(places)

    def _compute_first_place(self) -> int:
        """Возвращает место для лучшего результата."""
        return 1

    @abc.abstractmethod
    def _compute_next_place(self, last_place: int, last_place_peoples: int) -> int:
        """Возвращает место для следующего результата."""
        raise NotImplementedError


class MiddleSchoolIndividualPlaceGenerator(PlaceGenerator):
    """Класс для мест индивидуальных предметов в ОШ."""

    def _compute_next_place(self, last_place: int, last_place_peoples: int) -> int:
        return last_place + last_place_peoples


class PrimarySchoolIndividualPlaceGenerator(PlaceGenerator):
    """Класс для результатов индивидуальных предметов в НШ."""

    def _compute_next_place(self, last_place: int, last_place_peoples: int) -> int:
        if last_place <= 3:
            return last_place + 1
        else:
            return last_place + last_place_peoples
