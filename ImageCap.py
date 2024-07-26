import os
from camera_interface import CameraInterface, load_config

def capture_image(cam, filepath):
    success = 0
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    cam.capture_image(filepath)
    if os.path.isfile(filepath):
        print('image captured sucessfully')
        success = 1
    else:
        print('error in image capturing logic')
    return success

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Image Capture Script')
    parser.add_argument('cam_id', type=int, help='Camera ID to use')
    parser.add_argument('filepath', type=str, help='File path to save the captured image')
    args = parser.parse_args()

    try:
        cam = CameraInterface(cam_id=args.cam_id)
        config = load_config(cam.serial_number)

        # Capture a single image
        capture_image(cam, args.filepath)

    finally:
        cam.stop_acquisition()
        del cam
