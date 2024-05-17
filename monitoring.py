import subprocess
import time
import os
from collections import deque
import threading
import fnmatch


class Monitor:
    def __init__(self):
        self.start_time = time.time()
        self.stop_flag = False
        self.time_point = 0.01  # 0.01 seconds
        store_time_points = 6000  # 60 seconds
        self.cpu_usage_values = deque(maxlen=store_time_points)
        self.cpu_usage_thread = threading.Thread(target=self._calculate_cpu_usage)
        self.cpu_usage_thread.daemon = True
        self.cpu_usage_thread.start()

    def _calculate_cpu_usage(self):

        while not self.stop_flag:
            cpu_times1 = self._get_cpu_times()
            time.sleep(self.time_point)
            cpu_times2 = self._get_cpu_times()
            cpu_delta = [t2 - t1 for t1, t2 in zip(cpu_times1, cpu_times2)]
            total_time = sum(cpu_delta)
            idle_time_arr_n = 3
            idle_time = cpu_delta[idle_time_arr_n]
            cpu_usage = (total_time - idle_time) / total_time * 100
            self.cpu_usage_values.append(cpu_usage)

    def _get_cpu_times(self):
        with open('/proc/stat', 'r') as file:
            cpu_line = file.readline()
        return list(map(int, cpu_line.split()[1:]))

    def get_cpu_usage(self):
        return sum(self.cpu_usage_values) / len(self.cpu_usage_values)

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

    def stop(self):
        self.stop_flag = True
        timeout = 2
        self.cpu_usage_thread.join(timeout)

    def is_thread_alive(self):
        return self.cpu_usage_thread.is_alive()

    def __del__(self):
        self.stop()


class TestedAppMonitor(Monitor):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def get_app_size(self):
        return os.path.getsize(self.path)

    def get_tested_app_thread_usage(self):
        service_threads = [self.cpu_usage_thread]
        service_threads_num = len(service_threads)
        return self.get_current_thread_usage() - service_threads_num

    def get_line_count(self, file_type='py'):
        line_count = 0
        for root, dirs, files in os.walk(self.path):
            for file in fnmatch.filter(files, f'*.{file_type}'):
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                    line_count += len(lines)
        return line_count
