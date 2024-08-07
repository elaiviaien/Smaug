"""This module contains classes for metrics and metric lists."""

from dataclasses import dataclass
from typing import Any
import pickle


MAX_VALUES = {
    "cpu usage": 100,
    "cpu average": 100,
    "memory usage": 100,
    "memory usage average": 100,
    "swap memory usage": 100,
    "swap memory usage average": 100,
    "disk usage": 100,
}
QUANTITIES = {
    "cpu usage": "%",
    "cpu average": "%",
    "memory usage": "%",
    "memory usage average": "%",
    "swap memory usage": "%",
    "swap memory usage average": "%",
    "disk usage": "%",
    "disk usage difference": "%",
    "execution time": "s",
    "total thread usage": "n",
    "app size":"B"
}


@dataclass
class Metric:

    name: str
    value: Any
    epoch: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Metric":
        return cls(data["name"], data["value"], data["epoch"])

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "value": self.value, "epoch": self.epoch}

    def keys(self) -> list[str]:
        return self.to_dict().keys()

    def to_bytes(self) -> bytes:
        return pickle.dumps(self.to_dict())

    @classmethod
    def from_bytes(cls, data: bytes) -> "Metric":
        return cls.from_dict(pickle.loads(data))

    def __str__(self) -> str:
        return f"{self.name}: {self.value} (epoch {self.epoch})"

    def __repr__(self) -> str:
        return str(self)


class MetricList(list):

    def __init__(self, metrics: list[Metric] | None = None):
        if metrics is None:
            metrics = []
        super().__init__(metrics)
        if len(set([metric.name for metric in self])) != len(self):
            raise ValueError("All metrics should have unique names")

    def get(self, name: str) -> Metric:
        for metric in self:
            if metric.name == name:
                return metric
        raise ValueError(f"Metric {name} not found")

    def __str__(self) -> str:
        return "\n".join([str(metric) for metric in self])

    def __repr__(self) -> str:
        return str(self)
