import wx
import wx.grid as gridlib
import math
import  wx.lib.newevent
import os.path
import db
import re
from winmgr import WindowMgr

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
    origo = (960,540)
    delta_rad = 2*math.pi / 10
    def __init__(self, src_path):
        #match = re.search('\((\d+)\)', os.path.basename(src_path))
        match = re.search('\w+ (\w+)', os.path.basename(src_path))
        self.id = match.group(1)
        wx.Frame.__init__(self, wx.GetApp().TopWindow, wx.NewId(), 'Table')
        self.boxes = []
        self.players = [None]*10
        angle = 0
        self.origo = self.GetPositionTuple()
        for i in range(10):
            radius = 200 + 50*abs(math.cos(angle))
            box = StayOnTopFrame(self)
            delta_pos = int(radius*math.cos(angle)), int(radius*math.sin(angle))
            x, y = map(sum,zip(self.origo, delta_pos))
            box.MoveXY(x, y)
            self.boxes.append(box)
            angle += self.delta_rad
            
        self.Show()
        self.file = open(src_path)
        self.window = WindowMgr(self.id)
        self.on_timer()

    def on_timer(self):
        delta_pos = wx.Point(*self.window.get_rect()[0:2]) - self.GetPosition()
        #print delta_pos
        self.Move(self.GetPosition() + delta_pos)
        for box in self.boxes:
            box.Move(box.GetPosition() + delta_pos)
        wx.CallLater(10, self.on_timer)

    def update(self):
        hand = self.file.readlines()
        players = handparse.parse_hand(hand)
        self.players = [x if x else self.players[i] for i,x in enumerate(players)]
        for seat,box in enumerate(self.boxes):
            box.update(self.players[seat])
# -----------------------------------------------------------------------------
class StayOnTopFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        on_top = (
        	wx.MINIMIZE_BOX |
        	wx.MAXIMIZE_BOX |
        	wx.SYSTEM_MENU |
        	wx.CLOSE_BOX |
        	#wx.RESIZE_BORDER |
        	wx.CLIP_CHILDREN |
        	wx.STAY_ON_TOP)

        wx.Frame.__init__(
        	self,
        	parent,
        	title="Stay on top2",
        	style=on_top
        	)
 
        self.lastMousePos = (0, 0)
        panel = wx.Panel(self)
        panel.Bind(wx.EVT_MOTION, self.OnFrame1Motion)
        panel.Bind(wx.EVT_LEFT_DOWN, self.OnFrame1Click)
        panel.Bind(wx.EVT_RIGHT_DOWN, self.OnFrame1Click)
        self.SetSizeWH(100,50)
        
        self.text = wx.StaticText(panel, label='Placeholder')
        self.text.Bind(wx.EVT_MOTION, self.OnFrame1Motion)
        self.text.Bind(wx.EVT_LEFT_DOWN, self.OnFrame1Click)
        self.text.Bind(wx.EVT_RIGHT_DOWN, self.OnFrame1Click)

        self.Show()

    def OnFrame1Motion(self, event):
        if event.LeftIsDown():
	        x, y = wx.GetMousePosition()
	        x_cur, y_cur = self.GetScreenPosition()
	        delta_x, delta_y = x-self.lastMousePos[0],y-self.lastMousePos[1]
	        self.lastMousePos = x,y
	        new_x, new_y = x_cur + delta_x, y_cur + delta_y
        	self.MoveXY(new_x,new_y)
    	elif event.RightIsDown():
	        x, y = wx.GetMousePosition()
	        delta_x, delta_y = x-self.lastMousePos[0],y-self.lastMousePos[1]
	        for child in self.GetParent().GetChildren():
		        x_cur, y_cur = child.GetScreenPosition()
		        new_x, new_y = x_cur + delta_x, y_cur + delta_y
	        	child.MoveXY(new_x,new_y)
        	self.lastMousePos = x,y

        event.Skip()
    def OnFrame1Click(self, event):
    	self.lastMousePos = wx.GetMousePosition()

    def update(self, player):
        if player:
            stats = db.get_playerstats(player)
            #print stats
            self.text.SetLabel('{} {} {} {}%\n00 00 00'.format(player[:4],stats[2],stats[3], 100*stats[3]/stats[2]))
        else:
            self.text.SetLabel('Empty')
 
#----------------------------------------------------------------------
if __name__ == "__main__":

    app = wx.App(False)
    main = MainFrame()
    frame1 = StayOnTopFrame(main)
    frame1.Move((100,200))

    frame2 = StayOnTopFrame(main)
    frame2.Move((100,200))
    app.MainLoop()
