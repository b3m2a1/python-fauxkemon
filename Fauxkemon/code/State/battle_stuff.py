from .base_modules import *
from .version_data import *
from .file_sources import *

_game_specifics_modules={}
def GameSpecifics(game_version=None,game_modules=_game_specifics_modules):
    if game_version is None:
        game_version=base_game_source
    try:
        m=game_modules[game_version]
    except KeyError:
        data_src=getdir('game_specifics')
        m=Loader.load_module(data_src,execution_dict={'game_source':game_version})
        game_modules[game_version]=m
    return m

def CatchAlgorithm(directory_extension=None):
    if directory_extension is None:
        directory_extension=base_game_source
    specifics=GameSpecifics(directory_extension)
    return specifics.catch_algorithm    
    
def EffectCalculator(directory_extension=None):
    if directory_extension is None:
        directory_extension=base_game_source
    specifics=GameSpecifics(directory_extension)
    return specifics.EFC

def BattleEffect(name,directory_extension=None):
    if directory_extension is None:
        directory_extension=base_game_source
    specifics=GameSpecifics(directory_extension)
    return specifics.battle_statuses[name]


class LibraryEffect:
    
    def __init__(self,effect_name,arg=None,apply_to_user=False,hit_rate=1.0):
        effects=getdir('battle_effects')
        self.effect_file=os.path.join(effects,effect_name+'.py')
        if os.path.exists(self.effect_file):
            self.effect_module=Loader.load_module(self.effect_file)
            self.effect=self.effect_module.effect
        else:
            self.effect=self.print_effect
        self.hit_rate=hit_rate
        self.apply_to_user=apply_to_user
        self.arg=arg
    def print_effect(self,*a,**k):
        print(os.path.basename(self.effect_file))
    def __call__(self,attackORitem,target,user,damage,arg=None):
        attempt=random.random()
        if attempt<self.hit_rate:
            if arg is None:
                arg=self.arg
            if self.apply_to_user:
                target,user=(user,target)
            return self.effect(attackORitem,target,user,damage,arg)

battle_stats=('attack','defense','special_attack','special_defense','speed','evade','accuracy')
user_re=re.compile('user\[.+\]')
hp_re=re.compile('hp[+\-*]\d+')
stat_res={k:re.compile('{}[+\-*]\d+'.format(k)) for k in battle_stats}
def process_effect(effect_string):
    '''Processes a string into effect

hp[+-*][q] turns into a recover(A,P,E,D,([+-*],q)) call
[stat][+-*][q] turns inot a stat_change(A,P,E,0,([+-*],q)) call

everything else is turned into an effect library call if possible'''

    battle_statuses=GameSpecifics().battle_statuses
    
    effect_list=[]
    
    
    hit_rate=effect_string.rsplit('@',1)
    if len(hit_rate)==2:
        effect_string,hit_rate=hit_rate
        hit_rate=float(hit_rate)
    else:
        hit_rate=1.0      
    effects=effect_string.split('&')
    for eff in effects:
        apply_to_user=False
        if user_re.match(eff):
            apply_to_user=True
            eff=eff.split('user[',1)[1][:-1]
        if hp_re.match(eff):
            eff=eff.strip('hp')
            if '+' in eff:
                arg=-int(eff.strip('+'))
            elif '-' in eff:
                arg=-int(eff.strip('-'))
            elif '*' in eff:
                arg=float(eff.strip('*'))
            effect_list.append(LibraryEffect('change_hp',arg,apply_to_user,hit_rate))
            del arg  
        else:
            for k in battle_stats:
                if stat_res[k].match(eff):
                    eff=eff.strip(k)
                    if '*' in eff:
                        arg=(k,float(eff.strip('*')))
                    elif '+' in eff:
                        arg=(k,int(eff.strip('+')))
                    elif '-' in eff:
                        arg=(k,-int(eff.strip('-')))
                    effect_list.append(LibraryEffect('stat_change',arg,apply_to_user,hit_rate))
                    break
            else:
                if eff in battle_statuses:
                    effect_list.append(LibraryEffect('status_apply',eff,apply_to_user,hit_rate))
                else:
                    bits=eff.split('[',1)
                    if len(bits)==1:
                        arg=None
                    else:
                        arg=eval(bits[1][:-1])
                    effect_list.append(LibraryEffect(bits[0],arg,apply_to_user,hit_rate))                 
    
    def effect(attackORitem,player,enemy,damage,arg=None,effect_list=effect_list):
        damage=0;messages=[];animations=[]
        for effect in effect_list:
            r=effect(attackORitem,player,enemy,damage,arg)
            if not r is None:
                d,m,a=r
                if isinstance(d,str):
                    damage=d
                else:
                    damage+=d
                messages+=m;animations+=a
        if damage==0 and len(messages)==0:
            res=None
        else:
            res=(damage,messages,animations)
        return res
    
    return effect