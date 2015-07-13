import wx
import wx.grid as gridlib
import math
import  wx.lib.newevent
import os.path
import db
import re
from winmgr import WindowMgr
import handparse

seat_cords = [
    (0.398, 0.680), #0
    (0.175, 0.680), #1
    (0.017, 0.480), #2
    (0.017, 0.295), #3
    (0.260, 0.132), #4
    (0.530, 0.132), #5
    (0.790, 0.295), #6
    (2.000, 2.000), #7
    (0.790, 0.480), #8
    (0.620, 0.680)] #9

class App(wx.App):
    TableUpdateEvent, EVT_TABLE_UPDATE = wx.lib.newevent.NewEvent()
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        self.signal_newtable = False
        self.tables = {}
        return True

# -----------------------------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.NewId(), "Main")
        self.Bind(App.EVT_TABLE_UPDATE, self.OnTableUpdate)

    def OnTableUpdate(self, event):
        if event.src_path in wx.GetApp().tables:
            wx.GetApp().tables[event.src_path].update()
        else:
            wx.GetApp().tables[event.src_path] = (TableMainFrame(event.src_path))
# -----------------------------------------------------------------------------
class TableMainFrame(wx.Frame):
    def __init__(self, src_path):
        #match = re.search('\((\d+)\)', os.path.basename(src_path))
        match = re.search('\w+ (\w+)', os.path.basename(src_path))
        self.id = match.group(1)
        wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.NewId(), 'Table')
        self.players = [None]*10
            
        self.file = open(src_path)
        self.window = WindowMgr(self.id)


        self.boxes = []
        x, y = self.window.get_rect()[0:2]
        self.SetPosition((x,y))
        for i in range(10):
            box = StayOnTopFrame(self, i)
            x_off, y_off = seat_cords[i]

            box.SetPosition((x + x_off, y + y_off))
            self.boxes.append(box)

        self.Show()
        self.on_timer()
        self.update()


    def on_timer(self):
        # delta_pos = wx.Point(*self.window.get_rect()[0:2]) - self.GetPosition()
        # self.Move(self.GetPosition() + delta_pos)
        # for box in self.boxes:
        #     box.Move(box.GetPosition() + delta_pos)
        x, y, w, h = self.window.get_rect()
        w, h = w - x, h - y
        for i,box in enumerate(self.boxes):
            box.SetPosition((
                    int(x + (w*seat_cords[i][0])),
                    int(y + (h*seat_cords[i][1]))
                ))
        wx.CallLater(10, self.on_timer)

    def update(self):
        hand = self.file.readlines()
        players = handparse.parse_hand(hand)
        self.players = [x if x else self.players[i] for i,x in enumerate(players)]
        for seat,box in enumerate(self.boxes):
            box.update(self.players[seat])
# -----------------------------------------------------------------------------
class StayOnTopFrame(wx.Frame):

    def __init__(self, parent, seat):
        """Constructor"""
        wx.Frame.__init__(self, parent, wx.ID_ANY, 'Seat: %s'%seat,
                         style =
                           wx.FRAME_SHAPED
                         | wx.SIMPLE_BORDER
                         | wx.FRAME_NO_TASKBAR
                         | wx.STAY_ON_TOP
                         )
 

        self.seat = seat
        self.delta = (0,0)
        self.Bind(wx.EVT_LEFT_DOWN,     self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP,       self.OnLeftUp)
        self.Bind(wx.EVT_PAINT,         self.OnPaint)
        self.Bind(wx.EVT_MOTION,        self.OnMouseMove)
        self.text1 = 'Empty'
        self.text2 = ''
        img = wx.Image('C:\Users\cyka\Desktop\HUD\images\hud.png', wx.BITMAP_TYPE_PNG)
        self.bmp = wx.BitmapFromImage(img)
        self.SetClientSize((self.bmp.GetWidth(), self.bmp.GetHeight()))
        region = wx.RegionFromBitmapColour(self.bmp, wx.Colour(255, 0, 0, 0))
        self.SetShape(region)
        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0,0, True)

        # panel = wx.Panel(self)
        # panel.Bind(wx.EVT_MOTION, self.OnFrame1Motion)
        # panel.Bind(wx.EVT_LEFT_DOWN, self.OnFrame1Click)
        # panel.Bind(wx.EVT_RIGHT_DOWN, self.OnFrame1Click)
        # self.text = wx.StaticText(panel, label='Placeholder')
        # self.text.Bind(wx.EVT_MOTION, self.OnFrame1Motion)
        # self.text.Bind(wx.EVT_LEFT_DOWN, self.OnFrame1Click)
        # self.text.Bind(wx.EVT_RIGHT_DOWN, self.OnFrame1Click)

        self.Show()

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0,0, True)
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas'))
        dc.SetTextForeground((255,255,255))
        dc.DrawText(self.text1, 0, -1)
        dc.DrawText(self.text2, 0, 16)

    def OnLeftDown(self, evt):
        self.CaptureMouse()
        x, y = self.ClientToScreen(evt.GetPosition())
        originx, originy = self.GetPosition()
        dx = x - originx
        dy = y - originy
        self.delta = ((dx, dy))

    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
    def OnMouseMove(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            x, y = self.ClientToScreen(evt.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.Move(fp)
            print self.seat, self.GetParent().window.get_rect()[:2],self.ClientToScreen(self.GetPosition())

    def update(self, player):
        if player:
            stats = db.get_playerstats(player)
            try:
                self.text1 = '{} {:02d} {:02d} {:02d}'.format(
                    player[:5], stats[3], stats[4], 100*(stats[3]+stats[4])/stats[2])
                self.text2 = '{}'.format(stats[2])
            except:
                self.text1 = player[:5]
                self.text2 = '--'
        else:
            self.text1 = ('Empty')
            self.text2 = ('')
        self.Refresh()
 
#----------------------------------------------------------------------
if __name__ == "__main__":

    app = wx.App(False)
    main = MainFrame()
    frame1 = StayOnTopFrame(main)
    frame1.Move((100,200))

    frame2 = StayOnTopFrame(main)
    frame2.Move((100,200))
    app.MainLoop()
