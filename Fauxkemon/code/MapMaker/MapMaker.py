from ..Map import *
from ..PokemonBattle import *
from .Shared import *
from GeneralTools.PlatformIndependent import open_file
from collections import deque

maps=getdir('maps')

bg_color='grey85';base_rel='sunken'
bg_color_1='grey50';base_rel_1='groove'
base_fg='black';base_fg_2='white';base_rel_2='flat'
    
editor_desc='''The Fauxkemon Editor

From here you can edit maps, animations, or test the battle screen'''
class GameEditor(tk.Toplevel):
    '''The root editor frame'''
    def __init__(self,root_file=None):
        
        super().__init__()
        
        self.title('Game Editor')
        
        self.fg=FormattingGrid(self,rows=2,columns=4)
        self.fg.pack(fill='both',expand=True)
        
        self.info=self.fg.AddFormat(tk.Text,self,
            highlightthickness=0,cursor='arrow',bd=3,relief='sunken')
#         Standardizer.standardize(self.info)
        self.info.bind('<Button-1>',lambda e:'break')
        self.info.bind('<B1-Motion>',lambda e:'break')
        self.info.gridConfig(columnspan=4)
        self.info.insert('end',editor_desc)
        self.editors=[]
        for n,f in (
        
            ('Data Editor',PrepperWindow),
            ('Map Editor',MapInterface),
            ('Animation Editor',AnimationEditor),
            ('Battle Test',BattleTest)
            
            ):
            g=self.fg.AddFormat(CustomButton,text=n, 
                command=lambda s=self,f=f,n=n:s.editors.append((n,f(master=s)))
                )
        self.fg.grid_rowconfigure(1,minsize=25)
        
        self.fg.gridConfig(sticky='nsew')
        self.geometry('400x300')
        self.after(50,lambda:self.resizable(False,False))
        
        
    
    
editor_about='''
This is a map editor for Fauxkemon

Choose an old map to edit or make a new one

The map interface can also edit tiles and characters
'''

editor_help='''
Press Control-T to edit tiles and Control-E to edit characters

Tile mode:

    Select a tile on the left-hand bar to use it. Simply click or draw on the map where it should go.
    
    To edit tiles, first select 'No Selection' on the left hand side
        Double click of a tile name to edit that tile type
        Double click on a tile in tile-editing mode to edit that specific tile
        Control-Click will rotate a tile. This also rotates any event bindings
    
    To select tiles to copy and paste in, click on 'Select Tiles' on the left. 
        Shift-Click to clear the selection
        Command-C will copy the selection
        Shift-V-Click will paste the selection into the map
        Command-n will prepare a texture file (.tlf) which can be saved with Command-s
    
    Command-z will undo paste operations


Character Mode:
    
    Select a character on the left-hand bar to add it to the screen. Command-Click where it should go.
    
    To edit characters, first select 'No Selection' on the left
        Double click on a character name currently has no effect
        Double click on a character will open a window to edit that character
        
    
'''.strip()

battle_help='''

'''

animation_help='''

'''

class MapInterface(tk.Toplevel):
    
    bg_color=bg_color;base_rel=base_rel
    bg_color_1=bg_color_1;base_rel_1=base_rel_1
    base_fg=base_fg;base_fg_2=base_fg_2;base_rel_2=base_rel_2
            
    def __init__(self,calledon=None,mapname=None,**kwargs):
    
        super().__init__(**kwargs)
        self.called=calledon
        self.title('Map Editor')
        if mapname is None:            
            self.main=tk.Frame(self,bg=self.bg_color_1,bd=3,relief=self.base_rel_1)
            t=self.main.t=tk.Text(self.main,
                font=('Mono',15),
                cursor='arrow',
                bg=self.bg_color,
                fg=self.base_fg,
                relief=self.base_rel,
                height=min(10,len((editor_about+editor_help).splitlines())),
                bd=3,
                highlightthickness=0,
                wrap='word',
                width=50)
            t.insert('end',editor_about+editor_help)
            t.bind('<Button-1>',lambda e:'break')
            t.bind('<B1-Motion>',lambda e:'break')
            t.pack(fill='both',expand=True,anchor='n')
            b_conf={'bg':self.bg_color_1,'fg':self.base_fg_2,'relief':self.base_rel_2}
            b=self.main.p=CustomButton(self.main,text='Open prexisting file',
                inactive=b_conf,command=self.choose_map)
            m=self.main.m=CustomButton(self.main,text='Make new map',
                inactive=b_conf,command=self.new_map)
            b.pack(side='left')
            m.pack(side='left')
            self.main.pack(fill='both',expand=True)
        else:
            MapMaker(self,mapname=mapname).pack(fill='both',expand=True)
                
    def choose_map(self):
##        self.main.destroy()
        from tkinter.filedialog import askopenfilename as ask
        f=ask(parent=self,initialdir=maps,title='Choose a map')
        if f:
            try:
                m=MapMaker(self,file=f)
            except:
                tb.print_exc()
            else:
                self.geometry('750x500')
                m.pack(fill='both',expand=True)
                self.main.destroy()

    def new_map(self):
        self.main.p.pack_forget()
        self.main.m.pack_forget()
#         self.main.t.pack_forget()
        self.main.bind('b',lambda e,s=self.main:(s.tf.pack_forget(),
#             s.t.pack(fill='both',expand=True,anchor='n'),
            s.p.pack(side='left'),
            s.m.pack(side='left')))
        xv=tk.StringVar(value=36)
        yv=tk.StringVar(value=36)
        conf={'bg':self.bg_color_1,
            'fg':self.base_fg_2,
            'padx':0,
            'relief':'flat',
            'pady':0,
            'highlightthickness':0}
        self.main.tf=tf=tk.Frame(self.main)
        x=tk.Label(tf,text='Dimensions=(');
        X=tk.Entry(tf,textvariable=xv,
            width=2,
            relief='flat')
        i=tk.Label(tf,text=',')
        Y=tk.Entry(tf,textvariable=yv,width=2,relief='flat');y=tk.Label(tf,text=')')
        basetiles=['Blank','Grass','Dirt','Water','White Square']
        for w in (x,Y,i,X,y):
            w.pack(side='left')
        tf.pack()
        v=tk.StringVar(value='Base Type')
        o=tk.OptionMenu(self.main,v,*basetiles)
        o.pack()
        for w in (tf,x,X,i,Y,y,o):
            k=w.config()
            for c in conf:
                if c in k:
                    w.config({c:conf[c]})
        o.config(fg='black')
        def okcmd():
            self.main.destroy()
            bs=v.get()
            if bs=='Base Type':
                bs='Blank'
            self.geometry('750x500')
            MapMaker(self,width=int(xv.get()),height=int(yv.get()),basecell=bs).pack(fill='both',expand=True)
        b=CustomButton(self.main,text='Ok',command=okcmd,inactive=conf)
        b.pack()       

from .TileDrawer import *
from .TileEditorFrame import *
from .TileLister import *
from .CharacterLister import *
from .CharacterEditorFrame import *
from .CharacterDrawer import *

