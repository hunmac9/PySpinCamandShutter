# Setup Instructions for Windows

1. **Install the Arduino IDE**
   - Install the Arduino IDE and upload the ServoControl.ino code to each Arduino board.

2. **Install Visual Studio Code (VSCode)**
   - Download and install the latest version of Visual Studio Code from [Microsoft](https://code.visualstudio.com/).
   - Install the Spinnaker SDK and the Windows Python Spinnaker SDK for version 3.10 (tested with version 3.2.0.62, but should work with the latest version).
     - During Spinnaker installation, select the "Developer SDK" option and ensure that both the C# and C++ libraries are installed.
   - Close and reopen Visual Studio Code.
   - Click the "Node" button, then click "Clone Repository."
   - Paste the following URL into the repository entry box: `https://github.com/hunmac9/PySpinCamandShutter`.

3. **Install Python**
   - Download and install Python 3.10.11 (64-bit version is preferred). This is the latest version supported by the PySpin wrapper as of 07/24.
     - You can download Python from the [official Python website](https://www.python.org/).

4. **(Optional) Configure the PATH Environment Variable**
   - If you encounter issues with Python, you may need to set the PATH environment variable:
     - Navigate to: `My Computer > Properties > Advanced System Settings > Environment Variables`.
     - Add the Python installation location to the PATH variable. For example, if Python is installed at `C:\Python310\`, add this entry to the PATH variable:
       - `C:\Python310\`

5. **Install PySpin**
   - Run the following command to install PySpin for your Python version:
     ```sh
     python3.10 -m pip install [path to .whl file, e.g., C:/users/documents/spinnaker_python-4.6.x.x-cp310-cp310-win_amd64.whl]
     ```
     - Ensure that the wheel file matches your Python version (e.g., `cp310` for Python 3.10).

6. **Configure Python Installation in VSCode**
   - In VSCode, press `Ctrl + J` to open the integrated terminal.
   - Run the following commands to update and install necessary Python dependencies:
     ```sh
     python -m pip install pyserial opencv-python psutil matplotlib numpy==1.26.4
     ```

7. **Install Spinnaker SDK Prerequisites**
   - To ensure all prerequisites, such as drivers and Visual Studio redistributables, are installed:
     - Run the Spinnaker SDK installer that corresponds with the PySpin version you are installing. For example, if you are installing PySpin 3.0.0.0, install Spinnaker 3.0.0.0 beforehand and select only the Visual Studio runtimes and drivers.
     - Install at least version 4.6.

8. **Configure Arduino Communication Ports**
   - Open Arduino IDE
      - In the top arduino selection window, beneath each arduino will have the configured COM Ports
         - If, for example, it shows COM5 and COM6, in the config.ini type COM5 for PORT_ARDUINO_ONE
         ```
         PORT_ARDUINO_ONE = COM5
         PORT_ARDUINO_TWO = COM6
         ```

9. **Run main.py script**
   - In VSCode open the PySpinCamandShutter folder, press `Ctrl + J`
      - In the terminal type 
         ```
         python3.10 main.py
         ```
      - If there are any errors or missing dependencies returned, follow instructions to install them.
      - If the program operates the opposite shutter and camera, switch the PORT_ARDUINO_ONE and PORT_ARDUINO_TWO ports.

