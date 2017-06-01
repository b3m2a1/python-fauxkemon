from .Character import *
from .Tile import *


maps=getdir('maps')
class Map(WalkerCanvas):
    '''Map class for the characters to move on. Divided into a grid of tiles.'''
    Tile=Tile
    Character=Character
    root_directory=maps
    standard_dimensions=standard_screen_dimensions
    character_colorizing_ranges=character_colorizing_ranges
    
    map_save_file_structure='''
rowsxcolumns[:(tint_color_1)|(tint_color_2)|...|(tint_color_n)] [{(tint_range_1)|(tint_range_2)|...|(tint_range_n)]

tile_type_1_[pokemon_1: (possible_level_11,possible_level_12,...,possible_level_1n)[:appearance_rate_1]] [pokemon_2: (possible_level_21,possible_level_122,...,possible_level_2n)[:appearance_rate_2]]... [pokemon_n: (possible_level_n1,possible_level_n2,...,possible_level_nn)[:appearance_rate_n]]
tile_type_2_[pokemon_1: (possible_level_11,possible_level_12,...,possible_level_1n)[:appearance_rate_1]] [pokemon_2: (possible_level_21,possible_level_122,...,possible_level_2n)[:appearance_rate_2]]... [pokemon_n: (possible_level_n1,possible_level_n2,...,possible_level_nn)[:appearance_rate_n]]
...
tile_type_n_[pokemon_1: (possible_level_11,possible_level_12,...,possible_level_1n)[:appearance_rate_1]] [pokemon_2: (possible_level_21,possible_level_122,...,possible_level_2n)[:appearance_rate_2]]... [pokemon_n: (possible_level_n1,possible_level_n2,...,possible_level_nn)[:appearance_rate_n]]

#TILES#
tile_save_string_11|tile_save_string_12|..tile_save_string_1columns
tile_save_string_21|tile_save_string_22|..tile_save_string_2columns
...
tile_save_string_rows1|tile_save_string_rows2|..tile_save_string_rowscolumns
#CHARACTERS
character_save_string_1
character_save_string_2
...
character_save_string_n
#EXITS
exit_name_1->new_map_1.new_map_entrance_1
exit_name_2->new_map_2.new_map_entrance_2
...
exit_name_n->new_map_n.new_map_entrance_n
#ENTRANCES
entrance_name_2->(entrance_row_2,entrance_column_2)
entrance_name_2->(entrance_row_2,entrance_column_2)
...
entrance_name_2->(entrance_row_2,entrance_column_2)
'''.strip()

    def __init__(self,root=None,name='map',width=36,height=36,entry=(0,0),initialcharacter=True,               a_button=a_button,b_button=b_button,start_button=start_button,extension=None,
    tint_colors=None,game=None,flags=None,source=None,bounded=True,screen_tile_range=screen_tile_range,
    colorizing_ranges=None,character_colorizing_ranges=None,font=None,
    encounter_pokemon=None,manager=None,basecell='Blank',exitproc=None,event_library=None):
        self.name=name
        self.game=game
        self.source=source
        self.tint_colors=tint_colors
        self.processing_message=None
        self.processing_message_stack=deque()
        self.event_library=event_library
        if colorizing_ranges is None:
            colorizing_ranges=tile_colorizing_ranges
        self.colorizing_ranges=colorizing_ranges
        if not character_colorizing_ranges is None:
            self.character_colorizing_ranges=character_colorizing_ranges
        if exitproc is None:
            exitproc=lambda c,o,t:(c.remove(o,trigger='kill'),self.current.remove(o),self.Draw())
        self.file=None
        self.dir=None
        self.newcell=basecell
        self.adjacent_map_hold={}
        
        if manager is None:
            manager=root
            if not hasattr(manager,'map_frame'):
                manager.map_frame=manager
                
        if font is None:
            if hasattr(manager,'font'):
                font=manager.font
            else:
                font=PokeFont()
        elif not isinstance(font,dict):
            font=tuple(font)
        self.font=font
        
        if encounter_pokemon is None:
            encounter_pokemon={'=default=':{}}
        elif not isinstance(encounter_pokemon,dict):
            encounter_pokemon={'=default=':{}}.update(encounter_pokemon)
        elif not '=default=' in encounter_pokemon:
            encounter_pokemon['=default=']={}
        self.pokemon=encounter_pokemon
        self.text=None
        if flags is None:
            flags=[]
            _flags=set()
        elif isinstance(flags,list):
            _flags=set(flags)
        else:
            flags,_flags=flags
        self.flags=flags
        self._flags=_flags
                
        super().__init__(root,height,width,initialwalkers=0,bounded=bounded)
        
        Standardizer.standardize(self)
        self.default_screen_range=screen_tile_range
        self.SetSize(*screen_tile_range)
        self.walkerKwargs={'name':'main','initialcell':entry}
        self.exitproc=exitproc
        if initialcharacter:
            self.NewCharacter(*entry,NPC=False)
        else:
            self.character=None
        
        self.manager=manager
        
        self.a_button=a_button
        self.b_button=b_button
        self.start_button=start_button

        self.textwindow=None
        self.menu=None
        
        self.exits={}
        self.entries={}
        
        self.current_view='map'
        
        self.bind('<Configure>',lambda e:self.adjust_font_size(),'+')
        self.bind('<Button-1>',self.route_focus,'+')
        self.button_bind()
    
    def has_flag(self,flag):
        return flag in self._flags
        
    def set_flag(self,flag):
        if not flag in self._flags:
            self.flags.append(flag)
            self._flags.add(flag)
    def remove_flag(self,flag):
        if flag in self._flags:
            self.flags.remove(flag)
            self._flags.remove(flag)
    
    def flag_index(self,flag):
        return self.flags.index(flag) if flag in self._flags else -1
    
    def flag_get(self,index):
        return self.flags[index]
    
    @property
    def has_text_window(self):
        return (not self.text is None) and self.text.winfo_exists()
        
    def route_focus(self,event=None):
        view = 'text' if self.has_text_window else self.current_view
        if view=='text':
            if hasattr(self.text,'yn_dialog'):
                self.text.yn_dialog.focus_on()
            else:
                self.focus_set()
            ret='break'
        elif view=='menu':
            self.menu.focus_set()
            ret='break'
        elif view=='inventory':
            self.inventory.inventory.focus_on()
            ret='break'
        else:
            self.focus_set()
            ret=None
        return ret
            
    def adjust_font_size(self,std_font=None,window_width_std=None):
        '''Adjusts the font size for the map
        
Determines this by comparing the standard screen width to the average character width for the standard font and then comparing the equivalent for the current font at the standard font size

i.e., solve 
    font_size_std/font_size = average_char_width_std*window_size_std/char_width*window_size

where the char_widths are calculated with at font_size_std 
'''
        w_standard=standard_screen_dimensions[0] if window_width_std is None else window_width_std
        f_test=PokeFont() if std_font is None else std_font
              
        w_current=self.winfo_width()
        
        f=self.font
        f_base_size=f_test.cget('size')
        f.config(size=f_base_size)
        
        test=string.ascii_letters+string.digits+string.punctuation+' ' 
        std_size_avg=(f_test.measure(test)/len(test))
        char_size_avg=(f.measure(test)/len(test))
        
        new_font_size = f_base_size/(w_standard*std_size_avg)*(char_size_avg*w_current)
        
        f.config(size=int(new_font_size))
    
    def buffer_events(self,*events):
        for e in events:
            self.event_queue.add(*e)
    
    def ArrowMove(self,arrow):
        super().ArrowMove(arrow)
        self.step()
        
    def MoveWalkers(self,*args,**kwargs):
        '''Moves the specified characters'''
        super().MoveWalkers(*args,**kwargs)
        self.step()
        
                                       
    def SetCharacter(self,ob):
        '''Makes ob the base character'''
        if not self.character is None:
            self.character.npc_flag=True
        self.current=[ob]
        self.character=ob
        self.character.npc_flag=False
        
    def Clear(self):
        '''Clears all object from the map'''
        super().Clear()
        self.character=None
        
    def KillCurrent(self):
        '''No different from Clear. It's unclear why this is here.'''
        super().Clear()
        self.character=None

    def button_bind(self,mode=None):
        '''Applies the appropriate button bindings for the mode specified

mode='standard' will bind the arrows, a key, and start button to their usual effects
mode='both' will bind both a and b to call the objects ahead
mode='text' will cause a to be the text.seek function that runs through the message on screen
mode='YN' will cause up and down to choose Yes or No and a to select, b to select No
mode='disabled' will disable all buttons. Useful for cut-scenes.
mode='menu' will cause b to destroy the menu a is bound by the menu itself
anything else will cause the 'standard' binding to occur'''        
        
        aKey='<KeyPress-{}>'.format(self.a_button)
        bKey='<KeyPress-{}>'.format(self.b_button)
        startKey='<KeyPress-{}>'.format(self.start_button)
        toDo=[aKey,bKey,'<Up>','<Down>','<Left>','<Right>',startKey]
        try:
            startKey='<KeyPress-{}>'.format(self.start_key)
        except AttributeError:
            pass
        else:
            toDo.append(startKey)
        for x in toDo:
            self.unbind(x)
        
        if mode is None:
            if self.has_text_window:
                if hasattr(self.text,'yn_dialog'):
                    mode='YN'
                else:
                    mode='text'
            else:
                mode='standard'
        if mode=='standard':
