INSTRUCTIONS FOR WINDOWS

1. Install visual studio code from microsoft. Click the node symbol, and follow the prompts to install git. 
    install 7zip

-----------------------------------------------------------------------------
2. Close and reopen visual studio, click the node button, and click clone repository. Paste https://github.com/hunmac9/PySpinCamandShutter
   into the selected entry box. 
-----------------------------------------------------------------------------
3. Press ctrl+j to open the terminal, type tar -zxvf Python-3.10.14.tgz

-----------------------------------------------------------------------------
Install Visual Studio Code (VSCode) from Microsoft (latest version) and the Spinnaker SDK (tested with version 3.2.0.62, but should work with the latest version).
    For spinnaker, select the Developer SDK during installation and install the C# and C++ libraries.
-----------------------------------------------------------------------------
2. Next, install Python 3.10 from the internet. 64 bit version is preferred. While later versions may work,
   this is the latest version supported by the PySpin wrapper as of 7/24. 
-----------------------------------------------------------------------------
(Optional, if python is being funky) Set the PATH environment variable for the Python installation.

   My Computer > Properties > Advanced System Settings > Environment Variables

   Add the Python installation location to the PATH variable. For example,
   if you installed Python at C:\Python310\, you would add the following entry
   to the PATH variable:

   C:\Python310\<rest_of_path>
-----------------------------------------------------------------------------

3. Configure your Python installation. In VSCode, press control+j. In the command line, run the following
   commands (copy and paste one line at a time) to update and install dependencies for your associated Python version:

   python3.10 -m ensurepip
   python3.10 -m pip install pyenv-win pyserial opencv-python psutil numpy==1.26.4
-----------------------------------------------------------------------------
4. To ensure prerequisites such as drivers and Visual Studio redistributables
   are installed on the system, run the Spinnaker SDK installer that corresponds
   with the PySpin version number. For example, if installing PySpin 3.0.0.0,
   install Spinnaker 3.0.0.0 beforehand, selecting only the Visual Studio
   runtimes and drivers. Please install at least version 4.6
-----------------------------------------------------------------------------
5. Run the following command to install PySpin to your associated Python version. 

   python3.10 -m pip install [path to .whl file, eg, C:/users/documents/spinnaker_python-4.6.x.x-cp310-cp310-win_amd64.whl]

   Ensure that the wheel downloaded matches the Python version you are installing to! (eg cp310 for python 3.10)
-----------------------------------------------------------------------------
6. 