from Fauxkemon.code.State import *
from Fauxkemon.code.DataTypes.Attack import Attack

pokemon=getdir('pokemon')
chars=getdir('characters')
        
class Pokemon:            
    '''A Pokemon datatype

Stores EVs, IVs stats, base_stats, properties, and moves
'''
    def __init__(self,
                nameORnumber=None,
                 level=None,
                 idKey=None,
                 trainer=None,
                 source=base_game_source,
                 EVs=None,
                 IVs=None,
                 status=None,
                 EXP=0):
        self.trainer=trainer
        
        self.file=None
        self.src=source
        source=os.path.join(pokemon,source)
        self.idNo= idNo(5) if idKey is None else idKey
        self.catch_rate=128

        try:
            id=str(int(nameORnumber))
            ind=0
        except:
            id=nameORnumber
            ind=1
        for x in os.listdir(source):
            y=os.path.join(source,x)
            if os.path.isdir(y):
                bits=x.split('_')
                test=bits[ind]
                if id==test:
                    self.name=bits[1]
                    self.number=int(bits[0])
                    self.nickname=None
                    break
        else:
            raise Exception('Pokemon {} not found'.format(nameORnumber))

        if level is None:
            level=5

        self.level=level
        self.moves=[None]*4
        self.__status=status if not status is None else [None,None,None]
        self.__EXP=EXP
        self.dir=os.path.join(source,x)
        self.load_properties()
        self.health=self.stats['HP']
        types=self.type
        t=types[0]
        self.icon_dir=os.path.join(chars,self.src,'{} Icon'.format(string.capwords(t)))
        self.image=ImageWrapper(os.path.join(self.dir,'front.png'))
        self.icon=self.image.copy()
        self.icon.scale(.75)
        self.icon.set_base_image()
        self.icon.scale(.5)
        
        self.original_trainer=None

        if not EVs is None:
            if not isinstance(EVs,dict):
                EVs={e:v for e,v in EVs}
            self.__EVs.update(EVs)
        if not IVs is None:
            self.__IVs=IVs
    @property
    def tuple(self):
        return (self.name,self.level)
    def restore(self,arg='full'):
        if arg in ('full','all'):
            arg=(('hp','all'),('pp','all'),('status','all'))
        restore_messages=[None,None,None]
        for a in arg:
            if a[0]=='hp':
                restore_messages[0]=self.hp_restore(*a[1:])
            elif a[0]=='pp':
                restore_messages[1]=self.pp_restore(*a[1:])
            elif a[0]=='status':
                restore_messages[2]=self.status_restore(*a[1:])
        return restore_messages
        
    def hp_restore(self,quantity='all'):
        
        m='No effect...'
        if quantity=='all':
            self.ChangeHealth(self.max_health)
            m='Recovered all HP'
        elif isintance(quantity,float):
            self.ChangeHealth(self.max_health*quantity)
            m='Recovered HP'
        else:
            self.ChangeHealth(quantity)
            m='Recovered {} HP'.format(quantity)
        return m
    
    def pp_restore(self,moves='all',quantity='all'):
        
        if moves=='all':
            moves={m.name if not m is None else m for m in self.moves}
        m='No effect...'
        for mv in self.moves:
            if not mv is None and mv.name in moves:
                if quantity=='all':
                    m='Restored all pp'
                    q=mv.max_pp
                else:
                    q=int(quantity)
                    if len(moves)==1:
                        m='Restored {} pp'.format(q)
                mv.pp+=q
        return m      
    
    def status_restore(self,condition='all'):
        m='No effect...'
        if condition=='all':
            condition=(0,1,2)
        
        s=self.__status
        if isinstance(condition,str):
            try:
                i=s.index(condition)
            except IndexError:
                m='It would have no effect'
            else:
                self.__status[i]=None
        else:
            for i in condition:
                self.__status[i]=None
        
    def status_set(self,status='OK'):
        if status=='OK':
            status=(None,None,None)
        elif isinstance(status,str):
            status=(status,None,None)
        for i in range(3):
            self.__status[i]=status[i]   
    
    def remove_status(self,status):
        for i,s in enumerate(self.__status):
            if s is status:
                self.__status[i]=None    
                
    def show(self,root=None):
        '''Shows the status entry

Shows the status entry in the toplevel'''
        t=tk.Toplevel(root)
        p=self.stats_entry(t)
        p.pack()
        return t
        
    def register_to(self,trainer):
        self.original_trainer = trainer.ID
        
    def save(self,directory):
        '''saves the pokemon to a file for later loading'''

        if self.file is None:
            self.file=os.path.join(directory,'{0.name}_{0.idNo}.txt'.format(self))
