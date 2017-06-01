from Fauxkemon.code.State import *
from Fauxkemon.code.DataTypes.Pokemon import Pokemon

games=getdir('games')
trainers=getdir('trainers')
trainer_sprites=getdir('trainer_sprites')
chars=getdir('characters')
poke_dir=getdir('pokemon')
trainer_sprite_ext='__trainer_sprites__'

class Trainer:

    _root_source=trainers
    _message_flag_key='#message'
    party_size=party_size
    def __init__(self,name_ID=None,trainer_type=None,file=None,name='Trainer',
            pokedex=True,source=None,flags=None):
    
        import re
        from random import choice
        from string import digits

        if not source is None:
            self.dir=os.path.join(self._root_source,source)
        else:
            self.dir=self._root_source
        
        self.flags=set() if flags is None else flags
        
        self.trainer_type=name if trainer_type is None else trainer_type
        
        self.inventory=Inventory()
        if file is None:
            if name_ID is None:
                idKey=idNo(6)
                if pokedex:
                    self.pokedex=pokedex if isinstance(pokedex,Pokedex) else Pokedex(self.dir,ID=idKey)
                else:
                    self.pokedex=None
                number=idKey
                self.file=os.path.join(self.dir,'{}_{}.txt'.format(name,idKey))
                self.pokemon=[]
                self.messages={}
                self.game_name=(name,number)
                self.name=name
                self.ID=number
                self.money=100
                self.image_file_base=os.path.join(self.dir,trainer_sprite_ext,self.trainer_type)
                self.trainer_source=self.dir
                    
            else:

                def key_search(self,key):
                    f=None
                    for ext in os.listdir(self.dir):
                        if key in ext:
                            f=os.path.join(self.dir,ext)
                            break
                    else:
                        d=self.dir
                        loop_flag=True
                        if self.dir==self._root_source:
                                raise FileNotFoundError(
                                    "Could not locate trainer {} starting from {}".format(key,d)
                                    )
                        while loop_flag:
                            self.dir=os.path.split(self.dir)[0]
                            for ext in os.listdir(self.dir):
                                if key in ext:
                                    f=os.path.join(self.dir,ext)
                                    loop_flag=False
                                    break
                            else:
                                if self.dir==self._root_source:
                                    raise FileNotFoundError(
                                        "Could not locate trainer {} starting from {}".format(key,d)
                                        )
                    return f
                
                bits=name_ID.split('_',1)
                if len(bits)==2:
                    f=os.path.join(self.dir,name_ID+'.txt')
                    if not os.path.exists(f):
                        f=key_search(self,name_ID)
                else:
                    key=bits[0]
                    f=key_search(self,key)
                    
                self.load_from(f,pokedex=pokedex,source=source)
        else:
            self.load_from(file,pokedex=pokedex,source=source)
    
    def get_item(self,item):
        self.inventory.add(item)
            
    def load_from(self,file,pokedex=True,source=None):
        self.file=file
        directory,basename=os.path.split(file)
        self.dir=directory
        source=self._root_source if source is None else os.path.join(self._root_source,source)
        self.trainer_source=source
        basename,ext=os.path.splitext(basename)
        bits=basename.split('_')
        if len(bits)==1:
            bits.append(-1)
        name,num=bits
        self.name=name
        self.ID=num
        if pokedex:
            self.pokedex=pokedex if isinstance(pokedex,Pokedex) else Pokedex(self.dir,ID=self.ID)
        else:
            self.pokedex=None
        with open(file,encoding='utf-8') as src:
            flag_flag=False
            for line in src:
                line=line.strip()
                try:
                    key,res=line.split(':',1)
                except ValueError:
                    if flag_flag:
                        self.flags.add(line)
                else:
                    if key=='flags':
                        flag_flag=True
                    else:
                        if key=='pokemon':
                            self.pokemon=([
                                self.id_to_pokemon(r.split('_')[1]) if isinstance(r,str) else r
                                for r in eval('({},)'.format(res))] if res.strip() else [])
                        elif key=='money':
                            self.money=int(res)
