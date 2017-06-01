from ..DataTypes import *
from .config import *
from .EnemyAI import *
from .TextWindow import *
from .PokeImage import * 
from ..Map import Map

import random
        
class BattleCanvas(AnimationFrame):
    '''The canvas that organizes the battle
    
It opens a TextWindow in its holder (parent) to choose actions
It opens an EnemyAI for each enemy pokemon that chooses moves for that pokemon

Chosen actions are stored in a chosen_actions list that's run through each turn
The possible actions:
    - A null event is specified by 'pass'
    - An attack choice is a (key,attack) tuple where the key is either the 'player' key or the 'enemy' key

After each turn this list is restored to being empty

Attacks are actually used by use_attack, which calls apply_effects to determine what the attack does
Items are used by use_item, which again calls apply_effects

All menu effects are handled by the TextWindow and its children

At some point the actual battle actions will be split into their own class and a battle canvas will simply hold a battle class and provide a display for it.
'''
    standard_dimensions=standard_dimensions
    animation_source=animation_source
    player_key=player_key
    enemy_key=enemy_key
    text_height=text_height
    
    def __init__(self,root,pokemon1,pokemon2,
                 inventory1=None,inventory2=None,
                 text_root=None,
                 mode='wild',
                 a_button='a',
                 b_button='b',
                 font=None,
                 **kwargs):
        
        if font is None:
            if hasattr(root,'font'):
                font=root.font
            else:
                font=PokeFont()
        self.font=font
        if text_root is None:
            text_root=root
        self.holder=root
        super().__init__(root,**kwargs)
        
        self.turn=0
        self.bind_tag=''.join(
            (random.choice(string.ascii_letters) for x in range(6))
            )
        
        
        pokemon1.enter_battle(self,self.player_key)
        pokemon2.enter_battle(self,self.enemy_key)
        pokemon2=EnemyAI(pokemon2)
        if inventory1 is None:
            inventory1={'PokeBall':10}
        if inventory2 is None:
            inventory2={}
        self.inventories={self.player_key:inventory1,self.enemy_key:inventory2}
        self.enemy=self.Pokemon(pokemon2,self.enemy_key)
        self.animations=True
        self._size_check=tk.BooleanVar(value=True)
        self.player=self.Pokemon(pokemon1,self.player_key)
        self.pokemon={self.player_key:pokemon1,self.enemy_key:pokemon2}
        self.a_button=a_button
        self.b_button=b_button
        self.textwindow=TextWindow(text_root,self,a_button=self.a_button,b_button=self.b_button)
#         self.holder.textwindow=self.textwindow


        self.bind('<Configure>',
                  lambda e:(self._size_check.set(True),self.draw_pokemon())
                  )
        reroute=lambda e,self=self:(self._size_check.set(True),
                                    self.textwindow.focus_set())
        self.textwindow.bind('<Command-i>',lambda e,s=self:Interactor(s))
        self.bind('<Button-1>',reroute)
        self.bind('<FocusIn>',reroute)
        self.bind('<Expose>',lambda e:self.pack_pieces())
        self.chosen_actions=[]
    
    @property
    def player_pokemon(self):
        return self.pokemon[self.player_key]
    @property
    def enemy_pokemon(self):
        return self.pokemon[self.enemy_key].pokemon
    @property
    def pokemon_id(self):
        return self.player.canvas_obs[0]
    @property
    def pokemon_info_id(self):
        return self.player.canvas_obs[1]
    @property
    def enemy_id(self):
        return self.enemy.canvas_obs[0]
    @property
    def enemy_info_id(self):
        return self.enemy.canvas_obs[1]
    
        
    def apply_animation(self,AN_str,*AN_args,**AN_kwargs):
        '''Loads an animation by name and calls it'''
        Animation(self).call_animation(AN_str,*AN_args,**AN_kwargs)
    
    def change_pokemon(self,player=None,enemy=None):
        '''Swaps out pokemon

Swaps the player's pokemon if player is specified or the enemy pokemon if enemy is'''
##        self.delete('all')
        messages=[]
        obj=None
        m_can=self.player;e_can=self.enemy
        if player is None:
            player=self.pokemon[self.player_key]
        m=self.pokemon[self.player_key]
        objs=[]
        if not player==m:
##            for x in self.player.canvas_obs:
##                self.delete(x)
            player.enter_battle(self,self.player_key)
            self.pokemon[self.player_key].exit_battle()
            self.player=self.Pokemon(player,self.player_key)
            self.pokemon[self.player_key]=player
            messages.append('Sent out {}'.format(player.name))
            messages.append('Go {}!'.format(player.name))
            objs.append(self.player_key)
        if enemy is None:
            enemy=self.pokemon[self.enemy_key]
        e=self.pokemon[self.enemy_key]
        if not enemy==e:
