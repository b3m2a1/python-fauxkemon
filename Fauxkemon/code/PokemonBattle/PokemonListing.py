from ..DataTypes import *
from .BattleCanvas import *

class PokemonListing(tk.Frame):
        
    def __init__(self,root,team,mode='switch'):

        super().__init__(root)
        self.mode=mode
        self.team=team
        self.main=tk.Frame(self)
        self.a_button=self.master.a_button
        self.b_button=self.master.b_button
        self.main.pack(fill='both',expand=True)
        try:
            self.battle=self.master.battle
        except AttributeError:
            self.battle=tk.Frame(self.main)
        self.textwindow=self.master.textwindow
        self.choice_frames={}
        self.bind('<Command-i>',lambda e,self=self:Interactor(self))
        self.choosing=False
        
    def chooser_frame(self,P,w_scale=1,h_scale=1,
                      kwargs={'relief':'flat','bg':'gray95','bd':3},
                      **other_kw):
        '''A frame that opens the options dialog'''

        kwargs.update(other_kw)
        border_frame=FormattingElement(tk.Frame,self.chooser,**kwargs)
        if P is None:
            E=tk.Label(border_frame,text='-')
            kill_flag=False
        else:
            kill_flag=True
            E=UniformityFrame(border_frame)
            self.choice_frames[P]=E
            E.grid_columnconfigure(0,minsize=45*w_scale)
            E.grid_columnconfigure(2,minsize=55*w_scale)
            
            square=35*w_scale
            E.pokemon=P
            P.icon.reset()
            w,h=P.icon.dimensions
            m=max(w,h)
    ##        print(m)
            scale_factor=square/(m)
            P.icon.darken(.5)
            P.icon.scale(scale_factor) if scale_factor < 1 else None
            L=tk.Label(E)
            L.bind('<Expose>',lambda e,L=L,P=P:L.config(image=P.icon.Tk))
            L.square=square
            L.scale_factor=scale_factor
            text_size=int(12*w_scale)
            E.icon_lab=L;L.icon=P.icon
        
            cur=P.health;total=P.max_health
            F=FillBar(E,cur,total,width=85*w_scale,height=15*h_scale,
                      color='green4',mode='pill')
            E.fill_bar=F
            L2=tk.Label(E,text=P.name,justify='left')
            E.name_lab=L2
            L3=tk.Label(E,text='L:{}\n{}\{}'.format(P.level,cur,total),justify='left')
            E.info=L3
            L.grid(row=0,column=0,rowspan=2,sticky='w')
            L2.grid(row=0,column=1,sticky='nsew')
            F.grid(row=1,column=1,sticky='nsew')
            L3.grid(row=0,column=2,rowspan=2,sticky='w')  
            E.grid_rowconfigure(0,weight=1);E.grid_columnconfigure(1,weight=1)      
            E.P=P
            Standardizer.standardize(L,L2,L3,'battle')
            for w in (L,L2,L3):
                E.do_not_configure(w,'relief')
            def select(e=None,self=self,E=E,B=border_frame):
                if self.choice_dialog is None:
                    self.chooser.sel.frame['fg']='black'
                    lab=self.chooser.sel.frame.icon_lab
                    im=lab.icon
                    im.reset()
                    im.darken(.5)
                    im.scale(lab.scale_factor)
                    Standardizer.standardize(self.chooser.sel.frame,'battle')
                    self.chooser.sel.frame.fill_bar['bg']=Standardizer.config_map['battle']['bg']
                    lab['image']=im.Tk
                    lab['width']=lab.square
                    lab['height']=lab.square
                    
                
                    im=E.icon_lab.icon
                    im.reset()
                    im.scale(E.icon_lab.scale_factor)
                    E.icon_lab['image']=im.Tk
                    E.fill_bar['bg']=Standardizer.config_map['select']['bg']
                    Standardizer.standardize(E,'select')
                
                    self.current=self.chooser.buttons.index(B)
                    self.chooser.sel=B
                    self.focus_set()
                else:
                    self.choice_dialog.fg.focus_on()
                
            E.select=select
            border_frame.select=E.select
            border_frame.config=E.config
            if P.health>0:
                kill_flag=False
                E.bind('<Button-1>',E.select,to_all=True)
        border_frame.frame=E
        E.pack(fill='both',expand=True)
        return (border_frame,kill_flag)

    def switch_try(self):
        '''Opens up the frame to potentially switch a Pokemon into battle'''
        L=self.chooser
        P=L.sel.frame.P
        if not P is None and self.choice_dialog is None:
            
            C=self.choice_dialog=self.choose_this_dialog(P)
            i=self.team.index(P)
            l=len(self.chooser.buttons)
            C.place(x=100,rely=max(0,(i-.5)/l),relheight=1/l,anchor='ne')
            C.fg.focus_on()
            L.wait_window(C)
            self.choice_dialog=None
            self.focus_set()
            if C.flag:
                if P.health>0:
                    L.destroy()
                else:
                    self.textwindow.set_message("{} can't battle".format(P.name),wait=True)
                    self.focus_set()

    def order_switch(self,pokemon):
        '''Switches the order of two pokemon in a team'''
        team=self.team.pokemon if isinstance(self.team,Trainer) else self.team
        p=team[0]
        if not p is pokemon:
            i=team.index(pokemon)
            team[0]=pokemon
            team[i]=p           
    
    def choose_this_dialog(self,pokemon,mode=None):
        '''The little frame that provides the options

It's a frame which contains a formatting grid standardized to have the normal border

That formatting grid has 3 elements:
    Switch
    Stats
    Cancel

Cancel just closes the dialog
Stats opens up the stats window
Switch either swaps the pokemon to the top of the pokemon stack (on the map) or asks to switch it into battle.
Eventually the HM commands should be added in map mode'''
        
        mode=self.mode if mode is None else mode
        F=tk.Frame(self.main)
        F.flag=False
        cmds=[]
        [cmds.append(move) if not move is None and move.map_usable else None for move in pokemon.moves]
        F.fg=FormattingGrid(F,rows=3+len(cmds),
            active=Standardizer.config_map['select'],
            inactive=Standardizer.config_map['battle'],
            arrow_move=True,
        columns=1);
        Standardizer.standardize(F.fg,'border')
        F.current=0

        def pan(q=0,F=F,cmds=cmds):
            pass
