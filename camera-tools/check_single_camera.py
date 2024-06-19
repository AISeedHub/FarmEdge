import cv2


class CameraManager:
    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.cap = None

    def start_camera(self):
        open_cam = True

        while True:
            if open_cam and self.cap is None:
                self.cap = cv2.VideoCapture(self.camera_index)
                if not self.cap.isOpened():
                    print("Error: Couldn't open camera.")
                    continue

            if open_cam and self.cap is not None:
                # Read a frame from the camera
                ret, frame = self.cap.read()
                if ret:
                    # Display the frame
                    cv2.imshow('Camera', frame)

            # Break the loop if 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Close camera")
                break

            if open_cam and cv2.waitKey(1) & 0xFF == ord('s'):
                print("Stop camera")
                self.cap.release()
                self.cap = None
                open_cam = False

            if not open_cam and cv2.waitKey(1) & 0xFF == ord('r'):
                print("Re-open camera")
                open_cam = True

    def release_camera(self):
        # Release the camera and close the window
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Create an instance of CameraManager with the desired camera index (default is 0)
    camera_manager = CameraManager(camera_index='/dev/video2')

    # Start the camera
    camera_manager.start_camera()

    # Release the camera when done
    camera_manager.release_camera()




