from .config import *

class EnemyAI:
    effect_calculator=None
    def __init__(self,pokemon):
        self.pokemon=pokemon
        self.effect_calculator=EffectCalculator(pokemon.src)
        self.attacks=[x for x in self.pokemon.moves if not x is None]
        self.attack_weights={x:0 for x in self.attacks}
##        self.weight_attacks()
        
    def __getattr__(self,attr):
       return getattr(self.pokemon,attr)

    def weight_attacks(self,enemy):
        t=enemy.type
        for a in self.attacks:
            t2=a.type
            r=max(self.effect_calculator[t2,t],.05)
            p=a.attack
            if p==0 or isinstance(p,str):
                p=30
            w=int(r*p)

            self.attack_weights[a]=w
            
    def choose_attack(self,enemy):
        self.weight_attacks(enemy)
        at_list=[[x]*r for x,r in self.attack_weights.items()]
        at_w=[]
        for l in at_list:
            at_w+=l
        return random.choice(at_w)
