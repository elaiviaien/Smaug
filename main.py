import argparse
import logging
import os
import signal
import sys
import threading
import time

from core.logger import setup_logger, LoggerWriter
from core.metrics import Metric, MetricList
from core.runner import ScriptRunner
from core.visual import MetricsDisplay

logger = setup_logger(f"smaug_{os.getpid()}")
sys.stderr = LoggerWriter(logger, logging.ERROR)


class App:

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

        self._wait_scripts()

    def signal_handler(self, signal, frame) -> None:
        self.stop()

    def stop(self) -> None:
        self.stop_flag = True
        self.runner.stop()

    def _collect_data(self) -> None:
        collect_interval = 0.3  # 0.3 seconds
        while not self.stop_flag:
            epoch_now = int(time.time())

            cpu_metrics = self.monitor.cpu_monitor.record_stats()
            cpu_metrics.append(
                Metric('cpu average', self.monitor.cpu_monitor.get_average(), epoch=epoch_now)
            )

            memory_metrics = self.monitor.memory_monitor.record_stats()
            for key, value in self.monitor.memory_monitor.get_average().items():
                memory_metrics.append(Metric(f'{key} average', value, epoch=epoch_now))

            disk_metrics = self.monitor.disk_monitor.record_stats()
            disk_metrics.append(
                Metric('disk usage difference',
                       self.monitor.disk_monitor.get_diff(),
                       epoch=epoch_now)
            )

            process_metrics = MetricList([
                Metric('execution time',
                       self.monitor.process_monitor.get_execution_time(),
                       epoch=epoch_now),
                Metric('total thread usage',
                       self.monitor.process_monitor.get_total_thread_usage(),
                       epoch=epoch_now),
            ])
            thread_usage_diff = self.monitor.process_monitor.get_diff()['total thread usage diff']
            process_metrics.append(
                Metric('total thread usage difference', thread_usage_diff, epoch=epoch_now)
            )

            app_size_metric = Metric('app size',
                                     self.monitor.get_app_size(), epoch=epoch_now)

            metrics = (cpu_metrics + memory_metrics + disk_metrics
                       + MetricList([app_size_metric]) + process_metrics)

            self.display.update(metrics)
            time.sleep(collect_interval)

    def _wait_scripts(self) -> None:
        for process in self.runner.processes:
            process.wait()
        self.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the application with a specified main file."
    )
    parser.add_argument(
        "-mf", "--main-file", type=str, help="The main file to run (path)"
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=1,
        help="The number of times to run your script. Default is 1",
    )
    parser.add_argument(
        "-ub",
        "--use-buffer",
        type=lambda x: (str(x).lower() in ["true", "1", "yes"]),
        default=True,
        help="Use buffer for the script output. Default is True",
    )

    args = parser.parse_args()
    if args.main_file:
        num = args.num
        main_file = args.main_file
        use_buffer = args.use_buffer
        app = App(main_file, num, use_buffer)
