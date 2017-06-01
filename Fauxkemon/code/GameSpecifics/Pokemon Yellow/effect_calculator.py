#this is for gen 1
#tweak for gen 2 on and save in new file
class EffectCalculator:
    B='bug';D='dragon';E='electric';Fg='fighting';Fi='fire';Fl='flying'
    Gh='ghost';Gr='grass';Gd='ground';I='ice';N='normal';Po='poison'
    Py='psychic';R='rock';W='water'

    __base_effects={
        B: {Py:2,Gr:2,Fg:.5,Fi:.5,Fl:.5,Gd:.5,Po:.5},
        D: {D:2},
        E: {Fl:2,W:2,Gd:0,Gr:.5,D:.5},
        Fg:{N:2,Fl:.5,Po:.5,R:2,B:.5,Gh:0,Po:.5,I:2},
        Fi:{R:.5,B:2,Gr:2,Fi:.5,W:.5,D:.5},
        Fl:{Fg:2,R:.5,B:2,Gd:2},
        Gh:{N:0,Gh:2,Py:0},
        Gr:{Fl:.5,Po:.5,Gd:2,R:2,B:.5,Fi:.5,W:2,Gr:.5,E:.5},
        Gd:{Fl:0,Po:2,R:2,B:.5,Fi:2,Gr:.5,E:2},
        I: {Fl:2,Gd:2,W:.5,Gr:2,I:.5,D:2},
        N: {R:.5,Gh:0},
        Po:{Po:.5,Gd:.5,R:.5,B:2,Gh:.5,Gr:2,E:.5},
        Py:{Fg:2,Po:2,Py:.5},
        R: {Fg:.5,Fl:2,Gd:.5,B:2,Fi:2,I:2},
        W: {Gd:2,R:2,Fi:2,W:.5,Gr:.5,D:.5}
        }
    
    effect_map=__base_effects
    
    def __init__(self,*effect_triples):
        self.effect_map=self.__base_effects.copy()
    
    def revert(self):
        self.effect_map=self.__base_effects.copy()
        
    def calculate_effect(self,attacking,receiving):
        if isinstance(receiving,str):
            ret=self[attacking,receiving]
        else:
            vals=[self[attacking,x] for x in receiving]                    
            ret=1
            for x in vals:
                ret=ret*x
        return ret
           
    def __getitem__(self,types):
        if len(types)==1:
            ret=self.effect_map[types[0]]
        elif len(types)==2:
            m,t=types;
            m=m.strip().lower();
            ret=1;m_map=self.effect_map[m]
            for t in t:
                t=t.strip().lower()
                if t in m_map:
                    ret*=m_map[t]
        else:
            main=types[0]
            new=[]
            for t in types[1:]:
                if isinstance(t,str):
                    new.append(t)
                else:
                    for x in t:
                        new.append(x)
            ret=self.calculate_effect(main,types)
        return ret

    def __setitem__(self,pair,val):
        if isinstance(pair,str):
            self.effect_map[pair]=val
        else:
            self.effect_map[pair[0]][pair[1]]=val

EFC=EffectCalculator()
