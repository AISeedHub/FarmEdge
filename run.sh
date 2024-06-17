#!/bin/bash
nohup python /home/aiseed/FarmEdge/api/run.py &
cd /home/aiseed/FarmEdge/camera-control
dir="/home/aiseed/FarmEdge/camera-control"
cd "${dir%"${dir##*[![:space:]]}"}"
nohup python recording.py &