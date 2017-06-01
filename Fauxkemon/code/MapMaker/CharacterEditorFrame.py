from .Shared import *
from ..DataTypes import Trainer

character_editor_help='''
'''
class CharacterEditorFrame(tk.Toplevel):
    longMap=(('Character Type','charname'),
             ('Name','nickname'),
             ('Trainer','trainer')
             )
    extraMap=(('Size','size'),
             ('NPC','npc_flag'))
    
    
    writeMap=(('charname','charname'),('size','size'))
    bindMap=('a_button','start','select')
    
    class MessageEditor(tk.Toplevel):
        def __init__(self,tile):
            self.protocol('WM_DELETE_WINDOW',lambda e:(self.save(),self.destroy()))
        def save(self):
            pass
        
    def __init__(self,calledfrom,tile):
        #Sets up the paned window with the image on top recessed slightly and the props below
        super().__init__(bd=4,bg='gray25')
        self.panes=tk.PanedWindow(self,orient='vertical',showhandle=True,sashrelief='sunken')
        self.panes.pack(fill='both',expand=True)
        self.root=calledfrom
        self.saveCMD=self.root.bind('<FocusIn>',lambda e:self.save(),add='+')
        self.protocol('WM_DELETE_WINDOW',lambda*e:(
            self.save(),
            self.root.unbind('<FocusIn>',self.saveCMD),
            self.destroy()
            ))
        
        m=tk.Menu(self)
        for n,s in (
            ('Help',
             (
                ('Open Help',lambda:HelpText(character_editor_help)),
             )
            ),):
            M=tk.Menu(m)
            for name,com in s:
                M.add_command(label=name,command=com)
            m.add_cascade(label=n,menu=M)
        self.config(menu=m)
        
        #Checks whether the tile is a path or an actual tile
        if isinstance(tile,str):
            tile_path=tile
            self.dir=tile_path;self.im=os.path.join(tile_path,'front.png')
            self.char=os.path.basename(tile_path)
            self.source=os.path.basename(os.path.split(tile_path)[0])
            self.translate_event=translate_event
        else:
            self.char=tile
            self.dir=tile.dir
            self.source=os.path.basename(os.path.dirname(self.dir))
            print(self.source)
            self.translate_event=tile.translate_event
            
        self.title(str(self.char))
        self.props={}
        self.editor=tk.Frame(self.panes)
        self.make_scrollable_frames()
        c1=self.editor.propframe

        self.button_presses={'a_button':[]}
        
        self.propgrid=FormattingGrid(self.editor.propframe,rows=0,columns=2)

        for x,w in ((c1,self.propgrid),):
##            x.window=x.create_window(0,0,window=w,anchor='nw')
            w.pack(fill='both',expand=True)#place(relwidth=1,relheight=1)
##            x.bind('<Configure>',lambda e:x.config(scrollregion=x.bbox('all')))
##        self.propgrid.gridConfig(sticky='w')

        self.initialize()
        
        rows=max(l for l in self.propgrid.commands.lengths)+8
        self.panes.add(self.image,sticky='nsew',stretch='always',minsize=50)
        self.panes.add(self.editor,sticky='nsew',stretch='always',minsize=20*rows)
##            self.protocol('WM_DELETE_WINDOW',lambda *e:(self.save(),self.destroy()))
        self.bind('<Configure>',lambda e:self.resize())
##        self.bind('<Command-i>',lambda e:Interactor(self,initiallocals={'obs':self.bindings.commands}))
        self.geometry('500x500')
        self.panes.sash_place(0,50,50)


    def fake_bind(self,callback,frequency=1,trigger='enter',name='',to='events'):
        E=GridCanvas.Event(callback,frequency,trigger,name)
        evs=getattr(self,to)
        evs[trigger].append(E)
    
    def new_message(self):
        cell=self.char
        T=tk.Toplevel(self)
        E=tk.Entry(T)
        E.insert(0,'message')
        txt=RichText(T,width=75,height=10)
        txt.Insert('Welcome to the World of Fauxkemon!')
        E.pack(fill='x')
        txt.pack()
        def save_process(T=T,cell=cell,E=E,txt=txt):
            d=cell.dir
            n=E.get()
            t=txt.getAll()
            with open(os.path.join(d,n+'.txt'),'w+') as to:
                to.write(t)
            T.destroy()
        T.save_process=save_process
        T.protocol('WM_DELETE_WINDOW',lambda T=T:T.save_process())

    def new_trainer(self):
        '''Opens a pane to define a new trainer using the new trainer dialog'''
        
        tr=Trainer.NewTrainer(self,source=self.source)
        self.propgrid.trainer.delete(0,'end')
        self.propgrid.trainer.insert(0,str(tr))
        
    def make_scrollable_frames(self):
        
        f=tk.Frame(self.editor,bd=2,relief='ridge',bg='white')
        f.pack(fill='both',expand=True,anchor='w')
        self.editor.propframe=c=ScrollableFrame(f)
        c.pack(fill='both',expand=True)
        
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

        if isinstance(self.char,str):
            bind=self.bind
            self.bind=self.fake_bind
            self.background=ImageWrapper(self.im)
            self.draw=self.background.toTk()
            self.image=tk.Label(self.panes,image=self.draw,bg='gray95',relief='sunken')
            self.image.bind('<Double-Button-1>',self.edit_image)
            self.image.bind('<Command-Button-1>',self.edit_image)
