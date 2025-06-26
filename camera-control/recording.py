import cv2
import yaml
import numpy as np
import time
import os
import pytz
import datetime

TIMEZONE = pytz.timezone('Asia/Seoul')

# Save YAML configuration to file
config_file = 'config.yaml'

log_file = '~/camera-control.log'
# export all terminal output in this file to log file
import logging
import sys
import os

# Define the log file path. Expand the user home directory symbol (~).
log_file = os.path.expanduser(log_file)
# Create a logger object.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a file handler which logs even debug messages.
fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG)

# Create a console handler with a higher log level.
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# Create formatter and add it to the handlers.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handlers to the logger.
logger.addHandler(fh)
logger.addHandler(ch)


# Create a class to replace stdout and stderr
class StreamToLogger:
    def __init__(self, logger, log_level):
        self.logger = logger
        self.log_level = log_level

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


# Replace the standard output and standard error streams with the logging equivalents.
sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)


# Functions
def get_cpu_temperature():
    try:
        # Use psutil to get temperature
        temperature = os.popen("vcgencmd measure_temp").readline()
        return f"CPU Temperature: {temperature}"
    except Exception as e:
        return f"Unable to retrieve CPU temperature: {e}"


def read_config(config_file):
    # Read the YAML config file
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def verified_config(config):
    if len(config["CAMERA_INDEXES"]) != len(config["CAMERAS_NAME"]):
        print("Check the config number of cameras and names of cameras")
        exit()


def create_camera_folder(config):
    # set current directory is home directory of user
    current_dir = os.path.expanduser('~')
    # Create a folder for each camera
    for name in config["CAMERAS_NAME"]:
        print("Checking Folder Path:")
        print(current_dir + "/" + name)
        if not os.path.exists(current_dir + "/" + name):
            os.mkdir(current_dir + "/" + name)


def save_image(frames, config):
    current_dir = os.path.expanduser('~')
    # saving each frame into each camera folder and the name of frame is timestamp: year-month-day-hour-minute-second-millisecond
    for ix, frame in enumerate(frames):
        if frame is not None:
            # Get the current time
            # now = datetime.datetime.now(TIMEZONE)
            timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
            # Save the image
            cv2.imwrite(f"{current_dir}/{config['CAMERAS_NAME'][ix]}/{timestamp}.jpg", frame)
            print(f"Saved frame {ix} into {config['CAMERAS_NAME'][ix]}")


def generate_error_error_frame(config, message):
    # Generate a Black frame with error message
    error_frame = np.zeros((config['RES_DROP'].get('HEIGHT'), config['RES_DROP'].get('WIDTH'), 3), np.uint8)
    error_frame[:] = (0, 0, 255)
    text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    text_position = (int((error_frame.shape[1] - text_size[0]) / 2), int((error_frame.shape[0] - text_size[1]) / 2))
    cv2.putText(error_frame, message, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return error_frame


def create_layout(frames, config):
    """
    Create a nx2 frame with two cameras for each row. If number of camera is odd then create a blank frame
    """
    num_of_cams = len(config["CAMERA_INDEXES"])
    layout_rows = np.ceil(num_of_cams / 2)
    if num_of_cams % 2 == 1:
        blank_frame = np.zeros_like(frames[0])  # Blank frame
        text = "Press `q` to close the program"
        text_position = (
            int((blank_frame.shape[1] - cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][0]) / 2),
            int(blank_frame.shape[0] / 2)
        )
        cv2.putText(blank_frame, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        # adding the time: yyyy/mm/dd/hh/mm/ss into the bottom right corner of the frame
        text = time.strftime('%Y/%m/%d/%H:%M:%S', time.localtime())
        text_position = (
            int((blank_frame.shape[1] - cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][0]) / 2),
            int(blank_frame.shape[0] / 2) + 20
        )
        cv2.putText(blank_frame, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        # Print the CPU temperature
        text = get_cpu_temperature()
        text_position = (
            int((blank_frame.shape[1] - cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][0]) / 2),
            int(blank_frame.shape[0] / 2) + 40
        )
        cv2.putText(blank_frame, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        frames.append(blank_frame)

    # Combine frames for the layout
    layout = None

    for i in range(int(layout_rows)):
        row_frame = None
        for j in range(2):
            idx = i * 2 + j
            fr = frames[idx]
            row_frame = fr if row_frame is None else np.hstack((row_frame, fr))
        layout = row_frame if layout is None else np.vstack((layout, row_frame))

    return layout


def check_camera_status(frames):
    for ix, frame in enumerate(frames):
        if frame is None and list_camera_error[ix] is None and list_camera_error[ix] is None:
            camera_error_text = f"Camera {ix + 1} ({config['CAMERAS_NAME'][ix]}) is OFF"
            # adding time in message
            camera_error_text = camera_error_text + " at " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "/n"
            print(camera_error_text)
            list_camera_error[ix] = camera_error_text

        if frame is None:
            # try to re-open the camera
            list_camera_error[ix] = None
            try:
                # Attempt to open the camera
                cap = cv2.VideoCapture(camera_indexes[ix])
                # Check for USB reconnection
                if not cap.isOpened():
                    print("Camera disconnected. Attempting to reconnect failed")
                else:
                    print(f"Camera {ix + 1} ({config['CAMERAS_NAME'][ix]}) is ON")
                    # Set the resolution for both cameras (adjust as needed)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['RESOLUTION'].get('CAP_PROP_FRAME_WIDTH'))
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['RESOLUTION'].get('CAP_PROP_FRAME_HEIGHT'))
                    list_camera_error[ix] = cap
            except cv2.error as e:
                print(f"OpenCV Error: {e}")
    return camera_error_text


