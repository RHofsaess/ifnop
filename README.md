# ifhpc
iftop alternative in python for usage at HPC centers without permissions to use iftop (LOL).
It is possible to monitor the total traffic, the traffic of one or multiple interfaces and also of a single process.

NOTE: strace works different for RHEL / Ubuntu. This version is tested with RHEL8. The trace=... has to be adapted accordingly.