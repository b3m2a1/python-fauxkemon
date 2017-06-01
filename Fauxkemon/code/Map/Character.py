from ..State import *
from .Tile import Tile
from GeneralTools.PlatformIndependent import open_file

chars=getdir('characters')

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Character(WalkerCanvas.Walker):
    prop_type={'size':int,'speed':float,'charname':str}
    _file_tracker={}
    def __init__(self,parent,name=None,nickname='',initialcell=None,source=None,
                 NPC=True,walk_rate=.1,walk_pause=.025,jump_pause=.075,los=1,
                 trainer=None):
        self.npc_flag=NPC
        self.line_of_sight=los
        self.walkpause=walk_rate
        self.standpause=walk_pause
        self.jumppause=jump_pause
        self.step=0
        self.inventory=[]
        self.facing=(3/2)*math.pi
        self.kind=name
        self.nickname=nickname
        self.icon=name
        self.trainer=trainer
        self.events={'a_button':[]}
        wig=GridImage
        if not source is None:
            name=os.path.join(source,name)
        self.source=source
        self.dir=os.path.join(chars,name)
        if not os.path.exists(self.dir):
            for d in os.listdir(chars):
                test=os.path.join(chars,d,name)
                if os.path.exists(test):
                    self.dir=test
                    break
##        if not os.path.exists(dir):
##            pass
        self.im='front'
        im=os.path.join(self.dir,self.im+'.png')
        try:
            super().__init__(parent,widget=wig,classname=name,anchor='sw',
                             image=im,initialcell=initialcell,facing=self.facing)
        except FileNotFoundError:
            open_file(self.dir)
            raise
        self.base_position=character_positioning
        self.position=list(self.base_position)
        self.default_events={k:[] for k in self.events}
        self.get_props()
        self.colorize()
        
    @property
    def colorizing_ranges(self):
        try:
            r=self.parent.character_colorizing_ranges
        except AttributeError:
            r=character_colorizing_ranges
        return r
    
    def add_follower(self,char=None,ahead=None):
        if isinstance(ahead,int):
            char=self.ahead(ahead)[0]
        char.follow(self)
        
    def follow(self,char):
        char.followers.add(self)
        self.npc_flag=False
    
    def unfollow(self,char):
        char.followers.remove(self)
    
    def remove_follower(self,char):
        char.unfollow(self)
        
    def move_animation(self,iconchange=None):
        base=self.im
        im=self.im[0]+'move'
        self.change_image(im,self.step)
        yield self.walkpause 
        if not iconchange is None:
            self.change_icon(iconchange)
        self.change_image(base)
        if not self.npc_flag:
            self.center_view()
        yield self.standpause
        yield 'draw'
    
    def move_followers(self):
        motions=[f.move_behind(self,triggers=False,override=True) for f in self.followers]
        r='done'
        continue_flag=len(motions)
        while continue_flag:
            for move_step in motions:
                try:
                    r=next(move_step)
                except StopIteration:
                    continue_flag=False
                    yield 'done'
                    break
            if r not in ('break','done'):
                yield r

        yield 'done'
            
        
    def move(self,amt=None,triggers=True,override=False,iconchange=None):
        
        move_animation=self.move_animation(iconchange=iconchange)
        follower_animation=self.move_followers()
        next(follower_animation)
        yield next(move_animation)
        
        if amt is None:
            amt=self.speed   
        r=super().move(amt,triggers=triggers,override=override)
        self.step=(self.step+1)%2
        
        list(iter(lambda:next(follower_animation),'done'))
        for a in move_animation:
            yield a
        
        yield 'done'
    
    def move_behind(self,char,triggers=True,override=False,iconchange=None):
        for f in self.face(char):
            yield f
        move_animation=self.move_animation(iconchange=iconchange)
        follower_animation=self.move_followers()
        next(follower_animation)
        yield next(move_animation)
        super().move_behind(char,triggers=triggers,override=override)
        list(iter(lambda:next(follower_animation),'done'))
        self.step=0 
        for a in move_animation:
            yield a
    
    def move_to(self,cell,triggers=True,override=False,iconchange=None):
        for f in self.face(cell):
            yield f
        move_animation=self.move_animation(iconchange=iconchange)
        follower_animation=self.move_followers()
        next(follower_animation)
        yield next(move_animation)
        super().move_to(cell,triggers=triggers,override=override)
        list(iter(lambda:next(follower_animation),'done'))
        self.step=0 
        for a in move_animation:
            yield a 
    
    def make_character(self):
        if not self.parent.character is None:
            self.parent.character.npc_flag=True
        self.parent.current.clear()
        self.parent.current.append(self)
        self.parent.character=self
        self.npc_flag=False
        
    def activate(self,ahead):
        obs=self.ahead(ahead).obs
        self.current.parent.current.extend(obs)

    def Rotate(self,q=90):
        list(self.turn(q,mode='degrees'))
        
    def get_props(self,name=None,source=None,root=None):
        props=os.path.join(self.dir,'specs.txt')
        if not os.path.exists(props):
            with open(props,'w+') as to_write:
                lines=[
                    'charname:{}'.format(os.path.basename(self.dir).lower()),
                    'speed:1',
                    'size:1',
                    'a_button:(face,character_message)'
                    ]
                to_write.write('\n'.join(lines))
        with open(props) as data:
            for line in data:
                bits=line.split(':')
                try:
                    prop,val=[x.strip() for x in bits]
                except ValueError:
                    print(bits)
                else:
                    if prop=='a_button':
                        text=val.strip().replace('(','').replace(')','')
                        i=iter(text.split(','))
                        for e in i:
                            E=Tile.Event(self.translate_event(e),1.0,prop,name=e)
                            self.events[prop].append(E)
                            self.default_events[prop].append(e)
                    else:
                        val=self.prop_type[prop](val)
                        setattr(self,prop,val)
        
                            
    def change_icon(self,source):
        self.dir=os.path.join(chars,self.source,source)
        self.change_image(self.orientation,self.step)
        self.icon=source
    
    def hop(self,amt=None,height=.5):
        o=self.orientation
        base=self.im
        im=self.im[0]+'move'
        self.change_image(im)
        c=self.current
        yield self.standpause
        if amt is None:
            amt=self.speed
        if o in ('right','left'):
            theta=math.radians(30)
            if o=='right':
                next(self.turn(theta,mode='radians'))
            if o=='left':
                next(self.turn(-theta,mode='radians'))
            a1=amt*math.sin(theta)
            a2=amt*math.cos(theta)
        else:
            a1=height*amt
            a2=(1-height)*amt
        super().move(a1,triggers=False,override=True,ignore_walls=True)
        if o=='right':
            next(self.turn(-theta,mode='radians'))
        elif o=='left':
            next(self.turn(theta,mode='radians'))
        yield self.jumppause
        super().move(a2,triggers=False,override=True,ignore_walls=True)
        list(self.move(0))
        c.remove(self)
        self.change_image(o)
        yield 'done'
    
    @property
    def orientation(self):
        p=math.pi
        q=p/4
        t=2*p
        f=self.facing
        if f>=(t-q) or f<=(q):
            key='right'
        elif f<t-q and f>=p+q:
            key='front'
        elif f<p-q and f>q:
            key='back'
        else:
            key='left'
        return key
    
    @orientation.setter
    def orientation(self,val):
        if val=='right':
            v=0
        elif val=='back':
            v=90
        elif val=='left':
            v=180
        elif val=='front':
            v=270
        next(self.setfacing(v,mode='degrees'))
        
    @property
    def current(self):
        return self.parent.cellget(self.cell)

    def run(self):
        self.walkpause=.01
        self.standpause=.01
        
    def walk(self):
        self.walkpause=.075
        self.standpause=.025
    
    def delete(self):
        super().delete()
        yield 'done'
        
    def face(self,obj):
        i1,j1=obj.cell if isinstance(obj,Character) else obj.pos
        i2,j2=self.cell
        row_diff=i1-i2
        col_diff=j1-j2
        if abs(row_diff)>abs(col_diff):#NOTE THAT THIS PRIORITIZES FACING LEFT-RIGHT
            if row_diff>0:#MORE DOWN THAN ANYTHING
                f=270
            else:
                f=90
        else:
            if col_diff>0:
                f=0
            else:
                f=180

        for s in self.setfacing(f,mode='degrees'):
            yield s
        
    def turn(self,theta,mode='degrees'):
        r=next(super().turn(theta,mode=mode))
        self.correct_image()
        yield r
        
    def setfacing(self,theta,mode='degrees'):
        r=next(super().setfacing(theta,mode=mode))
        self.correct_image()
        yield r

    
    def change_image(self,key,number=None):
        orig=key
        if not number is None:
            key=key+'_{}'.format(number)
        key+='.png'
        p=os.path.join(self.dir,key)
        if not os.path.exists(p):
            p=os.path.join(self.dir,orig+'.png')
        if os.path.exists(p):
            self.ChangeImage(p)
        self.im=orig

    def ChangeImage(self,file):
        im=file
        ft=type(self)._file_tracker
        if not im in ft:
            super().ChangeImage(im)
            if not self.image is None:
                self.colorize()
                ft[im]=self.image.image
        else:
            self.image.image=ft[im]
            self.set_base_image()