def show_camera_layout(frames, config, camera_error_text):
    for ix in range(len(frames)):
        if frames[ix] is not None:
            frames[ix] = cv2.resize(frames[ix], (config['RES_DROP'].get('WIDTH'), config['RES_DROP'].get('HEIGHT')))
            text_position = (int((frames[ix].shape[1] -
                                  cv2.getTextSize(config["CAMERAS_NAME"][ix], cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][
                                      0]) / 2), 20)
            cv2.putText(frames[ix], config["CAMERAS_NAME"][ix], text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 1, cv2.LINE_AA)
        else:
            frames[ix] = generate_error_error_frame(config, list_camera_error[ix])
            text_position = (
                int((frames[ix].shape[1] - cv2.getTextSize(camera_error_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][
                    0]) / 2),
                20)
            cv2.putText(frames[ix], camera_error_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
                        cv2.LINE_AA)

    # Create a nx2 layout with two cameras for each row. If number of camera is odd then create a blank frame
    combined_frame = create_layout(frames, config)

    # Display the combined frame
    cv2.imshow("Camera", combined_frame)
    # using moveWindow() function
    cv2.moveWindow("Camera", 20, 20)


# Main Code
config = read_config(config_file)
print(config)
verified_config(config)
create_camera_folder(config)

interval_time = config['INTERVAL_TIME'] * 60
last_time = time.time() - interval_time

camera_indexes = config['CAMERA_INDEXES']
list_cap = []
list_camera_error = []


def open_cameras(camera_indexes, config):
    camera_caps = []
    for camera_index in camera_indexes:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("Error: Unable to open camera number :", camera_index)
            exit()
        print(f"Camera number {camera_index} is ON")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['RESOLUTION'].get('CAP_PROP_FRAME_WIDTH'))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['RESOLUTION'].get('CAP_PROP_FRAME_HEIGHT'))
        camera_caps.append(cap)
    return camera_caps


def close_cameras(list_cap):
    for cap in list_cap:
        if cap is not None:
            cap.release()


while True:
    # Measure the time of the main loop to sleep for the remaining time
    mainLoopStartTime = time.time()

    # Schedule the camera to work only in the day time
    now = datetime.datetime.now(TIMEZONE)
    # if now is not in between target hours then sleep for 1 hour
    if not (config['LIGHT_START_HOUR'] <= now.hour <= config['LIGHT_END_HOUR']):
        print("Sleeping for 1 hour")
        time.sleep(3600)
        continue

    # Usage
    list_cap = open_cameras(camera_indexes, config)
    list_camera_error = [None] * len(list_cap)
    # Read frames from all cameras
    frames = []
    for cap in list_cap:
        if cap is not None:
            frames.append(cap.read()[1])
        else:
            frames.append(None)
    # (Uncomment for display) Checking the camera status
    # camera_error_text = check_camera_status(frames)

    # Close all cameras
    close_cameras(list_cap)

    # saving images every interval_time
    if time.time() - last_time > interval_time:
        # print the time and log
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        last_time = time.time()
        save_image(frames, config)
        # Print the CPU temperature
        print(get_cpu_temperature())

    # write to log file the last time the image was saved (overwriting the previous time, if file not exists then create it)
    current_dir = os.path.expanduser('~')
    with open(current_dir + "/last_time.txt", "w") as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    # (Uncomment for display) Add titles to identify each camera (central top with red color)
    # show_camera_layout(frames, config, camera_error_text)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Measure the time of the main loop to sleep for the remaining time
    mainLoopEndTime = time.time()
    consumptionTime = mainLoopEndTime - mainLoopStartTime
    sleepTime = interval_time - consumptionTime
    
    # (For saving power consumption) Sleep for interval_time seconds
    print(f"Sleeping for {sleepTime} seconds")
    time.sleep(sleepTime)

cv2.destroyAllWindows()
