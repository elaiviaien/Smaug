
import os
from itertools import zip_longest
from .metrics import MetricList, MAX_VALUES, QUANTITIES


class MetricsDisplay:

    def __init__(self):
        self.metrics = None
        self.last_update = 0
        self.colors = {
            "black": "\033[1;30m",
            "red": "\033[1;31m",
            "green": "\033[1;32m",
            "yellow": "\033[1;33m",
            "blue": "\033[1;34m",
            "magenta": "\033[1;35m",
            "cyan": "\033[1;36m",
            "white": "\033[1;37m",
        }

    def clear_screen(self) -> None:
        clear_code = "\033c"
        print(clear_code, end="")

    def get_terminal_height(self) -> int:
        return os.get_terminal_size().lines

    def get_logs(self) -> list[str]:
        num_lines = self.get_terminal_height() - 1
        log_files = [
            f for f in os.listdir("logs") if f.startswith(f"smaug_{os.getpid()}_test")
        ]
        lines_per_file = num_lines // len(log_files)
        logs = []
        for log_file in log_files:
            with open(f"logs/{log_file}", "r", encoding="utf-8") as f:
                logs.extend(f.readlines()[-lines_per_file:])
        return logs

    def colored(self, text: str, color: str):
        return f"{self.colors[color]} {text}\033[0m"

    def color_log(self, log_line: str) -> str:
        timestamp_color = "green"
        level_color = "yellow"
        info_color = "blue"
        default_color = "magenta"
        parts = log_line.split(" ", 2)
        if len(parts) != 3:
            return f"{self.colors[default_color]}{log_line}\033[0m"

        timestamp, level, info = parts

        timestamp = f"{self.colors[timestamp_color]}{timestamp}\033[0m"
        level = f"{self.colors[level_color]}{level}\033[0m"
        info = f"{self.colors[info_color]}{info}\033[0m"

        return f"{timestamp} {level} {info}"

    def rate_value_color(self, value: int | float, max_value: int | float) -> str:
        default_color = "magenta"
        ok_color = "green"
        warning_color = "yellow"
        critical_color = "red"
        if value < max_value * 0.5:
            return ok_color
        if value < max_value * 0.8:
            return warning_color
        if max_value != 0:
            return critical_color
        return default_color

    def color_word(self, word: str, color: str):
        return f"{self.colors[color]}{word}\033[0m"

    def color_table(self, table_line: str) -> str:
        borders_color = "cyan"
        header_color = "cyan"
        if table_line.startswith("+"):
            return f"{self.colors[borders_color]}{table_line}\033[0m"
        if "Metric name" in table_line:
            for word in table_line.split("|"):
                if word.strip():
                    table_line = table_line.replace(
                        word.strip(), self.color_word(word.strip(), header_color)
                    )
        else:
            metric_name = table_line.split("|")[1].strip()
            metric_max_value = MAX_VALUES.get(metric_name, 0)

            color = self.rate_value_color(
                float(table_line.split("|")[2].strip()), metric_max_value
            )
            for word in table_line.split("|"):
                if word.strip():
                    table_line = table_line.replace(word, self.color_word(word, color))
        table_line = table_line.replace(
            "|", self.colors[borders_color] + "|" + "\033[0m"
        )
        return table_line

    def get_max_len(self) -> int:
        return max(
            (
                len(metric.name)
                if len(metric.name) > len(str(metric.value))
                else len(str(metric.value))
            )
            for metric in self.metrics
        )

    def display(self) -> None:
        metric_col_len = self.get_max_len() + 2
        value_col_len = 10
        q_col_len = 1
        space_len = 10
        split_row_len = metric_col_len + value_col_len + q_col_len + 8
        table_len = split_row_len

        split_row = "+" + "-" * split_row_len + "+\n"
        header = (
            f"| {'Metric name'.center(metric_col_len)} | {'Value'.center(value_col_len)}"
            f" | {'Q'.center(q_col_len)} |\n"
        )

        self.clear_screen()
        table = ""
        table += split_row
        table += header
        table += split_row
        for metric in self.metrics:
            table += (
                f"| {metric.name.center(metric_col_len)} "
                f"| {str(metric.value).center(value_col_len)} "
                f"| {QUANTITIES.get(metric.name, 'n').center(q_col_len)} |\n"
            )
        table += split_row
        table_lines = table.split("\n")

        logs = self.get_logs()
        logs = [line.strip() for line in logs]
        for table_line, log_line in zip_longest(table_lines, logs, fillvalue=""):
            if table_line and table_len != "\n" and table_lines[-1] != table_line:
                print(
                    f"{self.color_table(table_line)}{' '.center(space_len)}"
                    f" {self.color_log(log_line)}"
                )
            else:

                offset = table_len + space_len + 2
                print(f"{' '.center(offset)} {self.color_log(log_line)}")

    def update(self, new_metrics: MetricList) -> None:
        self.metrics = new_metrics
        self.display()
