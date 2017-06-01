import tkinter as tk

class BattleTest(tk.Toplevel):
    def __init__(self,master=None):        
        super().__init__(master)
        self.title('Pokemon Battle')
        self.resizable(False,False)
        self.large_string='375x516'
        self.small_string='375x375'
        self.geometry(self.small_string)
        self.r=tk.Frame(self,bd=5,bg='yellow',relief='ridge')
        self.r.pack(fill='both',expand=True,padx=3,pady=3)
        self.string=self.small_string
        self.b=None
        self.s=None
        self.v_flag=False
        self.load_battle()
        self.f=F=tk.Frame(self.r,height=150,width=350,bd=2,relief='sunken')
        self.bind('<Command-m>',self.toggle_shell)
        self.toggled=False
        self.tk=tk

    def draw_circles(self):
        for x,b in self.w.buttons.items():
            for k,i in b.button_hooks.items():
                
                x,y=self.w.coords(i)
                self.w.create_oval(x,y,x+10,y+10)
            
    def load_battle(self,event=None,k1=None,k2=None):
        import ..DataTypes as dev1
        import ..PokemonBattle as dev2
        import tkinter as tk
        from random import choice

        pokes=range(1,152)
        levs=range(5,20)
        nums=range(3,7)
        team1=[dev1.Pokemon(choice(pokes),level=choice(levs)) for i in range(choice(nums)-1)]
        team2=[dev1.Pokemon(choice(pokes),level=choice(levs)) for i in range(choice(nums))]
        team1.append(dev1.Pokemon('Magikarp',level=99))
        if not self.b is None:
            self.b.grid_forget()
        self.p1=team1
        self.p2=team2

        inventory={x:choice(range(100)) for x in ('PokeBall',
                                                  'Potion',
                                                  'Antidote',
                                                  'Paralyze Heal',
                                                  'Full Restore')}
        self.b=dev2.BattleHolder(self.r,self.p1,self.p2,inventory1=inventory,
                                 currently_visible=self.v_flag,width=350)
        self.b.battle.bind('<Double-Button-1>',self.toggle_shell)
        self.b.grid(row=0,sticky='nsew')
        if not self.s is None:
            self.s.holder=self.b
            self.s.battle=self.b.battle
        self.b.done_flag.trace('w',self.load_battle)

    def init(self,event=None):
        self.r.wait_visibility(self.r)
        self.geometry(self.string)
        
    def toggle_shell(self,event=None):
        if not self.toggled:
            self.string=self.large_string

            self.geometry(self.large_string)
            self.f.grid(row=1,ipadx=3,ipady=3)
            self.toggled=True
            
        else:
            self.string=self.small_string

            self.geometry(self.small_string)
            self.toggled=False
            self.f.grid_forget()
    
    def run(self):
        from newshell import shell
        
        F=self.f
        F.pack_propagate(False)
        self.r.grid_rowconfigure(0,weight=1,minsize=150)
        self.v_flag=True
        self.r.after(100,self.init)
        self.s=shell({'main':self,
                      'holder':self.b,
                      'battle':self.b.battle,
                      'r':self.r,
                      'b_p':self.draw_circles,
                      'M':self.b.battle.main,
                      'E':self.b.battle.enemy,
                      'T':self.b.battle.textwindow
                      },F)