##            for x in self.enemy.canvas_obs:
##                self.delete(x)
            
            enemy.enter_battle(self,self.enemy_key)
            enemy=EnemyAI(enemy)
            self.pokemon[self.enemy_key].exit_battle()
            self.enemy=self.Pokemon(enemy,self.enemy_key)
            self.pokemon[self.enemy_key]=enemy
            messages.append('Sent out {}!'.format(enemy.name))
            objs.append(self.enemy_key)
##        self.pack_pieces()
        changed=(not objs==[])
        if changed:
            if self.player_key in objs:
                for x in m_can.canvas_obs:
                    self.delete(x)
            if self.enemy_key in objs:
                for x in e_can.canvas_obs:
                    self.delete(x)
            self.textwindow.get_attacks(True)
            for x in messages[:-1]:
                self.set_message(x)
            self.set_message(messages[-1],wait=True)
            if self.enemy_key in objs:
                self.draw_pokemon(1)
                o=self.enemy.canvas_obs[0]
            if self.player_key in objs:
                self.draw_pokemon(0)
                o=self.player.canvas_obs[0]
            self.fade_ob(o,.9)
            self.tint_ob(o,r=250,a=10)
##            self.textwindow.bind_keys(mode='unbind',flag='ignore')
##            self.textwindow.focus_set()
##            key_wait(self.textwindow,'a')
            self.textwindow.bind_keys()
            self.fade_in(o,steps=5,img_mode='fade_restore')
        return changed                        
    
    def Pokemon(self,pokemon,mode,**kwargs):   
        '''Generates a PokeImage, binds it to p_hook and returns it'''     
        self.p_hook=PokeImage(self,pokemon,mode,**kwargs)
        return self.p_hook

    def draw_pokemon(self,key='both'):
        '''Draws either one or both pokemon, by index'''
        if key=='both':
            keys=(1,0)
        else:
            keys=(key,)
        w,h=self.window_dimensions
        if w>100 and h>100:
            hb=0#was the height of the textwindow, originally
            scale_factor=(w-100)/150
            if 0 in keys:
                if not self.player.canvas_obs is None:
                    for o in self.player.canvas_obs:
                        self.delete(o)
                self.player.image.reset()
                self.player.image.image=self.player.original
                self.player.image.apply_cutoff(amin=3)
                self.player.image.scale(1.5*scale_factor);
                self.player.image.set_base_image()
                self.player.draw(0,h-hb,w,h-hb,padx=5,pady=-5,state='hidden')
                self.apply_animation('PuffAnimation.py',self.player.canvas_obs[0])
                self.itemconfig(self.player.canvas_obs[0],state='normal')
                
            if 1 in keys:
                if not self.enemy.canvas_obs is None:
                    for o in self.enemy.canvas_obs:
                        self.delete(o)
                self.enemy.image.reset()
                self.enemy.image.image=self.enemy.original            
                self.enemy.image.scale(scale_factor);self.enemy.image.set_base_image()
                self.enemy.draw(w,0,0,0,padx=-5,pady=5,state='hidden')
                self.apply_animation('PuffAnimation.py',self.enemy.canvas_obs[0])
                self.itemconfig(self.enemy.canvas_obs[0],state='normal')
                
        else:
            def wait_call(self=self):
                self._size_check.set(False)
                self.wait_variable(self._size_check)
                self.after(250,self.draw_pokemon)
            self.after(10,wait_call)  
                     
    def blank(self):
        '''Hides the pokemon canvas objects'''
        for o in (self.player.canvas_obs,self.enemy.canvas_obs):
            for f in o:
                self.itemconfig(f,state='hidden')
    def restore(self):
        '''Unhides the hidden objects'''
        for o in (self.player.canvas_obs,self.enemy.canvas_obs):
            for f in o:
                self.itemconfig(f,state='normal')
    def pack_pieces(self):
        '''Waits until visible then packs all the canvas pieces'''
        if not self.master.winfo_viewable():
            self.wait_visibility(self.master)
            self.master.vis=True
        h=self.master.winfo_height()
        w=self.master.winfo_width()
        hb=self.text_height
        self.draw_pokemon()