from ..Preppers import *

class MapMaker(tk.Frame):

    TileDrawer=TileDrawer
    TileEditorFrame=TileEditorFrame
    TileLister=TileLister
    CharacterLister=CharacterLister
    CharacterEditorFrame=CharacterEditorFrame
    CharacterDrawer=CharacterDrawer

    TileConfigurer=lambda s,*a,**kw:s.TileEditorFrame(s,*a,**kw)
    CharacterConfigurer=lambda s,*a,**kw:s.CharacterEditorFrame(s,*a,**kw)
    
    def __init__(self,root,file=None,
            mapname=None,width=36,height=36,
            a_button=a_button,b_button=b_button,start_button=start_button,
            **kwargs):
        
        m=tk.Menu(root)
        for n,s in (
            ('File',
             (
                 ('New map',MapInterface),
                 ('Open map directory',lambda:open_file(maps)),
                 ('Open tile directory',lambda:open_file(tiles)),
                 ('Tile prepper instance',lambda:PrepperWindow())
             )
            ),
            ('Edit',
             (
                 ('Edit Character',lambda:self.EditMode('char')),
                 ('Edit Tiles',lambda:self.EditMode('tile'))
             )
            ),
            ('Help',
             (
                ('Open Help',lambda:HelpText(editor_help)),
             )
            )                
            ):
            M=tk.Menu(m)
            for name,com in s:
                M.add_command(label=name,command=com)
            m.add_cascade(label=n,menu=M)
        root.config(menu=m)

        self.last_changed=deque()
        
        self.drawevents=[None,None]
        super().__init__(root)
        #Sets up the main frame and stuff
        main=self#tk.Frame(root)
        #main.pack(fill='both',expand=True)
        main.grid_rowconfigure(1,weight=1)
        main.grid_columnconfigure(0,weight=1)
        #Sets up the non-map, non-tile widgets
        lf=tk.LabelFrame(main,text='Name')
        lf.grid(row=0,column=0,sticky='ew')
        self.name_v=tk.StringVar(self)
        self.nent=tk.Entry(lf,relief='flat',textvariable=self.name_v)
        self.nent.pack(padx=10,fill='x')
        self.panes=tk.PanedWindow(main,orient='horizontal')
        self.panes.grid(row=1,column=0,sticky='nsew')
        self.display=D=FormattingGrid(main,rows=6,columns=1,bd=3,relief='groove',bg='grey85')
        D.bind('<Button-1>',lambda e,s=self:s.focus_set())
        self.display.all=B=D.AddFormat(tk.Button,text='Expand View',command=self.ViewAll)
        self.display.revert=C=D.AddFormat(tk.Button,text='Revert View',command=self.RevertView)
        self.display.poke=P=D.AddFormat(tk.Button,text='Edit Pokemon',command=self.EditPokemon)
        self.display.gates=GP=D.AddFormat(tk.Button,text='Edit Entrances/Exits',command=self.EditGatePoints)
        self.display.m_cell=M=D.AddFormat(tk.LabelFrame,text='Mouse Cell')
        self.display.size_setter=S=D.AddFormat(tk.LabelFrame,text='View')
        S.view_crn=VC=tk.LabelFrame(S,text='View Corner');S.view_crn.pack(side='top',fill='x')
        self.i_corner=tk.StringVar(self);self.j_corner=tk.StringVar(self)
        for l in ('(',self.i_corner,',',self.j_corner,')'):
            if isinstance(l,str):
                tk.Label(VC,text=l).pack(side='left')
            else:
                tk.Entry(VC,textvariable=l,width=2,relief='flat').pack(side='left')
        S.view_set=VS=tk.LabelFrame(S,text='View Size');VS.pack(side='top',fill='x')
        self.i_size=tk.StringVar(self,value=str(screen_tile_range[0]))
        self.j_size=tk.StringVar(self,value=str(screen_tile_range[1]))
        for l in ('(',self.i_size,',',self.j_size,')'):
            if isinstance(l,str):
                tk.Label(VS,text=l).pack(side='left')
            else:
                tk.Entry(VS,textvariable=l,width=2,relief='flat').pack(side='left')
        
        for v in (self.i_corner,self.j_corner,self.i_size,self.j_size):
            v.trace('w',self.AdjustSize)

        self.transformation=tk.StringVar(value='rotate')
        self.tf=D.AddFormat(tk.Frame,relief='ridge',bd=2)#FormattingGrid,rows=1,columns=3
        i=0
        for n,choice in zip(('R','H','V'),('rotate','flip_horizontal','flip_vertical')):
            tk.Radiobutton(self.tf,variable=self.transformation,value=choice,text=n).grid(column=i,row=0)
            i+=1


        self.display.grid(row=0,column=1,rowspan=2,sticky='nsew')

        self.display.configure_rows(weight=0)
        self.display.configure_cols(weight=1)
        self.display.gridConfig(sticky='nsew')
        self.mouse_cell=tk.StringVar(value='None')
        M.l=tk.Label(M,textvariable=self.mouse_cell)
        M.l.pack(fill='both',expand=True)
        
        self.refresh_button=self.display.AddFormat(CustomButton,command=self.Reload,text='Reload Map')

        self.props=tk.Frame(main,bd=3,relief='groove',bg='grey45')
        self.props.grid(row=2,column=0,columnspan=2,sticky='nsew')
        self.props.bind('<Button-1>',lambda e,s=self:s.focus_set())
        
        
        
###---------------------TINT COLOR SHIT----------------------------###         
        self.tint_colors=tk.LabelFrame(self.props,text='Tint Colors')
        self.tint_colors.grid(row=1,column=0)
        self.tint_1=(
            tk.StringVar(value=''),
            tk.StringVar(value=''),
            tk.StringVar(value='')
            )
        self.tint_2=(
            tk.StringVar(self,value=''),
            tk.StringVar(self,value=''),
            tk.StringVar(self,value='')
            )
        
        
        def check_tint1(event=None,var=self.tint_1):
            for v in var:
                r=v.get()
                if not r:
                    r='a'
                try:
                    r=int(r)
                except ValueError:
                    return False
            else:
                if not event is True:
                    if check_tint2(True):
                        retint()
                else:
                    return True

        def retint(event=None):
            t1=tuple((eval(t.get()) for t in self.tint_1))
            t2=tuple((eval(t.get()) for t in self.tint_2))
            
            t=self.map.tint_colors
            e=(t1,t2)
            if not t==e:
                self.map.tint_colors=e
                self.colorize_map()
                    
                    
        def check_tint2(event=None,var=self.tint_2):
            for v in var:
                r=v.get()
                if not r:
                    r='a'
                try:
                    r=int(r)
                except ValueError:
                    return False
            else:
                if not event is True:
                    if check_tint1(True):
                        retint()
                else:
                    return True
                    
        self.tint_colors.tint_1=tk.Frame(self.tint_colors)
        self.tint1_entries=[
            tk.Entry(self.tint_colors.tint_1,width=3,
                                  textvariable=t,relief='flat')
                                for t in self.tint_1]            
         
        self.tint_colors.tint_1.grid(row=0,column=0)
        tk.Label(self.tint_colors.tint_1,text='(').pack(side='left')
        i=2
        for t in self.tint1_entries:
            t.pack(side='left')
            t.bind('<Leave>',check_tint1)
            if i>0:
                tk.Label(self.tint_colors.tint_1,text=',').pack(side='left')
                i-=1
        tk.Label(self.tint_colors.tint_1,text=')').pack(side='left')
            
        
        
        self.tint_colors.tint_2=tk.Frame(self.tint_colors)
        self.tint2_entries=[
            tk.Entry(self.tint_colors.tint_2,width=3,
                                  textvariable=t,relief='flat')
                                for t in self.tint_2]
         
        self.tint_colors.tint_2.grid(row=0,column=1)
        tk.Label(self.tint_colors.tint_2,text='(').pack(side='left')
        i=2
        for t in self.tint2_entries:
            t.pack(side='left')
            t.bind('<Leave>',check_tint2)
            if i>0:
                tk.Label(self.tint_colors.tint_2,text=',').pack(side='left')
                i-=1
        tk.Label(self.tint_colors.tint_2,text=')').pack(side='left')

