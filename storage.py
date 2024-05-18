import csv
import tempfile

from metrics import Metric


class TempStorage:
    def __init__(self):
        self._file = tempfile.NamedTemporaryFile(mode='w+', delete=True, prefix='smaug_', suffix='.csv', newline='')
        self._writer = None

    def save_record(self, data: Metric):
        if not self._writer:
            self._writer = csv.DictWriter(self._file, fieldnames=data.keys())
            self._writer.writeheader()
        self._writer.writerow(data.to_dict())
        self._file.flush()

    def get_record(self, epoch):
        with open(self._file.name, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row.get('epoch')) == epoch:
                    return Metric.from_dict(row)
        return None

    def get_last_records(self, tail=0) -> list[Metric]:
        with open(self._file.name, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            return [Metric.from_dict(row) for row in data[-tail:]]

    def delete_record(self, epoch):
        with open(self._file.name, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        with open(self._file.name, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                if int(row.get('epoch')) != epoch:
                    writer.writerow(row)

    def __del__(self):
        self._file.close()
