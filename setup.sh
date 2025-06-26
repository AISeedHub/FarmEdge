#!/bin/bash

if ! command -v python3 &> /dev/null
then
    apt-get install python3 python3-pip
fi

if ! dpkg -s cifs-utils >/dev/null 2>&1; then # check if cifs-utils is installed
# [Note] because the cifs-utils has no command, i use dpkg to check if it is installed
    apt install -y cifs-utils
else
    echo "cifs-utils is already installed."
fi

# [Warning] By PEP 668, pip install for python3 is not allowed. In the future, we should use venv to manage the dependencies.
$(which python3) -m pip install -r requirements.txt

echo "--------------------------------"

cp -r ./api /usr/local/sbin/
cp -r ./camera-control /usr/local/sbin/
chmod 777 /usr/local/sbin/camera-control/config.yaml
echo "Copied the API and camera-control scripts to /usr/local/sbin/"

cp aiseed-edge-api.service /etc/systemd/system/
echo "Copy aiseed-edge-api.service to /lib/systemd/system/"
cp aiseed-camera-recording.service /etc/systemd/system/
echo "Copy aiseed-camera-recording.service to /lib/systemd/system/"
# [Deprecated] "/etc/fstab" will automatically mount the CIFS share on system reboot
# cp aiseed-mount-share.service /etc/systemd/system/
# echo "Copy aiseed-mount-share.service to /lib/systemd/system/"

# Update /etc/fstab with the CIFS share entry
# [Note] _netdev is used to mount when internet is connected
# [Note] uid and gid are used to mount the CIFS share with the correct permissions
echo "//192.168.0.63/shared_folders  /home/aiseed/shared_folder  cifs  credentials=/etc/credentials.txt,uid=aiseed,gid=aiseed,iocharset=utf8,_netdev  0  0" | sudo tee -a /etc/fstab > /dev/null
echo "CIFS share entry added to /etc/fstab"

# Create the credentials file
echo "username=aiseed" | sudo tee /etc/credentials.txt > /dev/null
echo "password=0" | sudo tee -a /etc/credentials.txt > /dev/null
echo "Credentials file created"

# set the permissions
chmod 600 /etc/credentials.txt
echo "Permissions set for the credentials file"

echo "--------------------------------"

# Reload systemd daemon and wait for it to complete
echo "Reloading systemd daemon..."
systemctl daemon-reload
sleep 5s

# [Deprecated] "/etc/fstab" will automatically mount the CIFS share on system reboot
# systemctl enable aiseed-mount-share.service
# echo "Mount share service enabled"
# systemctl start aiseed-mount-share.service
# echo "Mount share service started"

echo "Setup completed. The CIFS share will be automatically mounted on system reboot."

echo "--------------------------------"

mount -a
echo "Mounted the CIFS share"

systemctl enable aiseed-edge-api.service
sleep 2s
systemctl start aiseed-edge-api.service
sleep 2s
echo "Edge API service started."

systemctl enable aiseed-camera-recording.service
sleep 2s
systemctl start aiseed-camera-recording.service
sleep 2s
echo "Camera recording service started."

echo "Check Status: "
systemctl status aiseed-edge-api.service --no-pager
systemctl status aiseed-camera-recording.service --no-pager

# [Deprecated] "/etc/fstab" will automatically mount the CIFS share on system reboot
# systemctl status aiseed-mount-share.service
df -h
