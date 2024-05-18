import csv
import tempfile


class TempStorage:
    def __init__(self):
        self._file = tempfile.NamedTemporaryFile(mode='w+', delete=True, prefix='smaug_', suffix='.csv', newline='')
        self._writer = None

    def save_record(self, data: dict, timestamp):
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        if not self._writer:
            self._writer = csv.DictWriter(self._file, fieldnames=['timestamp', *data.keys()])
            self._writer.writeheader()
        self._writer.writerow({'timestamp': timestamp_str, **data})
        self._file.flush()

    def get_record(self, timestamp):
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        with open(self._file.name, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('timestamp') == timestamp_str:
                    return row
        return None

    def get_last_records(self, tail=0):
        with open(self._file.name, 'r') as f:
            data = list(csv.DictReader(f))
            return data[-tail:]

    def delete_record(self, timestamp):
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        data = self.get_last_records()
        data = [row for row in data if row.get('timestamp') != timestamp_str]
        with open(self._file.name, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', *data[0].keys()])
            writer.writeheader()
            writer.writerows(data)

    def __del__(self):
        self._file.close()
