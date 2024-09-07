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

This script is a crude front-end for OpenDPS dpsctl.
It uses stdout redirect to simplify the implementation to the expense
of a more complex threading management.

"""

# Dpsctl related imports
import copy
import dpsctl
from argparse import Namespace
from time import sleep
from typing import Final

# Gui Stuff
from tkinter import *
from tkinter.ttk import *
from tkextrafont import Font

# Some Windows hacks
import pywinstyles

# General imports
import io
import sys
import threading
from contextlib import redirect_stdout
from datetime import datetime

# Hack to show proper taskbar icon under windows
try: 
    from ctypes import windll # Only exists on Windows.
    myappid = "company.dpsctl-gui.main.app"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError: 
    pass


###################################
# opendps commands
###################################
# Get the args structure dpsctl expect from the command line.
DPSCTL_NAMESPACE: Final = Namespace(device='', baudrate=9600, brightness=None, scan=False, function=None, list_functions=False, 
                             parameter=None, list_parameters=False, calibrate=False, calibration_set=None, calibration_report=False, 
                             calibration_reset=False, enable=None, ping=False, lock=False, unlock=False, query=False, json=False, 
                             verbose=False, version=False, firmware=None, switch_screen=None, force=False)

# Pre-Defined Commands
ping_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
ping_cmd.device = '192.168.1.251'
ping_cmd.ping = True

status_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
status_cmd.device = '192.168.1.251'
status_cmd.query = True

set_pwr_on_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
set_pwr_on_cmd.device = '192.168.1.251'
set_pwr_on_cmd.enable = 'on'

set_pwr_off_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
set_pwr_off_cmd.device = '192.168.1.251'
set_pwr_off_cmd.enable = 'off'

set_cv_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
set_cv_cmd.device = '192.168.1.251'
set_cv_cmd.function = 'cv'

set_cl_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
set_cl_cmd.device = '192.168.1.251'
set_cl_cmd.function = 'cl'

set_cc_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
set_cc_cmd.device = '192.168.1.251'
set_cc_cmd.function = 'cc'

set_funcgen_cmd = copy.deepcopy(DPSCTL_NAMESPACE)
set_funcgen_cmd.device = '192.168.1.251'
set_funcgen_cmd.function = 'funcgen'


# Execute a command and return value to the caller
# We need a lock on this command since the gui thread
# and status update thread can try to get the same stdout 
cmd_lock = threading.Lock()

def send_command(command):
    with io.StringIO() as buf, redirect_stdout(buf):
        # Fetch device status
        dpsctl.handle_commands(command)
        output = buf.getvalue()
        # Make sure we reset the buffer pointer for the next read to overwrite the previous read
        buf.seek(0)
    return output

###################################
# Gui
###################################
root = Tk()
icon = PhotoImage(file="assets\\app.png")
root.iconphoto(True, icon)
root.title("OpenDPS")
root.geometry("250x200")
root.resizable(False, False)

# Running state
is_running = False

# Mode options
selected_mode = StringVar()

# read the optionbox selected and change mode.
def change_mode():
    global is_running  # small hack
    # Always turnoff power output before changing mode
    with cmd_lock:
        send_command(set_pwr_off_cmd)
        is_running = False

    with cmd_lock:
        if selected_mode.get() == 'cv':
            send_command(set_cv_cmd)
        elif selected_mode.get() == 'cl':
            send_command(set_cl_cmd)
        elif selected_mode.get() == 'cc':
            send_command(set_cc_cmd)
        elif selected_mode.get() == 'funcgen':
            send_command(set_funcgen_cmd)

# Flip between running state with the same button
def toggle_running():
    global is_running
    if is_running:
        with cmd_lock:
            send_command(set_pwr_off_cmd)
            is_running = False
    else:
        with cmd_lock:
            send_command(set_pwr_on_cmd)
            is_running = True

# Create a frame to contain our status information
# This frame sets the size and don't use slaves sizes (grid_propagate)
bg_style = Style()
bg_style.configure('blackbg.TFrame', foreground="black", background='black')
status_frame = Frame(root, width=160, height=140, style='blackbg.TFrame')
status_frame.grid_propagate(False)
status_frame.grid(row=0, column=1, pady=10)
status_frame.columnconfigure(1, weight=1)

## This frame contains the mode options
options_frame = LabelFrame(root, text="Mode", width=60, height=140)
options_frame.grid_propagate(False)
options_frame.grid(row=0, column=0, padx=10, pady=10)
options_frame.columnconfigure(0, weight=1)

## Styles
bg_style = Style()
bg_style.configure("statuslbl.TLabel", foreground="gray95", background='black')
bg_err_style = Style()
bg_err_style.configure("status_err_lbl.TLabel", foreground="red", background='black')
bg_active_style = Style()
bg_active_style.configure("status_active_lbl.TLabel", foreground="palegreen1", background='black')

running_style = Style()
running_style.configure("running.TLabel", foreground="green")
stopped_style = Style()
stopped_style.configure("stopped.TLabel", foreground="red")

## Fonts
vi_font = Font(file="assets\\MartianMono.ttf", family='Martian', size=32, weight='bold')
vin_font = Font(family='Martian', size=10, weight='bold')
mode_font = Font(family='Martian', size=14, weight='bold')

## Mode radio buttonss
cv_radio = Radiobutton(options_frame, 
                    text="CV",
                    variable=selected_mode, 
                    command=change_mode,
                    value="cv")
cv_radio.grid(row=0, sticky='sw')

cl_radio = Radiobutton(options_frame, 
                    text="CL",
                    variable=selected_mode, 
                    command=change_mode, 
                    value="cl")
cl_radio.grid(row=1, sticky='sw')

cc_radio = Radiobutton(options_frame, 
                    text="CC",
                    variable=selected_mode, 
                    command=change_mode,
                    value="cc")
cc_radio.grid(row=2, sticky='sw')

func_radio = Radiobutton(options_frame, 
                    text="Func",
                    variable=selected_mode, 
                    command=change_mode,
                    state="disabled",
                    value="funcgen")
func_radio.grid(row=3, sticky='sw')


## Labels
running_label = Label(options_frame, text="Stopped", style='stopped.TLabel')
running_label.grid(row=4, pady=5, sticky='s')

voltage_label = Label(status_frame, text="0.00V", font=vi_font, style='statuslbl.TLabel')
voltage_label.grid(row=0, column=0, columnspan=2, padx=5, sticky='ne')

current_label = Label(status_frame, text="0.000A", font=vi_font, style='statuslbl.TLabel')
current_label.grid(row=1, column=0, columnspan=2, padx=5, sticky='ne')

current_target_label = Label(status_frame, text="0.000A", font=vi_font, style='statuslbl.TLabel')
current_target_label.grid(row=1, column=0, columnspan=2, padx=5, sticky='ne')

mode_label =  Label(status_frame, text="CV", font=mode_font, style='statuslbl.TLabel')
mode_label.grid(row=2, column=0, padx=5, sticky='sw')

vin_label =  Label(status_frame, text="V_in: 0.00V", font=vin_font, style='statuslbl.TLabel')
vin_label.grid(row=2, column=1, padx=6, sticky='se')

err_label =  Label(status_frame, text="", font=vin_font, style='status_err_lbl.TLabel')
err_label.grid(row=1, column=0, columnspan=2)
err_label.grid_remove() # This just saves where it goes

## Toggle Button
pwr_on_style = Style()
pwr_on_style.configure("pwron.TButton", foreground='green')
pwr_off_style = Style()
pwr_off_style.configure("pwroff.TButton", foreground='red')

toggle_button = Button(root, text="Power ON", command=toggle_running)
toggle_button.grid(row=1, column=0, columnspan=2, sticky='s')


def extract_status_values(status_text):
    # Remove the ending \n
    all_lines = status_text.rstrip('\n')

    # Extract necessary Text from Device Status
    all_lines = all_lines.replace(' ', '').split('\n')

    # All lines in all modes are in the format "Key:Value"
    status_vals = dict()  
    for line in all_lines:
        split = line.split(':')
        if len(split) >= 2: # Bug with 'cc' mode.
            status_vals[split[0]] = split[1]

    # Quick hack to add psu_output and clean-up current mode.
    func_str = status_vals['Func']
    if 'on' in func_str:
        status_vals['psu_output'] = True
    else:
        status_vals['psu_output'] = False

    # clean up current function
    status_vals['Func'] = func_str[:func_str.find('(')]
    
    return status_vals


def update_status():
    global selected_mode, is_running
    while True:
        # Fetch status from device
        with cmd_lock:
            output = send_command(status_cmd) 

        # Show error if we don't get the proper text
        if "Func" not in output:
            t_stamp = '[' + datetime.now().strftime('%H:%M:%S') + ']'
            voltage_label.config(text="")
            current_label.config(text="")
            vin_label.config(text="")
            mode_label.config(text="")
            err_label.grid()
            err_label.config(text = t_stamp + " Error Communicating")
        else:
            # Clear Error if present
            err_label.grid_remove()
            err_label.config(text="")

            # Extract All status values
            status_values = extract_status_values(output)

            # Exit if we're in funcgen mode for now.
            if status_values['Func'] == 'funcgen':
                selected_mode.set('funcgen')
                toggle_button.config(state='enabled')
                continue # Unsupported for now
            elif status_values['Func'] == 'cv':
                selected_mode.set('cv')
                cv_radio.configure(value='cv')
                toggle_button.config(state='enabled')
            elif status_values['Func'] == 'cl':
                selected_mode.set('cl')
                toggle_button.config(state='enabled')
            elif status_values['Func'] == 'cc':
                selected_mode.set('cc')
                toggle_button.config(state='disabled')


            # Target voltage in mV (3000 = 3v)
            target_voltage = status_values['voltage']
            fmt_target_voltage = '{0:.2f}V'.format(int(target_voltage)/1000)

            # Target current limit in mA (1500 = 1.5A)
            target_current_limit = status_values['current']
            fmt_target_current_limit = '{0:.3f}A'.format(int(target_current_limit)/1000)

            # DPS input voltage in Volt (With V included)
            dps_input_voltage = status_values['V_in']

            # Voltage output in Volts (With V included)
            output_voltage = status_values['V_out']

            # Current output in Amps (With A included)
            output_current = status_values['I_out']

            # Display output
            vin_label.config(text="V_in: " + dps_input_voltage)

            # Psu is Disabled
            if not status_values['psu_output']:
                # Psu not running
                is_running = False
                running_label.config(text='Stopped', style='stopped.TLabel')

                # Voltage
                voltage_label.config(text=fmt_target_voltage, style="statuslbl.TLabel")
                current_label.config(text=fmt_target_current_limit, style="statuslbl.TLabel")

                # Mode
                if status_values['Func'] == 'cl':
                    mode_label.config(text="CL")
                else:
                    mode_label.config(text=status_values['Func'].upper())

                # Enable Button
                toggle_button.config(text="Power ON")
            else:
                # Psu is running
                is_running = True
                running_label.config(text='Running', style='running.TLabel')

                # Voltage
                voltage_label.config(text=output_voltage, style="status_active_lbl.TLabel")

                # Mode (Show CVCL when running in CL)
                if status_values['Func'] == 'cl':
                    mode_label.config(text="CVCL")
                    current_label.config(text=output_current, style="status_active_lbl.TLabel")
                else:
                    mode_label.config(text=status_values['Func'].upper())
                    current_label.config(text=output_current, style="status_active_lbl.TLabel")

                # Enable Button
                toggle_button.config(text="Power OFF")

        # Give some breath to the controller
        sleep(0.4)

# Start our status update loop
thread = threading.Thread(target=update_status, daemon=True)
thread.start()

# Show the gui
root.mainloop()