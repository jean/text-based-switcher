#!/usr/bin/env python3

# Originally written by Jacob Vlijm, see http://askubuntu.com/a/648800/20835

import subprocess
import socket
import sys

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-a", "--application",
        action="store_true",
        help="Sort on application name")
parser.add_option("-w", "--workspace",
        action="store_true",
        help="Sort on workspace number")
parser.add_option("-t", "--window",
        action="store_true",
        help="Sort on window title")

(options, __) = parser.parse_args()

# list (column) header titles and their (data) position in the produced window data list
cols = [["Workspace", -1], ["Application name", -2] , ["Window name", -3]]

# rearrange columns, depending on the chosen option
if options.application:
    cols = [cols[1], cols[2], cols[0]]
elif options.workspace:
    cols = [cols[0], cols[2], cols[1]]
elif options.window:
    cols = [cols[2], cols[1], cols[0]]

# extract headers, list positions, to be used in the zenity list
col1 = cols[0][0]; i1 = cols[0][1]
col2 = cols[1][0]; i2 = cols[1][1]
col3 = cols[2][0]; i3 = cols[2][1]

# just a helper function
get = lambda cmd: subprocess.check_output([
    "/bin/bash", "-c", cmd
    ]).decode("utf-8")


def normal_window(w_id):
    """ function to distinguish "normal" windows from other types 
    
    (like the desktop etc)
    """
    w_type = get("xprop -id "+w_id)
    if " _NET_WM_WINDOW_TYPE_NORMAL" in w_type:
        return True
    else:
        return False


# analyse viewport data, to be able to calculate relative/absolute position of
# windows and current viewport.
xrandr_out = get("xrandr").split()
i = xrandr_out.index("current")
resolution = [
        int(xrandr_out[i+1]),
        int(xrandr_out[i+3].replace(",", ""))]

wmctrl_out = get("wmctrl -d").split()
virtual_resolution = [int(n) for n in wmctrl_out[3].split("x")]
ws_columns = int(virtual_resolution[0] / resolution[0])
ws_rows = int(virtual_resolution[1] / resolution[1])

vector = [int(n) for n in wmctrl_out[5].split(",")]
current_viewport = int(
        (vector[1]/resolution[1]) * ws_columns + 
        (vector[0]/resolution[0])+1)

# split windowdata by machine name
machine_name = socket.gethostname()
window_list = [
        [l.strip() for l in w.split(machine_name)]
        for w in get("wmctrl -lpG").splitlines()]

# split first section of window data
for i, w in enumerate(window_list):
    window_list[i][0] = window_list[i][0].split()

# filter only "real" windows
window_list = [w for w in window_list if normal_window(w[0][0])]

# adding the viewport to the window's data
for w in window_list:
    w.append(get("ps -p "+w[0][2]+" -o comm=").strip())
    relative_location = [int(n) for n in w[0][3:5]]
    absolute_location = [
            relative_location[0]+vector[0],
            relative_location[1]+vector[1]]
    viewport = int(
            (absolute_location[1]/resolution[1]) * 
            ws_columns +
            (absolute_location[0]/resolution[0])+1)

    if viewport == current_viewport:
        viewport = str(viewport)+"*"
    else:
        viewport = str(viewport)
    w.append(viewport)

# set sorting rules
if options.application:
    window_list.sort(key=lambda x: x[-2])
elif options.workspace:
    window_list.sort(key=lambda x: x[-1])
elif options.window:
    window_list.sort(key=lambda x: x[-3])

# calculate width and height of the zenity window:
# height = 140px + 23px per line
h = str(140+(len(window_list)*23))

# width = 250px + 8px per character (of the longest window title)
w = str(250+(max([len(w[-3]) for w in window_list])*8))

# define the zenity window's content
cmd = (u"zenity --list --hide-column=4 --print-column=4 "
        "--title='Window list' "
        "--width="+w+" "
        "--height="+h+" "
        "--column='"+col1+"' "
        "--column='"+col2+"' "
        "--column='"+col3+"' "
        "--column='w_id' " + 
        (" ").join(
            [(" ").join(
                [
                '"%s"'% w[i1],
                '"%s"'% w[i2],
                '"%s"'% w[i3].replace('-', '_'),
                '"%s"'% w[0][0]]
                ) for w in window_list]
            )
        )


# finally, call the window list
try:
    w_id = subprocess.check_output(["/bin/bash", "-c", cmd]
        ).decode("utf-8").split("|")[0]
    subprocess.Popen(["wmctrl", "-ia", w_id])
except subprocess.CalledProcessError:
    pass