##        print(self.file)
        with open(self.file,'w+',encoding='utf-8') as f:
            f.write('{0.name}|{0.level}|{0.idNo}\n'.format(self))
            f.write('#ATTRIBUTES#\n')
            for prop in ('nickname','original_trainer'):
                f.write('{}: {}\n'.format(prop,getattr(self,prop)))
            f.write('#PROPERTIES#\n')
            for prop in self.props:
                f.write('{}: {}\n'.format(prop,self.props[prop]))
            f.write('#STATS#\n')
            for stat in self.stats:
                f.write('{}: {}\n'.format(stat,self.stats[stat]))
            f.write('#STATUS#\n')
            f.write('status: {}\n'.format(self.__status))
            f.write('#ATTACKS#\n')
            for a in self.moves:
                if not a is None:
                    f.write('{0.save_string}\n'.format(a))
        return self.file
        
    @classmethod
    def from_file(cls,file,**kwargs):
        
        with open(file,encoding='utf-8') as pk_d:
            
            pokemon,level,idNo=next(pk_d).strip().split('|')
            level=int(level)
            kwargs['level']=level;kwargs['idKey']=idNo
            self=None
            attack_i=0
            
            flag=None
            IVs={}
            EVs={}
            kwargs['EVs']=EVs
            kwargs['IVs']=IVs
            for line in pk_d:
                line=line.strip()
                if line:

                    if line=='#ATTRIBUTES#':
                        flag='attributes'
                    elif line=='#PROPERTIES#':
                        flag='props'
                    elif line=='#STATS#':
                        flag='stats'
                    elif line=='#STATUS#':
                        flag='status'
                    elif line=='#ATTACKS#':
                        flag='attacks'
                        moves=[None]*4
                    elif line=='EVs':
                        flag='evs'
                    elif line=='IVs':
                        flag='ivs'
                    elif line[0]=='#':
                        flag=None
                    else:
                        if self is None and not flag in ('evs','ivs',None):
                            self=cls(pokemon,**kwargs)
                        if flag=='attributes':
                            attr,val=line.split(':',1)
                            setattr(self,attr,val)
                        elif flag=='props':
                            attr,val=line.split(':',1)
                            self.props[attr]=val
                        elif flag=='status':
                            attr,val=line.split(':',1)
                            if val.strip()!='OK':
                                self.status_set(eval(val))
                        elif flag=='stats':
                            attr,val=line.split(':',1)
                            self.stats[attr]=int(val)
                        elif flag=='attacks':
                            a=Attack.from_string(line)
                            self.moves[attack_i]=a
                            attack_i+=1
                        elif flag=='ivs':
                            attr,val=line.split(':')
                            val=int(val)%32
                            IVs[attr]=val
                        elif flag=='evs':
                            attr,val=line.split(':')
                            val=int(val)%32
                            EVs[attr]=val
                        
        self.health=self.stats['HP']
        return self
                
    def edit(self):
        '''Opens the base file for editing'''
        from GeneralTools.PlatformIndependent import open_file
        open_file(self.dir)

    def catch_try(self,item,src=None):
        '''Returns whether the pokemon is caught or not

Loads the appropriate catch algorithm for the game specified and applies it to the pokemon with the item used'''
        if self.original_trainer is None:
            if src is None:
                src=self.src
            alg=CatchAlgorithm(src)
            res=alg(self,item) 
        else:
            res=(False,'This Pokemon already has a trainer.')
        return         
        
    def load_properties(self):
        '''Loads the pokemon's base properties'''
        keys={'#PROPERTIES':'props','#BASESTATS':'base_stats'}
        f=os.path.join(self.dir,'props.txt')
        moveskey='#MOVELIST'
        def getmoves(file):
            ind=0
            for line in file:
                line=line.strip()
                if line:
                    try:
                        level,name=line.split(' ',1)
                    except ValueError:
                        print(self.dir,line)
                        raise
                    try:
                        level=int(level)
                    except ValueError:
                        print(self.dir)
                        raise
                    if level>self.level:
                        for line in file:
                            if '#'==line[0]:
                                break
                        break
                    else:
                        self.moves[ind]=Attack(name,source=self.src)
                        ind=(ind+1)%4
                    
        self.props={}
        self.base_stats={}
        to=self.props
        with open(f,encoding='utf-8') as props:
            for line in props:
                if moveskey in line:
                    getmoves(props)
                    break
                for k in keys:
                    if k==line[:len(k)]:
                        mode=keys[k]
                        to=getattr(self,mode)
                        break
                else:
                    line=line.strip()
                    if line:
                        k,v=line.strip().split(':')
                        to[k]=v

        for key,item in self.base_stats.items():
            try:
                item=int(item)
            except ValueError:
                print(self.dir)
                raise
            self.base_stats[key]=item
        for key,item in self.props.items():
            try:
                item=float(item)
            except ValueError:
                continue
            self.props[key]=item
            
        iv_ch=list(range(1,33))
        self.__EVs={k:0 for k in self.base_stats}
        self.__IVs={k:random.choice(iv_ch) for k in self.base_stats}
        self.calculate_stats()

    def calculate_stats(self):
        L=self.level
