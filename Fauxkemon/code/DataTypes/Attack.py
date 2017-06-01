from Fauxkemon.code.State import *
##from Fauxkemon.code.effect_calculator import *

attacks=getdir('attacks')

class Attack:
    effect_calculator=None
    keys=('type','mode','attack','effect','hit_rate','hits','priority','pp')
    def __init__(self,name,dir=None,source=None,pp=None):
        name=name.strip()
        if dir is None:
            dir=attacks
        if source is None:
            source=base_game_source
            
        dir=os.path.join(dir,source)
        
        self.effect_calculator=EffectCalculator(source)
        self.map_effect=None
        self.dir=dir
        self.__dict={}
        self.src=source
        self.file=os.path.join(dir,name+'.txt')
        if not os.path.exists(self.file):
            c=name.count(' ')
            if c==0:
                i=1
                for x in name[1:]:
                    if x.isupper():
                        new=name[:i]+' '+name[i:]
                        self.file=os.path.join(dir,new+'.txt')
                        break
                    i+=1
        if not os.path.exists(self.file):
            new=name.replace(' ','')
            self.file=os.path.join(dir,new+'.txt')
        if not os.path.exists(self.file):
            new=name.replace('-',' ')
            self.file=os.path.join(dir,new+'.txt')
        self.name=name
        self.load_props()
        if not pp is None:
            self.__dict['pp']=pp

    @property
    def attack(self):
        a=self.__dict['attack']
        try:
            a=float(a)
        except ValueError:
            a=0
        return a
    @property
    def map_usable(self):
        return (not self.map_effect is None)
    @property
    def hit_rate(self):
        h=self.__dict['hit_rate']
        try:
            h=float(h)
        except TypeError:
            h=1.0
        return h
    @property
    def type(self):
        return self.__dict['type']
    @property
    def effect(self):
        e=self.__dict['effect']
        return e
    @property
    def hits(self):
        try:
            r=self.__dict['hits']
        except KeyError:
            r=1
        else:
            try:
                r=int(r)
            except ValueError:
                r=[int(x) for x in r.split('-')]
                r=random.choice(range(*r))
        return r
    @property
    def pp(self):
        pp=int(self.__dict['pp'])
        return pp
    @pp.setter
    def pp(self,new):
        
        self.__dict['pp']=min(new,self.max_pp)
    @property
    def priority(self):
        p=self.__dict['priority']
        try:
            p=int(p)
        except TypeError:
            p=0
        return p
    @property
    def mode(self):
        return self.__dict['mode']
    
    def use(self,user,target):
        '''Applies the attack to target, assuming that user used it

Returns (damage,messages,animation,continue_key,effect_tuple)
where:
    damage is the damage done by the attack
    messages is the list of messages to be set by the battle screen
    animation is the battle animation to call
    continue_key is True if there are more steps to the attack, else False
    effect_tuple is the effect_tuple obtained from applying the attack effect
'''
        EFC=self.effect_calculator
        self.pp+=-1
        if self.mode=='special':
            defense=target.battle_stats['special_defense'][0]
            attack=user.battle_stats['special_attack'][0]
        else:
            defense=target.battle_stats['defense'][0]
            attack=user.battle_stats['attack'][0]
        
        h=self.hit_rate-max(target.battle_stats['evade'][0]-user.battle_stats['accuracy'][0],0)
        hits=self.hits
        hit_num=1
        def step(hit_num,self=self,target=target,user=user):
            attempt=random.random()
            if attempt<h:
                power=self.attack
                t=self.type
                o=target.type
                m=user.type
                if power>0:
                    if t in m:
                        power=power*1.5
                    mul=EFC[t,o]
                else:
                    mul=1
                messages=[]
                if mul==0:
                    dmg=0
                    if power>0:
                        messages=[get_message('doesnt_effect').format(target.name)]
                        continue_key=False
                        effect_tuple=None
                    else:
                        effect_tuple=self.apply_effect(user,target,dmg)                
                else:
                    if mul==.5:
                        messages=[get_message('not_very_effective')]
                    elif mul==2:
                        messages=[get_message('super_effective')]
                    power=power/2
                    att_ratio=(attack/defense)
                    dmg=int(power*att_ratio*mul)
                    effect_tuple=self.apply_effect(user,target,dmg)
                    if power==0:
                        if effect_tuple is None:
                            messages=[get_message('no_effect')]
                    if hit_num<hits:
                        continue_key=True 
                    else:
                        continue_key=False    
                                   
            else:
                dmg=0
                messages=[get_message('missed')]
                effect_tuple=None
                continue_key=False
            animation='shake_vertical'
            return ((dmg,messages,animation,continue_key),effect_tuple)          
        
        continue_flag=True
        while continue_flag:
            dmg_tup,eff_tup=step(hit_num)
            hit_num+=1
            continue_flag=dmg_tup[-1]
            dmg_tup=dmg_tup[:-1]
            yield (dmg_tup,eff_tup)
        if hit_num>2:
            yield ((0,['Hit {} times!'.format(hit_num-1)],[],False),None)
    
#     CantParse=lambda eff:ValueError("Couldn't parse effect: {}".format(eff))
    def apply_effect(self,user,target,base_dmg=0):
        '''This simply applies the loaded effect of the attack to the user and enemy specified'''
        out=self.effect(self,target,user,base_dmg)
        return out
        
    def copy(self):
        return super().copy()

    def load_props(self):
        keys=set(self.keys)
        with open(self.file,encoding='utf-8') as source:
            for line in source:
                if not '#'==line[0]:
                    bits=line.split(':',1)
                    if bits[0] in keys:
                        val=bits[1].strip()
                        if val=='-':
                            val=0
                        self.__dict[bits[0]]=val
                        keys.remove(bits[0])
#                     else:
#                         self.__effects[bits[0]]={bits[1].strip()}
                        
        self.__dict['effect']=process_effect(self.__dict['effect'])
        self.max_pp=self.pp

    def edit(self):
        from GeneralTools.PlatformIndependent import open_file
        open_file(self.file)
        
    def __repr__(self):
        return '{} w/ {} PP'.format(self.name,self.pp)

    @property
    def save_string(self):
        return '{0.name}_{0.pp}_{0.max_pp}'.format(self)
    @classmethod
    def from_string(cls,string):
        name,pp,max_pp=string.split('_')
        pp=int(pp);max_pp=int(max_pp)
        self=cls(name,pp=pp)
        self.max_pp=max_pp
        return self