#             if not self.textwindow is None:
#                 self.textwindow.destroy()
#                 self.textwindow=None
            if not self.menu is None:
                self.menu.place_forget()
            self.bind(aKey,lambda e:(self.character.call_ahead('a_button'),self.Draw()))
            self.bind(startKey,lambda e:self.OpenMenu())
            for key in ('Up','Down','Left','Right'):
                self.bind('<{}>'.format(key),self.ArrowMove)
            self.bind('<Control-r>', lambda e:self.character.run())
            self.bind('<Control-w>', lambda e:self.character.walk())
            self.current_view='map'
        elif mode=='both':
            self.bind(aKey,lambda e:(self.character.call_ahead('a_button'),self.Draw()))
            self.bind(bKey,lambda e:(self.character.call_ahead('b_button'),self.Draw()))
            self.current_view='map'
        elif mode=='text':
            self.bind(aKey,lambda e:self.text.seek())
            self.current_view='text'
        elif mode=='YN':
            for w in (self.text.no_frame,self.text.yes_frame):
                w.bind(aKey,self.text.select)
                w.bind(bKey,self.text.no)
                self.current_view='text'
        elif mode=='disabled':
            self.current_view='map'
        elif mode=='menu':
            self.bind(bKey,lambda e:self.menu.destroy())
            self.current_view='menu'
        else:
            self.button_bind()

    def DisplayPokedex(self,event):
        '''Should pack the character.trainer's PokedexDisplay frame in the map's master frame'''
        #open a pokedex menu from in event.widget.master
        raise NotImplementedError
    def DisplayPokemon(self,event):
        '''Displays the pokemon of the bound trainer as is done in battle, but with slightly different commands'''
        self.choose_pokemon(mode='map')
        event.widget.focus_set()

    def OpenItems(self,event):
        '''Should open the battle inventory frame, but in a text window placed on the map'''
        
        from ..PokemonBattle import InventoryWindow
        self.button_bind('disabled')
        self.inventory=tk.Frame(self)
        Standardizer.standardize(self.inventory,'border')
        self.inventory.inventory=InventoryWindow(self.inventory,self.character.trainer.inventory, controller=self)
        self.inventory.inventory.pack(fill='both',expand=True)
        self.inventory.place(relx=1,rely=1/7,anchor='ne')
        self.inventory.inventory.bind(self.b_button,lambda e,s=self:s.inventory.destroy())
        self.inventory.inventory.bind(self.a_button,lambda e,s=self,i=self.inventory.inventory:s.use_item(i.current_item))
        self.current_view='inventory'
        self.wait_window(self.inventory)
        
    def TrainerInfo(self,event):
        '''Should pack the trainer's InfoFrame in the map's master frame'''
        self.show_trainer(self.character.trainer)
        event.widget.focus_set()
        
    def SaveGame(self,event=None):
        '''Opens a yes-no dialog for saving'''
        def save_cmd(*args,self=self):
            self.CreateMessage('''Saving game...
#PAUSE 1000
---NEW MESSAGE---
Done
#DELAY 500''')
            try:
                self.master.SaveGame()
            except AttributeError:
                self.Save()
                
            yield 'done'

        def no_cmd(*args,self=self):
            self.menu.focus_set()
            yield 'break'
        self.create_message('Would you like to save the game?',
                            YN=((save_cmd,),(no_cmd,),None))
        
    def OptionsMenu(self,event):
        '''Should open a window to configure various pieces of the game'''

        raise NotImplementedError
    def OpenMenu(self,event=None):
        '''Opens the menu to select run the previous few commands'''
        if not self.character is None:
