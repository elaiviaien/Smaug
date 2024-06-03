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
    """A metric with a name, value, and epoch."""

    name: str
    value: Any
    epoch: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Metric":
        """Return a Metric object from the given dictionary."""
        return cls(data["name"], data["value"], data["epoch"])

    def to_dict(self) -> dict[str, Any]:
        """Return the metric as a dictionary."""
        return {"name": self.name, "value": self.value, "epoch": self.epoch}

    def keys(self) -> list[str]:
        """Return the keys of the metric."""
        return self.to_dict().keys()

    def to_bytes(self) -> bytes:
        """Return the metric as bytes."""
        return pickle.dumps(self.to_dict())

    @classmethod
    def from_bytes(cls, data: bytes) -> "Metric":
        """Return a Metric object from the given bytes."""
        return cls.from_dict(pickle.loads(data))

    def __str__(self) -> str:
        return f"{self.name}: {self.value} (epoch {self.epoch})"

    def __repr__(self) -> str:
        return str(self)


class MetricList(list):
    """A list of metrics."""

    def __init__(self, metrics: list[Metric] | None = None):
        if metrics is None:
            metrics = []
        super().__init__(metrics)
        if len(set([metric.name for metric in self])) != len(self):
            raise ValueError("All metrics should have unique names")

    def get(self, name: str) -> Metric:
        """Return the metric with the specified name."""
        for metric in self:
            if metric.name == name:
                return metric
        raise ValueError(f"Metric {name} not found")

    def __str__(self) -> str:
        return "\n".join([str(metric) for metric in self])

    def __repr__(self) -> str:
        return str(self)
