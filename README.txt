INSTRUCTIONS FOR WINDOWS
install the arduino IDE and upload the code to each arduino.
-----------------------------------------------------------------------------
Install Visual Studio Code (VSCode) from Microsoft (latest version) and the Spinnaker SDK and the Windows Python Spinnaker SDK for V3.10 (tested with version 3.2.0.62, but should work with the latest version).
    For spinnaker, select the Developer SDK during installation and install the C# and C++ libraries.2. Close and reopen visual studio, click the node button, and click clone repository. Paste https://github.com/hunmac9/PySpinCamandShutter
   into the selected entry box. 
-----------------------------------------------------------------------------
2. Next, install Python 3.10.11 from the internet. 64 bit version is preferred. While later versions may work,
   this is the latest version supported by the PySpin wrapper as of 7/24. 
-----------------------------------------------------------------------------
(Optional, if python is being funky) Set the PATH environment variable for the Python installation.

   My Computer > Properties > Advanced System Settings > Environment Variables

   Add the Python installation location to the PATH variable. For example,
   if you installed Python at C:\Python310\, you would add the following entry
   to the PATH variable:

   C:\Python310\<rest_of_path>
-----------------------------------------------------------------------------
5. Run the following command to install PySpin to your associated Python version. 

   python3.10 -m pip install [path to .whl file, eg, C:/users/documents/spinnaker_python-4.6.x.x-cp310-cp310-win_amd64.whl]

   Ensure that the wheel downloaded matches the Python version you are installing to! (eg cp310 for python 3.10)
-----------------------------------------------------------------------------

3. Configure your Python installation. In VSCode, press control+j. In the command line, run the following
   commands (copy and paste one line at a time) to update and install dependencies for your associated Python version:

   python -m ensurepip
   python -m pip install pyserial opencv-python psutil matplotlib numpy==1.26.4
-----------------------------------------------------------------------------
4. To ensure prerequisites such as drivers and Visual Studio redistributables
   are installed on the system, run the Spinnaker SDK installer that corresponds
   with the PySpin version number. For example, if installing PySpin 3.0.0.0,
   install Spinnaker 3.0.0.0 beforehand, selecting only the Visual Studio
   runtimes and drivers. Please install at least version 4.6
-----------------------------------------------------------------------------
