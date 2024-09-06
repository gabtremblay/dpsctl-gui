#!/usr/bin/env python

"""
The MIT License (MIT)

Copyright (c) 2024 Gabriel Tremblay (github.com/gtremblay)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

###########
This script is used to communicate with an OpenDPS device and can be used to
change all the settings possible with the buttons and dial on the device
directly. The device can be talked to via a serial interface or (if you added
an ESP8266) via wifi

##############

"""

# Dpsctl related imports
import dpsctl
import copy
from time import sleep
from argparse import Namespace
from typing import Final

# Gui Stuff
import darkdetect
import tkinter
from tkinter import ttk
import sv_ttk
import pywinstyles

# General imports
import sys
import io
from contextlib import redirect_stdout

# Get the args structure dpsctl expect from the command line.
DPSCTL_NAMESPACE: Final = Namespace(device='', baudrate=9600, brightness=None, scan=False, function=None, list_functions=False, 
                             parameter=None, list_parameters=False, calibrate=False, calibration_set=None, calibration_report=False, 
                             calibration_reset=False, enable=None, ping=False, lock=False, unlock=False, query=False, json=False, 
                             verbose=False, version=False, firmware=None, switch_screen=None, force=False)

## Only used in win32
def apply_theme_to_titlebar(root):
    version = sys.getwindowsversion()

    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")

        # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)


# Copy the template namespace object
ping_cmd = copy.deepcopy(DPSCTL_NAMESPACE)

ping_cmd.device = '192.168.1.251'
ping_cmd.ping = True

status_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
status_cmd.device = '192.168.1.251'
status_cmd.query = True
#for i in range(0,200):

# Snoop Stdout output to redirect to GUI.
with io.StringIO() as buf, redirect_stdout(buf):
    dpsctl.handle_commands(status_cmd)
    #    sleep(0.3)
    output = buf.getvalue()
    output += "oksala"

print(output)

    ## Start the Tkinter gui.
root = tkinter.Tk()

# Build the gui.
button = ttk.Button(root, text="Click me!")
button.pack()

# This is where the magic happens
sv_ttk.set_theme(darkdetect.theme())

# Darken titlebar under Windows Dark theme.
if sys.platform == 'win32' and darkdetect.isDark():
    apply_theme_to_titlebar(root)

root.mainloop()