#             new=F.current+q
#             if new>=0 and new<(3+len(cmds)):
#                 E=F.fg.get(F.current,0)
#                 F.current=new
#                 E.focus_set()

        if mode=='map':
            def switch_cmd(event=None,F=F,P=pokemon):
                self.order_switch(P)
                F.flag=True
                F.destroy()
                self.chooser.destroy()
                self.choose_pokemon(mode=mode)
        else:
            def switch_cmd(event=None,F=F):
                F.place_forget()
                F.flag=self.master.choice_message('Choose this pokemon?')
                F.destroy()
                
        L1=F.fg.AddFormat(tk.Label);Standardizer.standardize(L1,'battle')
        L1['text']='Switch'
        L1.bind(self.master.a_button,switch_cmd)
        
        F.fg.grid_config(sticky='nsew')
        
        def stat_cmd(event=None,pokemon=pokemon,pan=pan):
            p_frame=pokemon.stats_entry(self)
            p_frame.place(relwidth=1,relheight=1,anchor='nw')
            p_frame.focus_set()
            self.wait_window(p_frame)
        pan()
        L2=F.fg.AddFormat(tk.Label);Standardizer.standardize(L2,'battle')
        L2['text']='Stats'
        L2.bind(self.master.a_button,stat_cmd)
        
        def cancel_cmd(event=None,F=F):
            F.flag=False
            F.destroy()
        L3=F.fg.AddFormat(tk.Label);Standardizer.standardize(L3,'battle')
        L3['text']='Cancel'
        L3.bind(self.master.a_button,cancel_cmd)
        pan()