#             self.menu_visible=True
            if self.menu is None:
                self.generate_menu()
                self.menu.menu_pairs[-1][-1].focus_set()
            N=len(self.menu.menu_pairs)
            self.menu.place(relx=1,relheight=.75*(N/7),
                    relwidth=.25,anchor='ne')
            self.button_bind('menu')
            self.menu.focus_set()           
            self.wait_window(self.menu.wait_thing)
            self.focus_set()
            self.button_bind()
    
    def generate_menu(self):
        
        self.menu=tk.Frame(self,bg='black',bd=3,relief='ridge')
        self.menu.wait_thing=tk.Frame(self.menu)
        def close_menu(menu=self.menu):
            menu.place_forget()
            menu.wait_thing.destroy()            
            menu.wait_thing=tk.Frame(self.menu)
        
        self.menu.close_menu=close_menu
        
        self.menu.menu_pairs=menu_pairs=[
            ('SAVE',self.SaveGame),
            ('OPTION',self.OptionsMenu),
            ('EXIT',lambda e,s=self:self.menu.close_menu())
            ]
        
        if not self.character.trainer is None:
            menu_pairs.insert(0,(self.character.trainer.name,self.TrainerInfo))
            menu_pairs.insert(0,('ITEM',self.OpenItems))
            if len(self.character.trainer.pokemon)>0:
                menu_pairs.insert(0,('POKEMON',self.DisplayPokemon))
            if not self.character.trainer.pokedex is None:
                menu_pairs.insert(0,('POKEDEX',self.DisplayPokedex)) 
                
        N=len(menu_pairs)
        self.menu.menu_items=self.menu_items=FormattingGrid(self.menu,rows=N,columns=1, 
            active=Standardizer.configuration_map['select'], inactive=Standardizer.configuration_map['frame'],arrow_move=True)
        self.menu_items.pack(fill='both',expand=True)
        self.menu_items.gridConfig(sticky='nsew')
        
        i=0
        for n,c in menu_pairs:
            L=self.menu_items.AddFormat(tk.Label,text=n,font=self.font)
            L.bind(self.a_button,lambda e,c=c:c(e))
            L.bind('<KeyPress-{}>'.format(self.b_button),lambda e,s=self:self.menu.close_menu())
            menu_pairs[i]=(n,L)
            i+=1
            
        self.menu_items.Refresh()
        self.menu_items.configure_rows(weight=1);self.menu_items.configure_cols(weight=1);
        self.menu_items.bind('<Button-1>',self.route_focus)
        self.menu.bind('<FocusIn>',lambda e,s=self:s.menu.menu_items.focus_on())
        self.menu.bind('<Destroy>',lambda e,s=self:setattr(s,'menu',None))
    
    def choose_pokemon(self,mode='select'):
        '''Allows pokemon choice for things like the inventory window'''
        
        from ..PokemonBattle import PokemonListingFrame
        
        P=PokemonListingFrame(self.master,
                              self.character.trainer,
                              mode='map')
        P.pack(fill='both',expand=True)
        self.pack_forget()
        poke=P.choose_pokemon(mode)
        P.focus_set()
        P.destroy()
        self.pack(fill='both',expand=True)
        self.focus_set()
        return poke
        
    def encounterable_pokemon(self,tile_type='=default='):
        '''Chooses a weighted random pokemon from those available on the tile_type'''
        from ..DataTypes import Pokemon
        p_dict=self.pokemon
        if tile_type in p_dict:
            choices=p_dict[tile_type]
        else:
            choices=p_dict['=default=']
        if choices:
            options=[(k,choices[k]) for k in choices]
            probability_ranges=[o[1][1] if not o[1][1] is None else 1/len(options) for o in options]
            probability_sum=sum(probability_ranges)
            for i in range(1,len(probability_ranges)):
                probability_ranges[i]+=probability_ranges[i-1]
            test_value=random.random()*probability_sum
            for i,v in enumerate(probability_ranges):
                if v>test_value:
                    break
            pokemon,levels=options[i]
            pokemon=Pokemon(pokemon,random.choice(levels[0]))
        else:
            pokemon=None
        return pokemon
        
    def show_trainer(self,trainer):
        '''Displays the trainer in the master frame'''
        t_info=trainer.InfoFrame(self.master)
        t_info.pack(fill='both',expand=True)
        self.pack_forget()
        t_info.focus_set()
        self.wait_window(t_info)
        self.pack(fill='both',expand=True)
        self.focus_set()
    
    def show_pokedex(self,trainer):
        '''Displays the trainer's pokedex in the master frame'''
        t_info=trainer.PokedexFrame(self.master)
        t_info.pack(fill='both',expand=True)
        self.pack_forget()
        t_info.focus_set()
        self.wait_window(t_info)
        self.pack(fill='both',expand=True)
        self.focus_set()
        
    def process_message_text(self,text,cell=None,ob=None,trigger=None,do='all'):
        '''Process a message based on the special keys it finds and then formats it appropriately
        
#PAUSE <number> 
    -forces a pause of <number> milliseconds before going to the next message 
    
#DELAY <number>
    -forces the message to exists for <number> milliseconds before allowing it to be panned through
    
#YN
#Y
<yes commands>
#N
<no commands>
#YN
    -pops up a yes-no dialog after the message is done where yes executes the yes commands and no executes the no commands. 
    If either is omitted, that button does nothing
    Commands should be event library events. Events like cell_message naturally pass the appropriate objects to CreateMessage to execute the event.
#CMD
<commands>
#CMD
    -executes the commands at the end of the message. Commands should be as in the #YN case.

#FLAGBLOCK 

#FLAG <flag>
message_body
.
.
.

#FLAGBLOCK
    - keeps going through the #FLAG blocks until a flag is reached that isn't in the map's flag set and uses the message body for the most recent flag

The final generated text is then treated as a format string with the following arguments:
    map = the map this method is called on
    cell = the cell or character it is called on (defaults to None)
    ob = the object it is called on (defaults to None)
'''     

        yn_key='#YN';ykey='#Y';nkey='#N'
        YN=False
        cmd_key='#CMD';l2=len(cmd_key)
        cmds=lambda:()
        pause_key='#PAUSE'
        delay_key='#DELAY'
        flags_key='#FLAGBLOCK';flag_k='#FLAG '
        text=text.strip().splitlines()#[x for x in text.splitlines() if x.strip()]
        text_lines=iter(tuple(text))
        line_num=0
        wait=None
        
        do_set=set()
        if do=='all':
            for s in (yn_key,cmd_key,pause_key,delay_key,flags_key):
                do_set.add(s)
        else:
            if 'flags' in do:
                do_set.add(flags_key)
            if 'yn' in do:
                do_set.add(yn_key)
                
        def key_test(key,line,do_test=True):
            do_test=(not do_test) or key in do_set 
            key_t= key in line[:len(key)]
            return do_test and key_t
            
        for line in text_lines:
            if key_test(yn_key,line):
                text[line_num]=None
    ##            text=text.splitlines()
                Y=[];N=[]
                flag=None
                new=[]
                line_num+=1
                for line in iter(lambda t=text_lines:next(t), yn_key):
                    text[line_num]=None
                    l=line.strip()
                    if l==ykey:
                        flag='Y'
                    elif l==nkey:
                        flag='N'
                    elif flag=='Y':
                        Y.append(l)
                    elif flag=='N':
                        N.append(l)
                    y_events=[]
                    n_events=[]
                    for line in Y:
                        line=line.strip()
                        if line:
                            E=cell.translate_event(line)
                            y_events.append(lambda ob,c=cell,t=trigger,E=E:E(c,ob,t))
                    for line in N:
                        line=line.strip()
                        if line:
                            E=cell.translate_event(line)
                            n_events.append(lambda ob,c=cell,t=trigger,E=E:E(c,ob,t))
                    line_num+=1
                text[line_num]=None
                YN=(y_events,n_events,ob)
            elif key_test(cmd_key,line):
                cmds=[]
                text[line_num]=None
                line_num+=1
                for line in iter(lambda t=text_lines:next(t),cmd_key):
                    text[line_num]=None
                    E=cell.translate_event(line)
                    cmds.append(lambda ob,c=cell,t=trigger,E=E:E(c,ob,t))
                    line_num+=1
                text[line_num]=None
                cmds=(cmds,ob)
            elif key_test(pause_key,line):
                key,time=line.split();wait=int(time)
                text[line_num]=None
                line_num+=1
            elif key_test(delay_key,line):
                key,time=line.split();wait=('lock',int(time))
                text[line_num]=None
                line_num+=1
            elif key_test(flags_key,line):
                message=[]
                current_flag=None
                text[line_num]=None
                line_num+=1
                line_start=line_num
                for line in iter(lambda t=text_lines:next(t),flags_key):
                    if key_test(flag_k,line,False):
                        current_flag=line.split(flag_k)[1]
                        if self.has_flag(current_flag):
                            message=[]
                        else:
                            for line in iter(lambda t=text_lines:next(t),flags_key):
                                text[line_num]=None
                                line_num+=1
                            text[line_num]=None
                            line_num+=1
                            break
                    else:
                        message.append(line)                   
                    text[line_num]=None
                    line_num+=1
                text[line_num]=None
                flag_message,flag_yn,flag_cmds,flag_wait=self.process_message_text('\n'.join(message), cell,ob,trigger,do=do)
                text[line_start]=flag_message
                if flag_yn:
                    YN=flag_yn
                if isinstance(flag_cmds,tuple):
                    cmds=flag_cmds
                if flag_wait:
                    wait=flag_wait                    
            else:
                line_num+=1
        new_t=[None]*len(text)
        i=0
        for t in text:
            if not t is None:
                new_t[i]=t
                i+=1
        text='\n'.join(new_t[:i])
        return (text.format(map=self,cell=cell,ob=ob),YN,cmds,wait)
        
    def CreateMessage(self,text,cell=None,ob=None,trigger=None):
        '''Uses process_message to load the appropriate arguments to pass to create_message

Multiple messages can be created at once by separating them with '---NEW MESSAGE---'
'''     
        text=self.process_message_text(text,cell=cell,ob=ob,trigger=trigger,do='flags')[0]
        text=text.split('\n---NEW MESSAGE---\n')
        self.processing_message_stack.append(self.processing_message)
        processing_message_restore=self.processing_message
        if processing_message_restore is None:
            self.processing_message=True
        for t in text[:-1]:
            txt,YN,cmd,wait=self.process_message_text(t.strip(),cell,ob,trigger)
            self.create_message(txt,YN=YN,command=cmd,wait_time=wait)
        if processing_message_restore is None:
            self.processing_message=False
        t=text[-1]
        txt,YN,cmd,wait=self.process_message_text(t.strip(),cell,ob,trigger)
        self.create_message(txt,YN=YN,command=cmd,wait_time=wait)
        self.processing_message=self.processing_message_stack.pop()
                
    def create_message(self,text,YN=False,command=lambda:None,
        wait_time=None,last_message=None):
        
        if not self.text is None:
            self.text.destroy()
            
        f=self.font
        hset=4*f.metrics('linespace')
        
        bd_frame=BorderedFrame(self)
        self.text=frame=F=RichText(bd_frame,wrap='word',
                             width=10,height=2,font=f,cursor='arrow')
        F.pack(fill='both',expand=True)
        frame.last_message=not self.processing_message if last_message is None else last_message

        F.bind('<FocusIn>',self.route_focus)
        F.bind('<Button-1>',self.route_focus)
        F.bind('<B1-Motion>',self.route_focus)
        F.bind('<Destroy>',lambda e,s=self,F=F:(
            F.master.destroy(),
            s.button_bind(),
            s.focus_set())
            )
        
        F.Insert(text)
        F.see('0.0')
        F.flag=False
        def seek(self=self,F=F,YN=YN):
            '''Pans through the text line by line, calling the end process when the end of the text has been reached'''
            last=F.get('1.0','2.0 linestart')
            F.delete('1.0','2.0 linestart')
            text=F.get('1.0','end').strip()
            if not text:
                F.insert('end',last)
                return seek_end()
        
        def seek_end(self=self,F=F,YN=YN,command=command,f=f):
            '''Intended to either run the yes-no dialog or a command or exit otherwise'''
            if YN:
                y_events,n_events,call_ob=YN
                H=self.text.winfo_height()
                self.text.kill=F
                bh=25;bw=50
                self.text.pack_frame=BorderedFrame(self)
                self.text.yn_dialog=FormattingGrid(self.text.pack_frame,arrow_move=True, rows=0,columns=1)  
                self.text.yn_dialog.pack(fill='both',expand=True)
                self.text.yes_frame=Y=FormattingElement(tk.Label, self.text.yn_dialog,
                    text=' YES ')
                self.text.no_frame=N=FormattingElement(tk.Label, self.text.yn_dialog,
                    text=' NO  ')
                self.text.yn_dialog.Add(Y,N)
                Standardizer.standardize(N)
                Standardizer.standardize(Y)      
                H+=self.text.pack_frame['bd']+self.text.master['bd']
                self.text.pack_frame.place(relx=0,rely=1,y=-H,anchor='sw')
                on_config={'bg':'grey95','relief':'ridge','fg':'blue','bd':2}   
                def yes_choice(e=None,on_config=on_config,s=Standardizer):
                    self.text.choice='Y'
                    self.text.yes_frame.config(on_config) 
                    s.standardize(self.text.no_frame)
                def no_choice(e=None,on_config=on_config,s=Standardizer):
                    self.text.choice='N'
                    self.text.no_frame.config(on_config)
                    s.standardize(self.text.yes_frame)
                def select(e,F=F,N=N,Y=Y,self=self,
                                y_events=y_events,n_events=n_events):
                    self.processing_message_stack.append(True)
                    F.destroy()
                    F.pack_frame.destroy()
                    del F.yn_dialog
                    if self.text.choice=='Y':
                        add=y_events
                    else:
                        add=n_events
                    self.text=None
                    for e in add:
                        self.event_queue.add(e,call_ob)
                        self.step()
                    self.button_bind()
                    self.processing_message=self.processing_message_stack.pop()
                    
                                        
                self.text.yes=yes_choice;self.text.yes_frame.bind('<FocusIn>',self.text.yes)
                self.text.no=no_choice;self.text.no_frame.bind('<FocusIn>',self.text.no)
                self.text.select=select
                self.text.yes(1);self.text.yes_frame.focus_set()
                self.after_idle(lambda bb=self.button_bind:bb('YN'))
                return 'break'
                           

            else:
            
                F.destroy()
                self.text=None
                lm=F.last_message
                lm=lm if not lm is None else self.processing_message
                if lm:
                    self.after_idle(lambda bb=self.button_bind:bb())
                    
                
                try:
                    com,ob=command
                except TypeError:
                    com=command()
                    ob=None
                    if type(com).__name__!='generator':
                        com=False
                except ValueError:
                    com=command
                    ob=None
                    
                if not com is False:
                    self.processing_message_stack.append(True)
                    for e in com:
                        self.event_queue.prepend(e,ob)
                        self.step()
                    self.processing_message=self.processing_message_stack.pop()
                    
                return 'break'
            
        F.seek=seek
        F.seek_end=seek_end
        F.last=F.index('insert')
        h=self.winfo_height()
        bd_frame.place(rely=1,anchor='sw',height=hset,relwidth=1)
        F.see('0.0')
        
        if wait_time is None:
            wait_time=('lock',0)
        
        if isinstance(wait_time,tuple):
            self.button_bind('text')
            self.hold_update(wait_time[1])
            self.focus_set()
            self.wait_window(frame)
        else:
            self.button_bind('disabled')
            self.focus_set()
            self.hold_update(wait_time)
            return seek_end()
    
    def use_item(self,item):
        self.inventory.destroy()
        if not item is None:
            self.create_message("Map items are currently unsupported")
            self.button_bind()
        else:
            self.button_bind('menu')
            self.menu.focus_set()
        
    def NewCell(self,i,j):
        return self.Tile(self.newcell,self,i,j,source=self.source)
        
    def NewCharacter(self,i=None,j=None,NPC=True,name='Main',source=None):
        if i is None:
            i=(self.base_x+self.cols)//2
        if j is None:
            j=(self.base_y+self.rows)//2
            
        kw=dict(**self.walkerKwargs)
        if source is None:
            if self.file:
                d,b=os.path.split(self.file)
                if not d==maps:
                    source=os.path.basename(d)
        kw.update({'initialcell':[i,j],'name':name,'source':source})
        w=self.Character(self,**kw)
        self.AddObject(w)
        if not NPC:
            self.SetCharacter(w)
        self.Draw()

    def StartBattle(self,team1,team2):
        r=self.manager.StartBattle(team1,team2)
        self.button_bind()
        self.focus_set()
        return r
        
    def ExitMap(self,which,C=None,root=None,source=None):
        
