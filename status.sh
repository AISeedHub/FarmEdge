#!/bin/bash

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Permission denied. Please run as root."
    exit 1
fi

# Echo the recording.py process
ps -ef|grep -v grep|grep recording.py
# result: aiseed      2803       1  1 14:06 tty1     00:00:03 /usr/bin/python3 /usr/local/sbin/camera-control/recording.py

# Echo the api/run.py process
ps -ef|grep -v grep|grep api/run.py
# aiseed      2786       1  0 14:06 ?        00:00:00 /usr/bin/python3 /usr/local/sbin/api/run.py

# Echo the mount status
df -h |grep //

# Echo the crontab status
crontab -l 2>/dev/null