#                         elif key=='image':
#                             sprites=os.path.join(source,)
#                             self.image_file_base=os.path.join(sprites,self.trainer_type)
                        elif key=='name':
                            self.name=res.strip()
                        elif key=='type':
                            self.trainer_type=res.strip()
                        elif key=='inventory':
                            inv=eval(res)
                            self.inventory=Inventory(inv)
                        elif key=='messages':
                            break
            key='game_start'
            message=['Hi!']
            self.messages={}
            for line in src:
                line=line.strip()
                if line==self._message_flag_key:
                    self.messages[key]='\n'.join(message)
                    key=next(src).strip()
                    message=[]
                else:
                    message.append(line)
            self.messages[key]='\n'.join(message)

    def __str__(self):
        if isinstance(self.ID,int):
            s=''
        else:
            s='{}_{}'.format(self.name,self.ID)
        return s

    def add_pokemon(self,pokemon,screen=None):
        pokemon=Pokemon.get_pokemon(pokemon)
        if screen:
            def y_cmd(*a,s=screen,self=self,p=pokemon):
                p.set_nickname(s)
                yield 'done'
            def n_cmd(*a):
                yield 'done'          
            screen.create_message(
                'Would you like to give a nickname to {}?'.format(pokemon.name),YN=((y_cmd,),(n_cmd,),None)
                )
        flag=self.pokedex.has_pokemon(pokemon)
        if len(self.pokemon)==0 and screen:
            screen.menu=None
        if len(self.pokemon)<self.party_size:
            self.pokemon.append(pokemon)
        else:
            if screen:
                screen.create_message('{} was sent to the PC')
            if not self.pokedex is None:
                self.pokedex.save(pokemon)
                
