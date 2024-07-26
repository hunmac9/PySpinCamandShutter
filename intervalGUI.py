import gc
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import time
import threading
import os
import psutil
from datetime import datetime
import serial
import configparser
import argparse

class IntervalCaptureApp:
    def __init__(self, root, cam_id):
        # Initialization code (unchanged)
        self.max_retries = 5
        self.initial_retry_sleep_time = 1  # Initial sleep time before the first retry (in seconds)
        self.max_retry_sleep_time = 30  # Maximum sleep time between retries (in seconds)


        self.root = root
        self.root.title(f"Interval Capture - Camera {cam_id}")

        self.cam_id = cam_id
        self.is_running = False
        self.image_count = 0
        self.total_images = 0
        self.captured_images = 0
        self.manual_shutter_control = False

        self.interval_var = tk.DoubleVar(value=1.0)
        self.duration_var = tk.DoubleVar(value=1.0)
        self.laser_shutter_var = tk.DoubleVar(value=1.0)
        self.output_dir = tk.StringVar(value='./output')
        self.base_name = tk.StringVar(value='image_')

        # Load config
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # Initialize Arduino
        self.serial_conn = self.initialize_arduino()
        if not self.serial_conn:
            messagebox.showerror("Arduino Error", "Failed to initialize Arduino. Please check the connection.")

        # Interval input
        ttk.Label(root, text="Capture Interval (minutes):").grid(row=0, column=0, sticky=tk.W)
        self.interval_entry = ttk.Entry(root, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)

        # Duration input
        ttk.Label(root, text="Test Duration (hours):").grid(row=1, column=0, sticky=tk.W)
        self.duration_entry = ttk.Entry(root, textvariable=self.duration_var, width=10)
        self.duration_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)

        # Laser shutter exposure input
        ttk.Label(root, text="Laser Shutter Exposure (seconds):").grid(row=2, column=0, sticky=tk.W)
        self.laser_shutter_entry = ttk.Entry(root, textvariable=self.laser_shutter_var, width=10)
        self.laser_shutter_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        self.laser_shutter_var.trace('w', self.update_laser_shutter_time)

        # Output folder
        ttk.Label(root, text="Output Folder:").grid(row=3, column=0, sticky=tk.W)
        self.output_entry = ttk.Entry(root, textvariable=self.output_dir, width=40)
        self.output_entry.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        self.browse_button = ttk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=3, column=2, pady=5, padx=5, sticky=tk.W)

        # Base file name
        ttk.Label(root, text="Base File Name:").grid(row=4, column=0, sticky=tk.W)
        self.base_name_entry = ttk.Entry(root, textvariable=self.base_name, width=40)
        self.base_name_entry.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)

        # Progress indicator
        self.progress_label = ttk.Label(root, text="Captured 0 of 0 images")
        self.progress_label.grid(row=5, column=0, columnspan=3, pady=5, padx=5)

        # Button frame
        self.button_frame = ttk.Frame(root)
        self.button_frame.grid(row=6, column=0, columnspan=3, pady=5, padx=5)

        # Start and stop buttons
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_capture)
        self.start_button.grid(row=0, column=0, pady=5, padx=2)
        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_capture)
        self.stop_button.grid(row=0, column=1, pady=5, padx=2)
        self.stop_button.state(["disabled"])

        # Manual control buttons
        self.open_shutter_button = ttk.Button(self.button_frame, text="Open Shutter", command=self.manual_open_shutter)
        self.open_shutter_button.grid(row=0, column=2, pady=5, padx=2)

        self.close_shutter_button = ttk.Button(self.button_frame, text="Close Shutter", command=self.manual_close_shutter)
        self.close_shutter_button.grid(row=0, column=3, pady=5, padx=2)

        # Indicator light
        self.indicator = tk.Canvas(self.button_frame, width=20, height=20, bg="grey")
        self.indicator.grid(row=0, column=4, pady=5, padx=2)

        # Handle close button
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def browse_folder(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get(), title="Select Output Folder")
        if directory:
            self.output_dir.set(directory)

    def initialize_arduino(self):
        try:
            port = self.config.get('Arduino', 'PORT_ARDUINO_ONE') if self.cam_id == 0 else self.config.get('Arduino', 'PORT_ARDUINO_TWO')
            baudrate = self.config.getint('Arduino', 'BAUDRATE')
            ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for the serial connection to initialize
            print('Arduino initialized')
            return ser
        except Exception as e:
            print(f"Arduino initialization failed: {e}")
            return None

    def send_command(self, command):
        try:
            self.serial_conn.write((command + '\n').encode())
            time.sleep(1)  # Give Arduino time to process the command
            response = self.serial_conn.readline().decode().strip()
            return response
        except Exception as e:
            print(f"Failed to send command to Arduino: {e}")
            return None

    def start_capture(self):
        try:
            interval = self.interval_var.get()
            duration = self.duration_var.get()
            self.laser_shutter_time = self.laser_shutter_var.get()  # Set initial laser shutter time
            if interval <= 0 or duration <= 0 or self.laser_shutter_time <= 0:
                raise ValueError("Interval, duration, and laser shutter exposure must be greater than zero.")

            self.is_running = True
            self.image_count = 0
            self.total_images = int(duration * 60 / interval)
            self.captured_images = 0

            self.start_button.state(["disabled"])
            self.stop_button.state(["!disabled"])

            self.progress_label.config(text=f"Captured {self.captured_images} of {self.total_images} images")
            self.set_indicator("green")

            # Start the interval capture
            self.capture_thread = threading.Thread(target=self.interval_capture, args=(interval,))
            self.capture_thread.start()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def stop_capture(self):
        self.is_running = False
        self.start_button.state(["!disabled"])
        self.stop_button.state(["disabled"])
        self.set_indicator("red")
        self.progress_label.config(text=f"Capture stopped, {self.captured_images} pictures captured")
        print("Capture stopped by user.")

    def interval_capture(self, interval):
        while self.is_running and self.captured_images < self.total_images:
            start_time = time.time()
            self.manage_shutter_and_capture()
            self.captured_images += 1
            self.progress_label.config(text=f"Captured {self.captured_images} of {self.total_images} images")
            elapsed_time = time.time() - start_time
            sleep_time = max(0, interval * 60 - elapsed_time)
            # Adjust for interval in minutes
            for _ in range(int(sleep_time)):
                if self.is_running:
                    time.sleep(1)
                else:
                    print("Capture process interrupted by stop request.")
                    break
        if self.captured_images >= self.total_images:
            self.progress_label.config(text=f"Experiment Complete, {self.captured_images} pictures captured")
        if not self.is_running:
            self.progress_label.config(text=f"Capture stopped, {self.captured_images} pictures captured")

    def manage_shutter_and_capture(self):
        delay_before_capture = self.laser_shutter_time - 1

        if delay_before_capture <= 0:
            delay_before_capture = 0

        if self.serial_conn:
            # Open the laser shutter
            self.send_command("OPEN")
            # Delay to let the laser expose
            time.sleep(delay_before_capture)
        else:
            print("Arduino connection not available, skipping the shutter control.")
    
        # Capture image with retry logic
        self.capture_single_image()

        if self.serial_conn:
            # Close the laser shutter
            self.send_command("CLOSE")

    def capture_single_image(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name = f"{self.base_name.get()}_{timestamp}.tiff"
        filepath = os.path.join(self.output_dir.get(), file_name)

        retry_sleep_time = self.initial_retry_sleep_time
        for attempt in range(1, self.max_retries + 1):
            # Check available memory
            memory_info = psutil.virtual_memory()
            if memory_info.available < 100 * 1024 * 1024:  # Less than 100MB available
                print(f"Memory low, waiting {retry_sleep_time} seconds before retrying...")
                time.sleep(retry_sleep_time)
                retry_sleep_time = min(retry_sleep_time * 2, self.max_retry_sleep_time)
                continue

            try:
                result = subprocess.run(
                    ['python3.10', 'imageCap.py', str(self.cam_id), filepath],
                    check=True,  # This ensures that an exception is raised for non-zero exit codes.
                    capture_output=True,  # This captures stdout and stderr if needed.
                    text=True
                )
                print("Image captured successfully.")
                if os.path.isfile(filepath):
                    print(f'Image {filepath} captured successfully.')
                    break  # Break the loop if the capture was successful
            except subprocess.CalledProcessError as e:  # Specific error handling
                if "Spinnaker::Exception" in e.stderr:
                    print(f"Ignoring known issue on attempt {attempt}: {e.stderr.splitlines()[0]}")
                    if os.path.isfile(filepath):
                        print(f'Image {filepath} captured successfully despite the error.')
                        break  # Break the loop if the image file exists
                    else:
                        print('Capture failed, but ignoring as per request.')
                        break
            except Exception as e:  # Other exceptions
                print(f"Attempt {attempt} failed: {str(e)}")
                if attempt >= self.max_retries:
                    print(f"Capture failed after {attempt} attempts. Moving to next capture or stopping if this is the last one.")
                else:
                    print(f"Retrying capture ({attempt}/{self.max_retries}) after error: {str(e)}")
                gc.collect()
                print(f"Waiting {retry_sleep_time} seconds before retrying...")
                time.sleep(retry_sleep_time)  # Wait briefly before retrying
                retry_sleep_time = min(retry_sleep_time * 2, self.max_retry_sleep_time)  # Exponential backoff, capped at max_retry_sleep_time

    def update_laser_shutter_time(self, *args):
        # Update the laser shutter time
        self.laser_shutter_time = self.laser_shutter_var.get()

    def manual_open_shutter(self):
        if self.serial_conn and not self.is_running:
            self.send_command("OPEN")
            self.manual_shutter_control = True

    def manual_close_shutter(self):
        if self.serial_conn and not self.is_running:
            self.send_command("CLOSE")
            self.manual_shutter_control = False

    def set_indicator(self, color):
        self.indicator.config(bg=color)

    def on_closing(self):
        if self.is_running:
            if messagebox.askokcancel("Quit", "Interval capture is running. Are you sure you want to quit?"):
                self.stop_capture()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interval Capture GUI')
    parser.add_argument('cam_id', type=int, help='Camera ID to use')
    args = parser.parse_args()

    root = tk.Tk()
    app = IntervalCaptureApp(root, args.cam_id)
    root.mainloop()