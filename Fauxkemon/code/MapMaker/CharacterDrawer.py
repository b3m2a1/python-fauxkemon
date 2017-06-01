from .Shared import *

#useless class for now
class CharacterDrawer:
        def __init__(self,parent):
            self.parent=parent
            self._=parent
            self.event=None

        def create(self,event):
            t=self._.chars.char
            if t=='Select':
                E=self._.ClickGet(event)
                c=self._.map.ClickGet(event)
                self._.selectionBorder.cell[:]=c.pos
                c.border=self._.selectionBorder
                self._.map.AddObject(c.border)
                i,j=c.pos
                if not self._.selected[i,j] is c:
                    self._.selected[i,j]=c
                    
##            elif not t is None:
##                def create(event):
##                    E=self._.ClickGet(event)
##                    E.change_type(t)
##                        
##                E=self.event
##                c=self._.ClickGet(event)
##                if c!=E:
##                    self.event=None
##                    create(event)
