from .Shared import *

tile_editor_help='''
This is a tile editor

Tile Type: 
Size: The number of objects that can be on this tile at once. Usually 0 or 1.

'''

class TileEditorFrame(tk.Toplevel):
    propMap=(('Tile Type','tiletype'),
            ('Available Space','space'))
    
    writeMap=(('tiletype','tiletype'),('spaces','space'))
    bindMap=('a_button','start','select')
    
    bindingKeys=Tile.event_keys
    class MessageEditor(tk.Toplevel):
        def __init__(self,tile):
            self.protocol('WM_DELETE_WINDOW',lambda e:(self.save(),self.destroy()))
        def save(self):
            pass
        
    def __init__(self,calledfrom,tile):
        
        '''Sets up a paned window with three panes: the tile image, a formatting grid of properties, and a formatting grid of events.
    
Double clicking the tile image will open the tile file in a different program.

Both of the formatting grids are embedded in adjustable windows.'''
        #Sets up the paned window with the image on top recessed slightly and the props below
        super().__init__(bd=4,bg='gray25')
        
        m=tk.Menu(self)
        for n,s in (
            ('Help',
             (
                ('Open Help',lambda:HelpText(tile_editor_help)),
             )
            ),):
            M=tk.Menu(m)
            for name,com in s:
                M.add_command(label=name,command=com)
            m.add_cascade(label=n,menu=M)
        self.config(menu=m)
        
        self.panes=tk.PanedWindow(self,
            orient='vertical',showhandle=True,sashrelief='sunken')
            
        self.panes.pack(fill='both',expand=True)
        self.root=calledfrom
        self.attributes('-topmost',True)
        self.saveCMD=self.root.bind('<FocusIn>',lambda e:self.save(),add='+')
        self.protocol('WM_DELETE_WINDOW',lambda*e:(
            self.save(),
            self.root.unbind('<FocusIn>',self.saveCMD),
            self.destroy()
            ))
        #Checks whether the tile is a path or an actual tile
        if isinstance(tile,str):
            if tile=='__new__':
                self.withdraw()
                tile_window=self.new_tile()
                self.wait_window(tile_window)
                tile=tile_window.tile
                self.deiconify()
            tile_path=tile
            #Takes an absolute path to the tile source and gets the necessary info to configure its source file
            self.dir=tile_path;self.im=os.path.join(tile_path,'background.png')
            self.tile=os.path.basename(tile_path)
            self.source=os.path.basename(os.path.split(tile_path)[0])
        else:
            self.tile=tile
            self.dir=None
            
        self.title(str(self.tile))
        self.props={}
        self.editor=tk.Frame(self.panes)
        self.bindings=tk.Frame(self.editor)
        self.make_scrollable_frames()
#         c1=self.editor.propframe
#         c2=self.editor.bindframe

        self.events={x:[] for x in self.bindingKeys}
        self.button_presses={'a_button':[],'b_button':[],'start':[],'select':[]}
        
        self.current_binding=tk.StringVar(self)
        self.bindings.lb=tk.Listbox(self.bindings,bd=2,relief='ridge')
        
        def set_binding(e=None,ind='active',l=self.bindings.lb,c=self.current_binding):
            l.after_idle(lambda l=l,c=c:c.set(l.get(ind) ))
        for o in ('<Up>','<Down>',"<Return>"):
            self.bindings.lb.bind(o,set_binding)
        self.bindings.lb.bind('<Button-1>',lambda e,s=set_binding:s(ind='anchor'))
        self.bindings.lb.grid(row=0,column=0,rowspan=2,sticky='ns')
        self.bindings.grid_rowconfigure(0,weight=1)
        self.bindings.grid_columnconfigure(1,weight=1)
        self.bindings.binding_frames={}        
        add_button=tk.Button(self.bindings,text='Add Event',command=self.add_binding)
        add_button.grid(row=1,column=1,sticky='nsew')
        
        for s in self.bindingKeys:
            self.bindings.binding_frames[s]=F=FormattingGrid(self.editor.bindframe,rows=0,columns=1)
            self.bindings.lb.insert('end',s)
            F.gridConfig(sticky='w',pady=15)
            F.configure_rows(minsize=20)
            
            
        def bind_trace(*e,b = self.bindings.binding_frames, c = self.current_binding):
            [b[w].pack_forget() for w in b]
            s=c.get()
            if s in b:
                b[s].pack(fill='both',expand=True)
            
        self.current_binding.trace('w',bind_trace)
        self.current_binding.set(self.bindingKeys[0])
        self.bindings.lb.selection_set(0)
