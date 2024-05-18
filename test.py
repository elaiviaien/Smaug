import time
from metrics import Metric
from storage import TempStorage


def test_temp_storage():
    # Create a TempStorage object
    storage = TempStorage()

    # Create some Metric objects
    metric1 = Metric('cpu_usage', 23.5, int(time.time()))
    metric2 = Metric('memory_usage', 4096, int(time.time()))

    # Save the Metric objects to the TempStorage
    storage.save_record(metric1)
    storage.save_record(metric2)

    # Get a record from the TempStorage
    record = storage.get_record(metric1.epoch)
    print(record)

    # Get the last records from the TempStorage
    last_records = storage.get_last_records(2)
    print(last_records)

    # Delete a record from the TempStorage
    storage.delete_record(metric1.epoch)

    # Get the last records from the TempStorage again to verify the deletion
    last_records = storage.get_last_records(2)
    print(last_records)


test_temp_storage()
