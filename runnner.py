import os
import subprocess

from builder import Builder
from monitoring import TestedAppMonitor


class ScriptRunner:
    def __init__(self, main_file):
        self.main_file = main_file
        self.filename = os.path.basename(self.main_file)
        self.builder = Builder()
        self.build_dir = self.builder.build_dir
        self.monitor = TestedAppMonitor(self.build_dir)
        self.builder.build(self.dir_path)

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

    def run_script_in_venv(self):
        python_exe = f"{self.build_dir}/venv/bin/python"
        script_path = os.path.join(self.build_dir, self.filename)
        process = subprocess.Popen([python_exe, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print("Output:", stdout.decode())
        if stderr:
            print("Error:", stderr.decode())

    def run(self):
        self.run_script_in_venv()