#         self.bindings.lb.config(listvariable=self.current_binding)
        
        
        self.propgrid=FormattingGrid(self.editor.propframe,rows=0,columns=2)

        self.propgrid.pack(fill='both',expand=True)
        self.bindings.pack(fill='both',expand=True)

        self.propgrid.gridConfig(sticky='w')

        self.initialize()
        
        rows=max(l for l in self.propgrid.commands.lengths)+8
        self.panes.add(self.image,sticky='nsew',stretch='always',minsize=50)
        self.panes.add(self.editor,sticky='nsew',stretch='always',minsize=20*rows)
##            self.protocol('WM_DELETE_WINDOW',lambda *e:(self.save(),self.destroy()))
        self.bind('<Configure>',lambda e:self.resize())
        self.bind('<Command-i>',lambda e:Interactor(self,initiallocals={'obs':self.bindings.binding_frames}))
        self.geometry('500x700')
        self.panes.sash_place(0,50,50)


    def fake_bind(self,callback,frequency=1,trigger='enter',name='',to='events'):
        '''Configures an event, even though it will never be called on this widget'''
        E=GridCanvas.Event(callback,frequency,trigger,name)
        evs=getattr(self,to)
        evs[trigger].append(E)
        
    def add_binding(self,name=None):
        '''Inserts a new frame for adding and event next to the listing for that event.

Uses the Add command of a FormattingGrid to insert it at the end of the row.'''
        
        if name is None:
            name=self.current_binding.get()
        binding_frame=self.bindings.binding_frames[name]
        f=FormattingElement(tk.Frame,binding_frame,bd=2,bg='grey25')
        
        binding_frame.Add(f,mode='row')
#         i,j=binding_frame.commands.get_index(-1,0)
        W=f
        def erase_cmd(event=None,W=W,binding_frame=binding_frame):
            i,j=binding_frame.commands.index(W,nonIterable=True)
            binding_frame.Blank((i,j),reduce=True,collapse='row')
        l=CustomButton(f,text=' - ',command=erase_cmd)            
        l.pack(side='left')
        for n,w in (('func',20),('freq',3)):#,('args',8)):
            e=tk.Entry(f,width=w,relief='flat',bg='gray95')
            setattr(f,n,e)
            e.pack(side='left')
##        l.bind('<Button-1>',lambda e,i=i,j=j:self.bindings.Blank((i,j),reduce=False,collapse='row'))
##        x.itemconfig(x.window,window=self.bindings)
        
        return f
    
    def new_message(self):
        cell=self.tile
        T=tk.Toplevel(self)
        E=tk.Entry(T)
        E.insert(0,'message')
        txt=RichText(T,width=25)
        txt.Insert('Welcome to the World of Fauxkemon!')
        E.pack(fill='x')
        txt.pack()
        def save_process(T=T,cell=cell,E=E,txt=txt):
            try:
                d=cell.dir
            except AttributeError:
                d=self.dir
            n=E.get()
            t=txt.getAll()
            with open(os.path.join(d,n+'.txt'),'w+') as to:
                to.write(t)
            T.destroy()
        T.save_process=save_process
        T.protocol('WM_DELETE_WINDOW',lambda T=T:T.save_process())
        
    def make_scrollable_frames(self):
        
        self.editor.propframe=c=ScrollableFrame(self.editor)
        c.pack(fill='both',expand=True)
        self.editor.bindframe=c=ScrollableFrame(self.bindings)
