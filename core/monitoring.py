"""This module contains classes for monitoring the CPU, memory, disk, and process."""

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

logger = setup_logger("smaug")


class StaticMonitor(ABC):
    """Monitor the metrics statically."""

    def __init__(self):
        logger.info("Initializing StaticMonitor for %s", self.__class__.__name__)
        self.start_time = time.time()
        self.first_records = self.record_stats()
        logger.info("Initialized StaticMonitor for %s", self.__class__.__name__)

    @property
    def last_records(self) -> MetricList[Metric]:
        """Return the last records."""
        return self.record_stats()

    @abstractmethod
    def record_stats(self) -> MetricList[Metric]:
        """Record the statistics."""

    @abstractmethod
    def get_diff(self) -> dict | float | int:
        """Return the difference between the first and last records."""


class LiveMonitor(ABC):
    """Monitor the metrics live."""

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
        """Record the statistics."""

    @abstractmethod
    def get_average(self) -> float:
        """Return the average value of the metric."""

    def stop(self) -> None:
        """Stop the monitoring."""
        self.stop_flag = True
        logger.info("Stopping the monitoring thread for %s", self.__class__.__name__)

    def is_thread_alive(self) -> bool:
        """Return True if the 'collect data' thread is alive, False otherwise."""
        return self.collect_data_thread.is_alive()


class CPUMonitor(LiveMonitor):
    """Monitor the CPU."""

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
        return MetricList([Metric("cpu_usage", cpu_usage, int(time.time()))])

    def _get_cpu_times(self) -> list[int]:
        """Return the CPU times."""
        with open("/proc/stat", "r", encoding="utf-8") as file:
            cpu_line = file.readline()
        return list(map(int, cpu_line.split()[1:]))

    def get_average(self):
        records = self.temp_storages["cpu_usage"].get_last_records()
        values = [float(record.value) for record in records]
        return sum(values) / len(values) if values else 0


class MemoryMonitor(LiveMonitor):
    """Monitor the memory."""

    def get_virtual_memory_usage(self) -> float:
        """Return the virtual memory usage."""
        with open("/proc/meminfo", "r", encoding="utf-8") as mem:
            lines = mem.readlines()

        meminfo = {
            l.split(":")[0]: int(l.split(":")[1].strip().split(" ")[0]) for l in lines
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
        """Return the swap memory usage."""
        with open("/proc/meminfo", "r", encoding="utf-8") as mem:
            lines = mem.readlines()

        meminfo = {
            l.split(":")[0]: int(l.split(":")[1].strip().split(" ")[0]) for l in lines
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
                Metric("memory_usage", virtual_memory_usage, int(time.time())),
                Metric("swap_memory_usage", swap_memory_usage, int(time.time())),
            ]
        )

    def _get_memory_usage_avg(self) -> float:
        """Return the average memory usage."""
        records = self.temp_storages["memory_usage"].get_last_records()
        values = [float(record.value) for record in records]
        return sum(values) / len(values) if values else 0

    def _get_swap_memory_usage_avg(self) -> float:
        """Return the average swap memory usage."""
        records = self.temp_storages["swap_memory_usage"].get_last_records()
        values = [float(record.value) for record in records]
        return sum(values) / len(values) if values else 0

    def get_average(self):
        return {
            "memory_usage": self._get_memory_usage_avg(),
            "swap_memory_usage": self._get_swap_memory_usage_avg(),
        }


class DiskMonitor(StaticMonitor):
    """Monitor the disk."""

    def get_disk_usage(self, partition: str) -> float:
        """Return the disk usage."""
        usage = os.statvfs(partition)
        total = usage.f_blocks * usage.f_frsize
        used = (usage.f_blocks - usage.f_bfree) * usage.f_frsize
        percent = (used / total) * 100
        return percent

    def record_stats(self):
        disk_usage = round(self.get_disk_usage("/"), 3)
        return MetricList([Metric("disk_usage", disk_usage, int(time.time()))])

    def get_diff(self):
        return (
            self.last_records.get("disk_usage").value["used"]
            - self.first_records.get("disk_usage").value["used"]
        )


class ProcessMonitor(StaticMonitor):
    """Monitor the process."""

    def get_execution_time(self) -> float:
        """Return the execution time."""
        return time.time() - self.start_time

    def get_process_info(self, pid: int = os.getpid()) -> str:
        """Return the process information."""
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "comm="], stdout=subprocess.PIPE, check=True
        )
        return result.stdout.decode().strip()

    def get_total_thread_usage(self) -> int:
        """Return the total number of threads."""
        result = subprocess.run(["ps", "-eLF"], stdout=subprocess.PIPE, check=True)
        output = result.stdout.decode()
        header_line_num = 1
        num_threads = len(output.strip().split("\n")) - header_line_num
        return num_threads

    def record_stats(self):
        process_info = self.get_process_info()
        total_thread_usage = self.get_total_thread_usage()
        return MetricList(
            [
                Metric("process_info", process_info, int(time.time())),
                Metric("total_thread_usage", total_thread_usage, int(time.time())),
            ]
        )

    def _get_total_thread_usage_diff(self) -> int:
        return (
            self.last_records.get("total_thread_usage").value
            - self.first_records.get("total_thread_usage").value
        )

    def _get_current_thread_usage_diff(self) -> int:
        return (
            self.get_total_thread_usage()
            - self.first_records.get("total_thread_usage").value
        )

    def get_diff(self):
        return {
            "total_thread_usage_diff": self._get_total_thread_usage_diff(),
            "current_thread_usage_diff": self._get_current_thread_usage_diff(),
        }


class CombinedMonitor:
    """Monitor the CPU, memory, disk, and process."""

    def __init__(self):
        logger.info("Initializing CombinedMonitor")
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        self.disk_monitor = DiskMonitor()
        self.process_monitor = ProcessMonitor()
        logger.info("Initialized CombinedMonitor")

    def stop(self):
        """Stop the monitoring."""
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
    """Monitor the tested application."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__()

    def get_app_size(self) -> int:
        """Return the size of the tested application."""
        return os.path.getsize(self.path)