#         self._found_maps.clear()
        if hasattr(self.manager,'SwitchMap'):
            self.manager.SwitchMap(which,self,C=C,root=root,source=source)
        else:
            new=self.LoadMap(which,C=C,root=root,source=source)
            self.pack_forget()
            new.pack(fill='both',expand=True)
    
    _found_maps={}
    def FindMap(self,which,root=None,source=None):
        
        try:  
            name,where=self.exits[which]
        except KeyError:
            name=which
            where=None
#             name,where=next(iter(self.exits.values()))

        if source is None:
            source=os.path.dirname(self.file)
        f=os.path.join(source,name)
        if not os.path.exists(f):
            f=os.path.join(self.manager.map_dir,name)
            
        if os.path.exists(f):
            ind=0
            for n in os.listdir(f):
                n=os.path.splitext(n)[0]
                i_test=self.flag_index(n)
                ind=max(ind,i_test)
            
            f=os.path.join(f,self.flag_get(ind)+'.pmp')
        else:
            f+='.pmp'
            
        if root is None:
            root=self.master
        
        try:
            new=type(self)._found_maps[(f,root)]
            new=new.copy()
        except KeyError:
            try:
                new=type(self).LoadFromFile(root,f,manager=self.manager)
            except FileNotFoundError:
                raise FileNotFoundError('No map {}'.format(name))
            type(self)._found_maps[(f,root)]=new
            
        if new.entries:
            entries=iter(new.entries.values())
            try:
                where=new.entries[where]
            except KeyError:
                where=next(entries)
        else:
            rw,cl=new.basearray.dimensions
            for i in range(rw):
                where = None
                for j in range(cl):
                    test_cell=new[i,j]
                    if test_cell.space is None or test_cell.space > 0:
                        where=(i,j)
                        break
                if not where is None:
                    break
                    
        return (new,where)
        
    def LoadMap(self,which,C=None,root=None,source=None):

        Tile._file_tracker.clear()
        Character._file_tracker.clear()
        
        new,where=self.FindMap(which,root=root,source=source)                    
        
        if new.character:
            cell=new.character.current
            cell.remove(new.character)
            
        if C is None:
            C=self.character
            
        if not C is None:
            try:
                new.AddObject(C,where=where,override=True)
            except IndexError:
                for e in entries:
                    try:
                        new.AddObject(C,where=e,override=True)
                    except IndexError:
                        continue
                    break
            new.SetCharacter(C)
            C.center_view()
            
        return new

    def flash(self,fill='black',length=50,delay=None,times=1,**kwargs):
        w,h=self.window_dimensions

        if delay is None:
            delay = 50 if times>1 else 0

        kwargs['fill']=fill
        def flash(counter=times,first=False,length=length,delay=delay,kwargs=kwargs,self=self):
            if counter>0:
                if not first and delay>5:
                    wait_var=tk.BooleanVar(value=False)
                    self.after(delay,lambda w=wait_var:w.set(True))
                    self.wait_variable(wait_var)
                o=self.create_rectangle(0,0,w,h,**kwargs)
                self.update_idletasks()
                wait_var=tk.BooleanVar(value=False)
                self.after(length,lambda w=wait_var:w.set(True))
                self.wait_variable(wait_var)
                self.delete(o)
                flash(counter-1)
        flash(first=True)
                          
    def Save(self,locale=None):
        
        if locale is None:
            if self.file is None:
                from tkinter.filedialog import asksaveasfilename as ask
                self.file=ask(parent=self,defaultextension='.pmp')
                if self.file=='':
                    self.file=None
                    raise ValueError("Can't find file to save map as")
            file=self.file
        else:
            name=self.name
            me=os.path.join(locale,name)
            n=1
            file=me+'.pmp'
        if not file==self.file:
            name=self.name
            while os.path.exists(file):
                file=me+'_{}.pmp'.format(n)
                name=self.name+'_{}'.format(n)
                n+=1
            self.name=name
            self.file=file
        
        grid=self.basearray
        self.name=os.path.splitext(os.path.basename(self.file))[0]
        r,c=self.basearray.dim()
        ts=''
        if not self.tint_colors is None:
            ts=':'+'|'.join((str(x) for x in self.tint_colors))
        if not self.colorizing_ranges is None:
            ts+='{'+'|'.join((str(x) for x in self.colorizing_ranges))
        l1='{}x{}{}\n'.format(r,c,ts)
        
        if os.path.exists(self.file):
            with open(self.file) as protect:
                cur_t=protect.read()
        else:
            cur_t=''
        
