from .config import *
# sys.path.insert(0,os.path.dirname(__file__))
from .InventoryWindow import *

class TextWindow(tk.Frame):
    item_names=('FIGHT','ITEM','POKEMON','RUN')
    def __init__(self,root,battle,
                         a_button='a',
                         b_button='b',
                         font=None):
        super().__init__(root)
        Standardizer.standardize(self,'border')
        
        self.root=root
        root.grid_columnconfigure(0,weight=1)
        self.key_wait=50
        self.battle=battle
        self.bindtags((self.battle.bind_tag,)+self.bindtags())
        self.pack_propagate(False)
        self.attacks=None
        self.bat_ops=None
        self.selected=None
        self.resp_flag=False
        
        if font is None:
            if hasattr(root,'font'):
                font=root.font
            else:
                font=PokeFont()
        self.font=font
        
        self.player_key=battle.player_key
        self.enemy_key=battle.enemy_key
        self.inventory=None
        self.message_pane=RichText(self,bd=5)
        Standardizer.standardize(self.message_pane,'battle')
        self.message_pane.font=self.message_pane['font']
        self.message_pane.bind('<FocusIn>',lambda e:self.focus_set())
        
        self._messaging=False
        self.message_pane.bind('<Button-1>',lambda e:'break')
        self.message_pane.bind('<B1-Motion>',lambda e:'break')
        self._resizing=True
        self.master.bind('<Configure>',self.resize,'+')
        self._clicks=0
        self._display=tk.StringVar(value='options')
        self.last_att=None        
        #do bindings
        self.arrow_bindings=tuple(
            (Binding('<{}>'.format(x),self.arrow_response) for x in ('Up','Right','Left','Down'))
                     )
        self.a_button=a_button
        self.a_binding=Binding(a_button,self.a_response)
        self.a_lock=BindingLock(a_button)
        self.b_button=b_button
        self.b_binding=Binding(b_button,self.b_response)
        self.b_lock=BindingLock(b_button)
        self.bind_keys()
        self.grid_sel_ind=(0,0)
        self.set_size(.25)
        
        self.blank_frame=tk.Frame(self)
        Standardizer.standardize(self.blank_frame)
        self.battle_options()
        self.display_grid=self.bat_ops
        self.bat_ops.pack(fill='both',expand=True)
    
    @property
    def pokemon(self):
        return self.battle.pokemon[self.player_key]
    @property
    def pokemon_map(self):
        return self.battle.pokemon

    def set_size(self,pixels=None,percent=None):
        if pixels is None:
            pixels,percent=self._size
        else:
            if not isinstance(pixels,int):
                percent=pixels
                pixels=0
            if percent is None:
                percent=0
            elif percent>1:
                percent=percent/100                
            self._size=(pixels,percent)
        self.place(relheight=percent,height=pixels)
        
    def resize(self,event=None):
        #ALSO DO FONT RESIZING
        if not self._resizing:
            self._resizing=True
            self.set_size()
            self.after(50,lambda self=self:setattr(self,'_resizing',False))
#         fontsize=self.message_pane.font.ascent()
        
    def set_display(self,disp):
        old=self._display.get()
        try:
            self._display.set(disp)
            self.configure_display()
        except:
            self._display.set(old)
            self.configure_display()
            raise
        self.update_idletasks()
        
    def configure_display(self,*args):
        def show(widget):
            for x in (self.inventory,
                      self.message_pane,
                      self.bat_ops,
                      self.attacks,
                      self.blank_frame):
                if not x is None:
                    if x is widget:
                        x.pack(fill='both',expand=True)
                    else:
                        x.pack_forget()
                        
#             if not widget.winfo_viewable():
#                 widget.wait_visibility(widget)
                        
        w=self._display.get()
        
        if w=='null':
            show(self.blank_frame)
        elif w=='text':
            show(self.message_pane)
            self.display_grid=None
        elif w=='options':
            if self._size[1]==.5:
                self.set_size(.25)
            self.resp_flag=True
            self.battle_options()
            show(self.bat_ops)
            self.display_grid=self.bat_ops
        elif w=='attacks':
            self.resp_flag=True
            self.get_attacks()
            show(self.attacks)
            self.display_grid=self.attacks
        elif w=='inventory':
            self.set_size(.5)
            self.resp_flag=True
            self.get_inventory()
            show(self.inventory)
            self.display_grid=self.inventory.list_box
            
        
    def bind_keys(self,widget=None,mode='rebind',flag='rebound'):
        if mode=='rebind':
            self.a_binding.apply(self)
            self.b_binding.apply(self)
            for b in self.arrow_bindings:
                b.apply(self)
        else:
            self.resp_flag=False
            self.a_binding.remove(self)
            self.b_binding.remove(self)
            for b in self.arrow_bindings:
                b.remove(self)

    def bind_lock(self):
        self.resp_flag=False
        self.a_lock.lock(self)
        
    def bind_unlock(self):
        self.resp_flag=True
        self.a_lock.unlock(self)
        
    def arrow_response(self,event=None):
        G=self.display_grid
        if not G is None:
            e=event.keysym
            km={'Up':(-1,0),
                'Down':(1,0),
                'Left':(0,-1),
                'Right':(0,1)}
            x,y=self.grid_sel_ind
            px,py=km[e]
            x=max(min(1,x+px),0)
            y=max(min(1,y+py),0)
            o=self.display_grid.get(x,y)
            if hasattr(o,'select'):
                self.grid_sel_ind=(x,y)
                o.select()
        
    def a_response(self,event=None):
        self.a_lock.lock(self)
        self.resp_flag=True
        def b_test(self=self):
            if self.resp_flag:
                self.a_lock.unlock(self)
        self.after(self.key_wait,b_test)
        K=self._display.get()
        if K=='text':
            self._clicks+=-1
            if self._clicks>0:
                self._current+=1
                self.message_pane.see('{}.end'.format(self._current))
            else:
                self.set_display('options')
        elif K=='attacks':
            self.set_display('null')
            self.battle.hold_update(100)
            attack=self.selected.attack
            self.battle.choose_action(self.player_key,attack)
            self.battle.finish_turn()
        elif K=='inventory':
            i=self.inventory.current_item
            if i is None:
                self.set_display('options')
            else:
                r,u=self.battle.player_use_item()
                self.set_display('null')          
                if not r:
                    self.set_message(get_message('cant_use_that'),wait=True)
                    self.set_display('inventory')
                else:
                    self.inventory.adjust(u)
                    self.battle.choose_action(self.player_key,'pass')
                    self.battle.finish_turn()               
                
                
        elif K=='options':
            button=self.selected
            text=button['text']
            if text==self.item_names[0]:
                self.get_attacks()
                self.set_display('attacks')
            elif text==self.item_names[3]:
                r=random.random()
                R=(self.pokemon.stats['speed']/self.battle.enemy.pokemon.stats['speed'])
                if r<R:
                    self.set_message('Got away safely!',wait=350)
                    self.battle.holder.end_battle(True)
            elif text==self.item_names[2]:
##                self.set_message('Choose a pokemon')
                r=self.battle.holder.switch_pokemon(0)
                self.battle.focus_set()
                if r:
                    self.battle.choose_action(self.player_key,'pass')
                    self.battle.finish_turn()
                self.bind_unlock()
                self.bind_keys()
            elif text==self.item_names[1]:
                self.set_display('inventory')

    def b_response(self,event=None):
        w=self._display.get()
        if w=='text':
            self.a_response()
        elif w=='attacks':
            self.set_display('options')
        elif w=='inventory':
            self.set_display('options')
        
    def select_button(self,button):
        if hasattr(button,'select'):
            if not self.selected is None:
                Standardizer.standardize(self.selected,'battle')
            self.selected=button
            Standardizer.standardize(self.selected,'select')

    def select_attack(self,button):
        self.select_button(button)
        self.last_att=self.attack_list.index(button)

    def __getattr__(self,attr):
        return getattr(self.message_pane,attr)

    def set_message(self,text,YN=(),cmd=(),wait=250):
        if self._messaging:
            self.focus_set()
            self.event_generate(self.master.a_button)
        self._messaging=True
        self._clicks=len(text.splitlines())
        self._current=0
        self.message_pane.Clear()
        self.message_pane.Insert(text)
        self.set_display('text')
        self.update()
        if wait is True:
            key_wait(self,self.master.a_button)
        elif wait:
            self.battle.hold_update(wait)
        self._messaging=False
            

    def battle_options(self):
        if self.bat_ops is None:
            self.bat_ops=FormattingGrid(self,rows=2,columns=2)
            self.bat_ops.gridConfig(sticky='nsew')
            self.bat_buts=[FormattingElement(tk.Label,self.bat_ops,
                                             text=x) for x in self.item_names]
            for x in self.bat_buts:
##                ft=self.message_pane['font']
                x.select=lambda e=None,x=x:(
                    self.select_button(x),
                    self.focus_set()
                    )
                x.bind('<Button-1>',x.select)
                
            self.bat_ops.Add(*self.bat_buts)
            Standardizer.standardize_recursive(self.bat_ops,'battle')
            w,h=self.battle.window_dimensions
            h=self.battle.text_height
        
        self.selected=self.bat_buts[0]
        for x in self.bat_buts:
            x.select()
        self.bat_buts[0].select()

    def AttackButton(self,attack):
        if not attack is None:
            L=FormattingElement(tk.Label,
                                self.attacks,
                                text='{0.name}\n{0.pp}\{0.max_pp}'.format(attack)
                                )
            L.attack=attack
            def select(event=None,self=self,L=L):
                self.select_attack(L)
                self.focus_set()
            L.select=select
            L.bind('<Button-1>',select)
        else:
            L=FormattingElement(tk.Label,
                                self.attacks,
                                text='-') 
        return L
    def get_attacks(self,reload_flag=False):
        if reload_flag:
            if not self.attacks is None:
                self.attacks.destroy()
                self.attacks=None
        if self.attacks is None:
            self.last_att=None
            self.attacks=FormattingGrid(self,rows=2,columns=2)
            self.attack_list=[self.AttackButton(attack) for attack in self.pokemon.moves]
            self.attacks.Add(*self.attack_list)
            self.attacks.commands.collapse()
            self.attacks.gridConfig(sticky='nsew')
            self.attacks.Refresh()
            Standardizer.standardize_recursive(self.attacks,'battle')
        if self.last_att is None:
            self.attack_list[0].select()
        else:
            self.attack_list[self.last_att].select()
        for x in self.attacks.commands.items():
            try:
                a=x.attack
            except:
                continue
            x.config(text='{0}\n{1!s}\{2!s}'.format(a.name,a.pp,a.max_pp))
        
    def get_inventory(self):
        if self.inventory is None:
            self.inventory=InventoryWindow(self,self.battle.inventories[self.player_key])
            self.a_binding.apply(self.inventory)
            self.b_binding.apply(self.inventory)