##        print(self.pokemon)
        return flag

    def id_to_pokemon(self,pid):
        pid=os.path.splitext(os.path.basename(pid))[0].split('_')
        if len(pid)>1:
            pid=pid[1]
        else:
            pid=pid[0]
        ret=None
        if not self.pokedex is None:
            ret=self.pokedex.retrieve(pid)
        else:
            base_dir=os.path.dirname(self.file)
            for x in os.listdir():
                try:
                    name,num=x.split('_')
                except ValueError:
                    continue
                if num==pid:
                    ret=Pokemon.from_file(os.path.join(base_dir,x))
        if ret is None:
            raise FileNotFoundError("Couldn't find pokemon with id {}".format(pid))
        return ret
    
    @property
    def image_source_base(self):
        return os.path.join(self.trainer_source,trainer_sprite_ext,self.trainer_type)
    def image_file(self,orientation=None):
        if orientation is None:
            tests=['_{}.png'.format(flag) for flag in self.flags]
            tests.reverse()
        else:
            tests=['_{}.png'.format(orientation)]
        tests.append('.png')
        ret=None
        b=self.image_source_base
        for test in tests:
            f=b+test
            if os.path.exists(f):
                ret=f
                break
        else:
            if orientation is None:
                tests=['{}.png'.format(flag) for flag in self.flags]
                tests.reverse()
            else:
                tests=['{}.png'.format(orientation)]
            tests.append('{}'.format(self.trainer_type))
            for test in tests:
                f=os.path.join(b,'{}.png'.format(orientation))
                if os.path.exists(f):
                    ret=f
                    break
            else:
                for d in os.listdir(b):
                    try:
                        e=os.path.splitext(d)[1]
                    except IndexError:
                        continue
                    if e=='.png':
                        ret=os.path.join(self.image_source_base,d)
                        break
        if ret is None:
            raise FileNotFoundError('No available .png files for image base {}'.format(self.image_source_base))
        return ret
                
    def load_pokemon(self):
        self.pokemon=[P if isinstance(P,Pokemon) else Pokemon.get_pokemon(P) for P in self.pokemon]
        return self.pokemon
    
    def deposit_pokemon(self,pokemon):
        self.pokemon.remove(pokemon)
        self.pokedex.deposit(pokemon)
    
    def retrieve_pokemon(self,pid):
        if len(self.pokemon)<self.party_size:
            self.pokemon.append(self.id_to_pokemon)
        else:
            raise ValueError('Can only hold {} pokemon at one time'.format(self.party_size))

    def __iter__(self):
        return iter(self.load_pokemon())
    
    def index(self,p):
        return self.load_pokemon().index(p)
    
    def save(self,save_pokemon='full'):
        '''Saves the pokemon and whatnot to a file

Uses the trainer's pokedex if possible'''
        with open(self.file,'w+',encoding='utf-8') as f:
            
            save_dir=os.path.dirname(self.file)# if self.pokedex is None else self.pokedex.dir
            f.write('type:{}\n'.format(self.trainer_type))
            f.write('name:{}\n'.format(self.name.strip()))
            pokemon=[]
            for x in self:
            
                
                if isinstance(x,Pokemon):
                    if save_pokemon=='tuple':
                        p=x.tuple
                    else:
                        try:
                            p="'{}'".format(os.path.splitext(os.path.basename(
                                x.save(save_dir) if self.pokedex is None else self.pokedex.save(x)
                                ))[0])
                        except:
                            tb.print_exc()
                            p=None
        
                if not p is None:
                    pokemon.append(p)
            
            if not self.pokedex is None:
                self.pokedex.save()
                
            f.write('pokemon:{}\n'.format(','.join(pokemon)))
            f.write('money:{}\n'.format( self.money) )
            f.write('inventory:{}\n'.format( tuple(self.inventory.items()) ))

        return self.file
            
    @classmethod
    def from_file(cls,source):
        cls(file=source)
    
    _prop_string='''
Name: {0.name}
Money: {0.money}
'''.strip()
    @property
    def props_string(self):
        
        p=self._prop_string.format(self)

        return p
    
    @classmethod
    def NewTrainer(cls,*args,source=None,**kwargs):
        
        top=tk.Toplevel(*args,**kwargs)
        
        top.p_grid=FormattingGrid(top,bd=3,relief='groove',rows=0,columns=2)
        top.p_grid.grid(row=0,column=0,sticky='nsew')
        top.props=('Type','Name','Pokemon','Money','Inventory')
        top.eval_props=('Pokemon','Money','Inventory')
        
        top.var_map={k:'trainer_type' if k=='Type' else k.lower() for k in top.props}
        top.string_vars={k:tk.StringVar(top) for k in top.props}
        top.trainer=cls(trainer_type='Trainer',source=source,pokedex=False)
        
        top.f_text=tk.Text(top,width=50,wrap='word',height=5)
        top.f_text.grid(row=0,column=1,sticky='nsew')
        
        for k in top.props:
            top.string_vars[k].set( str( getattr(top.trainer,top.var_map[k]) ) )
        def save_action(*a,top=top):
            for k,v in top.string_vars.items():
                v=v.get()
                if v:
                    if k in top.eval_props:
                        v=eval(v)
                    setattr(top.trainer,top.var_map[k],v)
            top.trainer.save(save_pokemon='reduced')
            top.f_text.delete('0.0','end')
            with open(top.trainer.file,encoding='utf-8') as text:
                top.f_text.insert('end',text.read())
                
        save_action()
        for name in top.props:
            v=top.string_vars[name]
            top.p_grid.AddFormat(tk.Label,text=name).gridConfig(sticky='w')
            top.p_grid.AddFormat(tk.Entry,textvariable=v).gridConfig(sticky='ew')
            v.trace('w',save_action)
        
        top.grid_rowconfigure(0,weight=1)
        top.grid_columnconfigure(1,weight=1)
        top.wait_window(top)
        
        return top.trainer
        
    def InfoFrame(self,root,a_button=a_button,b_button=b_button,**kwargs):
        
        
        frame=tk.Frame(root,**kwargs)
        frame.font=PokeFont()
        frame.top_frame=BorderedFrame(frame)
        frame.top_frame.top_frame=tk.Frame(frame.top_frame)
        frame.top_frame.top_frame.pack(fill='both',expand=True)
        Standardizer.standardize(frame.top_frame.top_frame)
        for i in range(2):
            frame.grid_rowconfigure(i,weight=1,minsize=50)
            frame.grid_columnconfigure(i,weight=1)
        img=ImageLabel(frame.top_frame.top_frame,self.image_file(),expand='preserve')
        img.bind('<Button-1>',lambda e,f=frame:f.focus_set())
        flags_border=BorderedFrame(frame)
        flags=tk.Text(flags_border,highlightthickness=0,cursor='arrow',
            height=len(self.flags),font=frame.font)
        flags.pack(fill='both',expand=True)
        for f in self.flags:
            flags.insert('end',f)
        s=self.props_string
        prop_lines=s.splitlines()
        props=tk.Text(frame.top_frame.top_frame,cursor='arrow', height=len(prop_lines),width=max([len(x) for x in prop_lines]))
        Standardizer.standardize(props)
        def break_set(e,f=frame):
            f.focus_set()
            return 'break'
        for w in (props,flags):
            w.bind('<Button-1>',break_set)
            w.bind('<B1-Motion>',break_set)
        props.insert('end',s)
        
        props.place(x=0,y=0,relheight=1,anchor='nw')
        img.place(relx=1,y=0,relheight=1,anchor='ne')
        
        frame.top_frame.place(x=0,y=0,relwidth=1,relheight=.5,anchor='nw')
        flags_border.place(x=0,rely=1,relwidth=1,relheight=.5,anchor='sw')
        
        frame.bind('<KeyPress-{}>'.format(a_button),lambda e,f=frame:f.destroy())
        frame.bind('<KeyPress-{}>'.format(b_button),lambda e,f=frame:f.destroy())
        return frame


