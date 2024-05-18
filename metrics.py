from dataclasses import dataclass


@dataclass
class Metric:
    name: str
    value: float
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

    def __str__(self):
        return f"{self.name}: {self.value} (epoch {self.epoch})"

    def __repr__(self):
        return str(self)
