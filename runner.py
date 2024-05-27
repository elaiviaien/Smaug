""" Run a script and monitor it. """
import os
import subprocess

from builder import Builder
from monitoring import TestedAppMonitor


class ScriptRunner:
    """Run a script and monitor it."""

    def __init__(self, main_file, log_file):
        self.main_file = main_file
        self.log_file = log_file
        self.filename = os.path.basename(self.main_file)
        self.builder = Builder()
        self.monitor = TestedAppMonitor(self.builder.build_dir)
        self.builder.build(self.dir_path)
        self.processes = []

    @property
    def dir_path(self):
        """Return the directory path of the main file."""
        if os.path.isabs(self.main_file):
            return os.path.dirname(self.main_file)
        return os.path.dirname(os.path.abspath(self.main_file))

    @property
    def main_file(self):
        """Return the main file path."""
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
        """Run the script in a virtual environment."""
        for _ in range(num):
            python_exe = f"{self.builder.build_dir}/venv/bin/python"
            script_path = os.path.join(self.builder.build_dir, self.filename)
            process = subprocess.Popen(
                [python_exe, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.processes.append(process)

    def run(self, num=1):
        """Run the script."""
        self.run_script_in_venv(num)

    def stop(self):
        """Stop the script execution and monitoring."""
        for process in self.processes:
            process.terminate()
        self.monitor.stop()
