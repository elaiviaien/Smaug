""" Run a script and monitor it. """
import logging
import os
import subprocess
from threading import Thread
from typing import NoReturn

from .builder import Builder
from .monitoring import TestedAppMonitor
from .logger import setup_logger, LoggerWriter, get_file_handler

logger = setup_logger("smaug")


class ScriptRunner:
    """Run a script and monitor it."""

    def __init__(self, main_file: str, use_buffer: bool):
        logger.info(
            "Initializing ScriptRunner with main_file: %s",
            main_file,
        )
        self.main_file = main_file
        self.use_buffer = use_buffer
        self.filename = os.path.basename(self.main_file)
        self.builder = Builder()
        self.monitor = TestedAppMonitor(self.builder.build_dir)
        self.builder.build(self.dir_path)
        self.processes = []
        logger.info("Initialized ScriptRunner")

    @property
    def dir_path(self) -> str:
        """Return the directory path of the main file."""
        if os.path.isabs(self.main_file):
            return os.path.dirname(self.main_file)
        return os.path.dirname(os.path.abspath(self.main_file))

    @property
    def main_file(self) -> str:
        """Return the main file path."""
        return self._main_file

    @main_file.setter
    def main_file(self, path: str) -> None | NoReturn:
        if os.path.isabs(path):
            self._main_file = path
        else:
            self._main_file = os.path.abspath(path)
        if not os.path.exists(self._main_file):
            raise FileNotFoundError(f"Script {self._main_file} does not exist")
    def _log_output(self, process) -> None:
        """Log the output of the script."""
        test_logger = setup_logger(f"smaug_test_{process.pid}", stream_handler=False)
        while process.poll() is None:
            output = process.stdout.readline().decode().strip()
            while output:
                test_logger.info(output)
                output = process.stdout.readline().decode().strip()

            error = process.stderr.readline().decode().strip()
            while error:
                test_logger.error(error)
                error = process.stderr.readline().decode().strip()

    def run_script_in_venv(self, num: int) -> None:
        """Run the script in a virtual environment."""
        logger.info("Starting to run script in virtual environment %s times", num)
        for i in range(num):
            python_exe = f"{self.builder.build_dir}/venv/bin/python"
            script_path = os.path.join(self.builder.build_dir, self.filename)
            if self.use_buffer:
                cmd_args = [python_exe, script_path]
            else:
                cmd_args = [python_exe, "-u", script_path]
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(process)
            Thread(target=self._log_output, args=(process,), daemon=True).start()
        logger.info("Finished running script in virtual environment")

    def run(self, num: int = 1) -> None:
        """Run the script."""
        logger.info("Starting to run the script %s times", num)
        self.run_script_in_venv(num)
        logger.info("Finished running the script")

    def stop(self) -> None:
        """Stop the script execution and monitoring."""
        logger.info("Stopping the script execution and monitoring")
        for process in self.processes:
            process.terminate()
        self.monitor.stop()
        logger.info("Stopped the script execution and monitoring")