##        random=lambda v:random.gaussian(v,3)
        self.stats={}
        IVs=self.__IVs
        EVs=self.__EVs
        hp_floor=L+10
        stat_floor=5
        for k,v in self.base_stats.items():
            std=(((v+IVs[k])*2+math.sqrt(EVs[k])/4)*L/100)
            if k=='HP':
                v=std+hp_floor
            else:
                v=std+stat_floor
            self.stats[k]=int(v)

    def enter_battle(self,battle,key=None):
        self.battle_stats={x:[v,0] for x,v in self.stats.items()}
        self.battle_stats['accuracy']=[100,0]
        self.battle_stats['evade']=[0,0]
        s=self.__status.copy();s.append(None)
        self.battle_stats['status']=s
        self.battle_moves=self.moves
        self.battle_info=[battle,key]
        
    def apply_statuses(self,mode='before'):
        '''Applies all the statuses that go before or after and yields their results'''
        status=self.status 
        if not status=='OK':
            for s in status:
                if not s is None and (s.before_attack if mode=='before' else not s.before_attack):
                    s_tup=s.use(self)
                    yield ('status',s_tup)
                    
    def use_attack(self,attack,enemy,override=False):
        '''Uses the specified attack, either by name or by override

Makes a generator, so that after each attack step messages and things can be applied'''
        
        continue_key=True
        for t in self.apply_statuses('before'):
            continue_key=continue_key and t[1][0]=='continue'
            print(t[1][0])
            yield t
        
        if continue_key:
            yield ((0,['{} used {}'.format(self.name,attack.name)],[]),None)
            if isinstance(attack,Attack):
                if override:
                    for t_pair in attack.use(self,enemy):
                        yield t_pair
                attack=attack.name
            else:
                for x in self.moves:
                    if x is None:
                        continue
                    elif x.name==attack:
        ##                print(x.name)
                        self.last_attack=x
                        for t_pair in x.use(self,enemy):
                            yield t_pair
                        break
                else:
                    yield (None,None)
                
        for t in self.apply_statuses('after'):
            yield t 
    
    def disable(self):
        try:
            self.last_attack.disable()
        except AttributeError:
            pass
        
    def skip_turn(self):
        battle,key=self.battle_info
        i=0
        for a in battle.chosen_actions:
            if key in a:
                battle.chosen_actions[i]=(key,'pass')
            i+=1
    
    def take_damage(self,dmg):
        self.ChangeHealth(-dmg)
        
    def take_effect(self,attack,other,damage):
        return attack.apply_effect(self,other,damage)
    
    @staticmethod
    def call_effect(effect_string,target,user,damage,arg=None):
        return process_effect(effect_string)(target,user,damage,arg)

    def exit_battle(self):
        self.battle=None
        status=self.battle_stats['status']
        self.__status=self.battle_stats['status'][:2]
        self.battle_stats=None
        
    def stats_entry(self,root):
        return StatsEntry(root,self)

    @property
    def max_health(self):
        return self.stats['HP']

    @max_health.setter
    def max_health(self,new):
        self.stats['HP']=new
        
    @property           
    def KOed(self):
        r=self.health==0
        if r:
            self.__status[0]='KO'
        return r

    @property
    def status(self):
        for v in self.__status:
            if v is not None:
                status=list(self.__status)
                break
        else:
            status='OK'
        return status
    
    @property
    def type(self):
        t=self.props['type']
        return tuple(t.split(','))
    
    def ChangeHealth(self,quantity,mode='inc'):
        if mode=='inc':
            self.health+=quantity
        elif mode=='mul':
            self.health*=quantity
        else:
            self.health=quantity
                
        if self.health<0:
            self.health=0
            
        elif self.health>=self.max_health:
            self.health=self.max_health

    @property
    def EXP(self):
        return self.__EXP

    @EXP.setter
    def EXP(self,exp):
        diff=exp-self.next_level
        if diff>0:
            self.level_up()
            self.__EXP=diff
        else:
            self.__EXP=exp
            
    @property
    def next_level(self):
        return 10*self.level
    
    @property
    def experience_yield(self):
        return self.level
    
    def level_up(self):

        self.level+=1
        for s in self.stats:
            ##INSERT REAL LEVEL UP CODE
            ##CHECK LEARN MOVES
            amt=(1+random.random()/(10+self.level))
            print('{} grew by {} percent'.format(s,int((amt-1)*100)))
            self.stats[s]=int(self.stats[s]*amt)         
        self.__EXP=0
    
    @classmethod
    def get_pokemon(cls,pokemon,**kw):
                
        if not isinstance(pokemon,cls):
            if isinstance(pokemon,str):
                name=pokemon
            elif len(pokemon)>1:
                name,level=pokemon
                kw['level']=level
            else:
                name=pokemon[0]
            pokemon=Pokemon(name,**kw)
            
        return pokemon
    
    def set_nickname(self,screen):
        pass
    
    def __repr__(self):
        s='{0.name}{1}_{0.idNo}'.format(self,'' if self.nickname is None else ('_'+self.nickname))
        return s

