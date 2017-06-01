from Fauxkemon.code.State import *
from Fauxkemon.code.Map import Map
from Fauxkemon.code.MapMaker import *
from Fauxkemon.code.DataTypes import *
from Fauxkemon.code.PokemonBattle import BattleHolder

misc=getdir('misc')

class GameScreen(tk.Frame):
    base_bg='grey25'
    inner_base_bg='grey75'
    def __init__(self,root=None,game=None,edit_game=False,version='Pokemon Yellow',**kwargs):
    
        if not ('bg' in kwargs or 'background' in kwargs):
            kwargs['bg']=self.base_bg
        super().__init__(root,**kwargs)
        image_file=os.path.join(misc,'title.png')
        if os.path.exists(image_file):
            self.title_image=ImageLabel(self,image_file,bg=self.base_bg)
            self.title_image.pack(fill='both',expand=True,padx=10,pady=10)
            self.title_image.bind('<Button-1>',lambda e,s=self:s.focus_set())
        else:
            self.title_image=None
        
        self.screens=set()
        
        self.font=PokeFont()
        self.edit_flag=tk.BooleanVar(value=edit_game)
        
        self.bind('<Button-1>',lambda e,s=self:s.focus_set())
        
        def initialize(self=self,game=game,version=version):
            
            continue_flag=True            
            if game is None:
                try:
                    self.ChooseGame()
                except:
                    tb.print_exc()
                    continue_flag=False
            else:
                self.game=GameFolder(game,version)
                
            if continue_flag and hasattr(self,'game'):
                with open(self.game.flags,encoding='utf-8') as f:
                    flags=eval(f.read())
                if self.edit_flag.get():
                    #allow for choice of different start point
                    self.map=MapMaker(self,file=os.path.join(maps,self.game.ext,'Pallet Town.pmp'))
                    self.master.geometry('{}x{}'.format(self.winfo_width()+300,self.winfo_height()+100))
                else:
                    self.map=Map.LoadFromFile(self,self.game.map,flags=(flags,set(flags)),
                        a_button=a_button,b_button=b_button)
                    self.map.character.trainer=self.trainer
                    w,h=self.map.standard_dimensions
                    self['width']=w;self['height']=h
                if not self.title_image is None:
                    self.title_image.pack_forget()
                self.map.pack(fill='both',expand=True)
        
        if hasattr(self.master,'geometry'):
            self.master.geometry('{0[0]}x{0[1]}'.format(standard_screen_dimensions))
            self.master.menu=tk.Menu(self.master)
            self.master.config(menu=self.master.menu)
            self.master.menu.sub_menus={}
            for n,s in (
                ('Game',
                    (
                    ('Home Screen',lambda self=self:(self.destroy(), type(self)(self.master).pack(fill='both',expand=True))),
                    ('Quit',lambda self=self:self.master.master.destroy())
                    )
                ),
                ('Edit',
                    (
                    ('Open Editor',GameEditor),
                    )
                ),
                ('Window',
                    (
                    )
                ),
                ('Help',
                    (
                    )
                )
                ):
                sub_menu=tk.Menu(self.master.menu)
                self.master.menu.sub_menus[n]=sub_menu
                self.master.menu.add_cascade(label=n,menu=sub_menu)
                for l,c in s:
                    sub_menu.add_command(label=l,command=c)
                
        self.after(10,initialize)
    
    def destroy(self):
        
        super().destroy()
        self._choiceVar.set(True)

    def config(self,**kwargs):
        if 'menu' in kwargs:
            self.master.config(menu=kwargs['menu'])
            del kwargs['menu']
            
    def NewGame(self):
        self.start_screen=S=tk.Frame(self,relief='ridge',bd=2)
        S.v=tk.StringVar(value='Pokemon Yellow')
        versions=available_game_versions#from State
        S.version_chooser=tk.OptionMenu(S,S.v,*versions)
        S.nf=tk.LabelFrame(S,text='Name')#Make a new_game dialog for each version
        S.n=tk.StringVar(value='Name')
        S.e=tk.Entry(S.nf,textvariable=S.n)
        S.b=CustomButton(S,text='Begin Adventure',command=lambda S=S:S.destroy())
        S.version_chooser.pack(fill='x',expand=True)
        S.nf.pack(fill='x')
        S.e.pack(fill='both')
        S.b.pack()
        S.place(relwidth=.5,relx=.5,rely=.5,anchor='center')
        self.bind('b',lambda e,s=self,S=S:(S.v.set(''),S.destroy()))
        self.wait_window(S)
        if S.v.get() and S.n.get():
            self.game=GameFolder(game_source=S.v.get(),name=S.n.get(),root=self)
            self._choiceVar.set(True)
    
    def LoadGame(self,fileKey='',version=''):
        
        if not fileKey:
            from tkinter import ttk
            S=tk.Frame(self,bg=self.inner_base_bg)
            S.chosen_file_key=tk.StringVar(value=fileKey)
            S.chosen_version=tk.StringVar(value=version)
            S.T_frame=tk.Frame(S,relief='ridge',bd=2)
            T=ttk.Treeview(S.T_frame,columns=('Version','Game'))
            T.gid_map={}
            def initialize(event=None,T=T,S=S):
                gid=T.selection()[0]
##                vid=T.parent(gid)
                fileKey,version=T.gid_map[gid]
                S.chosen_file_key.set(fileKey)
                S.chosen_version.set(version)
