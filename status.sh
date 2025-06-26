ps -ef|grep -v grep|grep recording.py
# result: aiseed      2803       1  1 14:06 tty1     00:00:03 /usr/bin/python3 /usr/local/sbin/camera-control/recording.py

ps -ef|grep -v grep|grep api/run.py
# aiseed      2786       1  0 14:06 ?        00:00:00 /usr/bin/python3 /usr/local/sbin/api/run.py

df -h |grep //