#         self.textwindow.grid(row=0,column=0,sticky='nsew');
#         self.textwindow.set_size(hb-4)
        self.textwindow.focus_set()
        self.unbind('<Expose>')
    
    def choose_action(self,key,action):
        for i,k in enumerate(self.chosen_actions):
            if k==key:
                self.chosen_actions[i]=(key,action)
                break
        else:
            self.chosen_actions.append((key,action))
            
    def finish_turn(self):
        '''Finishes up the turn, after the player chooses their action

Randomly chooses which pokemon should go first based on a Gaussian distribution on the enemy's speed
'''
        cur=self.pokemon[self.enemy_key]
        player=self.pokemon[self.player_key]
        attk=cur.choose_attack(player)
        spd=cur.stats['speed']
        chat=self.chosen_actions[0][1]
        if chat=='pass':
            self.chosen_actions.insert(0,(self.enemy_key,attk))
        elif random.gauss(spd,spd*.1)*chat.priority>attk.priority*player.stats['speed']:
            self.chosen_actions.insert(0,(self.enemy_key,attk))
        else:
            self.chosen_actions.append((self.enemy_key,attk))
        self.next_turn()
    
    def mode_info(self,user,target):
        '''Returns the key for the user and the image for the target'''
        if user is self.player_pokemon or target is self.enemy_pokemon or target is self.pokemon[self.enemy_key]:
            mode_info=(self.player_key,self.enemy)
        else:
            mode_info=(self.enemy_key,self.player)
        return mode_info
        
    def user_target(self,user_key):
        '''Returns the user and target for the user key'''
        user=self.player_pokemon if user_key==self.player_key else self.enemy_pokemon
        target=self.enemy_pokemon if user_key==self.player_key else self.player_pokemon
        return (user,target)
        
    def next_turn(self):
        '''Runs through the actions chosen and applies the effects
    
Increments the turn counter by .5 until it's an integer'''
        
        if len(self.chosen_actions)>0:
            self.textwindow.bind_lock()
            self.turn+=.5
            iden,attk=self.chosen_actions.pop(0)
            user,target=self.user_target(iden)
            R=self.use_attack(user,target,attk)
            if not R=='done':
                if int(self.turn)==self.turn:
                    self.textwindow.battle_options()
                    self.textwindow.bind_unlock()
                else:
                    self.next_turn()
            self.chosen_actions=[]
        else:
            self.turn=int(self.turn)
            self.textwindow.set_display('options')
            self.textwindow.bind_unlock()
        
    def choice_message(self,message='Yes or No?',choices=(('Yes'+' '*3,True),
                                                          ('No'+' '*4,False)),
                       variable=None):
        '''Pops up a choice dialog

By default the choices are 'Yes'->True and 'No'->False
The message is 'Yes or No?' by default
'''
        choice=tk.StringVar(self)
        choice_dict={str(k):v for k,v in choices}
        choice_frame=FormattingGrid(self.master,rows=len(choices),columns=1,arrow_move=True,
            inactive=Standardizer.config_map['battle'],
            active=Standardizer.config_map['select'])
        Standardizer.standardize(choice_frame,'border')
        for k,v in choices:
            choice_frame.AddFormat(tk.Label,choice_frame,         text=k,justify='left').grid_config(sticky='nsew')
        Standardizer.standardize(choice_frame.get(0,0),choice_frame.get(1,0),'battle')
        choice_frame.grid_config(sticky='nsew')
        choice_frame.bind(self.a_button,lambda e,c=choice_frame:c.destroy())
        choice_frame.bind('<FocusIn>',lambda e,c=choice:c.set(
            e.widget['text'] if 'text' in e.widget.config() else ''
            ),'+')
        p,h=self.textwindow._size
        self.set_message(message)
        choice_frame.place(x=0,rely=1-h,anchor='sw')
        choice_frame.get(0,0).focus_set()
        self.wait_window(choice_frame)
        val=choice_dict[choice.get()]
        if not variable is None:
            variable.set(val)
        return val
        
    
    def process_message_text(self,text,**kw):
        '''Eventually this will be as well made as the Map process_message, but for now it's pretty rudimentary'''
        text,YN,cmd,wait=Map.process_message_text(text)
        text.format(battle=self,
            player=self.pokemon[self.player_key],
            enemy=self.pokemon[self.enemy_key]
                )
        return (text,YN,cmd,wait)
        
    def set_message(self,*args,**kwargs):
        self.textwindow.set_message(*args,**kwargs)
    create_message=set_message
    
    def CreateMessage(self,text):
        '''Mimic the map messaging system, somewhat'''
        self.create_message(*self.process_message_text(text))
    
    def use_attack(self,user,target,attack):
        '''Has user use the attack on target'''
                    
        if not attack=='pass':
            for attack_tuple,effect_tuple in user.use_attack(attack,target,override=True):
                if attack_tuple=='status':
                    r=self.apply_effects(target,user,None,effect_tuple,attack=attack)
                else:
                    r=self.apply_effects(user,target,attack_tuple,effect_tuple,attack=attack)
                if r=='done':
                    break
    
    def player_use_item(self,item):
        return self.use_item(self.player_pokemon,self.enemy_pokemon,item)
        
    def use_item(self,user,target,item):
        '''Has user use the item on target'''
        R=(True,0)
        try:
            I=item if isinstance(item,ItemClass) else Item(item_name)
        except FileNotFoundError as e:
            R=(False,0)
        else:
            try:
                R=(I.use(user,target,context='battle'),I.uses)
            except:
                I.edit(self)
                tb.print_exc()
                R=(False,0)
                
        if R[0] not in (True,False):
            self.textwindow.set_size(.25)
            self.textwindow.set_message(get_message('used_item').format('Trainer',I.name),wait=500)
            user.skip_turn()
            self.apply_effects(user,target,None,R[0],item=I)
            R=(True,R[1])
            
        return R
        
    def apply_damage(self,user,target,damage_tuple):
        '''Applies the damage of an attack by user on target according to the attack damage'''
        key,img=self.mode_info(user,target)
        if not damage_tuple is None:
            dmg,messages,animation=damage_tuple
            #set damage messages
            if not messages is None:
                for x in messages:
                    self.set_message(x,wait=battle_message_wait)
            if not isinstance(dmg,str) and dmg>0:
                #enemy was damaged
                missed=False
                target.take_damage(dmg)
                #need richer damage animation considerations
                if animation=='shake_vertical':
                    if key==self.enemy_key:
                        self.shake(20,self.vertical,step_q=4) 
                    else:
                        self.shake_obs(*self.enemy.canvas_obs, quantity=20,shake_vector=self.vertical,step_q=4)                                           
                else:
                    self.apply_animation(animation,img,user)
                self.flash_obs(img.canvas_obs[0],times=3,fade=1,pause=50)
                self.hold_update(25)
                img.update()
            elif dmg<0:
                missed=False
                target.take_damage(dmg)
                img.update()
    
    def apply_effect(self,user,target,effect_tuple):
        '''Applies the effect of an attack by user on target according to the attack effect'''
        key,img=self.mode_info(user,target)
        if not effect_tuple is None:
            damage,messages,animations=effect_tuple
            for anim in animations:
                if anim=='slow_shake_horizontal':
                    if key==self.enemy_key:
                        self.shake(20,step_q=10)
                    else:
                        self.shake_obs(*self.enemy.canvas_obs,quantity=20,step_q=10)
                elif anim=='transform':
                    self.apply_animation('transform_pokemon',user,img)
                else:
                    self.apply_animation(anim,user,img)
            for m in messages:
                if not m is None:
                    self.set_message(m,wait=battle_message_wait)
            if not isinstance(damage,str) and damage>0:
                target.take_damage(damage)
                self.flash_obs(img.canvas_obs[0],times=3,fade=1,pause=50)
                self.hold_update(25)
                img.update()
    
    def apply_statuses(self,user,mode='before'):
        '''Check the statuses currently on the pokemon. Try each, if not None'''
        status=user.status
        if not status=='OK':
            for k in status:
                if not k is None:
                    effect_tuple=k.apply(user)
                self.apply_effect(user,user,effect_tuple)
                
    def apply_effects(self,user,target,damage_tuple,effect_tuple,
                      attack=None,item=None):
        '''Takes the user and target and actually applies the effects of the attack or item used

First it applies the damage done and the associated messages and animations'''
        
        self.apply_damage(user,target,damage_tuple)
        self.apply_effect(user,target,effect_tuple)
        
        if not effect_tuple is None:
            str_effect=effect_tuple[0]
            if isinstance(str_effect,str):
                if str_effect=='caught':
                    self.holder.catch_pokemon(target)
                    return 'done'
                else:
                    pass

        if target.KOed:
            key,img=self.mode_info(user,target)
            pk_name=user.name
            o_name=target.name
            self.set_message('{} fainted!'.format(o_name),wait=1000)
            l=user.level
            exp=target.experience_yield
            if key==self.player_key:
                self.set_message('{} got {} experience'.format(pk_name,exp),wait=battle_message_wait)
                user.EXP+=exp
                l2=user.level
                if l2>l:
                    self.set_message('{} grew to level {}!'.format(pk_name,l2),wait=battle_message_wait)
                    self.draw_pokemon()
            self.slide_out(img.canvas_obs[0],'bottom',steps=5,step_rate=50)
            self.holder.next_pokemon()
            self.chosen_actions=[]
            return 'done'
    
    def end_fade(self,event=None):
        '''Fades the battle out at the end'''
        player_pk,player_bx=self.player.canvas_obs
        enem_pk,enem_bx=self.enemy.canvas_obs
        try:
            self.delete(player_bx)
        except:
            pass
        try:
            self.delete(enem_bx)
        except:
            pass

        obs=[]
        if not self.pokemon[self.player_key].KOed:
            obs.append(player_pk)
        if not self.pokemon[self.enemy_key].KOed:
            obs.append(enem_pk)
        
        self.fade_out('all',steps=10)
            

