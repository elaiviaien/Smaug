"""This module contains classes for metrics and metric lists."""
from dataclasses import dataclass
from typing import Any
import pickle

MAX_VALUES = {
    "cpu_usage": 100,
    "memory_usage": 100,
    "swap_memory_usage": 100,
    "disk_usage": 100,
}
QUANTITIES = {
    "cpu_usage": "%",
    "memory_usage": "%",
    "swap_memory_usage": "%",
    "disk_usage": "%",
    "execution_time": "s",
    "total_thread_usage": "n",
}


@dataclass
class Metric:
    """A metric with a name, value, and epoch."""
    name: str
    value: Any
    epoch: int

    @classmethod
    def from_dict(cls, data):
        """Return a Metric object from the given dictionary."""
        return cls(data["name"], data["value"], data["epoch"])

    def to_dict(self):
        """Return the metric as a dictionary."""
        return {"name": self.name, "value": self.value, "epoch": self.epoch}

    def keys(self):
        """Return the keys of the metric."""
        return self.to_dict().keys()

    def to_bytes(self):
        """Return the metric as bytes."""
        return pickle.dumps(self.to_dict())

    @classmethod
    def from_bytes(cls, data):
        """Return a Metric object from the given bytes."""
        return cls.from_dict(pickle.loads(data))

    def __str__(self):
        return f"{self.name}: {self.value} (epoch {self.epoch})"

    def __repr__(self):
        return str(self)


class MetricList(list):
    """A list of metrics."""
    def __init__(self, metrics=None):
        if metrics is None:
            metrics = []
        super().__init__(metrics)
        if len(set([metric.name for metric in self])) != len(self):
            raise ValueError("All metrics should have unique names")

    def get(self, name) -> Metric:
        """Return the metric with the specified name."""
        for metric in self:
            if metric.name == name:
                return metric
        raise ValueError(f"Metric {name} not found")

    def __str__(self):
        return "\n".join([str(metric) for metric in self])

    def __repr__(self):
        return str(self)
