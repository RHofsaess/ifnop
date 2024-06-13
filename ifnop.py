import time
import datetime
import logging
import os

import psutil
import pandas

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from utils import get_size


# ---------- HELPER ----------
def process_interface_list(logger: logging.Logger, provided_interfaces: str = '') -> list:
    """
    Helper function to process a provided interface list.

    Parameters
    ----------
    logger: logging.Logger
    provided_interfaces: str

    Returns
    -------
    list of selected interface
    """

    interface_list = [element.strip().lower() for element in provided_interfaces.split(',') if element.strip()]
    all_interfaces = psutil.net_if_addrs()

    # [DEBUG] log full psutil output
    # logger.debug(f"[process_interface_list] Full interfaces dict:\n {all_interfaces}")  # too spammy

    if "all" not in interface_list:  # if all is part of the provided interfaces, use all
        # check if interfaces are valid:
        diff = set(interface_list) - set(list(all_interfaces.keys()))
        if diff:  # if not empty -> unknown interface(s)
            logger.warning(f"[process_interface_list] Unknown interface(s): {diff} will be ignored...")
            logger.info(f"> [process_interface_list] All available interfaces: {all_interfaces.keys()}")
        selected_interfaces = set(interface_list) - set(diff)
        if len(selected_interfaces) < 1:
            logger.warning('[process_interface_list] No valid interfaces selected! Exiting')
            exit(1)
    else:  # running for all interfaces
        logger.info('> [process_interface_list] "all" selected: using all interfaces')
        selected_interfaces = list(psutil.net_if_addrs().keys())
    logger.info(f"[process_interface_list] Returning processed interface list: {selected_interfaces}")
    return selected_interfaces
# ------------ | -------------


# TODO add interface infos to be printed
def gather_interface_info(logger: logging.Logger, selected_interfaces: list) -> None:
    """
    Function to collect interface information. Only printed for loglevel INFO and DEBUG.
    NOTE: If a non-existing interface is specified, a warning is printed and it is ignored.

    Parameters
    ----------
    logger: logging.Logger
        Pre-configured logger.
    selected_interfaces: str
        Comma separated list of interfaces to filter on the specified interfaces. Default: no filter

    Returns
    -------
    dict
        Dictionary containing all or the specified interfaces info.
    """
    all_interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    logger.debug(
        f'[gather_interface_info] Running with logger: {logger} and selected interfaces: {selected_interfaces}')

    # [DEBUG] log all unprocessed outputs
    logger.debug(f"Full interfaces dict: {all_interfaces}")
    logger.debug(f"Full stats dict: {stats}")

    for intf, addrs in psutil.net_if_addrs().items():
        # use interface list for filtering
        if intf in selected_interfaces:
            logger.info(f"Interface: {intf}")


# TODO
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


def monitor_and_send(logger: logging.Logger, selected_interfaces: list, write_config: dict) -> None:
    """
    This function monitors one or more interfaces and sends the output in one of three ways:\n
    (1) To file, if an output file is specified -> can be used for further analysis or local plotting\n
    (2) As json via UDP to a configured host:port\n
    (3) To an influxdb\n
    All of the above ways can be used at the same time. Furthermore, the output can be submitted directly or as bachtes.

    **Note: This is for now only usable with a file based config. CLI can only be used for interactive monitoring!**

    Configuration: write_config
    The **write_config** is a subset of the whole config containing [WriteOut] and [Cred].\n
    - mode: [json, influx, file] [default: -]\n
    - outputfile: name for output file, if defined [default: -]\n
    - update: defines the update interval  [default: 10]\n
    - batchsize: nummer of data points that should be collected before writing [default: 1]\n
    - json_hostname\n
    - json_port\n
    - influx_bucket\n
    - influx_token\n


    The batch size defines, after how many data points, the buffer should be flushed, e.g.\n
    update = 30, batchsize = 10 => after 300s, 10 data points are writtem and buffers are flushed.
    By this, the RAM consumption should be reduced

    Parameters
    ----------
    logger
    selected_interfaces
    write_config

    Returns
    -------

    """
    # read in config
    logger.debug(f'[monitor_and_send] Reading in the write config...')

    # check modes to activate and if config is sane

    # ----- send functions -----
    def send_to_influx():
        pass
    def write_to_file():
        pass
    def stream_json():
        pass
    # ----------- | ------------