####-----------------------COLORIZING RANGE SHIT------------------------------####
        self.color_ranges=tk.LabelFrame(self.props,text='Colorizing Ranges')
        self.color_ranges.grid(row=1,column=1)
        self.color_ranges_1=(
            tk.StringVar(value=''),
            tk.StringVar(value='')
            )
        self.color_ranges_2=(
            tk.StringVar(value=''),
            tk.StringVar(value='')
            )
        self.color_ranges.color_ranges_1=tk.Frame(self.color_ranges)
        self.color_ranges.color_ranges_2=tk.Frame(self.color_ranges)
        self.color_ranges.color_ranges_1.grid(row=0,column=0)
        self.color_ranges.color_ranges_2.grid(row=0,column=1)
        self.color_ranges_1_entries=[
            tk.Entry(self.color_ranges.color_ranges_1,width=3,
                                  textvariable=t,relief='flat')
                                for t in self.color_ranges_1]    
        self.color_ranges_2_entries=[
            tk.Entry(self.color_ranges.color_ranges_2,width=3,
                                  textvariable=t,relief='flat')
                                for t in self.color_ranges_2]     
        def check_range1(event=None,self=self):
            for s in self.color_ranges_1:
                i=s.get() 
                if not i:
                    i='a'
                try:
                    i=int(i)
                except ValueError:
                    return False
            else:
                if not event is True:
                    if check_range2(True):
                        recolorize()
                else:
                    return True
        def recolorize(event=None,self=self):
            r1=tuple((int(s.get()) for s in self.color_ranges_1))
            r2=tuple((int(s.get()) for s in self.color_ranges_2))
            self.map.colorizing_ranges=(r1,r2)
            self.colorize_map()
        def check_range2(event=None,self=self):
            for s in self.color_ranges_2:
                i=s.get() 
                if not i:
                    i='a'
                try:
                    i=int(i)
                except ValueError:
                    return False
            else:
                if not event is True:
                    if check_range1(True):
                        recolorize()
                else:
                    return True
        tk.Label(self.color_ranges.color_ranges_1,text='(').pack(side='left')
        i=1
        for t in self.color_ranges_1_entries:
            t.pack(side='left')
            t.bind('<Leave>',check_range1)
            if i>0:
                tk.Label(self.color_ranges.color_ranges_1,text=',').pack(side='left')
                i-=1
        tk.Label(self.color_ranges.color_ranges_1,text=')').pack(side='left')
        tk.Label(self.color_ranges.color_ranges_2,text='(').pack(side='left')
        i=1
        for t in self.color_ranges_2_entries:
            t.pack(side='left')
            t.bind('<Leave>',check_range2)
            if i>0:
                tk.Label(self.color_ranges.color_ranges_2,text=',').pack(side='left')
                i-=1
        tk.Label(self.color_ranges.color_ranges_2,text=')').pack(side='left')

####-----------------------SIDEBAR SHIT?--------------------------------------####            
        self.base_frame=tk.Frame(self.panes)
        #Sets up the tile widgets
        self.tile_frame=lf=tk.LabelFrame(self.base_frame,text='Tile')
        self.tiles=self.TileLister(lf)
        self.tiles.pack(fill='both',expand=True)
        tf=tk.Frame(lf)
        self.tooltip=[1,1]
        def callback(index,var):
            def internal(a,b,c):
                v=var.get()
                try:
                    v=int(v)
                except:
                    v=1
                self.tooltip[index]=v
            return internal
        xv=tk.StringVar(value=1);xv.trace('w',callback(0,xv))
        yv=tk.StringVar(value=1);yv.trace('w',callback(1,yv))                                        
        x=tk.Label(tf,text='Tooltip=(');X=tk.Entry(tf,textvariable=xv,width=2,relief='flat')
        i=tk.Label(tf,text=',')
        Y=tk.Entry(tf,textvariable=yv,width=2,relief='flat');y=tk.Label(tf,text=')')
        for e in (x,Y,i,X,y):
            e.pack(side='left')
        self.tiles.pack(fill='both',padx=5,expand=True)
        b=tk.Button(lf,text='Reload Tiles',command=self.tiles.reload)
        new_tile=tk.Button(lf,text='New Tile',command=lambda:self.TileConfigurer('__new__'))
        new_tile.pack(fill='x')
        b.pack(fill='x')
        tf.pack(fill='both')
        #Sets up the character widgets
        self.char_frame=cf=tk.LabelFrame(self.base_frame,text='Character')
        self.chars=self.CharacterLister(cf)
        self.chars.pack(fill='both',expand=True,anchor='n')
        b=tk.Button(cf,text='Reload Characters',command=self.chars.reload)
        b.pack(fill='x',anchor='s')
        #
        self.tile_frame.pack(expand=True,fill='both')
        self.panes.add(self.base_frame,sticky='nsew')
        #Sets up the map widget
        self.map_editor=tk.Frame(self.panes,bg='black')
        b_text={'text':' + '}
        m_text={'text':' - '}
        self.row_add_bar=RA=ButtonGrid(self.map_editor,rows=0,columns=1,command=self.AddRow,button_kwargs=b_text,pass_button=True)
        self.col_add_bar=CA=ButtonGrid(self.map_editor,columns=0,rows=1,command=self.AddColumn,button_kwargs=b_text,pass_button=True)
        self.map_frame=tk.Frame(self.map_editor,bg='black')
        self.row_del_bar=RD=ButtonGrid(self.map_editor,rows=0,columns=1,command=self.DelRow,button_kwargs=m_text,pass_button=True)
        self.col_del_bar=CD=ButtonGrid(self.map_editor,rows=1,columns=0,command=self.DelColumn,button_kwargs=m_text,pass_button=True)
        

        #   col_add_bar
        #row MAPMAPMAP  row
        #_   MAPMAPMAP  _
        #add MAPMAPMAP  del
        #_   MAPMAPMAP  _
        #bar MAPMAPMAP  bar
        #   col_del_bar
        
        self.col_add_bar.grid(column=1,sticky='ew')
        self.row_add_bar.grid(row=1,column=0,sticky='ns')
        self.map_frame.grid(row=1,column=1,sticky='nsew')
        self.row_del_bar.grid(row=1,column=2,sticky='ns')
        self.col_del_bar.grid(row=2,column=1,sticky='ew')

        self.map_editor.grid_rowconfigure(1,weight=1)
        self.map_editor.grid_columnconfigure(1,weight=1)
        
        self.flash=tk.Label(self.map_frame,text='EMPTY',bg='black')
        
        if file is None and mapname is None:
            m=Map(self.map_frame,width=width,height=height,
                initialcharacter=False,a_button=a_button,b_button=b_button,
                  manager=self,**kwargs)
        else:
            if file is None:
                mapname+='.pmp'
                file=os.path.join(maps,mapname)
            m=Map.LoadFromFile(self.map_frame,file,manager=self)
        self.map=m
        self.i_corner.set(str(m.base_y))
        self.j_corner.set(str(m.base_x))

        for i in range(screen_tile_range[0]):
            self.row_add_bar.AddButton(i,0)
            self.row_del_bar.AddButton(i,0)
        for j in range(screen_tile_range[1]):
            self.col_add_bar.AddButton(0,j)
            self.col_del_bar.AddButton(0,j)

        for x in (RA,CA,RD,CD):
            x.gridConfig(sticky='nsew')

        for x in (RA,RD):
            x.configure_rows(weight=1)

        for x in (CA,CD):
            x.configure_cols(weight=1)
  