#         F.fg.bind('<Up>',lambda e:pan(-1))
#         F.fg.bind('<Down>',lambda e:pan(1))
#         F.fg.bind('<Button-1>',lambda e:pan(0))
        F.fg.pack(fill='both',expand=True);F.fg.Refresh()
        return F
        
    def choose_pokemon(self,mode='koed'):
        
        T=self.team
        if isinstance(T,Trainer):
            T=T.load_pokemon()
        w=self.winfo_width()
        h=self.winfo_height()
        
        self.choice_dialog=None
        
        if not hasattr(self,'_size_waiter'):
                self._size_waiter=None

        if w==1 or h==1:
            if self._size_waiter is None:
                self._size_waiter=tk.BooleanVar(self,value=False)
            self.after(50,lambda mode=mode:self.choose_pokemon(mode))
                
        else:
            if not self._size_waiter is None:
                self._size_waiter.set(True)
                
        if not self.choosing:
            if not self._size_waiter is None:
                self.choosing=True
                self.wait_variable(self._size_waiter)
                self._size_waiter=None
                w=self.winfo_width()
                h=self.winfo_height()
                self.choosing=False
                self._size_waiter=None
            rw,rh=self.master.standard_dimensions
            w_rat=w/rw
            h_rat=h/rh

            self.textwindow.set_message('Choose a Pokemon')
            self.textwindow.set_size(.1)
                        
            self.focus_set()
            self.chooser=L=FormattingGrid(self.main,rows=6,columns=1,
                width=w,height=h)
            
            self.chooser.bind('<Command-i>',lambda e:Interactor(self))
            
            self.chooser.buttons=buttons=[None]*len(T)
            i=0
            L.sel=None
            kill_flag=True
            for P in T:
                set_flag=False
                F,fl=self.chooser_frame(P,w_rat,h_rat)
                buttons[i]=F
                if kill_flag:
                    set_flag=True
                kill_flag=kill_flag and fl
                if set_flag:
                    if not kill_flag:
                        L.sel=F
                        F.select()
                i+=1
                button_num=i
            for j in range(i,party_size):
                f=self.chooser_frame(None,w_rat,h_rat)[0]
                buttons.append(f)
                
            if kill_flag:
                sel='kill'
            else:
                self.battle.blank()
                self.textwindow.bind_lock()
                self.chooser.Add(*buttons)
                self.chooser.place(relx=1,rely=0,width=-100,relwidth=1,relheight=1,anchor='ne')
                
                w=int(100*w_rat);h=int(35*h_rat)
                
                self.bind(self.master.a_button,lambda e,L=self:L.switch_try())
                if mode!='koed':
                    buttons[self.current].select()
                    self.bind(self.master.b_button,lambda e,L=L:(
                        setattr(L.sel.frame,'P',None),
                        L.destroy()
                        ))
                    
                self.current=0
                def pan(q):
                    i=self.current+q
                    if i<button_num and i>=0:
                        self.current=i
                        buttons[i].select()                          

                self.chooser.configure_rows(minsize=int(.9*self.master['height']/len(buttons)))
                self.chooser.configure_cols(minsize=w)
                self.chooser.gridConfig(sticky='nsew')
                self.bind('<Up>',lambda e,pan=pan:pan(-1))
                self.bind('<Down>',lambda e,pan=pan:pan(1))
                self.main.bind('<Button-1>',lambda e,b=buttons,s=self:b[s.current].select())
                self.chooser.commands[0,0].select()
                self.wait_window(L)
                self.textwindow.set_size(.25)
                self.battle.restore()
                self.textwindow.bind_unlock()
                sel=L.sel.frame.P
                self.chooser=None
        
            return sel

class PokemonListingFrame(tk.Frame):
    
    def __init__(self,root,team,textwindow=None,
                 a_button=a_button,b_button=b_button,
                 mode='map',**kwargs):
                 
        from .BattleHolder import BattleHolder
        self.standard_dimensions=BattleHolder.standard_dimensions
        self.text_height=BattleCanvas.text_height
        
        class FakeBattle(RichCanvas):
            bind_tag='asdasdasdasdasd'
            player_key=BattleCanvas.player_key
            enemy_key=BattleCanvas.enemy_key
            text_height=BattleCanvas.text_height
            def blank(self):
                pass
            def restore(self):
                pass
            
        self.FakeFrame=BattleHolder.FakeFrame
        super().__init__(root,**kwargs)
        self.a_button=a_button;self.b_button=b_button
        self.main=self.FakeFrame(self)
        self.battle=FakeBattle(self.main)
        self.main.grid(row=0,column=0,sticky='nsew')
        if textwindow is None:
            self.textframe=tk.Frame(self);
            self.textframe.grid(row=1,column=0,sticky='sew')
            self.grid_rowconfigure(0,weight=1)
            self.grid_columnconfigure(0,weight=1)        
            textwindow=TextWindow(self.textframe,self.battle)
        else:
            self.textframe=textwindow.master
        self.textwindow=textwindow
        Standardizer.standardize(textwindow)
        self.textwindow.grid(row=0,column=0,sticky='nsew')
        
        self.chooser=PokemonListing(self.main,team,mode='map')
        self.chooser.pack(fill='both',expand=True)

    def choose_pokemon(self,mode='map'):
        return self.chooser.choose_pokemon(mode=mode)