"""
Plugin that allows the aenea server to spawn a new Tkinter app that enumerates
the open windows for the desktop.  Each window is assigned a letter of the
alphabet so that the user may bring any one of up to 52 open windows to the
foreground.  Also includes a plugin to bring the dragon vm window to the
foreground.

TODO:   Enable window switching by executable name to avoid the delay associated
        with dictating "window select" wait... "<window letter>" wait...
"""

from Tkconstants import END
from Tkinter import Tk, Listbox
import re
import threading
from wmctrl import Window
from string import letters
from yapsy.IPlugin import IPlugin
from subprocess import call

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
                window = self.windows[i]
                letter = letters[i]
                new_title = '%s - %s' % (letter, window.wm_name)
                self.set_window_title(window, new_title)
                self.insert(END, new_title)

    def key_handler(self, event):
        index = letters.find(event.char)
        if index > -1:
            event.widget.windows[index].activate()
            self.restore_window_titles()
            event.widget.master.destroy()

    def set_window_title(self, window, title):
        call(['wmctrl', '-i', '-r', window.id, '-T', title])

    def restore_window_titles(self):
        for i in range(0, len(self.windows)):
            window = self.windows[i]
            self.set_window_title(window, window.wm_name)


class WindowSelectApplication(object):
    def __init__(self):
        super(WindowSelectApplication, self).__init__()
        self.tk = Tk()
        self.tk.wm_title('window-select')
        self.list_widget = WindowSelectListbox(self.tk, width=100)
        self.list_widget.pack()
        self.list_widget.focus_set()

    def start(self):
        self.tk.mainloop()


class WmctrlPlugin(IPlugin):
    """
    Function that launches a window that enumerates desktop windows.  A letter
    is assigned to each open window.  Pressing a letter key will bring the
    corresponding window to the foreground.

    Function that brings the windows vm running dragon to the foreground.
    """
    def register_rpcs(self, server):
        server.register_function(self.window_select)
        server.register_function(self.show_dragon)

    @staticmethod
    def window_select():
        threading.Thread(
            target=lambda: WindowSelectApplication().start()
        ).start()

    @staticmethod
    def show_dragon():
        windows = Window.list()
        pattern = re.compile('.* - Oracle VM VirtualBox.*')
        windows = [w for w in windows if pattern.match(w.wm_name)]
        if len(windows) > 0:
            windows[0].activate()