# TODO: not reviewed and refactored yet
def monitor_interactive(logger: logging.Logger, selected_interfaces: list,
                      output_file: str = '', update_interval: int = 10) -> None:
    """
    - we get the info per time interval
    - it can be streamed to stdout, file, or remote

    Parameters
    ----------
    update_interval
    """
    """

    Parameters
    ----------
    logger
    selected_interfaces
    output_file

    Returns
    -------

    """
    """
    Function to continuously monitor the network traffic of one or more interfaces.
    If a log file is specified, it will be also written to file per interface.
    The output is given in bytes with the following format:
    timestamp, upload, download, upstream, downstream

    This is the local mode. There are two modes. The other one is streaming the data to influx or alternatively via udp
    as json packets.

    Parameters
    ----------
    arg_dict: Dict
        Dictionary containing the config keys.
    Returns
    -------
    None

    """

    def write_data(df: pandas.DataFrame) -> int:
        # returns status code of transfer to check with while or so?
        pass

    stats = []  # for total statistics in the end
    start = datetime.datetime.now()

    msg = "Starting interactive measurement at:" + start.strftime('%Y-%m-%d_%H-%M-%S')
    logger.info(f'{msg}')

    io = psutil.net_io_counters(pernic=True,
                                nowrap=True)  # https://www.educative.io/answers/what-is-the-psutilnetiocounters-method

    accumulated_data = {}  # dict containing a list of the data dicts for each interface
    for interface, interface_io in io.items():
        # use provided interface list
        if interface in selected_interfaces:
            accumulated_data[interface] = []  # create a list per interface to be filled with the data dicts
            up, down = io[interface].bytes_sent - interface_io.bytes_sent, io[
                interface].bytes_recv - interface_io.bytes_recv
            # add init values per dict
            accumulated_data[interface].append(dict(timestamp=start, upload=io[interface].bytes_sent,
                                                    download=io[interface].bytes_recv, upstream=up / update_interval,
                                                    downstream=down / update_interval)
                                               )
            stats.append(dict(interface=interface, start_time=datetime.datetime.now(),
                              start_sent=io[interface].bytes_sent, start_rec=io[interface].bytes_recv))
    try:
        while True:
            time.sleep(update_interval)

            now = datetime.datetime.now()
            io_new = psutil.net_io_counters(pernic=True, nowrap=True)

            current_data = []
            for interface, interface_io in io.items():
                if interface in selected_interfaces:
                    up, down = (io_new[interface].bytes_sent - interface_io.bytes_sent,
                                io_new[interface].bytes_recv - interface_io.bytes_recv
                                )
                    current_data.append({
                        "interface": interface,
                        "timestamp": now,
                        "upload": get_size(io_new[interface].bytes_sent),
                        "download": get_size(io_new[interface].bytes_recv),
                        "upstream": f"{get_size(up / update_interval)}/s",
                        "downstream": f"{get_size(down / update_interval)}/s",
                    })

                    if output_file:  # or arg_dict["plotonexit"]:
                        # add current data to list of data dicts per interface
                        current = {
                            "timestamp": now,
                            "upload": io_new[interface].bytes_sent,
                            "download": io_new[interface].bytes_recv,
                            "upstream": up / update_interval,
                            "downstream": down / update_interval,
                        }
                        accumulated_data[interface].append(current)

            # update the I/O stats for the next iteration
            io = io_new

            df = pandas.DataFrame(current_data)
            #if arg_dict["sort"]:
            #    df.sort_values(f'{arg_dict["sort"]}', inplace=True, ascending=False)
            os.system("cls") if "nt" in os.name else os.system("clear")
            print(df.to_string())

    except KeyboardInterrupt:
        print("Keyboard interrupt... Processing please wait!")

        """
        if arg_dict["logtofile"]:
            if not os.path.exists("logs"):
                os.makedirs("logs")
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        for interface in accumulated_data.keys():
            df = pd.DataFrame(accumulated_data[interface])
            if arg_dict["logtofile"]:
                log_path = f"logs/{interface}_{timestamp}"
                df.to_csv(f"{log_path}.csv", index=False)
            if arg_dict["plotonexit"]:
                plot_interfaces(df, provided_interfaces)  # TODO: add timestamp to plots

        # for total, stats only contains one dict, so we directly access it via [0]
        stats[0].update(  # TODO: PER INTERFACE! (not [0]!)
            dict(end_time=datetime.datetime.now(), end_sent=io_new.bytes_sent, end_rec=io_new.bytes_recv)
        )
        show_stats(stats)
        exit()
        """
