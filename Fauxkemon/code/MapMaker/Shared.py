from ..Map.Character import *
from ..Map.Tile import *

import tkinter as tk

class HelpText(tk.Toplevel):
    
    def __init__(self,text):
        super().__init__()
        self.text=tk.Text(self,wrap='word')
        self.text.pack(fill='both',expand=True)
        self.text.insert('end',text)
        