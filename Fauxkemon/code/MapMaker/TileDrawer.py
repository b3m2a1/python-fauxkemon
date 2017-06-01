from .Shared import *

class TileDrawer:
    def __init__(self,parent):
        self.parent=parent
        self._=parent
        self.event=None
        self.last=None

    def create(self,event):
        t=self._.tiles.tile
        s=self._.tiles.source
        if t=='Select':
            E=self._.ClickGet(event)
            c=self._.map.ClickGet(event)
            self._.selectionBorder.cell[:]=c.pos
            c.border=self._.selectionBorder
            self._.map.AddObject(c.border)
            i,j=c.pos
            if not self._.selected[i,j] is c:
                self._.selected[i,j]=c
                
        elif not t is None:
                    
            E=self.event
            c=self._.ClickGet(event)
            if c!=E:
                self.event=None
                self.create_act(event,t,s)

    def create_act(self,event,t,s):
        E=self._.ClickGet(event)
        if not E is self.last:
            os=E.source
            on=E.name
            E.change_type(t,s)
            self.parent.last_changed.append((E,os,on))
            self.last=E
