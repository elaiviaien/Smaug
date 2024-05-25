import os
import subprocess

from builder import Builder
from monitoring import TestedAppMonitor
import signal


class ScriptRunner:
    def __init__(self, main_file):
        self.main_file = main_file
        self.filename = os.path.basename(self.main_file)
        self.builder = Builder()
        self.build_dir = self.builder.build_dir
        self.monitor = TestedAppMonitor(self.build_dir)
        self.builder.build(self.dir_path)
        self.processes = []
        signal.signal(signal.SIGINT, self.signal_handler)

    @property
    def dir_path(self):
        if os.path.isabs(self.main_file):
            return os.path.dirname(self.main_file)
        else:
            return os.path.dirname(os.path.abspath(self.main_file))

    @property
    def main_file(self):
        return self._main_file

    @main_file.setter
    def main_file(self, path):
        if os.path.isabs(path):
            self._main_file = path
        else:
            self._main_file = os.path.abspath(path)
        if not os.path.exists(self._main_file):
            raise FileNotFoundError(f"Script {self._main_file} does not exist")

    def run_script_in_venv(self, num):
        for _ in range(num):
            python_exe = f"{self.build_dir}/venv/bin/python"
            script_path = os.path.join(self.build_dir, self.filename)
            process = subprocess.Popen([python_exe, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)

    def signal_handler(self, signal, frame):
        for process in self.processes:
            process.terminate()
        print('Script execution was stopped')
        self.monitor.stop()
        print('Monitoring was stopped')

    def run(self, num=1):
        self.run_script_in_venv(num)