#         c.pack(fill='both',expand=True)
        c.grid(row=0,column=1,sticky='nsew')
        
    def resize(self):
        y=self.image.winfo_height()
        self.background.reset()
        self.background.resize((y,y))
        self.draw=self.background.Tk
        self.image.config(image=self.draw)

    def edit_image(self,event=None):
        try:
            PlatformIndependent.open_file(self.im,"Paintbrush")
        except:
            PlatformIndependent.open_file(self.im)
        
    def initialize(self):

        if isinstance(self.tile,str):
            bind=self.bind
            self.bind=self.fake_bind
            self.translate_event=translate_event
            self.background=ImageWrapper(self.im)
            self.draw=self.background.toTk()
            self.image=tk.Label(self.panes,image=self.draw,bg='gray25',relief='sunken')
            self.image.bind('<Double-Button-1>',self.edit_image)
            self.image.bind('<Command-Button-1>',self.edit_image)
            evs=self.events
            tile=self.tile
            Tile.get_props(self,self.tile,self.source)
            self.events=evs
            Tile.load_events(self)
            self.bind=bind
        else:
            self.events=self.tile.events
            self.button_presses=self.tile.button_presses
            self.background=self.tile.image.image
            self.draw=self.background.toTk()
            self.image=tk.Label(self.panes,image=self.draw)
            self.props['tiletype']=self.tile.tiletype
            self.props['space']=self.tile.space

        self.load_tile()
            
    def edit(self):
        from GeneralTools.PlatformIndependent import open_file
        d=self.dir
        if d is None:
            d=self.tile.dir
        open_file(d)
        
    def load_tile(self):
        from GUITools.ImageTools import ImageWrapper
        btmap={'a_button':'A-Command'}

        def frame(name,value,key):
            f=FormattingElement(tk.Frame,self.propgrid)
            t=type(value)
            s=str(value)
            l=tk.Label(f,text=name+':')
            v=tk.StringVar(value=s)
            w=8
            if 'Space' in name:
                w=3
            e=tk.Entry(f,relief='flat',textvariable=v,width=w)
            setattr(self.propgrid,key,e)
            l.pack(side='left');e.pack(side='left',fill='x',expand=True)
##            self.propgrid.Add(f)
            return f

        self.propgrid.AddFormat(tk.Label,text='Properties:')
##        self.propgrid.a_button_frame.gridConfig(columnspan=2)
        self.propgrid.AddFormat(CustomButton,text='Open',command=self.edit)
        for k,n in self.propMap:
            try:
                try:
                    v=getattr(self,n)
                except:
                    v=self.props[n]
            except:
                v=''
            f=frame(k,v,n)
            self.propgrid.Add(f)

        for key in self.events:
            for e in self.events[key]:
                f=e.f
                n=e.n
                frame=self.add_binding(key)
                frame.func.insert(0,e.n)
                frame.freq.insert(0,str(e.f))
                
        def frame(key,call):
            f=FormattingElement(tk.Frame,self.propgrid)
            f.name=key
            l=tk.Label(f,text=btmap[key])
            l.pack(side='left')
            f.call=tk.Entry(f,width=16,relief='flat')
            f.call.insert(0,call)
            f.call.pack(side='left',fill='x',expand=True)
            return f#self.propgrid.Add(f)
##        self.propgrid.commands.collapse()
        
        for key in self.button_presses:
            ls=self.button_presses[key]
            try:
                btmap[key]
            except KeyError:
                pass
            else:
                for e in ls:
                    n=e.n.strip()
                    if n:
                        f=frame(key,n)
                        self.propgrid.Add(f)
##                        self.propgrid.AddFormat(tk.Label,text='')
                        f.gridConfig(columnspan=2)
                        break
                else:
                    f=frame(key,'')
                    self.propgrid.Add(f)
