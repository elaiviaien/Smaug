from dataclasses import dataclass
from typing import Any
import pickle


@dataclass
class Metric:
    name: str
    value: Any
    epoch: int

    @classmethod
    def from_dict(cls, data):
        return cls(data['name'], data['value'], data['epoch'])

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "epoch": self.epoch
        }

    def keys(self):
        return self.to_dict().keys()

    def to_bytes(self):
        return pickle.dumps(self.to_dict())

    @classmethod
    def from_bytes(cls, data):
        return cls.from_dict(pickle.loads(data))

    def __str__(self):
        return f"{self.name}: {self.value} (epoch {self.epoch})"

    def __repr__(self):
        return str(self)
