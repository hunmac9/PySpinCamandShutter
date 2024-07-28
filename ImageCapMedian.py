import os
import numpy as np
import cv2
from camera_interface import CameraInterface, load_config

def capture_images(cam, num_images=5):
    images = []
    for i in range(num_images):
        try:
            img = cam.capture_image()
            if img is not None:
                images.append(img)
                print(f'Image {i+1} was captured succesfully')
            else:
                print(f'Failed to capture image {i+1}')
        except Exception as e:
            print(f'Exception occurred while capturing image {i+1}: {e}')
    return images

def stack_images_median(images):
    stack = np.stack(images, axis=-1)
    median_image = np.median(stack, axis=-1).astype(np.uint8)
    return median_image

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Image Capture Script')
    parser.add_argument('cam_id', type=int, help='Camera ID to use')
    parser.add_argument('filepath', type=str, help='File path to save the stacked image')
    args = parser.parse_args()

    cam = None
    try:
        cam = CameraInterface(cam_id=args.cam_id)
        config = load_config(cam.serial_number)

        # Capture five images in rapid succession
        images = capture_images(cam, num_images=5)

        if len(images) == 5:
            # Stack images using the median
            median_image = stack_images_median(images)

            # Save the median image
            os.makedirs(os.path.dirname(args.filepath), exist_ok=True)
            cv2.imwrite(args.filepath, median_image)
            print(f'Median image saved successfully to {args.filepath}')
        else:
            print('Failed to capture all five images')

    except Exception as e:
        print(f'Exception occurred: {e}')
    finally:
        if cam:
            try:
                cam.stop_acquisition()
            except Exception as e:
                print(f'Failed to stop acquisition: {e}')
            del cam