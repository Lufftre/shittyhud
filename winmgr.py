import re
import win32gui

class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""
    def __init__ (self, title):
        """Constructor"""
        self.title = title
        self.find_window_wildcard('.*{}.*'.format(title))
        print self.get_rect()

    def find_window(self, class_name, window_name = None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) != None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)

    def get_rect(self):
        return win32gui.GetWindowRect(self._handle)