class Pokedex:
    '''Combines Pokedex and PC storage'''
    
    def __init__(self,dir,game_source=base_game_source,ID=None):
        if ID is None:
            ID=idNo(6)
        self.source=game_source
        self.ID=ID
        self.in_game_pokemon={}#fill this from the pokemon directory
        self.seen=set()
        self.caught=set()
        self.dir=os.path.join(dir,'Pokedex_{}'.format(self.ID))
        self.pokemon={}#Should map IDs to pokemon
        self.load()
    
    @property
    def seen_file(self):
        return os.path.join(self.dir,'seenpokemon.txt')
    @property
    def seen_count(self):
        return len(self.seen)
        
    @property
    def caught_count(self):
        return len(self.caught)
    
    def prep_dir(self):
        
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
            with open(self.seen_file,'w+',encoding='utf-8') as seen:
                seen.write(str(self.seen))
                
    def save(self,obj=None):
        if obj is None or isinstance(obj,str):
            r=self.save_to_folder(obj)
        else:
            r=self.deposit(obj)
        return r
            
    def save_to_folder(self,dir=None):
        
        if dir is None:
            dir=self.dir   
        elif dir!=self.dir:
            dir=os.path.join(dir,'Pokedex_{}'.format(self.ID))
            self.dir=dir
            
#         if os.path.exists(dir): IS THIS ACTUALLY NECESSARY? CLEANER BUT DANGEROUS
#             shutil.rmtree(dir)
            
        self.prep_dir()
        for p in self.pokemon.values():
            p.save(dir)
        return dir
    
    def load(self):
        '''Loads all potential in game pokemon as well as all of the pokemon currently saved'''
        
        p_dir=os.path.join(poke_dir,self.source)
        for p in os.listdir(p_dir):
            try:
                p_name,p_num=p.split('_')
            except ValueError:
                continue
            self.in_game_pokemon[p_num]=p_name
            self.in_game_pokemon[p_name]=p_num
            self.prep_dir()
            with open(self.seen_file,encoding='utf-8') as seen:
                self.seen.update(eval(seen.read()))
            for o in os.listdir(self.dir): 
                try:
                    name,idNo=o.split('_')
                except ValueError:
                    continue
                else:
                    p=Pokemon.from_file(os.path.join(self.dir,o),source=self.source)
                    self.seen.add(p.name)
                    self.pokemon[p.idNo]=p
                    self.caught.add(p.name)
        
    def deposit(self,pokemon):
        self.pokemon[pokemon.idNo]=pokemon
        self.prep_dir()
        return pokemon.save(self.dir)
        
    def retrieve(self,pokemon_id):
        ret=None
        if pokemon_id in self.pokemon:
            ret=self.pokemon[pokemon_id]
        else:
            if os.path.exists(self.dir):
                for d in os.listdir(self.dir):
                    try:
                        b,s=os.path.splitext(os.path.basename(d))[0].split('_')
                    except ValueError:
                        tb.print_exc()
                        continue
                    if d==pokemon_id:
                        p=Pokemon.from_file(os.path.join(self.dir,d),source=self.source)
                        self.pokemon[pokemon_id]=p
                        ret=p
                        break
        if ret is None:
            raise FileNotFoundError("Couldn't find pokemon with id {} in pokedex: {}".format(pokemon_id,self.ID))

        return ret
    
    def has_pokemon(self,pokemon):
        if isinstance(pokemon,Pokemon):
            pokemon=pokemon.name
        return pokemon in self.caught
        
    def swap_pokemon(self,pokemon,p_id):
        p_new=self.retrieve[p_id]
        self.deposit(pokemon)
        return p_new
            
    def PCInterface(self,master,pokemon):
        pass
    
    def MapInterface(self,master,pokemon):
        
        map_frame=BorderedFrame(master)
    
    def __str__(self):
        if isinstance(self.ID,int):
            s=''
        else:
            s='Pokedex_{}'.format(self.ID)
        return s

class Inventory:
    '''Just an ordered dict with incrementation and decrementation'''
    def __init__(self,iterable=()):
        self.__dict=dict(iterable)
        self.__list=list(x for x in iterable) if isinstance(iterable,dict) else list(x[0] for x in iterable)
    
    def add(self,item):
        if item in self.dict:
            self.__dict[item]+=1
        else:
            self.__list.append(item)
            self.__dict[item]=1
    
    def remove(self,item,used=1):
        q=self.__dict[item]
        q-=used if isinstance(used,int) else 0
        if q>0:
            self.__dict[item]=q
        else:
            self.drop(item)
    
    def drop(self,item):
        del self.__dict[item]
        self.__list.remove(item)
    
    def __getitem__(self,item):
        return self.__dict[item]
        
    def __contains__(self,item):
        return item in self.__dict
    
    def __iter__(self):
        return iter(self.__list)
    
    def items(self):
        return ((key,self[key]) for key in self)
         
    def values(self):
        return (self[key] for key in self)
    
    def keys(self):
        return iter(self)
        