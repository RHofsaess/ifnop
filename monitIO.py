#!/usr/bin/env python3

# todo: size limitations for logs?
# todo: print default logging all the time + average speed etc

import psutil
import time
import datetime
import subprocess
import os
import threading
import re

import pandas as pd
from utils import get_size

# default values
updateInterval = 10

def default_logging(stats: dict) -> None:
    """
    Function for the default logging of total transferred size and speed.
    This function is always called on exit.
    Currently, only the total statistic is logged (not per interface).

    Parameters
    ----------
    stats: Dict
        Includes the timestamp and the transferred data at start and end.

    Returns
    -------
    None
    """
    # TODO: make flexible for each interface: it should give the total transferred amount for the if and other things

    # calculate total transferred
    runtime = stats["end_time"] - stats["start_time"]
    total_sent = stats["end_sent"] - stats["start_sent"]
    total_rec = stats["end_rec"] - stats["start_rec"]
    avg_speed = total_rec / runtime.total_seconds()

    print(f'{stats["interface"]} statistic:')
    print(f"time: {runtime.total_seconds()}s, sent: {get_size(total_sent)}, received: {get_size(total_rec)}, "
          f"average downstream over whole time of measurement: {get_size(avg_speed)}/s")


def watch_interfaces(arg_dict: dict) -> None:
    """
    Function to continuously monitor the network traffic of one or more interfaces.
    If a log file is specified, it will be also written to file per interface.
    The output is given in bytes with the following format:
    timestamp, upload, download, upstream, downstream

    Parameters
    ----------
    arg_dict: Dict
        Dictionary containing the config keys.
    Returns
    -------
    None
    """
    # todo: add ram monitoring for max log size + termination

    test = pd.DataFrame()

    updateInterval = arg_dict["update"]
    io = psutil.net_io_counters(pernic=True,
                                nowrap=True)  # https://www.educative.io/answers/what-is-the-psutilnetiocounters-method
    start = datetime.datetime.now()
    if arg_dict["verbose"]:
        print("start measurement at:", start.strftime('%Y-%m-%d_%H-%M-%S'))

    if arg_dict["interfaces"] != "all":
        provided_interfaces = arg_dict["interfaces"].split(",")
        # check if interfaces are valid:
        all_interfaces = list(psutil.net_if_addrs().keys())
        diff = set(provided_interfaces) - set(all_interfaces)
        if diff:  # if not empty -> unknown interface
            print(f"ERROR! unknown interface(s): {diff}!\nPlease select from the following:")
            print(all_interfaces)
            exit()
    else:
        provided_interfaces = list(psutil.net_if_addrs().keys())

    accumulated_data = {}  # dict containing the data frames for each interface
    columns = ["timestamp", "upload", "download", "upstream", "downstream"]

    for interface, interface_io in io.items():
        # use provided interface list
        if interface in provided_interfaces:
            accumulated_data[interface] = pd.DataFrame(columns=columns)

            up, down = io[interface].bytes_sent - interface_io.bytes_sent, io[
                interface].bytes_recv - interface_io.bytes_recv
            new_row = {"timestamp": start,
                       "download": io[interface].bytes_recv,
                       "upload": io[interface].bytes_sent,
                       "upstream": up / updateInterval,
                       "downstream": down / updateInterval}
            accumulated_data[interface] = accumulated_data[interface].append(new_row, ignore_index=True)

    try:
        while True:
            time.sleep(updateInterval)
            now = datetime.datetime.now()

            io_new = psutil.net_io_counters(pernic=True, nowrap=True)
            current_data = []
            for interface, interface_io in io.items():
                if interface in provided_interfaces:
                    up, down = io_new[interface].bytes_sent - interface_io.bytes_sent, io_new[
                        interface].bytes_recv - interface_io.bytes_recv
                    current_data.append({
                        "interface": interface,
                        "timestamp": now,
                        "download": get_size(io_new[interface].bytes_recv),
                        "upload": get_size(io_new[interface].bytes_sent),
                        "upstream": f"{get_size(up / updateInterval)}/s",
                        "downstream": f"{get_size(down / updateInterval)}/s",
                    })
                    if arg_dict["logtofile"]:
                        if not os.path.exists("logs"):
                            os.makedirs("logs")

                        # add current data to interface dfs
                        current = {
                            "timestamp": now,
                            "download": io_new[interface].bytes_recv,
                            "upload": io_new[interface].bytes_sent,
                            "upstream": up / updateInterval,
                            "downstream": down / updateInterval,
                        }
                        accumulated_data[interface] = accumulated_data[interface].append(current, ignore_index=True)  # TODO: can be optimized!

            # update the I/O stats for the next iteration
            io = io_new

            df = pd.DataFrame(current_data)
            if arg_dict["sort"]:
                df.sort_values(f'{arg_dict["sort"]}', inplace=True, ascending=False)
            os.system("cls") if "nt" in os.name else os.system("clear")
            print(df.to_string())

    except KeyboardInterrupt:
        for interface in accumulated_data.keys():
            log_path = f"logs/{interface}"
            accumulated_data[interface].to_csv(f"{log_path}.csv", index=False)
        exit()


