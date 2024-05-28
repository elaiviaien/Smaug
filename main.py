""" The main application that runs the script and collects the metrics. """

import argparse
import logging
import os
import signal
import sys
import threading
import time

from core.logger import setup_logger, LoggerWriter
from core.runner import ScriptRunner
from core.visual import MetricsDisplay

logger = setup_logger("smaug")
sys.stderr = LoggerWriter(logger, logging.ERROR)


class App:
    """The main application class that runs the script and collects the metrics."""

    def __init__(self, script_file: str, num: int, use_buffer: bool):
        os.makedirs("logs", exist_ok=True)

        self.runner = ScriptRunner(script_file, use_buffer)
        self.runner.run(num)
        self.monitor = self.runner.monitor
        self.display = MetricsDisplay()

        self.stop_flag = False
        self.collect_data_thread = threading.Thread(target=self._collect_data)
        self.collect_data_thread.start()
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame) -> None:
        """Handle the SIGINT signal to stop the application."""
        self.stop_flag = True
        self.runner.stop()

    def _collect_data(self) -> None:
        collect_interval = 0.3  # 0.3 seconds
        while not self.stop_flag:
            metrics = (
                self.monitor.cpu_monitor.record_stats()
                + self.monitor.memory_monitor.record_stats()
                + self.monitor.disk_monitor.record_stats()
            )
            self.display.update(metrics)
            time.sleep(collect_interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the application with a specified main file."
    )
    parser.add_argument("-mf","--main-file",
                        type=str, help="The main file to run (path)")
    parser.add_argument(
        "-n","--num",
        type=int,
        default=1,
        help="The number of times to run your script. Default is 1",
    )
    parser.add_argument(
        "-ub", "--use-buffer",
        type=lambda x: (str(x).lower() in ['true', '1', 'yes']),
        default=True,
        help="Use buffer for the script output. Default is True"
    )

    args = parser.parse_args()
    if args.main_file:
        num = args.num
        main_file = args.main_file
        use_buffer = args.use_buffer
        app = App(main_file, num, use_buffer)
