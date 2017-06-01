from . import *
from GeneralTools import open_file

editor_help_text='''This is the general Data Editor

Pokemon, tiles, attacks, and items can be edited here

Choose a game version with the top-most option menu and a data type with the one below it

The current file can be opened with the 'Open File' button and the directory with 'Open Directory'


'''
class FileBrowser(tk.Frame):

    dir_choices=('Pokemon','Tiles','Characters','Attacks','Items')
    props_dirs=('Pokemon','Tiles','Characters')
    game_choices=available_game_versions
    dir_map={k:getdir(k.replace(' ','_').lower()) for k in dir_choices}
    def __init__(self,root,**kw):
    
        super().__init__(root,**kw)
        self.root=self.master.master
        self.file_text=RichText(self,bd=2,relief='groove',highlightthickness=0)
        self.browser_bar=tk.Frame(self,bd=1,bg='black')
        self.button_bar=tk.Frame(self,bd=1,bg='black')
        self.file_text.grid(row=0,column=1,sticky='nsew')
        self.browser_bar.grid(row=0,column=0,rowspan=2,sticky='nsew')
        self.button_bar.grid(row=1,column=1,sticky='nsew')
        
        
        self.game=tk.StringVar(self,value=self.game_choices[0])
        self.game_chooser=tk.OptionMenu(self.browser_bar,self.game,*self.game_choices)
        self.game_chooser.grid(row=0,column=0,sticky='nsew')
        self.dir=tk.StringVar(self,value=self.dir_choices[0])
        self.dir_chooser=tk.OptionMenu(self.browser_bar,self.dir,*self.dir_choices)
        self.dir_chooser.grid(row=1,column=0,sticky='nsew')
        self.file_choices=tk.Listbox(self.browser_bar)
        self.file_choices.grid(row=2,column=0,sticky='nsew')
        self.browser_bar.grid_rowconfigure(2,weight=1)
        self._dir=None
        self._file=None
        
        self.dir_button=CustomButton(self.button_bar,text='Open Directory',command=self.open_dir)
        self.fil_button=CustomButton(self.button_bar,text='Open File',command=self.open_fil)
        self.ev_button=CustomButton(self.button_bar,text='Open Event Library',command=self.open_ev)
        self.eff_button=CustomButton(self.button_bar,text='Open Effect Library',command=self.open_eff)
        self.dir_button.grid(row=0,column=0,sticky='nsew')
        self.fil_button.grid(row=0,column=1,sticky='nsew')
        self.ev_button.grid(row=0,column=2,sticky='nsew')
        self.eff_button.grid(row=0,column=3,sticky='nsew')
        self.button_bar.grid_rowconfigure(0,weight=1)
        for i in range(4):
            self.button_bar.grid_columnconfigure(i,weight=1)
                
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        
        self.bind('<Expose>',self.load_dir)
        self.file_text.bind('<Key>',lambda e:self.root.title(
            '* {} *'.format(self.root.title().strip('* '))
            ))
        def focus_break(event=None):
            self.file_choices.focus_set()
            return 'break'
        self.file_text.bind('<Tab>',focus_break)
        self.file_text.bind('<Command-s>',self.save_file)
        self.file_text.bind('<FocusOut>',self.save_file)
        self.file_text.bind('<FocusIn>',self.file_check)
        self.bind('<FocusIn>',self.load_dir)
        for key in ('<Up>','<Down>','<Button-1>'):
            self.file_choices.bind(key,lambda e:self.after_idle(lambda e=e:self.load_file(e)))
        self.file_choices.bind('<Right>',lambda e:self.file_text.focus_set())
        for var in (self.dir,self.game):
            var.trace('w',lambda *a:self.load_dir())
    
    @property
    def directory(self):
        base_d=self.dir_map[self.dir.get()]
        d=os.path.join(base_d,self.game.get())
        if not os.path.exists(d):
            d=base_d
        return d
        
    @property
    def files(self):
        key=self.dir.get()
        dir=self.directory
        files=[];listing=os.listdir(dir)
        if key=='Tiles':
            listing=[os.path.join(b,t) 
                for b in listing 
                for t in 
                (os.listdir(os.path.join(dir,b)) 
                    if os.path.isdir(os.path.join(dir,b)) else 
                ())]
        if key=='Pokemon':
            for x in listing:
                if len(x.split('_'))==2 and os.path.isdir(os.path.join(dir,x)):
                    files.append(x)
        elif key=='Tiles':
            for x in listing:
                if os.path.splitext(x)[1]=='.tlf' or os.path.exists(
                    os.path.join(dir,x,'props.txt')
                    ):
                    files.append(x)
        elif key in 'Characters':
            for x in listing:
                d=os.path.join(dir,x)
                if os.path.isdir(d):
                    files.append(x)
                    
        elif key in ('Attacks','Items'):
            for x in listing:
                if os.path.splitext(x)[1]=='.txt':
                    files.append(x)
        files=sorted(files,key= (lambda s:int(s.split('_')[0])) if key=='Pokemon' else lambda s:s)
        return (f for f in files)
        
    @property
    def current(self):
        return self.current_file('active')
        
    def load_dir(self,event=None):
        if self.directory==self._dir:
            current=self.file_choices.get('active')
        else:
            current=None
        files=[o for o in self.files]
        try:
            ind=files.index(current)
        except ValueError:
            ind=0
        self.file_choices.delete('0','end')        
        for o in files:
            self.file_choices.insert('end',o)
        
        for f in (self.file_choices.selection_anchor,
                    self.file_choices.selection_set,
                    self.file_choices.activate,
                    self.file_choices.see):
            f(ind)
        self._dir=self.directory
        self.after(50,lambda:self.load_file(anchor='anchor'))
    
    def current_file(self,anchor='anchor'):
        dir=self.dir.get()
        file=os.path.join(
            self.directory,
            self.file_choices.get(anchor)
            )
        if dir in ('Pokemon','Tiles'):
            if not os.path.splitext(file)[1]=='.tlf':
                file=os.path.join(file,'props.txt')
        return file
    
    def file_check(self,event=None):
        if self._file is None:
            self.file_choices.focus_set()
            
    def load_file(self,event=None,anchor=None):
        anchor=anchor if not anchor is None else ('active' if 
                    (not event is None) and event.keysym in ('Up','Down','Left','Right') 
                    else 'anchor')
        file=self.current_file(anchor)        
        self.file_text.Clear()
        try:
            with open(file) as data:
                self.file_text.Append(data.read())
        except:
            self._file=None
            self.file_text.Append('This is a directory. Open it with the "Open File" button to edit it.')
        else:
            self._file=file
    
    def save_file(self,event=None):
        if not self._file is None:
            with open(self._file) as store:
                stored=store.read()
            try:
                with open(self._file,'w') as edit:
                    edit.write(self.file_text.get('all'))
            except:
                with open(self._file,'w') as edit:
                    edit.write(stored)
                raise
            else:
                t=self.root.title()
                self.root.title(t.strip('* '))
    
    def open_dir(self,event=None):
        open_file(self._dir)
    def open_fil(self,event=None):
        open_file(self.current_file())
    def open_ev(self,event=None):
        open_file(getdir('events'))
    def open_eff(self,event=None):
        open_file(getdir('battle_effects'))
    
    def set_geometry(self):
        self.root.geometry('{width}x{height}'.format(
                width=sum((x['width'] for x in (
                    self.file_choices,
                    self.dir_button,
                    self.ev_button,
                    self.eff_button,
                    self.fil_button)
                )),
                height=100+sum((x['height'] for x in (
                    self.file_text,
                    self.dir_button
                    )))
                    ))
        
class PrepperWindow(tk.Toplevel):
    def __init__(self,master=None,**kwargs):
        super().__init__(master,**kwargs)
        from GUITools.ExtraWidgets.ShellFrame import ShellFrame
        self.S=ShellFrame(self,variable_dict={'self':self,'os':os,'shutil':shutil,
                                     'P':PokemonPrepper(),
                                     'T':TilePrepper(),
                                     'A':AttackPrepper(),
                                     'I':ItemPrepper(),
                                     'PokemonPrepper':PokemonPrepper,
                                     'TilePrepper':TilePrepper,
                                     'AttackPrepper':AttackPrepper,
                                     'ItemPrepper':ItemPrepper
                                    })
        self.title('Data Editor')
        self.S.pack(fill='both',expand=True)
        self.browser=FileBrowser(self.S)
        self.S.set_widget(self.browser)
        self.S.shell.Editor=self.browser
        self.geometry('625x500')
#         self.browser.after_idle(self.browser.set_geometry)
        
        