####-----------------------TINT COLOR SHIT AGAIN-----------------####          
        tints=self.map.tint_colors
        if not tints is None:
            for tint_v,s in zip(self.tint_1,tints[0]):
                tint_v.set(str(s))
            for tint_v,s in zip(self.tint_2,tints[1]):
                tint_v.set(str(s))

####-----------------------COLORIZING SHIT AGAIN-----------------####    
        ranges=self.map.colorizing_ranges
        if not ranges is None:
            for col_v,s in zip(self.color_ranges_1,ranges[0]):
                col_v.set(str(s))
            for col_v,s in zip(self.color_ranges_2,ranges[1]):
                col_v.set(str(s))

####==========================BACK TO MAP SHIT-------------------####
        self.map.pack(fill='both',expand=True)
        self.name_v.set(self.map.name)
        self.name_v.trace('w',lambda*e,self=self:setattr(self.map,'name',self.name_v.get()))
        self.panes.add(self.map_editor,sticky='nsew')

        self.drawer=self.TileDrawer(self)
##        self.ClickGet=self.map.ClickGet
##        self.Draw=self.map.Draw
        self.makemode='tile'

        self.tiles.bind('<Double-Button-1>',lambda e:self.Edit(e,key='class'))
        self.chars.bind('<Double-Button-1>',lambda e:self.Edit(e,key='class'))

        self.map_bindings()
        
        for w in (self,self.nent,self.map):
            w.bind('<Command-r>',lambda e:self.Reload())
            w.bind('<Command-n>',lambda e:self.new_tile_type())
            w.bind('<Command-Shift-s>',lambda e:self.SaveAction(True))
            w.bind('<Command-s>',self.SaveAction)

        self.interp=None
        for w in (self,self.tiles,self.panes,self.nent,self.map):
            w.bind('<Command-i>',lambda e:self.Interact())
        self.map.focus_set()

        #allow for relinking map directory and event library
        
        self.selected=LinAlg.FullArray(dim=self.map.basearray.dimensions)
        self.copied=LinAlg.FullArray(dim=self.map.basearray.dimensions)
        self.selectionBorder=self.map.selectionBorder
        self.drawing=False
        
        self.resolve_title()
    
    def colorize_map(self):
        Character._file_tracker={}
        for c in self.map.basearray.items():
            if hasattr(c,'colorize'):
##                        c.reload_orientation()
                c.colorize(reload=True)
                for o in c.obs:
                    o.colorize()
                c.Draw()
                
    def AddRow(self,indexORwidget):
        iow=indexORwidget
        if isinstance(iow,int):
            i=iow
        else:
            i,j=iow.pos
##        self.row_add_bar.AddButton(i,0)
##        self.row_del_bar.AddButton(i,0)
        self.map.ExtendArray(i,mode='row',relative=True)
        self.Reload()
    def AddColumn(self,indexORwidget):
        iow=indexORwidget
        if isinstance(iow,int):
            j=iow
        else:
            i,j=iow.pos
##        self.col_add_bar.AddButton(0,j)
##        self.col_del_bar.AddButton(0,j)
        self.map.ExtendArray(j,mode='col',relative=True)
        self.Reload()
    def DelRow(self,indexORwidget):
        iow=indexORwidget
        if isinstance(iow,int):
            i=iow
        else:
            i,j=iow.pos
##        self.row_add_bar.DeleteButton(i,0)
##        self.row_del_bar.DeleteButton(i,0)
        self.map.ShortenArray(i,mode='row',relative=True)
        self.Reload()
    def DelColumn(self,indexORwidget):
        iow=indexORwidget
        if isinstance(iow,int):
            j=iow
        else:
            i,j=iow.pos
