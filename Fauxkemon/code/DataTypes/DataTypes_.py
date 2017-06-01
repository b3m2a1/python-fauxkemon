from Fauxkemon.code.State import *
from Fauxkemon.code.effect_calculator import *

pokemon=getdir('pokemon')
games=getdir('games')
trainers=getdir('trainers')
attacks=getdir('attacks')
chars=getdir('characters')

class Trainer:

    def __init__(self,name_ID=None,name='Trainer'):
        import re
        from random import choice
        from string import digits
        
        if name_ID is None:
            idKey=''.join((choice(digits) for x in range(3)))
            number=int(idKey)
            self.file=os.path.join(trainers,'{}_{}.txt'.format(name,idKey))
            self.pokemon=[]
            self.messages={}
            self.name=name
            self.ID=number
            self.prize=100
            self.image_file=os.path.join(trainers,name+'.png')
                
        else:
            self.load_from(os.path.join(trainers,name_ID+'.txt'))

    def load_from(self,file):
        self.file=file
        directory,basename=os.path.split(file)
        basename,ext=os.path.splitext(basename)
        name,num=basename.split('_')
        self.name=name
        self.ID=int(num)
        with open(file) as src:
            for line in src:
                line=line.strip()
                key,res=line.split(':',1)
                if key=='pokemon':
                    self.pokemon=[eval(x.replace(':',',')) for x in res.split(',') if x.strip()]
                elif key=='prize_money':
                    self.prize=int(res)
                elif key=='image':
                    sprites=os.path.join(directory,'__trainer_sprites__')
                    self.image_file=os.path.join(sprites,self.name+'.png')
                elif key=='messages':
                    break
            key=None
            for line in src:
                line=line.strip()
                if line=='#':
                    if key is None:
                        self.messages={}
                        message=[]
                    else:
                        self.messages[key]='\n'.join(message)
                    key=next(src).strip()
                else:
                    message.append(line)
            self.messages[key]='\n'.join(message)

    def __str__(self):
        return '{}_{}'.format(self.name,self.ID)
    
    def load_pokemon(self):
        
        return [Pokemon(p,l) for p,l in self.pokemon]

    def save(self):
        with open(self.file,'w+') as f:
            f.write('pokemon:{}\n'.format(','.join([str(x) for x in self.pokemon])))
            f.write('prize_money:{}\n'.format(self.prize))
            f.write('image:{}\n'.format(self.image_file))
            f.write('messages:\n')
            for k,t in self.messages.items():
                f.write('#\n{}\n{}\n'.format(k,t))
            
    @classmethod
    def from_file(cls,source):
        cls().load_from(source)
    
        
class Pokemon:            
        
    def __init__(self,nameORnumber,level=None,idKey=None,trainer=None,source=None):
        self.trainer=trainer

        if source is None:
            source='Pokemon Yellow'
        self.src=source
        source=os.path.join(pokemon,source)
        if idKey is None:
            self.idNo=idNo(5)
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
            self.__status=[None,None,None]
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
        else:
            self.LoadFromID(idKey)

    def show(self):
        t=tk.Toplevel()
        p=self.pokedex_entry(t)
        p.pack()
        return t

    def catch_try(self):
        raise NotImplementedError
    
    def load_properties(self):
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
        with open(f) as props:
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
##                        try:
##                            v=int(v)
##                        except TypeError:
##                            try:
##                                v=float(v)
##                            except TypeError:
##                                pass
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

    def enter_battle(self):
        self.battle_stats={x:[v,0] for x,v in self.stats.items()}
        self.battle_stats['accuracy']=[100,0]
        s=self.__status.copy();s.append(None)
        self.battle_stats['status']=s
        
    def use_attack(self,attack,enemy,override=False):
        if isinstance(attack,Attack):
            if override:
                return attack.use(self,enemy)
            attack=attack.name
        for x in self.moves:
            if x is None:
                continue
            elif x.name==attack:
##                print(x.name)
                return x.use(self,enemy)
        else:
            return (0,'none',['No attack...?',None])

    def take_damage(self,dmg):
        self.ChangeHealth(-dmg)
        
    def take_effect(self,eff,dmg=0,other=None):
        messages=[]
        out=[dmg,messages,None]
        if 'hp' in eff:
            eff.strip('hp')
            if '+' in eff:
                pass
            elif '-' in eff:
                pass
            else:
                pass
        elif 'transform' in eff:
            self.move_store=tuple(self.battle_moves)
            self.battle_moves=[x.copy() for x in other.moves]
            for x in self.battle_moves:
                x.pp=5
                x.max_pp=5
            out[2]='transform'
        else:
            for k in self.battle_stats:
                if k in eff:
                    eff=eff.strip(k)
                    f=float(eff[1:])
                    v,q=self.battle_stats[k]
                    if '*'==eff[0]:
##                        v,q=self.battle_stats[k]
                        self.battle_stats[k]*=f
    ##                    messages.append('{} multiplied by {}'.format(f))
                    elif '+'==eff[0]:                        
                        if f+q>6:
                            f=f-(6-q)
                        v=(1.25)*f*v
                        q+=f
                        if f==1:
                            self.battle_stats[k]=[v,q]
                            messages.append("{}'s {} rose".format(self.name,k))
                        elif f>1:
                            self.battle_stats[k]=v[q,q]
                            messages.append("{}'s {} sharply rose".format(self.name,k))                                      
                        else:
                            messages.append('{} cannot go any higher'.format(k))
                    elif '-'==eff[0]:
                        f=-f
                        if f+q<-6:
                            f=f(q+6)
                        v=(.75)*f*v
                        q+=q
                        if f==-1:
                            self.battle_stats[k]=[v,q]
                            messages.append("{}'s {} fell".format(self.name,k))
                        elif f<-1:
                            self.battle_stats[k]=[v,q]
                            messages.append("{}'s {} sharply fell".format(self.name,k))                                      
                        else:
                            messages.append('{} cannot go any lower'.format(k))
                    break
            else:
                mode='slow shake_horizontal'
                self.battle_stats['status'][1]=eff
                messages.append('{} was {}'.format(self.name,eff))
                out[2]=mode
        return out

    def exit_battle(self):
        status=self.battle_stats['status']
        self.__status=self.battle_stats['status'][:2]
        self.battle_stats=None
        
    def pokedex_entry(self,root):
        return self.PokedexEntry(root,self)

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
        for v in self.__stats:
            if v is not None:
                break
        else:
            v='OK'
        return v
    
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
            
    def LoadFromID(self,id):
        raise NotImplementedError

    @classmethod
    def FromID(cls,id):
        raise NotImplementedError            

    class PokedexEntry(tk.Frame):
        block_props=[('ATTACK','attack'),('DEFENSE','defense'),
                     ('SP. ATTK','special_attack'),('SP. DEF','special_defense'),
                     ('SPEED','speed')]
        def __init__(self,root,pokemon_instance):
            from string import capwords
            super().__init__(root,width=250,height=250)
