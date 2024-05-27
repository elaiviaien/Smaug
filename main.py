""" The main application that runs the script and collects the metrics. """

import signal
import threading
import time
import argparse

from runner import ScriptRunner
from visual import MetricsDisplay


class App:
    """The main application class that runs the script and collects the metrics."""
    def __init__(self, script_file, num):
        log_file = "smaug_logs.log"
        self.runner = ScriptRunner(script_file, log_file)
        self.runner.run(num)
        self.monitor = self.runner.monitor
        self.display = MetricsDisplay(log_file)

        self.stop_flag = False
        self.collect_data_thread = threading.Thread(target=self._collect_data)
        self.collect_data_thread.start()
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        """Handle the SIGINT signal to stop the application."""
        self.stop_flag = True
        self.runner.stop()

    def _collect_data(self):
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
    parser.add_argument("-mf", type=str, help="The main file to run (path)")
    parser.add_argument(
        "-n",
        type=int,
        default=1,
        help="The number of times to run your script. Default is 1.",
    )

    args = parser.parse_args()
    if args.mf:
        n = args.n
        main_file = args.mf
        app = App(main_file, n)