##        self.col_del_bar.DeleteButton(0,j)
##        self.col_del_bar.DeleteButton(0,j)
        self.map.ShortenArray(j,mode='col',relative=True)
        self.Reload()
    def undo(self,event=None):

        def undo_cmd(tup):
            c=tup[0]
            if isinstance(c,Tile):
                c.change_type(tup[2],tup[1])
            elif isinstance(c,Character):
                self.map.AddObject(c)
            else:
                for t in tup:
                    undo_cmd(t)
        try:
            r=self.last_changed.pop()
        except IndexError:
            pass
        else:
            undo_cmd(r)
        self.draw_call()

    def draw_call(self,bg=True):
        if not self.drawing:
            def drawp(self=self,bg=bg):
                if bg:
                    self.map.backgroundFlag=True
                self.Draw()
                self.drawing=False
            self.drawing=True
            self.after_idle(drawp)
            
    def ClickGet(self,event):
        e=self.map.ClickGet(event)
        if self.makemode=='char':
            try:
                e=e.obs[0]
            except IndexError:
                e=None
        return e

    def Draw(self,event=None):
        return self.map.Draw(event)
    
    def map_bindings(self):
        
        self.map.bind('<Button-1>',self.Create,add='+')
        self.map.bind('<B1-Motion>',lambda e:self.drawer.create(e))
        self.map.bind('<ButtonRelease-1>',lambda e:(self.Draw(),setattr(self.drawer,'last',None)))
        self.map.bind('<Command-Button-1>',self.CreateCharacter,add='+')
        self.map.bind('<Control-Button-1>',self.ClickTransform)
        self.map.bind('<Double-Button-1>',self.Edit)
        self.map.bind('<BackSpace>',lambda e:self.DeleteSelected())                                         
        self.map.bind('<Command-s>',self.SaveAction)
        self.map.bind('<Command-Shift-s>',lambda e:self.SaveAction(True))
        self.map.bind('<Command-c>',lambda e:self.Copy())
        self.map.bind('<Command-n>',lambda e:self.new_tile_type())
        self.map.bind('<Command-z>',self.undo)
        self.map.bind('<Shift-Button-1>',self.Paste)
        self.map.bind('<Control-e>',lambda e:self.EditMode('char'))
        self.map.bind('<Control-t>',lambda e:self.EditMode('tile'))
        self.map.bind('<Command-i>',self.Interact)

        self.map.bind('<Motion>', lambda e,self=self:self.mouse_cell.set( str( self.map.MouseCell(e) ) ) ) 
        self.map.bind('<Leave>',lambda e:self.mouse_cell.set('None'))

    def new_tile_type(self,event=None):
        r,c=self.copied.dimensions
        text=''
        for row in self.copied.rowiter():
            text+='{}\n'.format('|'.join((str(t.lookup_name) for t in row)))
        top=tk.Toplevel(self)
        wind=RichText(top,highlightthickness=0)
        wind.Insert(text)
        wind.pack(fill='both',expand=True)
        wind.save_bind()
        wind.track_edits_bind()
        wind.defaultext='.tlf'
        top.title('New Tile')
    
    def resolve_title(self):
        f=self.map.file
        char_len=100
        try:
            if len(f)>char_len+3:
                f=f[:int(char_len/2)]+'...'+f[-int(char_len/2):]
            self.master.title(f)
        except:
            pass
    def SaveAction(self,event=None):
        
        d=self.map.dir
        if d is None:
            d=maps
        
        if event is True:
            from tkinter.filedialog import asksaveasfilename as ask
            file=ask(parent=self,defaultextension='.pmp')
            if file!='':
                self.map.file=file
                d=None
        
        
        self.map.Save(d)
        self.resolve_title()
        self.nent.delete(0,'end')
        self.nent.insert(0,os.path.splitext(os.path.basename(self.map.file))[0])
        self.nent['fg']='purple'
        return 'break'
        
    def NoteChanges(self,event=None):
        t=self.master.title()
        if t[0]!="*":
            t='* {} *'.format(t)
            self.master.title(t)
        self.nent['fg']='black'
    
    @property
    def map_dir(self):
        from tkinter.filedialog import askdirectory as ask
        df=os.path.dirname(self.map.file)
        if not df:
            df=ask(parent=self,title='Choose Map Directory',initialdir=maps)
        return maps if not df else df
        
    def SwitchMap(self,which,old=None,C=None,root=None,source=None):
        self['bg']='black'
        if old is None:
            old=self.map
        old.pack_forget()
        self.map.hold_update(15)

        if isinstance(which,Map):
            new=which
        else:
            Tile._file_tracker.clear()
            Character._file_tracker.clear()
            try:
                new=old.LoadMap(which,C=C,root=root,source=source)
            except FileNotFoundError:
                old.pack(fill='both',expand=True)
                old.focus_set()
                raise

        self.NoteChanges()
        self.nent.delete(0,'end')
        self.map=new
        self.resolve_title()

        tints=self.map.tint_colors
        if tints is None:
            t1=t2=('','','')
        else:
            t1,t2=[[str(x) for x in t] for t in tints]
        for tint_v,s in zip(self.tint_1,t1):
            tint_v.set(s)
        for tint_v,s in zip(self.tint_2,t2):
            tint_v.set(s)
        ranges=self.map.colorizing_ranges
        if not ranges is None:
            for col_v,s in zip(self.color_ranges_1,ranges[0]):
                col_v.set(s)
            for col_v,s in zip(self.color_ranges_2,ranges[1]):
                col_v.set(s)
            
        self.map_bindings()
        self.map.pack(fill='both',expand=True)
        self.nent.insert(0,os.path.splitext(os.path.basename(self.map.file))[0])
        self.map.focus_set()
        
        self.selected=LinAlg.FullArray(dim=self.map.basearray.dimensions)
        self.copied=LinAlg.FullArray(dim=self.map.basearray.dimensions)

    def StartBattle(self,team1,team2):
        #flash black screen
        self.map.pack_forget()
        self.flash.pack(fill='both',expand=True)
##        if isintance(team1,Pokem
        protection=tk.Frame(self.map_frame)
        protection.pack(fill='both',expand=True)
        self.flash.pack_forget()
        w,h=(self.map_frame.winfo_width(),self.map_frame.winfo_height())
        battle=BattleHolder(protection,team1,team2,width=w,height=h)
        battle.pack(fill='both',expand=True)
        self.wait_variable(battle.done_flag)
        r=battle.done_flag.get()
        protection.destroy()
##        self.battle.pack_forget()
        self.map.pack(fill='both',expand=True)
        self.map.focus_set()
        return r
        
    def Reload(self):
        for tile in self.map.basearray.items():
            tile.reload()
        self.selected=LinAlg.FullArray(dim=self.map.basearray.dimensions)
        self.copied=LinAlg.FullArray(dim=self.map.basearray.dimensions)
        self.map.backgroundFlag=True
        self.map.Draw()
        
    def Interact(self,event=None):
##        Interactor(self)
        if self.interp is None:
            self.interp=tk.Frame(self)
            self.interp.pack_propagate(False)
            I=InterpreterText(self.interp,variables={'main':self,
                                                        'map':self.map,
                                                        'char':self.map.character},
                                        newThread=False)
            I.pack(fill='both',expand=True)
            try:
                self.master.geometry('{}x{}'.format(self.winfo_width(),self.winfo_height()+100))
            except AttributeError:
                pass
            self.interp['height']=100
            self.interp.grid(row=3,columnspan=2,sticky='nsew')
            
