#!/usr/bin/bash
python3 -m venv monitoring_venv
source monitoring_venv/bin/activate
pip install pip --upgrade
pip install psutil pandas influxdb-client matplotlib
