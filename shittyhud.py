import ConfigParser
import re
import os.path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
# -------------------------------------------------
import db
import hud
import wx

class MyHandler(FileSystemEventHandler):

    def on_modified(self, event):
        print event.event_type
        evt = hud.App.TableUpdateEvent(src_path=event.src_path)
        wx.PostEvent(wx.GetApp().TopWindow, evt)
        return

if __name__ == '__main__':
    db.create_table()
    app = hud.App(False)
    observer = Observer()
    observer.schedule(MyHandler(), "C:\Users\cyka\AppData\Roaming\PacificPoker\HandHistory\Lufftre")
    observer.start()
    try:
        app.MainLoop()
    finally:
        observer.join()
        print 'done'
