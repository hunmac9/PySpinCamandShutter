import subprocess
import tkinter as tk
from tkinter import ttk, filedialog
import threading
import multiprocessing as mp
import time
import serial
import configparser

# Read configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

PORT_ARDUINO_ONE = config['Arduino']['PORT_ARDUINO_ONE']
PORT_ARDUINO_TWO = config['Arduino']['PORT_ARDUINO_TWO']
BAUDRATE = int(config['Arduino']['BAUDRATE'])

# Dictionary to keep track of subprocesses and their status by camera ID
camera_processes = {}

# Arduino ports dictionary
PORTS_ARDUINO = {
    0: PORT_ARDUINO_ONE,  # Port for Arduino controlling shutter for Camera 0
    1: PORT_ARDUINO_TWO   # Port for Arduino controlling shutter for Camera 1
}

def initialize_arduino(port):
    try:
        ser = serial.Serial(port, BAUDRATE, timeout=1)
        time.sleep(2)  # Wait for the serial connection to initialize
        return ser
    except Exception as e:
        print(f"Arduino initialization failed for port {port}: {e}")
        return None

def send_command(ser, command):
    try:
        ser.write((command + '\n').encode())
        time.sleep(1)  # Give Arduino time to process the command
        response = ser.readline().decode().strip()
        return response
    except Exception as e:
        print(f"Failed to send command to Arduino: {e}")
        return None

def run_camera_control(cam_id, text_widget, event):
    try:
        # Initialize Arduino for the corresponding camera ID
        arduino_conn = initialize_arduino(PORTS_ARDUINO[cam_id])
        
        if arduino_conn:
            send_command(arduino_conn, 'OPEN')  # Open the laser shutter

        proc = subprocess.Popen(['python', 'liveView.py', str(cam_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        camera_processes[cam_id] = (proc, arduino_conn, False)  # Store the process, Arduino connection and stopped flag
        text_widget.insert(tk.END, f"Camera {cam_id}: Started successfully, going to open live view.\n")

        # Read the output in real-time
        for line in proc.stdout:
            text_widget.insert(tk.END, line)
            if "Camera is disconnected" in line:
                event.set()

        proc.wait()
        if proc.returncode != 0:
            _, _, stopped = camera_processes.get(cam_id, (None, None, False))
            if not stopped:  # Ensure it's not an expected stopped process
                text_widget.insert(tk.END, f"Camera {cam_id} failed to start.\n")
                text_widget.insert(tk.END, proc.stderr.read())
                text_widget.insert(tk.END, f"Camera {cam_id} will not open, please close any open cameras and try again.\n")
    except Exception as e:
        _, _, stopped = camera_processes.get(cam_id, (None, None, False))
        if not stopped:  # Ensure it's not an expected stopped process
            text_widget.insert(tk.END, f"Camera {cam_id} failed with error: {str(e)}\n")

def stop_camera_control(cam_id, text_widget):
    if cam_id in camera_processes:
        proc, arduino_conn, _ = camera_processes[cam_id]
        try:
            camera_processes[cam_id] = (proc, arduino_conn, True)  # Set stopped flag to True
            proc.terminate()
            proc.wait(timeout=5)  # Wait for the process to terminate
            text_widget.insert(tk.END, f"Camera {cam_id}: Stopped successfully.\n")
        except Exception as e:
            text_widget.insert(tk.END, f"Failed to stop Camera {cam_id}: {str(e)}\n")
        finally:
            if arduino_conn:
                send_command(arduino_conn, 'CLOSE')  # Close the laser shutter
                arduino_conn.close()
            del camera_processes[cam_id]

def delayed_start_camera(cam_id, text_widget):
    time.sleep(0.1)  # Add a small delay
    event = mp.Event()
    p = threading.Thread(target=run_camera_control, args=(cam_id, text_widget, event))
    p.start()
    return p, event

def delayed_stop_camera(cam_id, text_widget):
    threading.Thread(target=stop_camera_control, args=(cam_id, text_widget)).start()

def on_camera_button_click(cam_id, text_widget):
    text_widget.insert(tk.END, f"Trying to start camera {cam_id}...\n")
    # Run the subprocess in a separate thread to avoid blocking the GUI
    p, event = delayed_start_camera(cam_id, text_widget)
    # Ensure to handle the disconnection event properly
    def monitor_event():
        event.wait()
        text_widget.insert(tk.END, f"Camera {cam_id} disconnected.\n")
        stop_camera_control(cam_id, text_widget)
    
    threading.Thread(target=monitor_event).start()

def on_stop_camera_button_click(cam_id, text_widget):
    text_widget.insert(tk.END, f"Stopping camera {cam_id}...\n")
    # Stop the subprocess in a separate thread to avoid blocking the GUI
    delayed_stop_camera(cam_id, text_widget)

def launch_interval_capture(cam_id, text_widget):
    text_widget.insert(tk.END, f"Camera {cam_id}: Stopped live capture in order to start interval capture.\n")
    # Stop the camera first
    stop_camera_control(cam_id, text_widget)
    # Launch interval capture
    text_widget.insert(tk.END, f"Launching interval capture for camera {cam_id}...\n")
    threading.Thread(target=lambda: subprocess.Popen(['python', 'intervalGUI.py', str(cam_id)])).start()

def on_closing():
    for cam_id in list(camera_processes.keys()):  # Use list to avoid RuntimeError: dictionary changed size during iteration
        stop_camera_control(cam_id, text_widget)
    root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Camera Control")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Add the text widget below the buttons
    text_widget = tk.Text(frame, width=60, height=20)
    text_widget.grid(row=3, column=0, columnspan=3, pady=10)

    # Create buttons for starting and stopping camera IDs 0 and 1 in a 3x2 format
    button0_start = ttk.Button(frame, text="Start Camera 0", command=lambda: on_camera_button_click(0, text_widget))
    button0_start.grid(row=0, column=0, padx=5, pady=5)

    button0_stop = ttk.Button(frame, text="Stop Camera 0", command=lambda: on_stop_camera_button_click(0, text_widget))
    button0_stop.grid(row=0, column=1, padx=5, pady=5)

    button0_interval = ttk.Button(frame, text="Launch Interval Capture for Camera 0", command=lambda: threading.Thread(target=launch_interval_capture, args=(0, text_widget)).start())
    button0_interval.grid(row=0, column=2, padx=5, pady=5)

    button1_start = ttk.Button(frame, text="Start Camera 1", command=lambda: on_camera_button_click(1, text_widget))
    button1_start.grid(row=1, column=0, padx=5, pady=5)

    button1_stop = ttk.Button(frame, text="Stop Camera 1", command=lambda: on_stop_camera_button_click(1, text_widget))
    button1_stop.grid(row=1, column=1, padx=5, pady=5)

    button1_interval = ttk.Button(frame, text="Launch Interval Capture for Camera 1", command=lambda: threading.Thread(target=launch_interval_capture, args=(1, text_widget)).start())
    button1_interval.grid(row=1, column=2, padx=5, pady=5)

    # Bind the close event to the on_closing function
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
