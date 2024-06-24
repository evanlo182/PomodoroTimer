This app is currently in the process of being uploaded to the Mac App Store, and is only available for Mac currently.
In the meantime, to use this as a standalone Mac app, here are the steps.

If you don't have an installation of Python, download and follow the instructions for that here: https://www.python.org/downloads/

Install pip if you don't already have it installed: https://pip.pypa.io/en/stable/installation/

Then, open a terminal and tyoe the command `pip install customtkinter pygame requests`

After that, ensure all code in the repository is in the same folder, and in the terminal, enter the command `python3 setup.py py2app`. 

Once that is complete, the built app should be in the `dist` folder generated from the last command. Open this file, and copy it to the `Applications` folder on your Mac.

Open the app and enjoy!