##                    self.propgrid.AddFormat(tk.Label,text='')
                    f.gridConfig(columnspan=2)
        self.propgrid.AddFormat(CustomButton,text='New Message',command=self.new_message)
        self.propgrid.Refresh()
        self.propgrid.configure_cols(weight=1)
        self.propgrid.gridConfig(sticky='nsew')
    def event_frame(self,key,call,root=None):
        if root is None:
            root=self.propgrid
        
    def new_tile(self):
        return NewTileWindow()
        
    def save(self):
        '''Saves the info on the screen to the appropriate file'''
        if not isinstance(self.tile,str):
            self.tile.clear_events()
            m=self.propgrid.commands.row_dim()
            self.tile.tiletype=self.propgrid.tiletype.get()
            space=self.propgrid.space.get()
            try:
                space=int(space)
                self.tile.space=space
            except:
                pass
            for i in range(m):
                r=self.propgrid.commands.row(i)
                
                for e in r:
                    try:
                        ev=e.call.get()
                    except:
                        pass
                    else:
                        if ev:
                            call=self.tile.translate_event(ev)
                            self.tile.bind(call,frequency=1,trigger=e.name,name=ev)
            for k in self.bindingKeys:
                bind_frame=self.bindings.binding_frames[k]
                m=bind_frame.commands.dimensions[0]
                for i in range(m):
                    r=bind_frame.commands.row(i)
                    for x in r:
                        fr=float(x.freq.get())
                        fn=x.func.get()
                        if fr and fn:
                            call=self.tile.translate_event(fn)
                            self.tile.bind(call,frequency=fr,trigger=k,name=fn)
            
        else:
            btmap={'A-Command':'a_button','Start-Command':'start'}
            old=os.path.join(self.dir,'props.txt')
            back=os.path.join(self.dir,'backup.txt')
            try:
                shutil.copy(old,back)
            except:
                os.remove(back)
                shutil.copy(old,back)
            
            try:
                with open(old,'w+') as file:
                    for k,n in self.writeMap:
                        e=getattr(self.propgrid,n)
                        v=e.get()
                        file.write('{}: {}\n'.format(k,v))
                    string=[]
                    m=self.propgrid.commands.row_dim()
                    for i in range(1,m):
                        r=self.propgrid.commands.row(i)
                        for e in r:
                            try:
                                ev=e.call.get()
                            except:
                                pass
                            else:
                                if ev:
                                    s='{} {}'.format(e.name,ev)
                                    string.append(s)
                
    ##                for key in self.bindMap:
    ##                    for e in self.button_presses[key]:
    ##                        s='{} {}'.format(key,e.name)
    ##                        string.append(s)
                    if string:
                        file.write('buttons: {}\n'.format(','.join(string)))
                    
                    string=[]
                    for k in self.bindingKeys:
                        bind_frame=self.bindings.binding_frames[k]
                        m=bind_frame.commands.dimensions[0]
                        for i in range(m):
                            r=bind_frame.commands.row(i)
                            for x in r:
                                fr=float(x.freq.get())
                                fn=x.func.get()
                                if fr and fn:
                                    call=self.tile.translate_event(fn)
                                    self.tile.bind(call,frequency=fr,trigger=k,name=fn)
                    
                    if string:
                        file.write('events: {}\n'.format(','.join(string)))
            except:
                with open(back) as backup:
                    stored_text=backup.read()
                with open(old,'w+') as file:
                    file.write(stored_text)
                raise
                    
class NewTileWindow(tk.Toplevel):
    props=('Tile Type','Available Space','Events')
    __src_dir=os.path.dirname(__file__)
    blank=os.path.join(__src_dir,'blank.png')
    def __init__(self):
        super().__init__()
        self.title('New Tile')
        self.l_b=tk.Button(self,text='Load Image',command=self.load_pic)
        self.im_b=tk.Button(self,text='Create Image',command=self.choose_picture)
        self.src_b=tk.Button(self,text='Choose Tile Location',command=self.choose_loc)
        self.name_e=tk.Entry(self,width=10)
        self.name_e.insert(0,'tile_name')
        self.name_e.grid(row=2)
        self.src_b.grid(row=1)
        self.protocol('WM_DELETE_WINDOW',lambda:(setattr(self,'tile',self.tile_path),self.destroy()))

    def choose_loc(self):
        from tkinter.filedialog import askdirectory
        d=askdirectory(initialdir=tiles)
        self.loc=d
        self.src_b.config(text=os.path.basename(self.loc))
        p=self.tile_path
        if not os.path.exists(p):
            os.mkdir(p)
        self.props=os.path.join(self.tile_path,'props.txt')
        if not os.path.exists(self.props):
            with open(self.props,'w') as touch:
                touch.write('props')
            
        self.im_b.grid(row=0)

    @property
    def tile_name(self):
        return self.name_e.get()
    
    @property
    def tile_path(self):
        return os.path.join(self.loc,self.tile_name)
    
    def choose_picture(self):
        p=self.tile_path
        f=os.path.join(p,'background.png')
        if not os.path.exists(f):
            shutil.copy(self.blank,f)
        PlatformIndependent.open_file(f)
        self.l_b.grid(row=2,column=1)

    def load_pic(self):
        self.l_b['text']=''
        self.im=ImageWrapper(os.path.join(self.tile_path,'background.png'))
        self.l_b['image']=self.im.Tk
