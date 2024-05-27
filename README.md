# Smaug
### Know everything about your a̶p̶p̶s treasures 

Smaug is a lightweight monitoring tool for Python scripts, much akin to the grand dragon of 'The Hobbit', Smaug, who knew every nook of his treasure trove. This application is intimately acquainted with the intricacies of scripts, providing detailed insights into their performance and resource usage.

## Features

- **CPU Monitoring**: Smaug can monitor the CPU usage of your Python scripts, providing real-time data on how much processing power your script is using.

- **Memory Monitoring**: Smaug can also monitor the memory usage of your scripts, showing you how much RAM your script is using at any given time.

- **Disk Monitoring**: Smaug can monitor the disk usage of your scripts, providing data on how much disk space your script is using.

- **Process Monitoring**: Smaug can monitor the execution time of your scripts, as well as the total thread usage.

## Built With

This project is built exclusively with Python 3 and its standard libraries. No external libraries are used, showcasing the power and versatility of Python's built-in modules. Here are some of the key standard libraries used:
## Usage

To use Smaug, you need to run the `main.py` file with the appropriate arguments. The `-mf` argument is used to specify the path to the script you want to monitor, and the `-n` argument is used to specify the number of times you want to run your script.

Here is an example:

```bash
python3 main.py -mf path_to_your_script -n 1
```

In this example, Smaug will run the script located at 'path_to_your_script' once and monitor its performance and resource usage.

For more information on the available arguments, you can use the `-h` or `--help` flag:

```bash
python3 main.py -h
```

## Requirements

Smaug requires Python 3.10<= to run. You can download the latest version of Python from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)

## Installation

To install Smaug, you can simply clone this repository to your local machine:

```bash
git clone https://github.com/elaiviaien/Smaug
```
### Demo
We provide a demo script that you can use to test Smaug. The demo script is located in the `use_cases` directory. You can run the demo script with the following command:
```bash
python3 main.py -mf use_cases/chrome/main.py -n 1
```
It will run the demo script once and monitor ( chrome instance ) its performance and resource usage.
## To Do

Here are some potential enhancements and features that could be added to Smaug:

- [ ] **Logging**: Add a feature to log the monitoring data to a file for later analysis.

- [x] **Type hints**: Add type hints to the codebase to improve readability and maintainability.

- [ ] **Max load testing**: Add a feature to test the maximum number of instances of a script that can be run simultaneously.

- [ ] **Network Monitoring**: Implement a feature to monitor network usage of the script.

- [ ] **GPU Monitoring**: Add support for monitoring GPU usage, especially useful for scripts involving machine learning or other GPU-intensive tasks.

- [ ] **Alert System**: Implement an alert system that notifies the user when certain thresholds are exceeded.

- [ ] **Logging to File**: Add an option to log the monitoring data to a file for later analysis.

- [ ] **Support for Other Languages**: Extend Smaug to support scripts written in languages other than Python.


## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
