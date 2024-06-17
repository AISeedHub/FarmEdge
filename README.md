# FarmEdge

Services run on Edge devices

## Installation

1. Automatic installation the flask service and camera service on each pi by running the `setup.sh` script as root
2. Setting up the services manually (we're doing this approach) :
   1. Mounting the shared folder : `sudo mount.cifs -o username=aiseed,uid=aiseed,gid=aiseed //192.168.0.63/shared_folders /home/aiseed/shared_folder`
   2. Starting the services by running the `run.sh` script

---

## Development Notes

### 1. Idea

#### Short Claim: The idea is to have a service that runs on each edge device that can be queried by the main server to get the status of the device (**SERVER**)

- `setup.sh` script:
    - installing all the required packages
    - copying the service file to the systemd directory
    - enabling and starting the service (with this script, the service will start on boot)
- `aiseed-edge-api.service`: executing the `run.py` script (aka starting the Flask API)
- `aiseed-camera-recoding.service`: executing the `recording.py` script to capture the photo and save it to the main
  server
- `aiseed-mount-share.service`: mounting the shared folder from the main server to the edge devices

### 2. Script for Testing:

- `sudo netstat -tulpn | grep LISTEN`: check if the Flask service is running
- `sudo nano /etc/fstab`: check if the shared folder is mounted (possible to be written in many times)
- Remove the services before running the script again, example:
    - `sudo systemctl stop aiseed-edge-api.service`
    - `sudo systemctl disable aiseed-edge-api.service`
    - `sudo remove /etc/systemd/system/aiseed-edge-api.service`

#### @Copyright 2024 Andrew Lee - All Rights Reserved