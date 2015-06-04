"""
Plugin that allows the aenea server to spawn a new Tkinter app that enumerates
the open windows for the desktop.  Each window is assigned a letter of the alphabet
so that the user may bring any one of up to 52 open windows to the foreground.

NOTE:   Requires that the system's NATIVE python interpreter can run this file
        from outside of the aenea server.

TODO:   Enable window switching by executable name to avoid the delay associated
        with dictating "window select" wait... "<window letter>" wait...
"""

from Tkconstants import END
from Tkinter import Tk, Listbox
import os
import subprocess
from wmctrl import Window
from string import letters
from yapsy.IPlugin import IPlugin


enabled = True


class WindowSelectListbox(Listbox):
    def __init__(self, parent, **kwargs):
        Listbox.__init__(self, parent, **kwargs)
        self.windows = []
        self._update_windows()
        self.bind('<Key>', self.key_handler)

    def _update_windows(self):
        self.windows = Window.list()
        self.delete(0, END)

        for i in range(0, len(self.windows)):
            if not i > len(letters):
                list_item = '%s - %s' % (letters[i], self.windows[i].wm_name)
                self.insert(END, list_item)

    @staticmethod
    def key_handler(event):
        index = letters.find(event.char)
        if index > -1:
            event.widget.windows[index].activate()
            event.widget.master.destroy()


class WindowSelectApplication():
    def __init__(self):
        self.tk = Tk()
        self.tk.wm_title('window-select')
        self.list_widget = WindowSelectListbox(self.tk, width=100)
        self.list_widget.pack()
        self.list_widget.focus_set()

    def start(self):
        self.tk.mainloop()


def launch_app():
    subprocess.Popen(['/usr/bin/python', os.path.realpath(__file__)])


class WindowSelectPlugin(IPlugin):
    def register_rpcs(self, server):
        server.register_function(launch_app)


if __name__ == '__main__':
    app = WindowSelectApplication()
    app.start()
