import functools
import threading
import os
import time
import psutil


import matplotlib.pyplot as plt
import pandas as pd


def get_size(byte: int) -> str:
    """
    Function to convert size format.

    Parameters
    ----------
    byte : int
        bytes to be converted

    Returns
    -------
    str
        size of bytes in a nice format
    """

    for order in ['', 'K', 'M', 'G', 'T', 'P']:
        if byte < 1024:
            return f"{byte:.2f}{order}B"
        byte /= 1024

# RAM monitoring -- NOT USED YET --
# TODO testing
# TODO add typing
def continuous_monitor_ram(interval: int = 10, max_ram: int = 82500000):
    """Decorator to continuously monitor RAM usage of a function."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            stop_monitoring = threading.Event()

            def monitor():
                process = psutil.Process()
                while not stop_monitoring.is_set():
                    current_mem = process.memory_info().rss
                    if current_mem > max_ram:
                        print(f"Memory used by process: {get_size(current_mem)}")
                        print("Terminating...")
                        os.kill()
                    time.sleep(interval)

            # Start monitoring in a separate thread
            thread = threading.Thread(target=monitor)
            thread.daemon = True  # Set as a daemon so it will terminate when main finishes
            thread.start()

            # Execute the main function
            result = func(*args, **kwargs)

            # Stop the monitoring thread after the function completes
            stop_monitoring.set()
            thread.join()  # Ensure monitoring thread has finished

            return result

        return wrapper

    return decorator


# Plotting
def make_plots(name: str) -> None:
    """
    Plotting function that is called on termination when specified.
    It calls the according plotting functions with the correct arguments.

    Parameters
    ----------
    name

    Returns
    -------

    """
    pass



def plot_process():
    pass

def plot_interface():
    pass
def plot_total():
    pass