##            self.parent.backgroundFlag=True

    def colorize(self,color_ranges=None,colors=None):
        if color_ranges is None:
            color_ranges=self.colorizing_ranges
        if colors is None:
            colors=self.parent.tint_colors
        if not colors is None and not self.image is None:                
            self.image.reset()
            self.image.color_ranges(*zip(color_ranges,colors))
            self.image.set_base_image()
        
    def apply_color(self,colorname=None,r=1,g=1,b=1,a=1):
        if not self.image is None:
            if not colorname is None:
                self.recolor(colorname)
            else:
                self.adjust_color(r,g,b,a)
##                self.set_background(self.image)
                
    def correct_image(self):
        p=math.pi
        q=p/4
        t=2*p
        if self.facing>=(t-q) or self.facing<=(q):
            key='right'
        elif self.facing<t-q and self.facing>=p+q:
            key='front'
        elif self.facing<p-q and self.facing>q:
            key='back'
        else:
            key='left'
        if self.im!=key:
            self.change_image(key)

    def set_message(self,text,cell=None,ob=None,trigger=None):
        if ob is None:
            ob=self
        self.current.set_message(text,cell,ob,trigger)
    create_message=set_message
    
    def call(self,trigger='a_button',mode='append'):
        return self.call_ahead(0,trigger,mode=mode)
        
    def call_ahead(self,ahead=1,trigger='a_button',mode='append'):
        if isinstance(ahead,str):
            trigger=ahead
            ahead=1
        return self.ahead(ahead).call(trigger,self,mode=mode,lock=(trigger=='a_button'))
        
    def call_event(self,event,arg=None,cell=None,ob=None,trigger=None):
        if ob is None:
            ob=self
        return self.current.call_event(event,arg=arg,ob=ob,cell=cell,trigger=trigger)
        
    def make_active(self):
        self.current.parent.SetCharacter(self)
        
    def deactivate(self):
        try:
            self.current.parent.current.remove(self)
        except ValueError:
            pass
        
    def translate_event(self,string):
        return self.current.translate_event(string)

    @classmethod
    def from_string(cls,line,parent):
     
        from Fauxkemon.code.DataTypes.Trainer import Trainer
        
        name,celpos=line.strip().split('@')
        try:
            source,name=name.split('_')
        except ValueError:
            source=None
        cell,rest=celpos.split('+')
        cell=[int(x) for x in cell.split('x')]
        pos,props=rest[:-1].split('{',1)
        pos=[float(x) for x in pos.split('x')]
        self=cls(parent,name,initialcell=cell,source=source)
        events_cleared=False
        for key_pair in props.split('|'):
            key,val=key_pair.split(':',1)
            if key=='trainer':
                if val:
                    try:
                        val=Trainer(val,source=self.source,flags=self.parent.flags)
                    except FileNotFoundError:
                        val=None
                else:
                    val=None
            elif key=='events':
                
                if val:
                    if not events_cleared:
                        for k in self.events:
                            self.events[k].clear()
                    val=eval(val)
                    for k,l in val.items():
                        new=[Tile.Event(self.translate_event(x),1.0,k,x)
                            for x in l]
##                        val[k]=new
                        self.events[k].extend(new)
##                else:
                val=self.events
                    
            setattr(self,key,val)

        return self
    
    @property
    def save_string(self):
        #need to have save events properly, too
        #also track nickname and trainer info/other writeable props
        kwargs=[]
        for k in ('nickname','trainer','orientation','events','inventory'):
            val=getattr(self,k)
            if val is None:
                val=''
            if k=='events':
                v={}
                for key,calls in val.items():
                    v[key]=[x.n for x in calls]
                if v and not v==self.default_events:
                    val=v
                else:
                    val=''
            
            
            kwargs.append('{}:{!s}'.format(k,val))
        props=(self.source+'_' if not self.source is None else '', self.kind,self.cell,self.position,'|'.join(kwargs))
        s='{0}{1}@{2[0]!s}x{2[1]!s}+{3[0]!s}x{3[1]!s}{{{4}}}'.format(*props)
        return s
    
    def __repr__(self):
        return '{0}_{1}@{2[0]!s}x{2[1]!s}+{3[0]!s}x{3[1]!s}'.format(
            self.source + '_' if not self.source is None else '',self.kind,self.cell,self.position
            )
                
