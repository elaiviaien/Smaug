"""Storage classes for metrics."""

import pickle
import tempfile
from pickle import UnpicklingError
from typing import Any

from .metrics import Metric
from .logger import setup_logger

logger = setup_logger("smaug")


class TempStorage:
    """A temporary storage for metrics."""

    def __init__(self, name: str = None, max_size: int = 1000):
        prefix = "smaug_" if not name else f"smaug_{name}_"
        self._file = tempfile.NamedTemporaryFile(
            mode="wb+", delete=True, prefix=prefix, suffix=".pkl"
        )
        self.max_size = max_size * 1024  # in kilobytes

    def save_record(self, data: Metric) -> None:
        """Save a record to the storage."""
        pickle.dump(data.to_bytes(), self._file)
        self._file.flush()

    def get_record(self, epoch: int) -> Metric | None:
        """Get a record from the storage."""
        self._file.seek(0)
        while True:
            try:
                record = pickle.load(self._file)
                if record.get("epoch") == epoch:
                    return Metric.from_dict(record)
            except EOFError:
                break
        return None

    def get_last_records(self, tail: int = 0) -> list[Metric]:
        """Get the last N records from the storage."""
        self._file.seek(0)
        records = []
        while True:
            try:
                record = pickle.load(self._file)
                records.append(Metric.from_bytes(record))
            except (EOFError, UnpicklingError):
                break
        return records[-tail:]

    def delete_record(self, epoch: int) -> None:
        """Delete a record from the storage."""
        self._file.seek(0)
        records = []
        while True:
            try:
                record = pickle.load(self._file)
                if record.get("epoch") != epoch:
                    records.append(record)
            except EOFError:
                break
        self._file.seek(0)
        self._file.truncate()
        for record in records:
            pickle.dump(record, self._file)
        self._file.flush()

    def __del__(self):
        self._file.close()


class BatchTempStorage(dict):
    """A batch temporary storage for metrics."""

    def __missing__(self, key: Any) -> TempStorage:
        self[key] = TempStorage(key)
        return self[key]