##            self.master.geometry('{}x{}
        else:
            self.interp.destroy()
            try:
                self.master.geometry('{}x{}'.format(self.winfo_width(),self.winfo_height()-100))
            except AttributeError:
                pass
            self.interp=None

    def ClickTransform(self,event):
        E=self.ClickGet(event)
        T=self.transformation.get()
        if T=='rotate':
            E.Rotate()
        elif T=='flip_horizontal':
            E.Flip('horizontal')
        elif T=='flip_vertical':
            E.Flip('vertical')
            
    def Create(self,event):

        self.NoteChanges()
        m=self.makemode
        if m=='tile':
            self.TileChange(event)
        elif m=='item':
            raise NotImplementedError
        elif m=='character':
            self.CreateCharacter(event)
        elif m=='link':
            raise NotImplementedError
        self.draw_call()
    
    def TileChange(self,event):

        import os
        
        t=self.tiles.tile
        c=self.map.ClickGet(event)
        if t=='Select':
            m,n=c.pos
            x,y=self.tooltip
            q=(x*y)
            if q==1:
                obs=[c]
            else:
                obs=[None]*q
                for i in range(0,x):
                    for j in range(0,y):
                        try:
                            obs[j*x+i]=self.map.cellget((m+j,n+i))
                        except:
                            obs[j*x+i]=None
            for c in obs:
                if not c is None:
                    self.selectionBorder.cell[:]=c.pos
                    c.border=self.selectionBorder
                    self.map.AddObject(c.border)
                    i,j=c.pos
                    try:
                        sel=self.selected[i,j]
                    except IndexError:
                        tb.print_exc()
                        print('Out of bounds: {}x{}'.format(i,j))
                    else:                    
                        if not sel is c:
                            self.selected[i,j]=c
                        else:
                            c.remove(c.border)
                            self.selected[i,j]=self.selected.Empty
                    
        elif not t is None:
            s=self.tiles.source
            tile_path=os.path.join(tiles,s,t+'.tlf')
            if os.path.isfile(tile_path):
                positions=[]
                i,j=c.pos
                j_hook=j
                with open(tile_path) as f:
                    for line in f:
                        line=line.strip()
                        if line:
                            j=j_hook
                            for name in line.split('|'):
                                name=name.strip()
                                positions.append(((i,j),name))
                                j+=1
                            i+=1

                to_add=[]
                for tup,n in positions:
                    c=self.map.cellget(tup)
                    os=c.source
                    on=c.name
                    c.change_type(n,source=s)
                    c.Background()
                    to_add.append((c,os,on))
                    self.drawer.last=c
                self.last_changed.append(to_add)
                    
            else:
                m,n=c.pos
                x,y=self.tooltip
                q=(x*y)
                if q==1:
                    obs=[c]
                else:
                    obs=[None]*q
                    for i in range(0,x):
                        for j in range(0,y):
                            obs[j*x+i]=self.map.cellget((m+j,n+i))
                for c in obs:
                    os=c.source
                    on=c.name
                    c.change_type(t,source=s)
                    c.Background()
                    self.last_changed.append((c,os,on))
                    self.drawer.last=c
                    
##        self.map.Draw()

    def EditGatePoints(self):
        W=13
        
        try:
            gp_edit=self.gate_point_editor
        except AttributeError:
            self.gate_point_editor=gp_edit=None
        else:
            if not self.gate_point_editor.winfo_exists():
                gp_edit=None
        if gp_edit is None:
            self.gate_point_editor=T=tk.Toplevel(self)
            T.title('Entrance/Exit config')
            T.attributes('-topmost',True)
            L=tk.LabelFrame(T,text='Exits')
            exits=F=EntryGrid(L,columns=3,rows=4)
            F[0,0]='Exit Name';F[0,1]='New Map Name';F[0,2]='Which Entrance'
            for i in range(3):
                F.command_configure(0,i,state='readonly',relief='flat')
            F.pack(fill='both',expand=True)
        
            B=tk.Button(L,text='+',command=lambda F=F:(F.AddRow(),F.configure_all(width=W)))
            B.pack(fill='x',anchor='s',expand=True)
            L.pack(fill='both',side='right')
            n=3
            i=1
        
            exit_items=sorted(self.map.exits.items(),key=lambda t:t[0])
            for k,e in exit_items:
    ##            try:
                F[i,0]=k;F[i,1]=e[0];F[i,2]=e[1]
    ##            except IndexError:
    ##                print(i)
    ##                raise
                i+=1
                if i>=n:
                    F.AddRow()
                    n+=1
            F.configure_all(width=W)
            L=tk.LabelFrame(T,text='Entrances')
            entries=F=EntryGrid(L,columns=3,rows=4)
            F[0,0]='Entrance Name';F[0,1]='Row';F[0,2]='Column'
            for i in range(3):
                F.command_configure(0,i,state='readonly',relief='flat')
            B=tk.Button(L,text='+',command=lambda F=F:(F.AddRow(),F.configure_all(width=W)))
            F.pack(fill='both',expand=True)
            B.pack(fill='x',anchor='s',expand=True)
            L.pack(fill='both',side='right')
            n=3
            i=1
            entrance_items=sorted(self.map.entries.items(),key=lambda t:t[0])
            for k,e in entrance_items:
                F[i,0]=k;F[i,1]=e[0];F[i,2]=e[1]
                i+=1
                if i>=n:
                    F.AddRow()
                    n+=1
            F.configure_all(width=W)

            def save_action(exits=exits,entries=entries):
                self.map.exits={}
                I=exits.RowIterator()
                next(I)
                for n,m,v in I:
                    if n:
                        self.map.exits[n]=(m,v)
                self.map.entries={}
                I=entries.RowIterator()
                next(I)
                for n,r,c in I:
                    if n:
                        self.map.entries[n]=(int(r),int(c))

            T.protocol('WM_DELETE_WINDOW',lambda:(save_action(),T.destroy()))

        
    def Deselect(self):
        cf=False
        r,c=self.selected.dimensions
        for i in range(r):
            for j in range(c):
                x=self.selected[i,j]
                if not x is self.selected.Empty:
                    x.remove(x.border,triggers=())
                    self.selected[i,j]=self.selected.Empty
                    cf=True
        if cf:
            self.Draw()

    def Copy(self):
        self.selected.collapse()
        r,c=self.copied.dim()
        for i in range(r):
            for j in range(c):
                x=self.selected[i,j]
                y=self.copied[i,j]
                if x is self.selected.Empty and y is self.selected.Empty:
                    break
                self.copied[i,j]=x
        self.Deselect()

    def Paste(self,where):

        self.tiles.tile=None
        if not self.copied is None:
            if isinstance(where,tk.Event):
                where=self.map.ClickGet(where).pos
            xs,ys=where
            r,c=self.copied.dim()
            for i in range(r):
                for j in range(c):
                    x=self.copied[i,j]
                    if x is self.copied.Empty:
                        break
                    self.map.cellget((i+xs,j+ys)).string_set(x.save_string())
        self.Deselect()
        
    def ItemCreate(self,event,item):
        raise NotImplementedError
    
    def CreateCharacter(self,event):
        c=self.map.ClickGet(event)
        if not self.makemode=='char':
            if not self.map.character:
                self.map.NewCharacter(*c.pos,NPC=False)
        else:
            t=self.chars.char
            if t=='Select':
                m,n=c.pos
                x,y=self.tooltip
                q=(x*y)
                if q==1:
                    obs=[c]
                else:
                    obs=[None]*q
                    for i in range(0,x):
                        for j in range(0,y):
                            obs[j*x+i]=self.map.cellget((m+j,n+i))
                for c in obs:
                    self.selectionBorder.cell[:]=c.pos
                    c.border=self.selectionBorder
                    self.map.AddObject(c.border)
                    i,j=c.pos
                    if not self.selected[i,j] is c:
                        self.selected[i,j]=c
                    else:
                        c.remove(c.border)
                        self.selected[i,j]=self.selected.Empty
            elif t=='No Selection':
                pass
            else:
                self.map.NewCharacter(*c.pos,name=t,source=self.chars.source)

    def DeleteSelected(self):
        rmv=[]
        Em=self.selected.Empty
        if self.makemode=='tile':
            for t in self.selected.items():
                if not t is Em:
                    n=t.name
                    s=t.source
                    t.change_type('Blank')
                    rmv.append((t,s,n))
                
        elif self.makemode=='char':
            for t in self.selected.items():
                if not t is Em:
                    for x in t.obs:
                        rmv.append((x,))
                    t.clear_objects()

        if rmv:
            self.last_changed.append(rmv)
        self.Deselect()
        
    def EditMode(self,key):
        self.makemode=key
        if key=='tile':
            self.char_frame.pack_forget()
            self.tile_frame.pack(fill='both',expand=True)
            self.drawer=self.TileDrawer(self)
        elif key=='char':
            self.tile_frame.pack_forget()
            self.char_frame.pack(fill='both',expand=True)
            self.drawer=self.CharacterDrawer(self)
                                  
    def Edit(self,event,**kwargs):
        m=self.makemode
        if m=='tile':
            self.EditTile(event,**kwargs)
        elif m=='char':
            self.EditChar(event,**kwargs)

    def EditChar(self,event,key='char'):
        if key=='class':
            char=self.chars.char
            if not char is None and not char in ('No Selection','Select'):
                char=os.path.join(chars,self.chars.source,char)
                self.CharacterConfigurer(char)
        else:
            tile=self.map.ClickGet(event)
            try:
                char=tile[0]
            except IndexError:
                pass
            else:
                self.CharacterConfigurer(char)
    
    def EditTile(self,event,key='tile'):
        if key=='class':
            tile=self.tiles.tile
            if not tile is None and not tile in ('No Selection','Select'):
                tile=os.path.join(tiles,self.tiles.source,tile)
                if self.tiles.trf=='tile':
                    self.TileConfigurer(tile)
                else:
                    PlatformIndependent.open_file(tile+'.tlf','TextWrangler')
        else:
            tile=self.map.ClickGet(event)
            self.TileConfigurer(tile)
    
    def AdjustSize(self,*whatever):
        i_corner=self.i_corner.get()
        j_corner=self.j_corner.get()
        i_size=self.i_size.get()
        j_size=self.j_size.get()
        if i_corner and j_corner and i_size and j_size:
            i_corner=int(i_corner) 
            j_corner=int(j_corner)
            i_size=int(i_size)
            j_size=int(j_size)
            x,y,i,j=self.SetView(j_corner,i_corner,i_size,j_size)
            self.j_corner.set(str(x))
            self.i_corner.set(str(y))
            self.i_size.set(str(i))
            self.j_size.set(str(j))
        
    def SetView(self,x,y,i,j):
        r,c=self.map.basearray.dimensions
        i=max(min(r,i),1);j=max(min(j,c),1)
        x=min(x,c-j);y=min(y,r-i)
        self.map.base_x=x
        self.map.base_y=y
        self.map.SetSize(i,j)
        self.map.CalculateBounds()
        self.backgroundFlag=True
        self.Draw()
        if i!=screen_tile_range[0]:
            self.row_add_bar.grid_forget()
            self.row_del_bar.grid_forget()
        else:
            self.row_add_bar.grid(row=1,column=0,sticky='ns')
            self.row_del_bar.grid(row=1,column=2,sticky='ns')
        if j!=screen_tile_range[1]:
            self.col_add_bar.grid_forget()
            self.col_del_bar.grid_forget()
        else:
            self.col_add_bar.grid(row=0,column=1,sticky='ew')
            self.col_del_bar.grid(row=2,column=1,sticky='ew')
        return (x,y,i,j)
        
    def ViewAll(self):

        for a in (self.col_add_bar,self.row_add_bar,
                  self.col_del_bar,self.row_del_bar):
            a.grid_forget()
        r,c=self.map.basearray.dim()
        self.save_dim=[self.map.cols,self.map.rows]
        self.save_pos=[self.map.base_x,self.map.base_y]
        self.save_size=(self.winfo_width(),self.winfo_height())
        w=25*c+50;h=25*r+100
