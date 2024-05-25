from runner import ScriptRunner
import time
app = ScriptRunner('use_cases/chrome/main.py')
app.run(2)
time.sleep(5)
print("Current thread usage diff:", app.monitor.process_monitor.get_diff(),
        "Memory usage diff:", app.monitor.memory_monitor.get_average(),
        "CPU usage diff:", app.monitor.cpu_monitor.get_average(),
        "Disk usage diff:", app.monitor.disk_monitor.get_diff(),
        "Execution time:", app.monitor.process_monitor.get_execution_time(),
        "Total thread usage:", app.monitor.process_monitor.get_total_thread_usage())
time.sleep(5)
print("Current thread usage diff:", app.monitor.process_monitor.get_diff(),
        "Memory usage diff:", app.monitor.memory_monitor.get_average(),
        "CPU usage diff:", app.monitor.cpu_monitor.get_average(),
        "Disk usage diff:", app.monitor.disk_monitor.get_diff(),
        "Execution time:", app.monitor.process_monitor.get_execution_time(),
        "Total thread usage:", app.monitor.process_monitor.get_total_thread_usage())
app.stop()