class PokedexFrame(UniformityFrame):
    
    def __init__(self,root,pokemon):
    
        self.pokemon=pokemon
        self.image=ImageLabel(self,pokemon.image,expand='preserve')
        self.message_test=None
        self.p_height='None' if not 'height' in pokemon.props else pokemon.props['height']
        self.p_weight='None' if not 'weight' in pokemon.props else pokemon.props['weight']
        self.p_tagline='None' if not 'description' in pokemon.props else pokemon.props['description']
        props=[
            (self.pokemon.name,),
            (self.pokemon.number,),
            (self.p_tagline,),
            ('Height',self.p_height),
            ('Weight',self.p_weight)]
        self.props_text=tk.Text(self,
            height=len(props))
        Standardizer.standardize(self.props_text.config)
        self.props_test['relief']='groove'
        w=0
        for p in props:
            if len(p)>1:
                text='{0[0]}: {0[1]}'.format(p)
            else:
                text=p
            w=max(w,len(text))
            self.props_text.insert('end',text)
        self.props_text.config(width=w+5)
        
        self.image.place(x=0,rely=.25,relwidth=.25,relheight=.5,anchor='sw')
        self.props_text.place(relx=1,rely=0,relheight=1,anchor='ne')
    
class StatsEntry(UniformityFrame):
    block_props=[('ATTACK','attack'),('DEFENSE','defense'),
                 ('SP. ATTK','special_attack'),('SP. DEF','special_defense'),
                 ('SPEED','speed')]
    base_dimensions=(300,300)
    def __init__(self,root,pokemon_instance):
        w=root.winfo_width()
        h=root.winfo_height()
        super().__init__(root,width=w,height=h,bg='black',bd=2)
        self.pokemon=P=pokemon_instance
        self.l_flag=False
        self.sub_frame=tk.Frame(self)
        self.font=Standardizer.config_map['frame']['font']
        self.bind('<Configure>',lambda e:(setattr(self,'l_flag',False),
        self.sub_frame.destroy(),self.load()))
        self.bind(root.a_button,self.switch_modes)
        self.mode=0
        self.pack_propagate(False)
        Standardizer.standardize_recursive(self)
        

    def load(self,event=None):

        top_h=self.top_h=.35
        top_w=self.top_w=.4
        bottom_h=self.bottom_h=1-top_h
        bottom_w=self.bottom_w=.5
        self.sub_frame=tk.Frame(self,width=self.winfo_width(),height=self.winfo_height())
        from string import capwords
        P=pokemon_instance=self.pokemon
        root=self.master
        w=root.winfo_width()
        h=root.winfo_height()
        bw,bh=self.base_dimensions
        w_scale=w/bw
        h_scale=h/bh
        self.scale=(w_scale,h_scale)
        
        #Image
        self.imPane=UniformityFrame(self.sub_frame)