def watch_total(arg_dict: dict) -> None:
    """
    Function to continuously monitor the total network traffic.
    If a log file is specified, it will be also written to file.
    The output is given in bytes with the following format:
    timestamp, upload, download, upstream, downstream

    Parameters
    ----------
    arg_dict : Dict
        Argparse dict containing the config keys.

    Returns
    -------
        None
    """
    updateInterval = arg_dict["update"]
    io = psutil.net_io_counters()
    bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
    stats = {"start_time": datetime.datetime.now(),
             "start_sent": io.bytes_sent,
             "start_rec": io.bytes_recv,
             }  # initial values

    if arg_dict["logtofile"]:
        outfile = "total.csv"
    else:
        outfile = "default.log"
        if arg_dict["verbose"]:
            print(f"Only default logging to {outfile} enabled.")

    with open(outfile, "a") as f:
        try:
            while True:
                time.sleep(updateInterval)
                io_new = psutil.net_io_counters()

                up, down = io_new.bytes_sent - bytes_sent, io_new.bytes_recv - bytes_recv
                upload = io_new.bytes_sent
                download = io_new.bytes_recv
                upstream = up / updateInterval
                downstream = down / updateInterval
                print(f"upload: {get_size(upload)}   "
                      f", download: {get_size(download)}   "
                      f", upstream: {get_size(int(upstream))}/s   "
                      f", downstream: {get_size(int(downstream))}/s   ", end="\r")
                if arg_dict["logtofile"]:
                    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    write_str = f"{now}, {upload}, {download}, {upstream}, {downstream}\n"
                    f.write(write_str)
                # update
                bytes_sent, bytes_recv = io_new.bytes_sent, io_new.bytes_recv
        except KeyboardInterrupt:
            # do things
            print("Keyboard interrupt... Processing please wait!")
            stats.update({"end_time": datetime.datetime.now(),
                          "end_sent": io_new.bytes_sent,
                          "end_rec": io_new.bytes_recv,
                          "interface": "total",
                          }
                         )
            default_logging(stats)
            # TODO: add plotting?
            exit()


def watch_process(arg_dict: dict) -> None:
    """
    Function to watch a process, specified with --pid/-p.

    Parameters
    ----------
    arg_dict: dict
        Argparse dict containing the config keys.

    Returns
    -------
    None
    """
    # TODO: exchange write to file with pandas df
    # TODO plotting
    # TODO add total stats with default logging

    ###################################################
    # for threading
    downstream = 0
    total_bytes = 0
    stop_monitoring = threading.Event()
    args = arg_dict
    ###################################################



    def get_bandwidth() -> None:  # interval: int
        nonlocal downstream, stop_monitoring, args

        with open("logs/process.log", "a") as f:
            while not stop_monitoring.is_set():
                bandwidth = downstream / args["update"]  # Bytes received in the last second

                if arg_dict["logtofile"]:
                    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    write_str = f"{now}, {bandwidth}\n"
                    f.write(write_str)

                os.system("cls") if "nt" in os.name else os.system("clear")
                print(f"Downstream bandwidth (pid: {args['pid']}): {get_size(int(bandwidth))} /s")
                downstream = 0  # Reset for the next interval
                threading.Event().wait(args["update"])  # Wait for 1 second

    def monitor_network_traffic() -> None:
        nonlocal downstream, total_bytes, args

        cmd = ["strace", "-e", "trace=recvfrom", "-p", args["pid"]]  # send or recvfrom ...

        # Start a background thread to print total bytes every second
        threading.Thread(target=get_bandwidth).start()  # (interval)

        with subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True) as process:

            for line in process.stderr:
                # match = re.search(r'(recv|recvfrom).*=\s+(\d+)$', line)
                match = re.search(r'=\s+(\d+)$', line)
                if match:
                    bytes_received = int(match.group(1))
                    # bytes_received = int(match.group(2))
                    downstream += bytes_received
                    total_bytes += bytes_received

    start = datetime.datetime.now()

    try:
        monitor_network_traffic()
    except KeyboardInterrupt:
        # do things
        end = datetime.datetime.now()
        stop_monitoring.set()
        print("stopping...")
        """
        print("Keyboard interrupt... Processing please wait!")
        stats.update({"end_time": datetime.datetime.now(),
                      "end_sent": io_new.bytes_sent,
                      "end_rec": io_new.bytes_recv,
                      "interface": "total",
                      }
                     )
        default_logging(stats)
        # TODO: evtl: add plotting?
        """
        exit()
