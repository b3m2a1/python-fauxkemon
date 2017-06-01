#! usr/local/bin/python3.4

from . import *
    
class BattleHolder(tk.Frame):
    
    standard_dimensions=standard_dimensions
    animation_source=animation_source
    player_key=player_key
    enemy_key=enemy_key
    text_height=text_height
    
    class FakeFrame(tk.Frame):
        def __init__(self,root):
            super().__init__(root)
        def __getattr__(self,attr):
            return getattr(self.master,attr)
        
    def __init__(self,root,team1,team2,inventory1=None,inventory2=None,
                 next_mode='switch',currently_visible=False,
                 a_button='a',b_button='b',**kwargs):
        super().__init__(root,**kwargs)


        mode='wild'
        tr_1=isinstance(team1,Trainer)
        if tr_1:
            if len(team1.load_pokemon())==0:
                team1.add_pokemon(('Pikachu',5))
            if inventory1 is None:
                inventory1=team1.inventory
        elif len(team1)==0:
            team1=[Pokemon('Pikachu',level=5)]
        for p in team1:
            if not p.KOed:
                break
        tr_2=isinstance(team2,Trainer)
        if tr_2:
            if len(team2.load_pokemon())==0:
                team2.add_pokemon(('Magikarp',5))
            if inventory2 is None:
                inventory2=team2.inventory
        elif len(team2)==0:
            team2=[Pokemon('Magikarp',level=5)]
        for e in team2:
            if not e.KOed:
                break
        if tr_1 and tr_2:
            mode='trainer'
        self.mode=mode
        self.team_names=['Trainer' if tr_1 else 'Pokemon',
                         team2.name if tr_2 else 'Wild {}'.format(team2[0].name)]
        
       
        self.pokemon=[p,e]
        self.teams=[team1,team2]
        
        self.battle_started=False
        
        self.next_mode=next_mode
        self.done_flag=tk.StringVar(value='waiting')
        self.chooser=None
        self.vis=currently_visible

        self.a_button=a_button
        self.b_button=b_button
        
        self.battle=B=BattleCanvas(self,*self.pokemon,
                                   inventory1=inventory1,
                                   inventory2=inventory2,
                                   a_button=a_button,
                                   b_button=b_button,
                                   mode=mode,
                                   text_root=self,
                                   **kwargs)
        self.textwindow=self.battle.textwindow
        self['width']=standard_dimensions[0]
        self['height']=standard_dimensions[1]
        self.battle.place(x=0,y=0,anchor='nw',relwidth=1,relheight=.75)
        self.textwindow.place(x=0,rely=1,anchor='sw',relheight=.25,relwidth=1)

    def destroy(self):
        self.done_flag.set('destroyed')
        super().destroy()

    def choice_message(self,*args,**kwargs):
        return self.battle.choice_message(*args,**kwargs)
        
    def choose_pokemon(self,team_ind,mode='koed'):
        T=self.teams[team_ind]
        if team_ind==0:
            self.chooser=L=PokemonListing(self,T)
            L.place(x=0,y=0,relheight=.9,relwidth=1)
            L.sel=sel=L.choose_pokemon(mode=mode)
            L.destroy()
            self.chooser=None
        else:
            for P in T:
                if not P.KOed:
                    sel=P
                    break
            else:
                sel='kill'
        return sel
        
    def switch_pokemon(self,index=0):
        P=self.choose_pokemon(index,'switch')
#         self.textwindow.set_display('options')
        if P is None:
            self.textwindow.set_display('options')
        else:
            self.pokemon[index]=P           
            if index==0:
                self.battle.change_pokemon(player=self.pokemon[0])
            else:
                self.battle.change_pokemon(enemy=self.pokemon[1])
        return index
        
    def next_pokemon(self):
        
        h=self['height'];w=self['width']
        P=None
        self.battle.chosen_actions.clear()
        switches=[]
        continues=[True,True]
        done=False
        
        tests=[{x if not x.KOed else None for x in t} for t in self.teams] 
        for t in tests:
            if None in t:
                t.remove(None)
        if not any(tests[0]):
            i=0
            done=True
        elif not any(tests[1]):
            i=1
            done=True
        else:
            for i in range(2):
                if self.pokemon[i].KOed:
                    P=self.choose_pokemon(i)
                    if P=='kill':
                        continues[i]=False
                    self.pokemon[i]=P
                    switches.append(i)
                
        
                if all(continues):
                    if switches==[1]:
                        if self.next_mode=='switch':
                            if len(tests[0])>1:
                                choose_new=tk.BooleanVar()
                                self.battle.choice_message('Switch pokemon?',
                                                           variable=choose_new)                    
                                if choose_new.get():
                                    P=self.choose_pokemon(0,mode='switch')
                                    if not P is None:
                                        self.pokemon[0]=P
                                        switches.append(0)        
                    flump=[None,None]
                    for i in switches:
                        flump[i]=self.pokemon[i]
                    self.battle.place(x=0,y=0,relheight=.75,relwidth=1,anchor='nw')
                    self.battle.change_pokemon(*flump)
                else:
                    for i in range(2):
                        if not continues[i]:
                            done=True
                            self.battle.textwindow.bind(self.a_button,self.end_battle)
                            self.battle.textwindow.focus_set()
                            break
                    self.battle.place(x=0,y=0,relheight=.75,relwidth=1,anchor='nw')
        if done:
            self.battle.set_message('{} was defeated'.format(self.team_names[i]),wait=True)
            self.end_battle()
            
    def end_battle(self,event=None,won=False):
        self.battle.end_fade()
        if won:
            self.done_flag.set('won')
        else:
            self.done_flag.set('lost')
        
    def catch_pokemon(self,caught_pokemon):

        t=self.teams[0]
        if isinstance(t,Trainer):
            ret=t.add_pokemon(caught_pokemon)
            #pokedex_stuff
        self.destroy()        