##                version=T.item(vid,'text')
                S.destroy()
                
            for v in os.listdir(games):
                vd=os.path.join(games,v)
                if os.path.isdir(vd):
                    vid=T.insert('','end',text=v)
                    for g in os.listdir(vd):
                        game_dir=os.path.join(vd,g)
                        if os.path.isdir(game_dir):
                            name=g.split('_',1)[1]
                            gid=T.insert(vid,'end',text=name,tags=(g,))
                            T.gid_map[gid]=(g,v)
##                            T.tag_bind(gid,'<Button-1>',lambda e:setattr(T,'sel',gid)
                            T.tag_bind(g,'<Double-Button-1>',initialize)
                            T.tag_bind(g,'<Return>',initialize)
                            T.tag_bind(g,'<BackSpace>',lambda e,T=T,g=gid,d=game_dir:(T.delete(g), shutil.rmtree(d)))
                            
            S.T_frame.pack(fill='both',expand=True,padx=5,pady=5)
            T.pack(fill='both',expand=True)
            B=CustomButton(S.T_frame,text='Select game',command=initialize)
            B.pack(anchor='center')
            S.place(relx=.5,rely=.5,relwidth=.5,anchor='center')
            self.bind('b',lambda e,s=self,S=S:(S.chosen_file_key.set(''),S.destroy()))
            self.wait_window(S)
            fileKey=S.chosen_file_key.get();version=S.chosen_version.get()            
            
        if fileKey and version:
            self.game=GameFolder(root=self,file_key=fileKey,game_source=version)
            self._choiceVar.set(True)
        
    def ChooseGame(self):
        self.game_chooser=C=tk.Frame(self,bg=self.inner_base_bg)
        C.place(relx=.5,rely=.5,anchor='center')
        C.grid=G=FormattingGrid(C,relief='ridge',bd=2,rows=4,columns=2)
        F=FontObject(self)
        F.config(size=32)
        G.l=G.InsertFormat(0,0,tk.Label,text='Fauxkemon',font=F)
        self._choiceVar=tk.BooleanVar(value=False)
        def do(command,G=G):
            G.b1.disable()
            G.b2.disable()
            self.after(10,command)
        def undo(G=G):
            G.b1.enable()
            G.b2.enable()
        G.b1=G.InsertFormat(1,0,CustomButton,text='New Game',
                         relief='groove',command=lambda:(do(self.NewGame),undo()))
        G.b2=G.InsertFormat(2,0,CustomButton,text='Previous Game',relief='groove',
                         command=lambda:(do(self.LoadGame),undo()))
        G.b3=G.InsertFormat(3,1,CustomCheckButton,
            variable=self.edit_flag,
            on={'bg':self.inner_base_bg,'fg':'white','relief':'sunken'},
            off={'bg':'white','fg':'black','relief':'groove'},
            text='Edit Game',
            width=10) 
        G.b4=G.InsertFormat(3,0,CustomButton,
            text='Open Editor',
            command=GameEditor)

##        C.grid.Refresh()
        for b in (G.l,G.b1,G.b2):
            b.gridConfig(columnspan=2)
            
        G.gridConfig(sticky='nsew')
        G.b3.gridConfig(sticky='e');G.b4.gridConfig(sticky='w')
        C.grid.pack(anchor='center',padx=5,pady=5)
        self.wait_variable(self._choiceVar)
        C.destroy()
    
    def SaveGame(self):
        self.game.save_flag=True
        M=self.map
        M.file=self.game.map
        M.Save()
        T=M.character.trainer
        T.file=self.game.trainer
        T.save()
        with open(self.game.flags,'w+',encoding='utf-8') as flags:
            flags.write(str(M.flags))
    
    @property
    def map_dir(self):
        return os.path.join(getdir('maps'),self.game.ext)
    def SwitchMap(self,which,old=None,C=None,root=None,source=None,soft=False):
        
        self['bg']='black'
        if old is None:
            old=self.map
        if not soft:
            old.pack_forget()
            self.map.hold_update(15)

        if isinstance(which,Map):
            new=which
        else:
            try:
                new=old.LoadMap(which,
                                C=C,
                                root=root,
                                source=self.map_dir
                                )
            except:
                old.pack(fill='both',expand=True)
                old.focus_set()
                raise
                
        new.flags=old.flags
        new._flags=old._flags
        
        self.map=new
        self.map.file=self.game.map
#         self.map.flags=old.flags
##        self.map.Save()
        self.map.pack(fill='both',expand=True)
        self.map.focus_set()

    def StartBattle(self,team1,team2):
        #flash black screen
        self.map.pack_forget()
##        if isintance(team1,Pokem
        self.battle_protection=tk.Frame(self)
        self.battle_protection.pack(fill='both',expand=True)
        w,h=(self.winfo_width(),self.winfo_height())
        self.battle_protection.battle=BattleHolder(self.battle_protection,team1,team2,width=w,height=h)
        self.battle_protection.battle.pack(fill='both',expand=True)
        self.wait_variable(self.battle_protection.battle.done_flag)
        r=self.battle_protection.battle.done_flag.get()
        self.battle_protection.destroy()
        self.battle_protection=None
##        self.battle.pack_forget()
        self.map.pack(fill='both',expand=True)
        self.map.focus_set()
        return r

    @property
    def trainer(self):
        t=self.map.character.trainer
        if t is None:
            t=self.game.load_trainer()
            self.map.character.trainer=t
        return t