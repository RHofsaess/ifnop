#!/usr/bin/env python3
import argparse

import monitIO


# TODO: add check for python version -> append does not work else!!
# TODO: add -d for detached
# TODO: decorator for ram monitoring + flag -m / --max-ram
# TODO: add log size to default log
# TODO: add check if -t is used with something else

# ******************************************************************************************************************** #
# This is a small monitoring tool that does not need direct access to the sockets and therefore is usable at (our) HPC #
# center.                                                                                                              #
# It is possible to monitor the total traffic, as well as certain interfaces.                                          #
# The purpose is to monitor the in and outgoing network traffic when running an XCache on the HoreKa login node.       #
#                                                                                                                      #
# To stop the measurement, use crtl+c. This is caught and the logs/ statistics are printed and written to file before  #
# exiting.                                                                                                             #
# ******************************************************************************************************************** #

parser = argparse.ArgumentParser(description="Network traffic monitoring tool for HPC.")
parser.add_argument("-d", "--detached", action="store_true", help="Run detached for 1 hour.")
parser.add_argument("-i", "--interfaces", type=str, default="all",
                    help="Name of the network interface(s). >,< separated list [Default=all]")
parser.add_argument("-l", "--logtofile", action='store_true', help="Enable logging to file for multiple interfaces.")
parser.add_argument("-p", "--pid", type=str, help="Process ID to be monitored.")
parser.add_argument("-s", "--sort", type=str, help="Sort output [download,upload,downstream,upstream")
parser.add_argument("-t", "--total", action='store_true', help="Total size of transfers over all interfaces. (Does not work with the other flags!)")
parser.add_argument("-u", "--update", type=int, default=10, help="Update interval in seconds. [Default=10]")
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument("-x", "--plot-on-exit", type=bool, default=False, help="Show network traffic plots.")
args = vars(parser.parse_args())


def main():
    # check if total or interface based
    if args["total"]:
        monitIO.watch_total(args)
    elif args["pid"]:
        monitIO.watch_process(args)
    elif args["interfaces"]:  # per interface
        monitIO.watch_interfaces(args)
    else:
        exit("Unknown configuration. Exiting...")


if __name__ == "__main__":
    main()
