import cv2


def get_connected_camera_indices(max_attempts=10):
    connected_cameras = []

    for index in range(max_attempts):
        try:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                print(f"Failed to open camera with index {index}")
                continue
            else:
                ret, frame = cap.read()
                if ret:
                    connected_cameras.append(index)
                    # Display the frame
                    cv2.imshow('Camera', frame)
                cap.release()
        except cv2.error as e:
            print(f"OpenCV Error: {e}")

    return connected_cameras


if __name__ == "__main__":
    max_attempts = 30  # Adjust as needed
    connected_cameras = get_connected_camera_indices(max_attempts)

    if not connected_cameras:
        print("No cameras detected.")
    else:
        print("Connected camera indices:", connected_cameras)


