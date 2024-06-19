import cv2
import yaml
import numpy as np
import time
import os
import pytz
import datetime

# YAML Configuration
config_data = """
CAMERA_INDEXES:
  - 0
  - 4

CAMERAS_NAME:
  - "shared_folder/merryQueen_floor_2"
  - "shared_folder/merryQueen_floor_3"

RESOLUTION: # Resolution for saving the image 4K
  CAP_PROP_FRAME_WIDTH: 3840
  CAP_PROP_FRAME_HEIGHT: 2160

RES_DROP: # resolution to show in camera grid. Recommended: 480x360
  WIDTH: 800
  HEIGHT: 600

INTERVAL_TIME: 10 # Minute :time to capture the image 

LIGHT_START_HOUR: 6
LIGHT_END_HOUR: 19
"""

TIMEZONE = pytz.timezone('Asia/Seoul')

# Save YAML configuration to file
config_file = 'config.yaml'
with open(config_file, 'w') as yaml_file:
    yaml_file.write(config_data)


# Functions
def get_cpu_temperature():
    """
    Returns the current temperature of the CPU.

    This method uses the `vcgencmd` command to measure the CPU temperature using the `os.popen` function. It captures the output and returns it as a string.

    Returns:
        str: A string representing the CPU temperature in the format `CPU Temperature: X.XX°C`.
            - "X.XX" is the current temperature of the CPU in degrees Celsius.

    Raises:
        Exception: If there is an error retrieving the CPU temperature, an exception is raised with
            an error message.

    """
    try:
        # Use psutil to get temperature
        temperature = os.popen("vcgencmd measure_temp").readline()
        return f"CPU Temperature: {temperature}"
    except Exception as e:
        return f"Unable to retrieve CPU temperature: {e}"


def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def read_config(config_file):
    """
    Args:
        config_file: The file path to the YAML config file that needs to be read.

    Returns:
        config: A dictionary containing the parsed config from the YAML file.

    Raises:
        FileNotFoundError: If the specified config_file does not exist.
        IOError: If there is an error while reading the config_file.
    """
    # Read the YAML config file
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def verified_config(config):
    """
    Args:
        config (dict): A dictionary containing the camera indexes and names.

    """
    if len(config["CAMERA_INDEXES"]) != len(config["CAMERAS_NAME"]):
        print("Check the config number of cameras and names of cameras")
        exit()


def create_camera_folder(config):
    """
    Creates a folder for each camera based on the given configuration.

    Args:
        config: A dictionary containing the configuration details.

    """
    # get the current directory
    current_dir = os.getcwd()
    # Create a folder for each camera
    for name in config["CAMERAS_NAME"]:
        print("Checking Folder Path:")
        print(current_dir + "/" + name)
        if not os.path.exists(current_dir + "/" + name):
            os.mkdir(current_dir + "/" + name)


def save_image(frames, config):
    """
    Args:
        frames: List of frames to be saved.
        config: Configuration dictionary.

    Returns:
        None

    Description:
        This method saves each frame into its respective camera folder. The name of each saved frame is a timestamp of the form 'year-month-day-hour-minute-second-millisecond'. The frames
    * are saved as JPEG images.
    """
    # saving each frame into each camera folder and the name of frame is timestamp: year-month-day-hour-minute-second-millisecond
    for ix, frame in enumerate(frames):
        if frame is not None:
            cv2.imwrite(f"{config['CAMERAS_NAME'][ix]}/{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}.jpg",
                        frame)
            print(f"Saved frame {ix} into {config['CAMERAS_NAME'][ix]}")


def generate_error_error_frame(config, message):
    """
    Args:
        config: A dictionary containing configuration parameters.
        message: A string representing the error message.

    Returns:
        error_frame: A NumPy array representing the black frame with the error message.

    Raises:
        None
    """
    # Generate a Black frame with error message
    error_frame = np.zeros((config['RES_DROP'].get('HEIGHT'), config['RES_DROP'].get('WIDTH'), 3), np.uint8)
    error_frame[:] = (0, 0, 255)
    text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    text_position = (int((error_frame.shape[1] - text_size[0]) / 2), int((error_frame.shape[0] - text_size[1]) / 2))
    cv2.putText(error_frame, message, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return error_frame


def create_layout(frames, config):
    """
    Args:
        frames: A list of frames to be included in the layout.
        config: A configuration dictionary containing camera indexes and other settings.

    Returns:
        layout: A combined layout of frames.

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
            _, frame = cap.read()
            # Adjust the gamma value to reduce the brightness of the image
            frame = adjust_gamma(frame, gamma=0.5)  # gamma value can be adjusted as needed
            frames.append(frame)
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
    with open("last_time.txt", "w") as file:
        file.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    # (Uncomment for display) Add titles to identify each camera (central top with red color)
    # show_camera_layout(frames, config, camera_error_text)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # (For saving power consumption) Sleep for interval_time seconds
    print(f"Sleeping for {interval_time} seconds")
    time.sleep(interval_time)

cv2.destroyAllWindows()
