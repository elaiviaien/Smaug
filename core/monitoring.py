
import os
import subprocess
import threading
import time
from abc import abstractmethod, ABC
from types import TracebackType
from typing import Type, Optional

from .metrics import Metric, MetricList
from .storage import BatchTempStorage
from .logger import setup_logger

logger = setup_logger(f"smaug_{os.getpid()}")


class StaticMonitor(ABC):

    def __init__(self):
        logger.info("Initializing StaticMonitor for %s", self.__class__.__name__)
        self.start_time = time.time()
        self.first_records = self.record_stats()
        logger.info("Initialized StaticMonitor for %s", self.__class__.__name__)

    @property
    def last_records(self) -> MetricList[Metric]:
        return self.record_stats()

    @abstractmethod
    def record_stats(self) -> MetricList[Metric]:
        pass

    @abstractmethod
    def get_diff(self) -> dict | float | int:
        pass


class LiveMonitor(ABC):

    def __init__(self):
        logger.info("Initializing LiveMonitor for %s", self.__class__.__name__)
        self.stop_flag = None
        self.time_point = 0.1  # 0.1 seconds
        self.temp_storages = BatchTempStorage()
        self.collect_data_thread = threading.Thread(
            target=self._save_stats_periodically
        )
        self.collect_data_thread.start()
        logger.info("Initialized LiveMonitor for %s", self.__class__.__name__)

    def _save_stats_periodically(self) -> None:
        logger.info("Starting the monitoring thread for %s", self.__class__.__name__)
        while not self.stop_flag:
            records = self.record_stats()
            for record in records:
                self.temp_storages[record.name].save_record(record)
                time.sleep(self.time_point)

    @abstractmethod
    def record_stats(self) -> list[Metric]:
        pass

    @abstractmethod
    def get_average(self) -> float:
        pass

    def stop(self) -> None:
        self.stop_flag = True
        logger.info("Stopping the monitoring thread for %s", self.__class__.__name__)

    def is_thread_alive(self) -> bool:
        return self.collect_data_thread.is_alive()


class CPUMonitor(LiveMonitor):

    def record_stats(self):
        cpu_times1 = self._get_cpu_times()
        time.sleep(self.time_point)
        cpu_times2 = self._get_cpu_times()
        cpu_delta = [t2 - t1 for t1, t2 in zip(cpu_times1, cpu_times2)]
        total_time = sum(cpu_delta)
        idle_time_list_n = 3
        idle_time = cpu_delta[idle_time_list_n]
        cpu_usage = (
            (total_time - idle_time) / total_time * 100 if total_time != 0 else 0
        )
        cpu_usage = round(cpu_usage, 3)
        return MetricList([Metric("cpu usage", cpu_usage, int(time.time()))])

    def _get_cpu_times(self) -> list[int]:
        with open("/proc/stat", "r", encoding="utf-8") as file:
            cpu_line = file.readline()
        return list(map(int, cpu_line.split()[1:]))

    def get_average(self):
        records = self.temp_storages["cpu usage"].get_last_records()
        values = [float(record.value) for record in records]
        return round(sum(values) / len(values),3) if values else 0


