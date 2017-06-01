
import tkinter as tk
from Fauxkemon.code.GameInterface.GameScreen import *

class GameRoot(tk.Tk):
    
    class ChildTracker(dict):
        def __init__(self,parent,child_dict=None):
            if child_dict is None:
                child_dict={}
            self.parent=parent
            super().__init__(**child_dict)
        def __setitem__(self,key,value):
            super().__setitem__(key,value)
        def __delitem__(self,key):
            super().__delitem__(key)
            self.parent.destroy_proc()            
        @property
        def widgets(self):
            return [v for x,v in self.items()]
        
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.withdraw()
        self.children=self.ChildTracker(self)
        top=tk.Toplevel(self)
        self.game_screen=GameScreen(top);top.title('Fauxkemon')
        self.game_screen.pack(fill='both',expand=True)
        
    def destroy_proc(self):
        for c in self.children.values():
            if c.winfo_exists():
                break
        else:
            self.destroy()
            self.quit()
    
    def destroy(self):
        vals=tuple(self.children.values())
        for c in vals:
            try:
                c.destroy()
            except:
                pass
        try:
            super().destroy()
        except:
            pass
        
