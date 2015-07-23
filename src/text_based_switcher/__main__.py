# -*- coding: utf-8 -*-
"""
===================
text_based_switcher
===================

Commandline handling
"""
# Originally written by Jacob Vlijm, see http://askubuntu.com/a/648800/20835

import logging
import optparse
import socket
import subprocess
import sys

from text_based_switcher import __version__, LOG


def main(argv=sys.argv):
    """Main function called from console command
    """
    logging.basicConfig()
    exit_code = 1
    try:
        app = Application(argv)
        app.run()
        exit_code = 0
    except KeyboardInterrupt:
        exit_code = 0
    except Exception as exc:
        LOG.exception(exc)
    sys.exit(exit_code)


class Application(object):
    """The main Application class

    :param argv: The command line as a list as ``sys.argv``
    """
    def __init__(self, argv):
        # ap = argparse.ArgumentParser()
        # ap.add_argument('--version', action='version', version=__version__)
        # self.args = ap.parse_args(args=argv[1:])
        parser = optparse.OptionParser()
        parser.add_option("-a", "--application",
                action="store_false",
                help="Sort on application name")
        parser.add_option("-w", "--workspace",
                action="store_true",
                help="Sort on workspace number")
        parser.add_option("-t", "--window",
                action="store_false",
                help="Sort on window title")

        (options, __) = parser.parse_args()
        self.options = options

    def get_output(self, cmd):
        return subprocess.check_output(["/bin/bash", "-c", cmd]).decode("utf-8")

    def normal_window(self, w_id):
        """ function to distinguish "normal" windows from other types 
        
        (like the desktop etc)
        """
        w_type = self.get_output("xprop -id "+w_id)
        if " _NET_WM_WINDOW_TYPE_NORMAL" in w_type:
            return True
        else:
            return False

    def run(self):
        # analyse viewport data, to be able to calculate relative/absolute position of
        # windows and current viewport.
        xrandr_out = self.get_output("xrandr").split()
        i = xrandr_out.index("current")
        resolution = [
                int(xrandr_out[i+1]),
                int(xrandr_out[i+3].replace(",", ""))]

        wmctrl_out = self.get_output("wmctrl -d").split()
        virtual_resolution = [int(n) for n in wmctrl_out[3].split("x")]
        ws_columns = int(virtual_resolution[0] / resolution[0])
        ws_rows = int(virtual_resolution[1] / resolution[1])

        vector = [int(n) for n in wmctrl_out[5].split(",")]
        current_viewport = int(
                (vector[1]/resolution[1])*ws_columns + 
                (vector[0]/resolution[0])+1)

        # split windowdata by machine name
        machine_name = socket.gethostname()
        window_list = [
                [l.strip() for l in w.split(machine_name)]
                for w in self.get_output("wmctrl -lpG").splitlines()]

        # split first section of window data
        for i, w in enumerate(window_list):
            window_list[i][0] = window_list[i][0].split()

        # filter only "real" windows
        window_list = [w for w in window_list if self.normal_window(w[0][0])]

        # adding the viewport to the window's data
        for window in window_list:
            window.append(
                    self.get_output("ps -p "+window[0][2]+" -o comm=").strip())
            relative_location = [int(n) for n in window[0][3:5]]
            absolute_location = [
                    relative_location[0]+vector[0],
                    relative_location[1]+vector[1]]
            viewport = int(
                    (absolute_location[1]/resolution[1])*ws_columns +
                    (absolute_location[0]/resolution[0])+1)

            if viewport == current_viewport:
                viewport = "*"+str(viewport)
            else:
                viewport = str(viewport)
            if viewport.startswith('-'):
                viewport = viewport.replace('-', '_')
            window.append(viewport)

        # set sorting rules
        if self.options.application:
            window_list.sort(
                    key=lambda x: (x[-2].lower(), x[-1], x[-3].lower()))
        elif self.options.workspace:
            window_list.sort(
                    key=lambda x: (x[-1], x[-3].lower(), x[-2].lower()))
        elif self.options.window:
            window_list.sort(
                    key=lambda x: (x[-3].lower(), x[-1], x[-2].lower()))

        # calculate width and height of the zenity window:
        # height = 140px + 23px per line
        height = str(140+(len(window_list)*23))

        # width = 250px + 8px per character (of the longest window title)
        width = str(250+(max([len(window[-3]) for window in window_list])*8))

        escape = lambda s: s.replace('"', '\\"')

        # define the zenity window's content
        cmd = (u"zenity --list --hide-column=4 --print-column=4 "
                "--title='Window list' "
                "--width=%s "% width +
                "--height=%s "% height +
                "--column='Window name' "
                "--column='Application name' "
                "--column='Workspace' "
                "--column='w_id' " + " ".join(
                    [(" ").join(
                        ['"%s"'% escape(window[-3]), # window title
                         '"%s"'% escape(window[-2]), # application name
                         '"%s"'% escape(window[-1]), # workspace name
                         '"%s"'% escape(window[0][0])]
                         ) for window in window_list]))

        # finally, call the window list
        try:
            w_id = subprocess.check_output(["/bin/bash", "-c", cmd]
                ).decode("utf-8").split("|")[0]
            subprocess.Popen(["wmctrl", "-ia", w_id])
        except subprocess.CalledProcessError:
            pass




if __name__ == '__main__':
    main()
