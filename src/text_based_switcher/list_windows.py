#!/usr/bin/env python3
import subprocess
import socket
import sys

arg = sys.argv[1]
# list (column) header titles and their (data) position in the produced window data list
cols = [["Workspace", -1], ["Application name", -2] , ["Window name", -3]]
# rearrange columns, depending on the chosen option
if arg == "-app":
    cols = [cols[1], cols[2], cols[0]]
elif arg == "-ws":
    cols = [cols[0], cols[2], cols[1]]
elif arg == "-win":
    cols = [cols[2], cols[1], cols[0]]
# extract headers, list positions, to be used in the zenity list
col1 = cols[0][0]; i1 = cols[0][1]
col2 = cols[1][0]; i2 = cols[1][1]
col3 = cols[2][0]; i3 = cols[2][1]
# just a helper function
get = lambda cmd: subprocess.check_output([
    "/bin/bash", "-c", cmd
    ]).decode("utf-8")
# analyse viewport data, to be able to calculate relative/absolute position of windows
# and current viewport
def get_spandata():
    xr = get("xrandr").split(); pos = xr.index("current")
    res = [int(xr[pos+1]), int(xr[pos+3].replace(",", "") )]
    spandata = get("wmctrl -d").split()
    span = [int(n) for n in spandata[3].split("x")]
    cols = int(span[0]/res[0]); rows = int(span[1]/res[1])
    curr_vector = [int(n) for n in spandata[5].split(",")]
    curr_viewport = int((curr_vector[1]/res[1])*cols + (curr_vector[0]/res[0])+1)
    return {"resolution": res, "n_columns": cols, "vector": curr_vector, "current_viewport": curr_viewport}

posdata = get_spandata()
vector = posdata["vector"]; cols = posdata["n_columns"]
res = posdata["resolution"]; currvp = posdata["current_viewport"]
# function to distinguish "normal" windows from other types (like the desktop etc)
def check_window(w_id):
    w_type = get("xprop -id "+w_id)
    if " _NET_WM_WINDOW_TYPE_NORMAL" in w_type:
        return True
    else:
        return False
# split windowdata by machine name
mach_name = socket.gethostname()
wlist = [[l.strip() for l in w.split(mach_name)] for w in get("wmctrl -lpG").splitlines()]
# split first section of window data
for i, w in enumerate(wlist):
    wlist[i][0] = wlist[i][0].split()
# filter only "real" windows
real_wlist = [w for w in wlist if check_window(w[0][0]) == True]
# adding the viewport to the window's data
for w in real_wlist:
    w.append(get("ps -p "+w[0][2]+" -o comm=").strip())
    loc_rel = [int(n) for n in w[0][3:5]]
    loc_abs = [loc_rel[0]+vector[0], loc_rel[1]+vector[1]]
    abs_viewport = int((loc_abs[1]/res[1])*cols + (loc_abs[0]/res[0])+1)
    abs_viewport = str(abs_viewport)+"*" if abs_viewport == currvp else str(abs_viewport)
    w.append(abs_viewport)
# set sorting rules
if arg == "-app":
    real_wlist.sort(key=lambda x: x[-2])
elif arg == "-ws":
    real_wlist.sort(key=lambda x: x[-1])
elif arg == "-win":
    real_wlist.sort(key=lambda x: x[-3])
# calculate width and height of the zenity window:
# height = 140px + 23px per line
h = str(140+(len(real_wlist)*23))
# width = 250px + 8px per character (of the longest window title)
w = str(250+(max([len(w[-3]) for w in real_wlist])*8))
# define the zenity window's content
cmd = "zenity --list --hide-column=4 --print-column=4 --title='Window list' "\
      "--width="+w+" --height="+h+" --column='"+col1+"' --column='"+col2+"' --column='"+col3+\
      "' --column='w_id' "+(" ").join([(" ").join([
          '"'+w[i1]+'"','"'+w[i2]+'"','"'+w[i3]+'"','"'+w[0][0]+'"'
          ]) for w in real_wlist])
# finally, call the window list
try:
    w_id = subprocess.check_output(["/bin/bash", "-c", cmd]).decode("utf-8").split("|")[0]
    subprocess.Popen(["wmctrl", "-ia", w_id])
except subprocess.CalledProcessError:
    pass
