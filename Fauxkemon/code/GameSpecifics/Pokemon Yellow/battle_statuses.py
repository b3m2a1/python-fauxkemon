'''This is the module that defines all of the possible battle statuses'''

import abc,random

class Status(abc.ABC):
    _id_strings=('status',)
    _past_tense='statused at!'
    _app_string='{} was '+_past_tense
    _short_key="STS"
    _remove_string='{} was cured of status'
    _remove_chance=.5
    _p_counter={}
    _base_count=5
    battle_only=True
    before_attack=False
    @classmethod
    def apply(self,pokemon):
        self._p_counter[pokemon]=self._base_count
        return self._app_string.format(pokemon.name)
    @abc.abstractclassmethod
    def use(cls,pokemon):
        pass
    @classmethod
    def remove_try(self,pokemon):
        r=random.random()
        r_flag=False
        if r<self._remove_chance:
            r_flag=True
        elif self._p_counter[pokemon]<1:
            r_flag=True
        else:
            self._p_counter[pokemon]-=1
        if r_flag:
            self.remove(pokemon)
        return r_flag
    @classmethod
    def remove(self,pokemon):
        del self._p_counter[pokemon]
        pokemon.remove_status(self)
    
class Poison(Status):
    _p_counter={}
    _id_strings=('poison','POISON','Poison','psn','PSN')
    _past_tense='poisoned'
    _app_string='{} was '+_past_tense
    _eff_response='{} was hurt by poison'
    _short_key='PSN'
    _dmg_percent=1/16
    battle_only=False
    @classmethod
    def use(self,pokemon):
        H=pokemon.max_health
        dmg=int(H*self._dmg_percent)
        animations=[]
        messages=[self._eff_response.format(pokemon.name)]
        ret=(dmg,messages,animations)
        return ret
            
class Toxic(Poison):
    _p_counter={}
    _id_strings=('toxic','TOXIC')
    _past_tense='badly poisoned'
    _app_string='{} was '+_past_tense
    _poison_map={}
    battle_only=False
    @classmethod
    def apply(self,pokemon):
        self._p_counter[pokemon]=self._base_count
        self._poison_map[pokemon]=16
        return super().apply(pokemon)
    @classmethod
    def use(self,pokemon):
        H=pokemon.max_health
        dmg=int(H*(1/self._poison_map[pokemon]))
        self._poison_map[pokemon]+=1
        animations=[]
        messages=[self._eff_response.format(pokemon.name)]
        ret=(dmg,messages,animations)
        return ret
    
class LeechSeed(Toxic):
    _p_counter={}
    _id_strings=('leech_seed','seed','LEECH_SEED','leech seed')
    _past_tense='seeded'
    _app_string='{} was '+_past_tense
    _eff_response='{} was hurt by leech seed'
    battle_only=True
    
class Freeze(Status):
    _p_counter={}
    _id_strings=('freeze','frozen','FRZ')
    _short_string='FRZ'
    _past_tense='frozen'
    _eff_response='{} is '+_past_tense
    _remove_string='{} defrosted'
    battle_only=True
    before_attack=True
    
    @classmethod
    def use(self,pokemon):
        if self.remove_try(pokemon):
            ret=('continue',[self._remove_string.format(pokemon.name)],[])
        else:
            ret=(0,[self._eff_response.format(pokemon.name)],[])
        return ret
    
class Flinch(Status):
    _id_strings=('flinch',)
    _eff_response='{} flinched'
    _app_string=''
    battle_only=True
    before_attack=True
    
    @classmethod
    def apply(self,pokemon):
        pass
        
    @classmethod
    def use(self,pokemon):
        pokemon.skip_turn()
        dmg=0
        animations=[]
        messages=[self._eff_response.format(pokemon.name)]
        ret=(dmg,messages,animations)
        return ret

class Burn(Poison):
    _p_counter={}
    _id_strings=('burn','burned','BRN')
    _short_string='BRN'
    _app_string='{} was burned'
    _eff_response='{} was hurt by burn'
    battle_only=False
                 
class Paralyze(Freeze):
    _p_counter={}
    _id_strings=('paralysis','paralyze','FRZ')
    _short_string='FRZ'
    _app_string='{} was paralyzed'
    _pre_string='{} is paralzed. It might not be able to move.'
    _eff_response="{} is fully paralyzed"
    _remove_string='{} was cured of '+_id_strings[0]
    _remove_chance=0
    _use_chance=.25
    battle_only=False
    before_attack=True
    @classmethod
    def use(self,pokemon):
        if self.remove_try(pokemon):
            ret=('continue',[self._remove_string.format(pokemon.name)],[])
        else:
            r=random.random()
            if r<self._use_chance:
                ret=(0,[s.format(pokemon.name) for s in (self._pre_string,self._eff_response)],[])
            else:
                ret=('continue',[s.format(pokemon.name) for s in (self._pre_string,)],[])
            
        return ret
    
class Confusion(Status):
    _p_counter={}
    _id_strings=('confuse','confusion')
    _pre_string='{} is confused'
    _app_string='{} was confused'
    _eff_response='{} hurt itself in confusion'
    _remove_string='{} came to!'
    _use_chance=.25
    _dmg_percent=1/16
    battle_only=True
    before_attack=True
    
    @classmethod
    def use(self,pokemon):
        r=random.random()
        if self.remove_try(pokemon):
            ret=('continue',[self._remove_string.format(pokemon.name)],[])
        elif r<self._use_chance:
            ret=(pokemon.max_health*self._dmg_percent,[s.format(pokemon.name) for s in (self._pre_string,self._eff_response)],[])
        else:
            ret=('continue',[self._pre_string.format(pokemon.name)],[])
        return ret

class Sleep(Status):
    _p_counter={}
    _id_strings=('sleep','SLEEP','SLP')
    _app_string='{} fell asleep'
    _eff_response='{} is fast asleep'
    _remove_string='{} woke up!'
    battle_only=False
    before_attack=True
    
    @classmethod
    def use(self,pokemon):
        r=self.remove_try(pokemon)
        if r:
            ret=('continue',[self._remove_string.format(pokemon.name)],[])
        else:
            ret=(0,[self._eff_response.format(pokemon.name)],[])
        return ret

class Rest(Sleep):
    _p_counter={}
    _id_strings=('rest')
    _remove_chance=2
    _base_count=2
        
class Disable(Status):
    _p_counter={}
    _id_strings=('disable','DISABLE')
    _app_string='{} was disabled'
    _eff_response='{} is disabled'
    _remove_string='{} is disabled no more'
    battle_only=True
    
    @classmethod
    def apply(self,pokemon):
        m=pokemon.disable()
        if m is None:
            ret='It had no effect...'
        else:
            ret=self._app_string.format(m.name)
        return ret
    
_status_list=(Poison,Paralyze,Burn,Freeze,Toxic,
              LeechSeed,Flinch,Confusion,Sleep,Disable)
battle_statuses={x:s for s in _status_list for x in s._id_strings}