##        self.map.Clear()
        root=self.master
        gstring='{}x{}'.format(h,w)
        flag=True
        while flag:
            try:
                root.geometry(gstring)
                flag=False
            except:
                try:
                    root=root.master
                except:
                    flag=False
        else:
            self.map.SetSize(r,c)
            self.display.all.grid_forget()
            self.display.revert.grid(row=0,column=0)
            self.map.button_bind('disabled')
            self.after(100,self.Draw)

    def RevertView(self):
        self.col_add_bar.grid(row=0,column=1,sticky='ew')
        self.row_add_bar.grid(row=1,column=0,sticky='ns')
        self.row_del_bar.grid(row=1,column=2,sticky='ns')
        self.col_del_bar.grid(row=2,column=1,sticky='ew')
        x,y=self.save_size
        rel_w=self.winfo_width()-self.map.winfo_width()
        rel_h=self.winfo_height()-self.map.winfo_height()
        gstring='{}x{}'.format(rel_w+self.map.standard_dimensions[0],
                               rel_h+self.map.standard_dimensions[1])
        root=self.master
        flag=True
        while flag:
            try:
                root.geometry(gstring)
                flag=False
            except:
                try:
                    root=root.master
                except:
                    flag=False
        else:
            self.map.SetSize(*self.save_dim)
            x_dif=self.save_pos[0]-self.map.base_x
            y_dif=self.save_pos[1]-self.map.base_y
            self.map.MoveView(x_dif,y_dif)
            self.display.revert.grid_forget()
            self.display.all.grid(row=0,column=0)
            self.map.button_bind()
            self.after(100,self.Draw)
        
    def EditPokemon(self):
        try:
            pk_edit=self.pk_edit
        except AttributeError:
            self.pk_edit=pk_edit=None
        else:
            if not self.pk_edit.winfo_exists():
                pk_edit=None
        if pk_edit is None:
            self.pk_edit=T=tk.Toplevel(self,bd=3,relief='ridge')
            T.title('Pokemon')
            help_text='''
Add encounterable pokemon for a given tile type below, e.g.:

grass:
Mew { levels: 1-20 rate:.1
Pikachu { levels: 1,2,5-10,99 rate:.1
Zapados { levels: 5

For Pokemon found while fishing, use the tile type 'fishing'
'''.strip()
            T.H=help_bar=RichText(T,
                highlightthickness=0,height=len(help_text.splitlines()),
                bd=3,relief='groove',cursor='arrow')
            help_bar.Append(help_text)
            help_bar.grid(row=0,column=0,sticky='nsew')
            help_bar.bind('<B1-Motion>',lambda e:'break')
            help_bar.bind('<FocusIn>',lambda e,T=T:T.R.focus_set())
            T.R=R=RichText(T)
            R.grid(row=1,column=0,sticky='nsew')
            T.grid_rowconfigure(1,weight=1);T.grid_columnconfigure(0,weight=1)
            
            tile_pokemons=sorted(self.map.pokemon.items(),key=lambda p:p[0])
            for tile,pokemon in tile_pokemons:
                R.Append('{}:\n'.format(tile))
                pokemon=sorted([(p,pokemon[p]) for p in pokemon],key=lambda d:d[0])
                
                for p in pokemon:
                    pokemon=p[0]
                    levels,rate=p[1]
                    levels_sorted=sorted(levels);
                    level_ranges=[]
                    enumerator=enumerate(levels_sorted)
                    i,v=next(enumerator)
                    this_range=[v,v]
                    for i,v in enumerator:
                        if v!=this_range[1]+1:
                            level_ranges.append(this_range)
                            this_range=[v,v]
                        else:
                            this_range[1]=v
                    level_ranges.append(this_range)
                        
                    levels=[('{0[0]}-{0[1]}' if r[1]>r[0]+1 else '{0[0]},{0[1]}' if r[1]==r[0]+1 else '{0[0]}').format(r)
                        for r in level_ranges]
                    R.Append('{pokemon} {{ levels: {levels} rate: {rate}\n'.format(
                        pokemon=p[0],
                        levels=','.join(levels),
                        rate='Default' if rate is None else rate
                        ))