##            evs=self.events
            tile=self.char
            Character.get_props(self,self.char,self.source)
            self.bind=bind
        else:
            self.button_presses=self.char.events
            self.background=self.char.image
            self.draw=self.background.toTk()
            self.image=tk.Label(self.panes,image=self.draw)
            self.props['charname']=self.char.kind
            self.props['size']=self.char.size
            self.props['nickname']=self.char.nickname
            self.props['npc_flag']=self.char.npc_flag
            self.props['trainer']=(lambda:'' if self.char.trainer is None else str(self.char.trainer))()

        self.load_tile()
            
    def edit(self):
        from GeneralTools.PlatformIndependent import open_file
        d=self.char.dir
##        if d is None:
##            d=self.tile.dir
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
            e=tk.Entry(f,relief='flat',textvariable=v,width=25)
            setattr(self.propgrid,key,e)
            l.pack(side='left');e.pack(fill='x',side='left',expand=True)
            self.propgrid.Add(f)
            f.gridConfig(columnspan=2)
            
        self.propgrid.AddFormat(tk.Label,text='Properties:')
        self.propgrid.AddFormat(CustomButton,text='Open',command=self.edit,relief='flat')
        for k,n in self.longMap:
            try:
                v=self.props[n]
            except KeyError:
                v=''
            frame(k,v,n)
        def frame(name,value,key):
            f=FormattingElement(tk.Frame,self.propgrid)
            t=type(value)
            s=str(value)
            l=tk.Label(f,text=name+':')
            if key in ('size',):
                v=tk.StringVar(value=s)
                e=tk.Entry(f,width=3,textvariable=v,relief='flat')
            elif key in ('npc_flag',):
                v=tk.BooleanVar(value=value)
                e=tk.Checkbutton(f,variable=v)
                e.get=lambda:str(v.get())
            setattr(self.propgrid,key,e)
            l.pack(side='left');e.pack(fill='x',side='left',expand=True)
            self.propgrid.Add(f)
        for k,n in self.extraMap:
            try:
                v=self.props[n]
            except KeyError:
                v=''
            frame(k,v,n)
        def frame(key,call):
            f=FormattingElement(tk.Frame,self.propgrid)
            f.name=key
            l=tk.Label(f,text=btmap[key])
            l.pack(side='left')
            f.call=tk.Entry(f,width=24,relief='flat')
            f.call.insert(0,call)
            f.call.pack(fill='x',side='left',expand=True)
            self.propgrid.Add(f)
            f.gridConfig(columnspan=2)
##        self.propgrid.commands.collapse()
        
        for key in self.button_presses:
            ls=self.button_presses[key]
            string=[]
            try:
                btmap[key]
            except KeyError:
                pass
            else:
                for e in ls:
                    n=e.n.strip()
                    if n:
                        string.append(n)
                if string:
                    string='({})'.format(','.join(string))
                    frame(key,string)
                else:
                    frame(key,'')
                    
        self.propgrid.AddFormat(CustomButton,text='New Message',command=self.new_message)
        self.propgrid.AddFormat(CustomButton,text='Edit Inventory',command=self.edit_items)
        self.propgrid.AddFormat(CustomButton,text='New Trainer',command=self.new_trainer)
        self.propgrid.configure_cols(weight=1)
        self.propgrid.gridConfig(sticky='ew')
        
    def edit_items(self):
        
        T=tk.Toplevel()
##        T.transient(True)
##        T.attributes('-transient',True)
        T.title('Inventory')
        
        R=RichText(T)
        R.pack(fill='both',expand=True)
        for x in self.char.inventory:
            R.Append(x+'\n')

        def pack_up():
            text=R.getAll()
            self.char.inventory=text.splitlines()

        T.protocol('WM_DELETE_WINDOW',lambda:(pack_up(),T.destroy()))
            
    def save(self):
        if not isinstance(self.char,str):
##            self.char.clear_events()
            m=self.propgrid.commands.row_dim()
            self.char.charname=self.propgrid.charname.get()
            size=self.propgrid.size.get()
            try:
                size=int(size)
                self.char.size=size
            except:
                pass
            npc_flag=eval(self.propgrid.npc_flag.get())
            nickname=self.propgrid.nickname.get()
            self.char.nickname=nickname
            if not npc_flag:
                self.char.make_active()
            else:
                self.char.deactivate()
            trainer=self.propgrid.trainer.get()
            if trainer=='':
                self.char.trainer=None
            else:
                self.char.trainer=Trainer(trainer,source=self.char.source)
                
            for i in range(m):
                r=self.propgrid.commands.row(i)
                
                for e in r:
                    try:
                        evstring=e.call.get()
                    except:
                        pass
                    else:
                        trig=e.name
                        evstring=evstring.strip('(').strip(')')
                        self.char.events[trig]=[]
                        for ev in evstring.split(','):
                            ev=ev.strip()
                            if ev:
                                call=self.translate_event(ev)
                                self.char.events[trig].append(GridCanvas.Event(call,frequency=1,trigger=trig,name=ev))
            
        else:
            btmap={'A-Command':'a_button'}
            old=os.path.join(self.dir,'specs.txt')
            back=os.path.join(self.dir,'backup.txt')
            try:
                shutil.copy(old,back)
            except FileNotFoundError:
                from GeneralTools.PlatformIndependent import open_file
                open_file(self.dir)
            except OSError:
                os.remove(back)
                shutil.copy(old,back)
            
                
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
                    file.write('a_button: {}\n'.format(','.join(string)))
                    
##                string=[]
##                m=self.bindings.commands.row_dim()
##                for i in range(m):
##                    r=self.bindings.commands.row(i)
##                    k=r[0].name
##                    for x in r[1:]:
##                        fr=float(x.freq.get())
##                        fn=x.func.get()
##                        if fr and fn:
##                            string.append('{} {} {}'.format(k,fr,fn))
                    
##                if string:
##                    file.write('events: {}\n'.format(','.join(string)))
