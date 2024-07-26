import numpy as np
import cv2
import PySpin
import os
import json
import time

CONFIG_FILE = "camera_config.json"

def save_config(serial_number, config):
    all_configs = load_all_configs()
    all_configs[serial_number] = config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(all_configs, f, indent=4)

def load_all_configs():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def load_config(serial_number):
    all_configs = load_all_configs()
    return all_configs.get(serial_number, {
        "ExposureTime": 0,
        "Gain": 0,
        "BlackLevel": 0
    })

class CameraInterface:
    def __init__(self, cam_id=0, config=None):
        self.system = PySpin.System.GetInstance()
        self.camera_list = self.system.GetCameras()
        self.num_cameras = self.camera_list.GetSize()
        
        # Print list of available cameras
        self.list_cameras()
        
        # Validate the cam_id
        if cam_id < 0 or cam_id >= self.num_cameras:
            raise IndexError(f"Camera ID {cam_id} is out of bounds. Available cameras: {self.num_cameras - 1}")

        self.camera = self.camera_list[cam_id]
        self.camera.Init()
        self.node_map = self.camera.GetNodeMap()

        # Get the camera's serial number
        nodemap_tldevice = self.camera.GetTLDeviceNodeMap()
        self.serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber')).GetValue()

        # Turn off auto settings and gamma
        self.set_auto_settings_off()
        
        # Set camera to continuous mode
        self.camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        
        # Apply the configuration settings
        if config:
            self.apply_config(config)
        
        self.start_acquisition()

    def list_cameras(self):
        print("Connected Cameras:")
        for i, cam in enumerate(self.camera_list):
            nodemap_tldevice = cam.GetTLDeviceNodeMap()
            device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber')).GetValue()
            device_model_name = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceModelName')).GetValue()
            print(f"{i}: {device_model_name} (Serial: {device_serial_number})")

    def set_auto_settings_off(self):
        settings = {
            "ExposureAuto": "Off",
            "GainAuto": "Off",
            "GammaEnabled": "False"
        }

        for prop, value in settings.items():
            try:
                self.set_property(prop, value)
                print(f"Set {prop} to {value}")
            except Exception as e:
                print(f"Failed to set {prop}: {e}")

    def set_property(self, prop, value):
        node = self.node_map.GetNode(prop)
        
        if not PySpin.IsAvailable(node) or not PySpin.IsWritable(node):
            raise Exception(f"Unable to set {prop}")
        
        if node.GetPrincipalInterfaceType() == PySpin.intfIFloat:
            value_node = PySpin.CFloatPtr(node)
            value_node.SetValue(value)
        elif node.GetPrincipalInterfaceType() == PySpin.intfIEnumeration:
            value_node = PySpin.CEnumerationPtr(node)
            node_entry = value_node.GetEntryByName(value)
            value_node.SetIntValue(node_entry.GetValue())
        elif node.GetPrincipalInterfaceType() == PySpin.intfIInteger:
            value_node = PySpin.CIntegerPtr(node)
            value_node.SetValue(value)
        elif node.GetPrincipalInterfaceType() == PySpin.intfIBoolean:
            value_node = PySpin.CBooleanPtr(node)
            value_node.SetValue(value == "True" or value is True)

    def get_property_min(self, prop):
        node = self.node_map.GetNode(prop)
        if not PySpin.IsAvailable(node):
            raise Exception(f"Property {prop} is not available")
        if node.GetPrincipalInterfaceType() == PySpin.intfIFloat:
            return PySpin.CFloatPtr(node).GetMin()
        elif node.GetPrincipalInterfaceType() == PySpin.intfIInteger:
            return PySpin.CIntegerPtr(node).GetMin()
        else:
            raise Exception(f"Property {prop} does not have a minimum value")

    def start_acquisition(self):
        self.camera.BeginAcquisition()

    def stop_acquisition(self):
        self.camera.EndAcquisition()

    def restart_acquisition(self):
        self.stop_acquisition()
        self.camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.start_acquisition()

    def get_frame(self):
        image = self.camera.GetNextImage()
        if image.IsIncomplete():
            print('Image incomplete with image status {0}...'.format(image.GetImageStatus()))
            return np.ndarray((0, 0))
        frame = image.GetNDArray()
        image.Release()
        return frame

    def capture_image(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.stop_acquisition()
        self.camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
        for attempt in range(3):
            try:
                self.start_acquisition()
                print('Acquisition started successfully')
                break  # Exit the loop if the acquisition starts successfully
            except Exception as e:
                if attempt == 2:  # Last attempt
                    print(f'Failed to start acquisition after 3 attempts: {e}')
                    # Optionally raise the exception or handle it as needed
                else:
                    print(f'Failed to start acquisition (attempt {attempt + 1}/3), trying again in 0.5 seconds...')
                    time.sleep(0.5)
        frame = self.get_frame()
        self.stop_acquisition()
        cv2.imwrite(filename, frame)
        print(f"Image saved to {filename}")
        self.camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.start_acquisition()

    def apply_config(self, config):
        for prop, value in config.items():
            try:
                self.set_property(prop, value)
                print(f"Loaded {prop} with value {value}")
            except Exception as e:
                print(f"Failed to load {prop}: {e}")

    def __del__(self):
        try:
            if hasattr(self, 'camera') and self.camera is not None:
                if self.camera.IsStreaming():
                    self.stop_acquisition()
                self.camera.DeInit()
        except Exception as e:
            print(f"Exception during camera de-initialization: {e}")
        finally:
            if hasattr(self, 'camera_list') and self.camera_list is not None:
                self.camera_list.Clear()
            if hasattr(self, 'system') and self.system is not None:
                self.system.ReleaseInstance()
