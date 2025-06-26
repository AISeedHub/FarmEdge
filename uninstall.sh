#!/bin/bash

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Permission denied. Please run as root."
    exit 1
fi

# Create backup directory with today's date and time
BACKUP_DIR="/home/aiseed/backup_FarmEdge_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Stop and disable services
SERVICES=(aiseed-edge-api.service aiseed-camera-recording.service)
for SERVICE in "${SERVICES[@]}"; do
    if [ -f "/etc/systemd/system/$SERVICE" ]; then
        echo "Stopping $SERVICE..."
        systemctl stop "$SERVICE"
        echo "Disabling $SERVICE..."
        systemctl disable "$SERVICE"
        echo "Removing $SERVICE..."
        rm -f "/etc/systemd/system/$SERVICE"
        echo ""
    fi
done


# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Remove installed scripts and configs
echo "Removing installed scripts and configs..."
rm -rf /usr/local/sbin/api
if [ -f /usr/local/sbin/camera-control/config.yaml ]; then
    cp -r /usr/local/sbin/camera-control/config.yaml "$BACKUP_DIR/"
    chmod 777 "$BACKUP_DIR/config.yaml"
    rm -rf /usr/local/sbin/camera-control
fi

# Unmount and clean up CIFS share
echo "Unmounting and cleaning up CIFS share..."
umount /home/aiseed/shared_folder 2>/dev/null

# Backup and remove the line containing '/shared_folder' in /etc/fstab
if grep -q "/shared_folder" /etc/fstab; then
    grep "/shared_folder" /etc/fstab > "$BACKUP_DIR/fstab_shared_folder_line.bak"
    sed -i '/\/shared_folder/d' /etc/fstab
fi

# Backup and remove the credentials.txt file
if [ -f /etc/credentials.txt ]; then
    cp /etc/credentials.txt "$BACKUP_DIR/"
    chmod 777 "$BACKUP_DIR/credentials.txt"
    rm -f /etc/credentials.txt
fi

# Remove the cron job
echo "Removing the cron job..."
crontab -l | grep -v '/usr/local/sbin/reboot_with_log.sh' | crontab -
rm -f /usr/local/sbin/reboot_with_log.sh


echo "Cleanup and backup completed. Backup directory: $BACKUP_DIR"