#         x,y=P.image.dimensions
#         self.font.config(size=int(12*h_scale))
#         extra=5+self.font.measure('ascent')
#         scale_factor=((top_h*h)-extra)/y
#         P.image.scale(scale_factor)
        self.image=ImageLabel(self.imPane,P.image,expand='preserve')
        self.image.bind('<Double-Button-1>',lambda e,p=P:P.edit())
        self.no=tk.Label(self.imPane,text='No. {}'.format(P.number),font=self.font)
        self.no.pack(side='bottom',anchor='sw')
        self.image.pack(side='bottom',fill='both',anchor='sw')
        self.imPane.place(x=0,y=0,relwidth=top_w, relheight=top_h,anchor='nw')#grid(row=0,column=0,sticky='sw')
        #Health block
        self.status_canvas=tk.Canvas(self.sub_frame,bg='black')
        self.type_health=tk.Frame(self.status_canvas)
        
        self.p_name=test=tk.Label(self.type_health,text=P.name,font=self.font)
        self.p_name.pack(anchor='nw')
        self.type_health.prp=F=UniformityFrame(self.type_health)

        l=tk.Label(F,text=':L{}'.format(P.level),font=self.font)
        H=tk.Label(F,text='HP:',font=self.font)
        F.hp_label=H
        val,max_h=(P.health,P.max_health)
        F.hb=B=self.health_bar(F,val,max_h)
        F.hr=n=tk.Label(F,
                        text='{!s:>3}/{!s:>3}'.format(val,max_h),
                        font=self.font)
        exp,nex_p=(P.EXP,P.next_level)
        self.type_health.exp=ex=tk.Label(self.type_health,
                       text='EXP: {} NEXT LEVEL: {}'.format(exp,nex_p),
                        font=self.font
                       )
        l.grid(row=0,column=0,columnspan=2)
        H.grid(row=1,column=0,sticky='e');B.grid(row=1,column=1,sticky='w')
        n.grid(row=2,column=0,columnspan=2);
        B.b.update()
        F.pack(expand=True)
        status=P.status
        if not status in ('OK','K.O'):
            for s in status:
                if not s is None:
                    if not s.battle_only:
                        status=s._short_key
                        break
            else:
                status='OK'
        self.type_health.status=S=tk.Label(self.type_health, text='STATUS/{}'.format(status),font=self.font)
        S.pack(anchor='sw',pady=1)
#         ex.pack(anchor='sw',pady=1)
        self.status_canvas.place(relx=top_w,y=0,relheight=top_h,relwidth=(1-top_w),anchor='nw')
        self.type_health.place(relheight=1,relwidth=1,width=-5,height=-5)
##        cw=self.status_canvas.winfo_width()
##        ch=self.status_canvas.winfo_height()
##        self.status_canvas.create_line(cw,0,cw,ch,0,ch,arrow='last',width=3)
        #Stats
        self.bd_frame=tk.Frame(self.sub_frame,bd=3,relief='ridge',bg='black')
        self.stats=tk.Frame(self.bd_frame)
        self.stats.pack(fill='both',expand=True)
        #Adds the bars to the stats frame
        i=0
        for p,k in self.block_props:
            self.prop_bar(p,P.stats[k]).grid(row=i)
            self.stats.grid_rowconfigure(i,weight=1)
            i+=1
        self.bd_frame.place(rely=top_h,relwidth=bottom_w,relheight=(1-top_h),anchor='nw')
        #That miscellaneous other shit
        self.misc_canvas=tk.Canvas(self.sub_frame,bg='black')
        self.misc=tk.Frame(self.misc_canvas)
        element=P.props['type']
            #Types
        try:
            e1,e2=element.split(',')
            e1,e2=(capwords(x) for x in (e1,e2))
            a=self.misc_bar('Type1',e1)
            b=self.misc_bar('Type2',e2)
            a.pack(side='top',anchor='w')
            b.pack(side='top',anchor='w')
        except:
            l=self.misc_bar('Type',capwords(element))
            l.pack(side='top',anchor='w')
            #IdNo
        l=self.misc_bar('IDNo.',P.idNo)
        l.pack(side='top',anchor='w')
            #OT
        OT=str(P.original_trainer)
        l=self.misc_bar('O.T',OT)
        l.pack(side='top',anchor='w')
        self.misc_canvas.place(relx=bottom_w,relwidth=(1-bottom_w),
                        rely=top_h,relheight=(1-top_h),anchor='nw')
        self.misc.place(relwidth=1,relheight=1,width=-5,height=-5)
