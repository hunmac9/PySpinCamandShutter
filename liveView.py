import numpy as np
import cv2
import time
import argparse
from camera_interface import CameraInterface, save_config, load_config

def update_exposure(val):
    try:
        cam.set_property("ExposureTime", max(val, cam.get_property_min("ExposureTime")))
        config["ExposureTime"] = val
        save_config(cam.serial_number, config)
    except Exception as e:
        print(e)

def update_gain(val):
    try:
        cam.set_property("Gain", val)
        config["Gain"] = val
        save_config(cam.serial_number, config)
    except Exception as e:
        print(e)

def update_black_level(val):
    try:
        cam.set_property("BlackLevel", val)
        config["BlackLevel"] = val
        save_config(cam.serial_number, config)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Camera Control Script')
    parser.add_argument('cam_id', type=int, help='Camera ID to use')
    args = parser.parse_args()

    try:
        cam = CameraInterface(cam_id=args.cam_id)
        config = load_config(cam.serial_number)

        cv2.namedWindow("Camera Feed")
        # Adding trackbars for adjusting camera settings with initial values from config
        cv2.createTrackbar("Exposure", "Camera Feed", config.get("ExposureTime", int(cam.get_property_min("ExposureTime"))), 13181, update_exposure)
        cv2.createTrackbar("Gain", "Camera Feed", config.get("Gain", 0), 47, update_gain)
        cv2.createTrackbar("Black Level", "Camera Feed", config.get("BlackLevel", 0), 12, update_black_level)

        try:
            while True:
                for attempt in range(3):
                    try:
                        frame = cam.get_frame()
                        if frame.size == 0:
                            continue
                        
                        # Resize the frame to a smaller size
                        resized_frame = cv2.resize(frame, (640, 480))
                        
                        cv2.imshow("Camera Feed", resized_frame)
                        if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
                            break
                        break  # Exit the for loop if successful
                    except PySpin.SpinnakerException as e:
                        if "Stream has been aborted" in str(e):
                            print(f"Attempt {attempt + 1}/3: Stream aborted, retrying...")
                            time.sleep(0.5)
                            cam.restart_acquisition()
                        else:
                            raise e
        finally:
            cam.stop_acquisition()
            del cam
            cv2.destroyAllWindows()
    except Exception as e:
        print(f"An error occurred: {e}")
