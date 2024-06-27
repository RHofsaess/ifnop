#!/usr/bin/env python3
import argparse
import configparser
import logging
import os

from ifnop import process_interface_list, gather_interface_info, monitor_interactive, monitor_and_send
from logger_conf import configure_logger

# TODO: consistent ' "
# ******************************************************************************************************************** #
# This is a small monitoring tool that does not need direct access to the sockets and therefore is usable at (our) HPC #
# center.                                                                                                              #
# It is possible to monitor the total traffic, as well as certain interfaces.                                          #
# The purpose is to monitor the in and outgoing network traffic when running an XCache on an HPC login node.           #
# Currently, interactive mode is controlled via CLI arguments and detached mode via a config file.                     #
#                                                                                                                      #
# To stop the measurement, use crtl+c. This is caught and the logs/ statistics are printed and written to file before  #
# exiting.                                                                                                             #
# ******************************************************************************************************************** #


def parse_config_file(config_file: str) -> str:
    """Check the provided config file path."""
    if os.path.isfile(config_file):
        print('> [parse_config_file] Configure from file specified and config file found!')
        return config_file
    else:
        exit('> [parse_config_file] Error: config file not found!')


def main() -> None:
    parser = argparse.ArgumentParser(description="Network Interface Monitoring Tool")
    parser.add_argument('--config', type=parse_config_file, help="Reading configuration from file.\n This overrides "
                                                                 "CLI arguments!\n")
    parser.add_argument('--logtofile', type=str, nargs='?', const='', default=None,
                        help="Enable logging to a file. If given without argument, it defaults to an empty string.")
    parser.add_argument('-l', '--loglevel', type=str, choices=['DEBUG', 'INFO', 'WARNING'], default='WARNING',
                        help="Set the logging level (e.g., DEBUG > INFO > WARNING)")
    parser.add_argument('--monit_io', type=str, help='Additional I/O monitoring for the provided process')  # TODO sanitize for interactive
    parser.add_argument('-i', '--interfaces', type=str, default='all',
                        help='Comma-separated list of network interfaces to monitor (e.g. "eth0, eth1")')
    parser.add_argument("-u", "--update", type=int, default=10, help="Update interval in seconds. [Default=10]")
    #parser.add_argument("-s", "--sort", type=str, help="Sort output [download,upload,downstream,upstream")
    args = vars(parser.parse_args())

    if args["config"]:
        # NOTE:
        print('> Reading config file...\n'
              ' +++++ NOTE: in config mode, all CLI flags other than "config" are ignored! +++++ ')
        config = configparser.ConfigParser()
        config.read(args["config"])

        # ----- Logging -----
        # Read logging configuration
        args["logtofile"] = config.get('Logging', 'logtofile', fallback=None)
        args["loglevel"] = config.get('Logging', 'loglevel', fallback='INFO')

        # ----- Network -----
        args["interfaces"] = config.get('Network', 'interfaces', fallback='')  # TODO assert?
        # print(f'> [DEBUG] cfg: {args["interfaces"]}')

        # ----- IO -----
        # IO is created manually as the IO monitoring is optional and does not need to be configured
        try:
            io = {"monit_io": config.getboolean('IO', 'monit_io', fallback=False)}
            if io["monit_io"]:
                io["process"] = config.get('IO', 'process')
            else:
                process = config.get('IO', 'process', fallback='')
                if process != '':
                    print(f'> [WARNING] Process "{process}" configured but monit_io not set!')
        except Exception as e:
            exit(f'Config Error! {e}')

        # ----- write_config -----
        # For a sanitization of the config it is better to split off the parts that are only relevant when a config file
        # is provided. The sanitization then mainly happens in ifnop.py. IO excluded
        # WriteOut
        WriteOut = dict(config.items('WriteOut'))
        # Influx
        Influx = dict(config.items('Influx'))
        # File
        File = dict(config.items('File'))
        # Json
        Json = dict(config.items('Json'))
        # combine
        write_config = WriteOut | Influx | File | Json | io

    # ------------------------------------
    # ----- Setup logging and config -----
    # ------------------------------------
    # Convert log level string to logging level
    level = getattr(logging, args["loglevel"], logging.WARNING)
    # Configure logger based on command-line arguments
    logger = configure_logger(level=level, logtofile=args["logtofile"])  # TODO: verify that the log to file/stdout work

    # Print full parsed config
    logger.debug(f'> Full config:\n {args}')

    # sanitize interface filter list
    args["interfaces"] = process_interface_list(logger, args["interfaces"])

    # Gather and log network interface information
    if level <= 20:  # not warning
        gather_interface_info(logger, args["interfaces"])

    if args["config"]:
        logger.info(f'Config provided. Writing mode enabled.')
        try:
            monitor_and_send(logger, args["interfaces"], write_config)
        except Exception as e:
            exit(f'Smth went wrong!: {e}')
    else:
        logger.warning(f'No config file provided. Running interactively.')
        monitor_interactive(logger, args["interfaces"], update_interval=args["update"])


if __name__ == "__main__":
    main()