#         print(len(cur_t))
            
        try:
            with open(self.file,'wb+') as file:
                file.write(l1.encode())
                for key,val in self.pokemon.items():
                    text=key+'_'
                    for p,l in val.items():
                        text+='[{}:{}]'.format(p,'{}:{}'.format(*l if len(l)!=2 or isinstance(l[0],int) else l)
                        )
                    text+='\n'
                    file.write(text.encode())
                file.write('#TILES#\n'.encode())
                    
                lines=[]
                for i in range(r):
                    l=(t.save_string() for t in self.basearray[i])
                    lines.append(self.gridsep.join(l))
                file.write('\n'.join(lines).encode())
                file.write('\n#CHARACTERS#'.encode())
                if not self.character is None:
                    file.write(('\n'+self.character.save_string).encode())
                else:
                    file.write('\n'.encode())
                for x in self:
                    if isinstance(x,Tile):
                        for ob in x.obs:
                            if not ob is self.character:
                                file.write(('\n'+ob.save_string).encode())
                file.write('\n#EXITS#\n'.encode())
                for k,t in self.exits.items():
                    ws='{0}->{1[0]}.{1[1]}\n'.format(k,t)
                    file.write(ws.encode())
                
                file.write('#ENTRANCES#\n'.encode())
                for k,c in self.entries.items():
                    ws='{}->{}\n'.format(k,list(c))
                    file.write(ws.encode())
        except:
            with open(self.file,'wb+') as file:
                file.write(cur_t.encode())
            raise
            
    