##            self.pack_propagate(False)
            self.pokemon=P=pokemon_instance
            #Image
            self.imPane=tk.Frame(self,width=125,height=100)
            self.imPane.pack_propagate(False)
            self.image=tk.Label(self.imPane,image=P.image.Tk)
            self.no=tk.Label(self.imPane,text='No. {}'.format(P.number))
            self.no.pack(side='bottom',anchor='sw')
            self.image.pack(side='bottom',anchor='sw')
            
            self.imPane.grid(row=0,column=0,sticky='sw')
            #Health block
            mainhealth=tk.Frame(self,width=125,height=100,bg='black')
            mainhealth.pack_propagate(False)
            self.type_health=tk.Frame(mainhealth,width=123,height=98,bg='white')
            self.type_health.pack_propagate(False)
            test=tk.Label(self.type_health,text=P.name)
            test.pack(anchor='nw')
            F=tk.Frame(self.type_health)

            l=tk.Label(F,text=':L{}'.format(P.level))
            B=self.health_bar(F,P.health//2,P.stats['HP'])
            H=tk.Label(F,text='HP:',font=('Arial',11))
            n=tk.Label(F,text='{!s:>3}/{!s:>3}'.format(B.b.val,B.b.max))
            l.grid(row=0,column=0,columnspan=2)
            H.grid(row=1,column=0,sticky='e');B.grid(row=1,column=1,sticky='w')
            n.grid(row=2,column=0,columnspan=2)
            F.pack(expand=True)
            B.b.update()
            S=tk.Label(self.type_health,text='STATUS/{}'.format(P.status))
            S.pack(anchor='sw',pady=1)
            mainhealth.grid(row=0,column=1)
            self.type_health.pack(anchor='nw')
            #Stats
            self.stats=tk.Frame(self,bd=2,relief='ridge',width=125,height=150)
            self.stats.pack_propagate(False)
            #Adds the bars to the stats frame
            for p,k in self.block_props:
                self.prop_bar(p,P.stats[k]).pack(anchor='w')
                
            self.stats.grid(row=1,column=0)
            #That miscellaneous other shit
            self.misc=tk.Frame(self,height=150,width=125)
            self.misc.pack_propagate(False)
            element=P.props['type']
                #Types
            try:
                e1,e2=element.split(',')
                e1,e2=(capwords(x) for x in (e1,e2))
                a=self.misc_bar('Type1',e1)
                b=self.misc_bar('Type2',e2)
                a.pack()
                b.pack()
            except:
                l=self.misc_bar('Type',capwords(element))
                l.pack()
                #IdNo
            l=self.misc_bar('IDNo.',P.idNo)
            l.pack(side='top',anchor='w')
                #OT
            OT=str(P.original_trainer)
            l=self.misc_bar('O.T',OT)
            l.pack()
            
            self.misc.grid(row=1,column=1)          
        def misc_bar(self,n,v):
            f=tk.Frame(self.misc,width=125,height=40)
            l=tk.Label(f,text=n+'/')
            v=tk.Label(f,text=str(v))
            l.place(x=0,y=0,anchor='nw')
            v.place(x=5,rely=1,anchor='sw')
            
            return f
        
        def prop_bar(self,name,value):
            f=tk.Frame(self.stats,width=125,height=30)
            l=tk.Label(f,text=name,font=11)
            v=tk.Label(f,text=str(value),font=11)
            l.place(x=0,y=0,anchor='nw')
            v.place(relx=1,rely=1,anchor='se')
            
            return f

        def health_bar(self,root,cur,total):
            F=tk.Frame(root,width=85,height=15,bd=0,bg='gray')
            B=FillBar(F,cur,total,width=85,height=15,color='green4',mode='pill')
##            F.pack_propagate(False)
            B.pack(fill='both',expand=True)
            F.b=B
            return F

class Attack:
    keys=('type','mode','attack','effect','hit_rate','priority','pp')
    def __init__(self,name,dir=None,source=None):
        name=name.strip()
        if dir is None:
            dir=attacks
        if not source is None:
            dir=os.path.join(dir,source)
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

    @property
    def attack(self):
        a=self.__dict['attack']
        try:
            a=float(a)
        except ValueError:
            a=0
        return a
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
            r=self.__dict['repeats']
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
        
        self.__dict['pp']=new
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
    
    def use(self,pokemon,other):
        #attach messages to be set by the battle screen            
        self.pp+=-1
        if self.mode=='special':
            defense=other.stats['special_defense']
            attack=pokemon.stats['special_attack']
        else:
            defense=other.stats['defense']
            attack=pokemon.stats['attack']
        attempt=random.random()
        h=self.hit_rate
        hits=self.hits
        if attempt<h:
            power=self.attack
            t=self.type
            o=other.type
            m=pokemon.type
            if power>0:
                if t in m:
                    power=power*1.5
                mul=EFC[t,o]
            else:
                mul=1
            messages=[None,None]
            if mul==0:
                obj='user'
                messages[0]=["It doesn't affect {}...".format(other.name)]
                dmg=0
                eff='none'
            else:
                if mul==.5:
                    messages[0]=["It's not very effective..."]
                elif mul==2:
                    messages[0]=["It's super effective!"]
                power=power/2#scale down power factor
                att_ratio=(attack/defense)#tweak to get right
                dmg=int(power*att_ratio*mul)*hits
                if hits>1:
                    messages[0].insert(0,'Hit {} times'.format(hits))
                attempt=random.random()
                obj,effects,r=self.effect
                if attempt<r:
                    eff=random.choice(effects)
                    messages[1]=[eff]
                else:
                    eff='none'
                if power==0:
                    if effects!=['none']:
                        messages[0]=None
                    else:
                        messages[0]=['It had no effect...']
        else:
            dmg=0
            eff='none'
            obj='user'
            messages=[["The attack missed!"],None]
        return (dmg,(obj,eff),messages)

    def copy(self):
        return super().copy()

    def load_props(self):
        keys=set(self.keys)
        with open(self.file) as source:
            for line in source:
                if not '#'==line[0]:
                    bits=line.split(':',1)
                    if bits[0] in keys:
                        val=bits[1].strip()
                        if val=='-':
                            val=0
##                        try:
##                            val=float(val)
##                        except ValueError:
##                            pass
##                        else:
##                            try:
##                                val=int(val)
##                            except ValueError:
##                                pass
                        self.__dict[bits[0]]=val
                        keys.remove(bits[0])
##        self.effect=self.effect.split('_')
        e=self.__dict['effect']
##        eff,rate=e.rsplit('_',1)
##        obj,eff=eff.split('_',1)
##        e=e.rsplit('_',1)
        try:
            effect,rate=e.rsplit('_',1)
        except ValueError:
            effect='none'
            rate=0
        else:
            try:
                rate=float(rate)
            except:
                effect=effect+'_'+rate
                rate=1
            try:
                obj,effect=effect.split('_',1)
            except ValueError:
                obj='user'
            effect=effect.split('|')
                
        self.__dict['effect']=(obj,effect,rate)
        self.max_pp=self.pp
    
    def __repr__(self):
        return '{} w/ {} PP'.format(self.name,self.pp)
