"""Ядро вычислений пайплайна."""

from typing import Any

from pipeline.data_class import PipelineBaseObject, PipelineCallback, PipelineRow
from pipeline.node import PipelineNodeSpec, PipelineNodeType


class Engine:
    """Класс для работы с пайплайном."""

    _callbacks: dict[str, PipelineCallback] = {}

    def __init__(self, specs: dict[str, PipelineNodeSpec]):
        """Сохраняем список всех нод."""
        self.specs = specs
        self._cache: dict[str, Any] = {}

    @classmethod
    def from_raw_cfg(cls, raw_cfg: Any) -> "Engine":
        """Читаем пайплайн из ямла."""
        if not isinstance(raw_cfg, dict):
            raise ValueError("Top-level pipeline config must be a mapping: node_name -> node_cfg")

        specs = {}
        for name, node in raw_cfg.items():
            if not isinstance(name, str):
                raise ValueError("node_name in pipeline must be a string")
            specs[name] = PipelineNodeSpec.from_raw_cfg(name, node)
        return cls(specs)

    @classmethod
    def callback(cls, fn: PipelineCallback) -> None:
        """Декоратор для регистрации callback."""
        cls._callbacks[fn.__name__] = fn

    def run(self, target: str) -> PipelineBaseObject:
        """Вычисляет один таргет."""
        self._cache.clear()
        return self._eval(target)

    @classmethod
    def _get_cb(cls, spec: PipelineNodeSpec) -> PipelineCallback:
        if not spec.callback:
            raise ValueError(f"Node '{spec.name}' requires callback")
        if spec.callback not in cls._callbacks:
            raise KeyError(f"Callback '{spec.callback}' not registered")
        return cls._callbacks[spec.callback]

    def _eval(self, node_name: str) -> PipelineBaseObject:
        """Вычисляет один таргет."""
        cached = self._cache.get(node_name)
        if cached is not None:
            return cached
        if node_name not in self.specs:
            raise KeyError(f"Unknown node '{node_name}'")

        spec = self.specs[node_name]
        match spec.type:
            case PipelineNodeType.DB_READ:
                cb = Engine._get_cb(spec)
                out = cb(PipelineRow())
            case PipelineNodeType.MERGER:
                out = self._make_object_from_deps(spec.input)
            case PipelineNodeType.AGGREGATOR:
                cb = Engine._get_cb(spec)
                inp = self._make_object_from_deps(spec.input)
                out = cb(inp)
            case _:
                raise ValueError("Unsupported PipelineNodeType")

        out.validate(spec.output)
        self._cache[node_name] = out
        return out

    def _make_object_from_deps(self, deps: list[str]) -> PipelineBaseObject:
        """Вычисляет зависимости и складывает в объект."""
        return PipelineRow(**{inp: self._eval(inp) for inp in deps})