class MemoryMonitor(LiveMonitor):

    def get_virtual_memory_usage(self) -> float:
        with open("/proc/meminfo", "r", encoding="utf-8") as mem:
            lines = mem.readlines()

        meminfo = {
            line.split(":")[0]: int(line.split(":")[1].strip().split(" ")[0]) for line in lines
        }
        total_memory = meminfo["MemTotal"]
        free_memory = meminfo["MemFree"]
        buffers = meminfo["Buffers"]
        cached = meminfo["Cached"]
        used_memory = total_memory - free_memory - buffers - cached
        memory_usage = (
            round(used_memory / total_memory * 100, 4) if total_memory != 0 else 0
        )
        return memory_usage

    def get_swap_memory_usage(self) -> float:
        with open("/proc/meminfo", "r", encoding="utf-8") as mem:
            lines = mem.readlines()

        meminfo = {
            line.split(":")[0]: int(line.split(":")[1].strip().split(" ")[0]) for line in lines
        }
        total_swap = meminfo["SwapTotal"]
        free_swap = meminfo["SwapFree"]
        used_swap = total_swap - free_swap
        swap_usage = round(used_swap / total_swap * 100, 4) if total_swap != 0 else 0
        return swap_usage

    def record_stats(self):
        virtual_memory_usage = round(self.get_virtual_memory_usage(), 3)
        swap_memory_usage = round(self.get_swap_memory_usage(), 3)
        return MetricList(
            [
                Metric("memory usage", virtual_memory_usage, int(time.time())),
                Metric("swap memory usage", swap_memory_usage, int(time.time())),
            ]
        )

    def _get_memory_usage_avg(self) -> float:
        records = self.temp_storages["memory usage"].get_last_records()
        values = [float(record.value) for record in records]
        return round(sum(values) / len(values),3) if values else 0

    def _get_swap_memory_usage_avg(self) -> float:
        records = self.temp_storages["swap memory usage"].get_last_records()
        values = [float(record.value) for record in records]
        return round(sum(values) / len(values),3) if values else 0

    def get_average(self):
        return {
            "memory usage": self._get_memory_usage_avg(),
            "swap memory usage": self._get_swap_memory_usage_avg(),
        }


class DiskMonitor(StaticMonitor):

    def get_disk_usage(self, partition: str) -> float:
        usage = os.statvfs(partition)
        total = usage.f_blocks * usage.f_frsize
        used = (usage.f_blocks - usage.f_bfree) * usage.f_frsize
        percent = (used / total) * 100
        return percent

    def record_stats(self):
        disk_usage = round(self.get_disk_usage("/"), 3)
        return MetricList([Metric("disk usage", disk_usage, int(time.time()))])

    def get_diff(self):
        return round(
            self.last_records.get("disk usage").value
            - self.first_records.get("disk usage").value,
            3
        )


class ProcessMonitor(StaticMonitor):

    def get_execution_time(self) -> float:
        return int(time.time() - self.start_time)

    def get_process_info(self, pid: int = os.getpid()) -> str:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "comm="], stdout=subprocess.PIPE, check=True
        )
        return result.stdout.decode().strip()

    def get_total_thread_usage(self) -> int:
        result = subprocess.run(["ps", "-eLF"], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        header_line_num = 1
        num_threads = len(output.strip().split("\n")) - header_line_num
        return num_threads

    def record_stats(self):
        process_info = self.get_process_info()
        total_thread_usage = self.get_total_thread_usage()
        return MetricList(
            [
                Metric("process info", process_info, int(time.time())),
                Metric("total thread usage", total_thread_usage, int(time.time())),
            ]
        )

    def _get_total_thread_usage_diff(self) -> int:
        return (
            self.last_records.get("total thread usage").value
            - self.first_records.get("total thread usage").value
        )

    def _get_current_thread_usage_diff(self) -> int:
        return (
            self.get_total_thread_usage()
            - self.first_records.get("total thread usage").value
        )

    def get_diff(self):
        return {
            "total thread usage diff": self._get_total_thread_usage_diff(),
            "current thread usage diff": self._get_current_thread_usage_diff(),
        }


class CombinedMonitor:

    def __init__(self):
        logger.info("Initializing CombinedMonitor")
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        self.disk_monitor = DiskMonitor()
        self.process_monitor = ProcessMonitor()
        logger.info("Initialized CombinedMonitor")

    def stop(self):
        logger.info("Stopping CombinedMonitor")
        self.cpu_monitor.stop()
        self.memory_monitor.stop()
        logger.info("Stopped CombinedMonitor")

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.stop()
        logger.info("Stopped the monitoring")


class TestedAppMonitor(CombinedMonitor):

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__()

    def get_app_size(self) -> int:
        return os.path.getsize(self.path)