#                 text=['{}:{}'.format(k,l) for k,l in pokemon.items()]
#                 R.Append('{}:{{{}}}\n'.format(tile,'|'.join(text)))
                
            def save_act(T=T):
                
                pokemans=None
                defaults=self.map.pokemon['=default=']
                self.map.pokemon={'=default=':defaults}
                line_set=R.getAll().splitlines();end_count=len(line_set)
                line_set.append('')
                for i,x in enumerate(line_set):
                    x=x.strip()
                    if i==end_count or x:
                    
                        if i==end_count:
                            if not pokemans is None:
                                self.map.pokemon[current_tile]=pokemans
                                
                        elif x[-1]==':' or (
                            (pokemans is None or len(pokemans)>0) and not ('{' in x)
                            ):
                            if not pokemans is None:
                                self.map.pokemon[current_tile]=pokemans
#                             print(x)
                            current_tile=x[:-1]
                            pokemans={}
                            
                        else:
                            bits=x.split('{')
                            if len(bits)==1:
                                p=bits[0];levels=(5,);rate=None
                            else:
                                p,app=bits
                                if not p:
                                    p='<RANDOM>'                         
                                r_key='rate:'
                                rate_index=app.find(r_key)
                                if rate_index>0:
                                    app,rate=app.split('rate:')
                                    try:
                                        rate=float(rate)
                                    except ValueError:
                                        rate=None
                                else:
                                    rate=None
                                    
                                levels=app.strip().strip('levels:')
                                levels_new=[]
                                for l in levels.split(','):
                                    if '-' in l:
                                        m,M=l.split('-')
                                        m=int(m);M=int(M)
                                        levels_new.extend(range(m,M+1))
                                    else:
                                        levels_new.append(int(l))
                                        
                                levels=tuple(levels_new)
                            pokemans[p.strip()]=(levels,rate)
                                
                T.destroy()                    
            T.protocol('WM_DELETE_WINDOW',save_act)
        
class BattleTest(tk.Toplevel):
    def __init__(self,master=None):  
        from GUITools.ExtraWidgets.ShellFrame import ShellFrame      
        super().__init__(master)
        self.title('Pokemon Battle')
        m=tk.Menu(self)
        for n,s in (
            ('Help',
             (
                ('Open Help',lambda:HelpText(battle_help)),
             )
            ),):
            M=tk.Menu(m)
            for name,com in s:
                M.add_command(label=name,command=com)
            m.add_cascade(label=n,menu=M)
        self.config(menu=m)
        self.S=ShellFrame(self,bg='gray15',bd=3,relief='groove')
        self.battle_frame=tk.Frame(self.S);self.S.set_widget(self.battle_frame)
        self.S.pack(fill='both',expand=True);self.S.toggle_shell()
        self.b=None
        self.toggled=False
        self.init()
    
    def draw_circles(self):
        for x,b in self.w.buttons.items():
            for k,i in b.button_hooks.items():
                
                x,y=self.w.coords(i)
                self.w.create_oval(x,y,x+10,y+10)
            
    def load_battle(self,event=None,k1=None,k2=None):
        from .. import DataTypes as dev1
        from .. import PokemonBattle as dev2
        import tkinter as tk
        from random import choice

        pokes=range(1,152)
        levs=range(5,20)
        nums=range(3,7)
        team1=[dev1.Pokemon(choice(pokes),level=choice(levs)) for i in range(choice(nums)-1)]
        team2=[dev1.Pokemon(choice(pokes),level=choice(levs)) for i in range(choice(nums))]
        team1.append(dev1.Pokemon('Magikarp',level=99))
        if not self.b is None:
            self.b.destroy()
        self.p1=team1
        self.p2=team2

        inventory={x:choice(range(1,100)) for x in ('PokeBall',
                                                  'Potion',
                                                  'Antidote',
                                                  'Paralyze Heal',
                                                  'Full Restore')}
        self.b=dev2.BattleHolder(self.battle_frame,self.p1,self.p2,inventory1=inventory,
                                 currently_visible=True,width=350)
        self.b.battle.bind('<Double-Button-1>',self.toggle_shell)
        self.b.pack(fill='both',expand=True)
        self.S.holder=self.b
        self.S.battle=self.b.battle
        self.b.done_flag.trace('w',self.load_battle)

    def init(self,event=None):
        if not self.winfo_viewable():
            self.wait_visibility(self)
        self.load_battle()
        
    def toggle_shell(self,event=None):
        self.S.toggle_shell()

animation_help='''This is the animation editor

Commands can be typed on the right and run with Command-Enter

Commands are simply animation frame functions, plus the key words repeat and end_repeat

repeat [<times> [<var>]] repeats the following commands <times> times, binding the iteration value to <var>

end_repeat ends a repeating block

variables defined in run are bound to the animation frame can be accessed via attr[<var>]
'''
class AnimationEditor(tk.Toplevel):
    
    animations=getdir('animations')
    images=os.path.join(animations,'Images')
    def __init__(self,master=None):
        from GUITools.GraphicsWidgets.AnimationFrame.AnimationWriter import AnimationWriter as AW
        from GUITools.ExtraWidgets.ShellFrame import ShellFrame
        
        super().__init__(master)
        
        self.title('Animation Editor')
        
        m=tk.Menu(master)
        for n,s in (
            ('Help',
             (
                ('Open Help',lambda:HelpText(animation_help)),
             )
            ),):
            M=tk.Menu(m)
            for name,com in s:
                M.add_command(label=name,command=com)
            m.add_cascade(label=n,menu=M)
        self.config(menu=m)
        
        S=ShellFrame(self,bg='gray15',bd=3,relief='groove')
        A=AW(S,animation_source=self.animations,
             image_source=self.images,
             bd=2,relief='groove')
        S.set_widget(A);S.pack(fill='both',expand=True)
        
        self.geometry('600x500')

    
