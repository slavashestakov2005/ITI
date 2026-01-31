"""Класс для вычесления нод."""

from typing import Any

from pipeline.node import Node, node_from_raw_cfg
from pipeline.object import Callback, Object, Row
from utils import YAML


def not_found_callback(inp: Object) -> Object:
    """Заглушка для нод без пользовательских колбеков."""
    raise ValueError("Callback was empty in yaml, but called")


class NodeExecutor:
    """Класс для обработки нод."""

    _callbacks: dict[str, Callback] = {}

    def __init__(self, specs: dict[str, Node]):
        """Сохраняем список всех нод."""
        self._specs = specs
        self._cache: dict[str, Any] = {}

    @classmethod
    def from_raw_cfg(cls, raw_cfg: YAML) -> "NodeExecutor":
        """Читаем пайплайн из ямла и возвращяем готовый обьект."""
        if not isinstance(raw_cfg, dict):
            raise ValueError("Top-level pipeline config must be a mapping: node_name -> node_cfg")

        specs = {}
        for name, node in raw_cfg.items():
            if not isinstance(name, str):
                raise ValueError("node_name in pipeline must be a string")
            specs[name] = node_from_raw_cfg(node)
        return cls(specs)

    @classmethod
    def callback(cls, fn: Callback) -> None:
        """Декоратор для регистрации callback."""
        cls._callbacks[fn.__name__] = fn

    @classmethod
    def clear(cls) -> None:
        """Очищает список колбеков."""
        cls._callbacks = {}

    def run(self, target: str) -> Object:
        """Запускает вычисление ноды."""
        self._cache.clear()
        return self._eval(target)

    @classmethod
    def _get_callback(cls, callback: str) -> Callback:
        """Возвращяет калбек по названию."""
        if not callback:
            return not_found_callback
        if callback not in cls._callbacks:
            raise KeyError(f"Callback '{callback}' not registered")
        return cls._callbacks[callback]

    def _eval(self, node_name: str) -> Object:
        """Рекурсивно вычисляет ноды."""
        cached = self._cache.get(node_name)
        if cached is not None:
            return cached
        if node_name not in self._specs:
            raise KeyError(f"Unknown node '{node_name}'")

        spec = self._specs[node_name]
        inp = self._make_object_from_deps(spec.input)
        out = spec.compute(self._get_callback(spec.callback), inp)
        self._cache[node_name] = out
        return out

    def _make_object_from_deps(self, deps: list[str]) -> Object:
        """Вычисляет зависимости и складывает в объект."""
        return Row(**{inp: self._eval(inp) for inp in deps})
