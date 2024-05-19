import os
import subprocess
import threading
import time
from abc import abstractmethod, ABC

from metrics import Metric
from storage import BatchTempStorage


class StaticMonitor(ABC):
    def __init__(self):
        self.start_time = time.time()
        self.first_records = self.record_stats()

    @property
    def last_records(self):
        return self.record_stats()

    @abstractmethod
    def record_stats(self) -> list[Metric]:
        pass


class LiveMonitor(ABC):
    def __init__(self):
        self.stop_flag = None
        self.time_point = 0.1  # 0.1 seconds
        self.temp_storages = BatchTempStorage()
        self.collect_data_thread = threading.Thread(target=self._save_stats_periodically)
        self.collect_data_thread.start()
        super().__init__()

    def _save_stats_periodically(self):
        while not self.stop_flag:
            records = self.record_stats()
            for record in records:
                self.temp_storages[record.name].save_record(record)
                time.sleep(self.time_point)

    @abstractmethod
    def record_stats(self) -> list[Metric]:
        pass

    def stop(self):
        self.stop_flag = True

    def is_thread_alive(self):
        return self.collect_data_thread.is_alive()


class CPUMonitor(LiveMonitor):
    def record_stats(self):
        cpu_times1 = self._get_cpu_times()
        time.sleep(self.time_point)
        cpu_times2 = self._get_cpu_times()
        cpu_delta = [t2 - t1 for t1, t2 in zip(cpu_times1, cpu_times2)]
        total_time = sum(cpu_delta)
        idle_time_arr_n = 3
        idle_time = cpu_delta[idle_time_arr_n]
        cpu_usage = (total_time - idle_time) / total_time * 100 if total_time != 0 else 0
        return [Metric('cpu_usage', cpu_usage, int(time.time()))]

    def _get_cpu_times(self):
        with open('/proc/stat', 'r') as file:
            cpu_line = file.readline()
        return list(map(int, cpu_line.split()[1:]))

    def get_cpu_usage(self):
        records = self.temp_storages['cpu_usage'].get_last_records()
        values = [float(record.value) for record in records]
        return sum(values) / len(values) if values else 0


class MemoryMonitor(LiveMonitor):
    def get_virtual_memory_usage(self):
        with open('/proc/meminfo', 'r') as mem:
            lines = mem.readlines()

        meminfo = {l.split(':')[0]: int(l.split(':')[1].strip().split(' ')[0]) for l in lines}
        total_memory = meminfo['MemTotal']
        free_memory = meminfo['MemFree']
        buffers = meminfo['Buffers']
        cached = meminfo['Cached']
        used_memory = total_memory - free_memory - buffers - cached
        memory_usage = f'{used_memory}/{total_memory} kB ({used_memory / total_memory * 100:.2f}%)'
        return memory_usage

    def get_swap_memory_usage(self):
        with open('/proc/meminfo', 'r') as mem:
            lines = mem.readlines()

        meminfo = {l.split(':')[0]: int(l.split(':')[1].strip().split(' ')[0]) for l in lines}
        total_swap = meminfo['SwapTotal']
        free_swap = meminfo['SwapFree']
        used_swap = total_swap - free_swap
        swap_usage = f'{used_swap}/{total_swap} kB ({used_swap / total_swap * 100:.2f}%)' if total_swap != 0 else 'No swap space'
        return swap_usage

    def record_stats(self):
        virtual_memory_usage = self.get_virtual_memory_usage()
        swap_memory_usage = self.get_swap_memory_usage()
        return [Metric('memory_usage', virtual_memory_usage, int(time.time())),
                Metric('swap_memory_usage', swap_memory_usage, int(time.time()))]


class DiskMonitor(StaticMonitor):
    def get_disk_usage(self, partition):
        usage = os.statvfs(partition)
        total = usage.f_blocks * usage.f_frsize
        free = usage.f_bfree * usage.f_frsize
        used = (usage.f_blocks - usage.f_bfree) * usage.f_frsize
        percent = (used / total) * 100
        return {
            'partition': partition,
            'total': total,
            'used': used,
            'free': free,
            'percent': percent,
        }

    def record_stats(self):
        disk_usage = self.get_disk_usage('/')
        return [Metric('disk_usage', disk_usage, int(time.time()))]


class ProcessMonitor(StaticMonitor):
    def get_execution_time(self):
        return time.time() - self.start_time

    def get_process_info(self, pid=os.getpid()):
        result = subprocess.run(['ps', '-p', str(pid), '-o', 'comm='], stdout=subprocess.PIPE)
        return result.stdout.decode().strip()

    def get_total_thread_usage(self):
        result = subprocess.run(['ps', '-eLF'], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        header_line_num = 1
        num_threads = len(output.strip().split('\n')) - header_line_num
        return num_threads

    def get_current_thread_usage(self):
        return threading.active_count()

    def record_stats(self):
        process_info = self.get_process_info()
        total_thread_usage = self.get_total_thread_usage()
        current_thread_usage = self.get_current_thread_usage()
        return [Metric('process_info', process_info, int(time.time())),
                Metric('total_thread_usage', total_thread_usage, int(time.time())),
                Metric('current_thread_usage', current_thread_usage, int(time.time())),
                Metric('execution_time', self.get_execution_time(), int(time.time()))]


class CombinedMonitor:
    def __init__(self):
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        self.disk_monitor = DiskMonitor()
        self.process_monitor = ProcessMonitor()

    def stop(self):
        self.cpu_monitor.stop()
        self.memory_monitor.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class TestedAppMonitor(CombinedMonitor):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def get_app_size(self):
        return os.path.getsize(self.path)