##        cw=self.misc_canvas.winfo_width()
##        ch=self.misc_canvas.winfo_height()
##        self.misc_canvas.create_line(cw,0,cw,ch,0,ch,arrow='last',width=3)
        #and put it all together
        self.sub_frame.pack(fill='both',expand=True)
        Standardizer.standardize_recursive(self.sub_frame,'frame',standardize=tk.Label)
        self.bind('<Button-1>',lambda e:self.focus_set(),to_all=True)
        
    def misc_bar(self,n,v):
        w=self.winfo_width();h=self.winfo_height()
        w=int((1-self.bottom_w)*w);h=int(self.bottom_h/4*h)
        f=tk.Frame(self.misc,width=w,height=h)
        l=tk.Label(f,text=n+'/',font=self.font)
        v=tk.Label(f,text=str(v),font=self.font)
        l.place(x=0,y=0,anchor='nw')
        v.place(x=int(w/10),rely=1,anchor='sw')
        
        return f
    
    def prop_bar(self,name,value):
        w_scale,h_scale=self.scale
        w=self.winfo_width();h=self.winfo_height()
        w=int(.9*self.bottom_w*w);h=int(self.bottom_h/6*h)
        
        f=tk.Frame(self.stats,width=w,height=h)
        l=tk.Label(f,text=name,font=self.font)
        v=tk.Label(f,text=str(value),font=self.font)
        l.place(x=5,y=0,anchor='nw')
        v.place(relx=1,rely=1,anchor='se')
        
        return f

    def health_bar(self,root,cur,total):
        w_scale,h_scale=self.scale
        w=self.winfo_width();h=self.winfo_height()
        w=int((1-self.top_w)*w)-self.font.measure('HP:')-10
        h=int(self.top_h/5*h)
        F=tk.Frame(root,width=w,height=h)
        B=FillBar(F,cur,total,width=w,height=h,color='green4',mode='pill')
        F.pack_propagate(False)
        B.pack(fill='both',expand=True)
        F.b=B
        return F

    def switch_modes(self,event=None):
        from string import capwords
        if self.mode==1:
            self.destroy()
        else:
            self.mode=1
            self.type_health.status.pack_forget()
            self.type_health.exp.pack(anchor='sw',pady=1)
            w_scale,h_scale=self.scale
            self.bd_frame.place_forget();self.misc_canvas.place_forget()
            self.attack_frame=tk.Frame(self.sub_frame,bd=3,relief='ridge')
            f=self.attack_frame
            P=self.pokemon
            i=0
            for A in P.moves:
                if not A is None:
                    F=tk.Frame(f)
                    name_label=tk.Label(F,text=A.name,font=self.font)
                    pp_label=tk.Label(F,text='{: >2}/{: >2}'.format(A.pp,A.max_pp),font=self.font)
##                    f.grid_rowconfigure(i,weight=1)
                    type_label=tk.Label(F,text=capwords(A.type),font=self.font)
                    name_label.place(x=0,y=0,anchor='nw')
                    type_label.place(relx=.1,rely=1,anchor='sw')
                    pp_label.place(relx=1,rely=1,anchor='se')
                else:
                    F=tk.Label(f,text='-',font=self.font)
                F.place(rely=i,relheight=.25,relwidth=1)
                i+=.25
##            f.grid_columnconfigure(0,weight=1)
            Standardizer.standardize_recursive(f)
            Standardizer.standardize(f,'border')
            f.place(x=0,rely=self.top_h,relwidth=1,relheight=(1-self.top_h),anchor='nw')


class FakePokemon:
    def __init__(self,image_file=None):
        #set properties so that this can be used as an image in battles without pokemon
        pass
    
    