#     _tile_re='
    @classmethod
    def LoadFromFile(cls,root,source,manager=None,**kwargs):
        '''Assumes the file is formatted in standard Map save file structure'''

        map_name=os.path.splitext(os.path.basename(source))[0]
        with open(source) as file:
            l=next(file).strip()
            bits=l.split(':')
            if len(bits)>1:
                l,colors=bits
                colors=colors.split('{')
                if len(colors)>1:
                    colors,col_ranges=colors
                    col_ranges=tuple((eval(x) for x in col_ranges.split('|')))
                else:
                    col_ranges=None
                    colors=colors[0]
                colors=tuple((eval(x) for x in colors.split('|')))
            else:
                bits=l.split('{')
                if len(bits)>1:
                    l,col_ranges=bits
                    col_ranges=tuple((eval(x) for x in col_ranges.split('|')))
                else:
                    col_ranges=None
                colors=None
            r,c=(int(x) for x in l.split('x'))
            encounterable=None
            
            tiles_key='#TILES#';tiles_key_length=len(tiles_key)
            
            for line in file:
                if tiles_key==line[:tiles_key_length]:
                    break
                tile_type,pokemon=line.strip().split('_',1)
                pokes={}
                for x in pokemon.split(']'):
                    x=x.strip()
                    if x:
                        x=x.strip('[')
                        poke_bits=x.split(':')
                        if len(poke_bits)==1:
                            p=poke_bits[0];lvs=str(tuple(range(2,100)));appearance=None
                        elif len(poke_bits)==2:
                            p,lvs=poke_bits;appearance=None
                        else:
                            p,lvs,appearance=poke_bits[:3]
                            try:
                                appearance=float(appearance)
                            except ValueError:
                                appearance=None
                        lvs=lvs.strip('(),')
                        lvs=tuple((int(x) for x in lvs.split(',')))
                        pokes[p]=(lvs,appearance)
                if encounterable is None:
                    encounterable={}
                encounterable[tile_type]=pokes
                    
            self=cls(root,width=c,height=r,initialcharacter=False,tint_colors=colors, colorizing_ranges=col_ranges,encounter_pokemon=encounterable,manager=manager, name=map_name,**kwargs)
            
            self.file=source
            self.dir=os.path.dirname(source)
            for i in range(r):
                l=next(file).strip()
                vals=l.split(cls.gridsep)
                for j in range(c):
                    v=vals[j]
                    T=cls.Tile.FromString(self,v,ignore_errors=True)
                    self.basearray[i,j]=T
            
            char_flag=True
            characters_key='#CHARACTERS#';characters_key_length=len(characters_key)
            exits_key='#EXITS#';exits_key_length=len(exits_key)
            for line in file:
                if characters_key==line[:characters_key_length]:
                    continue
                elif exits_key==line[:exits_key_length]:
                    break
                elif not line.strip():
                    char_flag=False
                    continue
                char=self.Character.from_string(line,self)
                if char_flag:
                    self.SetCharacter(char)
                    char_flag=False
                self.AddObject(char)
                if self.character:
                    self.character.center_view()
                    
            entrance_key='#ENTRANCES';entrance_key_length=len(entrance_key)
            for line in file:
                if entrance_key==line[:entrance_key_length]:
                    break
                num,ex=line.split('->')
                name,to=ex.split('.')
                self.exits[num]=(name,to.strip())
            for line in file:
                num,en=line.split('->')
                en=eval(en)
                self.entries[num]=en
        self.name=map_name
        return self
    
    def screen_edge(self,side='top'):
        my,mx,MY,MX=self.something
        
    def map_edge(self,side='top'):
        '''Iterates through the indices of the specified map edge'''
        r,c=self.basearray.dimensions
        if side=='top':
            for j in range(c):
                yield (0,j)
        elif side=='right':
            for i in range(r):
                yield (i,c-1)
        elif side=='bottom':
            for j in range(c):
                yield (r-1,c-1-j)
        else:
            for i in range(r,0):
                yield (r-1-i,0)
    def edge_center(self,side='top'):
        '''Returns the index of the middle-most cell on the specified side'''
        r,c=self.basearray.dimensions
        if side=='top':
            i,j=(0,int(c/2))
        elif side=='right':
            i,j=(int(r/2),c-1)
        elif side=='bottom':
            i,j=(r-1,int(c/2))
        else:
            i,j=(int(r/2),0)
        return (i,j)
    def map_border(self):
        '''Iterates through the indices around the map border, from top left going around clockwise'''
        r,c=self.basearray.dimensions
        for j in range(c):
            yield (0,j)
        for i in range(r):
            yield (i,c-1)
        for j in range(c):
            yield (r-1,c-1-j)
        for i in range(r,0):
            yield (r-1-i,0)
    def adjacent_maps(self,walls='all'):
        '''Returns all adjacent maps to this one, either by loading via the stored maps or by checking a wall for exit_window+exit_map combinations'''
        
        if walls=='all':
            walls=('top','right','bottom','left')
        elif isinstance(walls,str):
            walls=(walls,)
            
        for wall in walls:
            if wall in self.adjacent_map_hold:
                for map_entry in self.adjacent_map_hold[wall]:
                    yield map_entry
            else:
                map_list=[]
                self.adjacent_map_hold[wall]=map_list
                for tile in self.map_border() if wall=='all' else self.map_edge(wall):
                    leave_events=self[tile].events['exit_window']
                    for e in leave_events:
                        name=e.name
                        if 'exit_map'==name[:8]:
                            new_map,where=map_entry=self.FindMap(name.split('[')[1][:-1])
                            r,c=new_map.basearray.dimensions
                            if wall=='top' and where[0]==r-1:
                                map_list.append(map_entry)
                            elif wall=='right' and where[1]==0:
                                map_list.append(map_entry)
                            elif wall=='bottom' and where[0]==0:
                                map_list.append(map_entry)
                            elif wall=='left' and where[1]==c-1:
                                map_list.append(map_entry)
                            break 
                for m in map_list:
                    yield m