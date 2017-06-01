from ..State import *

tiles=getdir('tiles')
event_library=getdir('events')

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Tile(GridCanvas.Cell):
    '''An extension to the standard GridCanvas cell. 
Takes an image and more event bindings
Can be colorized and saved to/loaded from a file'''
    Event=GridCanvas.Event
    _file_tracker={}
    _root_source=tiles
    _event_root=event_library
    def __init__(self,name,parent,i,j,source=None,folder_extension=None,
                 orientation=(0,0,0),
                 initialcolor=None):
        
        self.dir_root=self._root_source
        if not folder_extension is None:
            self.dir_root=os.path.join(self.dir_root,folder_extension)
        if isinstance(orientation,int):
            orientation=(orientation,0,0)
        self._draw_mode='below'
        if not name=='Blank':
            if source is None:
                source='User Made'
            self.dir=os.path.join(self.dir_root,source,name)
            self.im=os.path.join(self.dir,'background.png')
            if not os.path.exists(self.im):
                for x in os.listdir(self.dir_root):
                    source=x
                    self.dir=os.path.join(self.dir_root,source,name)
                    self.im=os.path.join(self.dir,'background.png')
                    if os.path.exists(self.im):
                        break
                else:
                    raise FileNotFoundError('Could not find tile source '+name)
            self.source=source
            self.name=name
            self.props={}
            self.items=[]
            self.get_props(name)
            props=self.props
##                self.facing='down'
        else:
            name='Blank'
            self.tiletype='Blank'
            props=parent.cellconfig
            self._events=[]
            self._buttons=[]
            self.image=None
            self.im=None
            self.name=name
            self.source=''
        super().__init__(parent,i,j,**props)

        self.draw_mode=self._draw_mode
        self.event_library=self.parent.event_library
        if self.event_library is None:
            self.event_library=self._event_root
        
        self.lookup_name=name
        self.button_presses={'a_button':[],'b_button':[],'start':[],'select':[]}
##            self.events['a_button']=[];self.events['b_button']=[]
        self.load_events()
        self.orientation=[0,0,0]

        try:
            im=self.im
        except AttributeError:
            self.im=None
        else:
            self.set_background(im)
        
        for i in range(orientation[0]%4):
            self.Rotate()
        for i in range(orientation[1]%2):
            self.Flip('horizontal')
        for j in range(orientation[2]):
            self.Flip('vertical')
        self.base_events=[str(e) for s in (self.events,self.button_presses)
                          for x,y in s.items()
                          for e in y]
            
    @property
    def color_ranges(self):
        '''Returns the ranges for creating the colorizing mask'''
        try:
            colorizing_ranges=self.parent.colorizing_ranges
        except AttributeError:
            colorizing_ranges=tile_colorizing_ranges
        return colorizing_ranges

    def set_background(self,file):
        '''Sets the background of the cell to the file provided'''
        im=file
        ft=type(self)._file_tracker
        if not im in ft:
            super().set_background(im)
            if not self.image is None:
                self.colorize()
                ft[im]=self.image.image
        else:
            im=ft[im]
            if self.image is None:
                self.image=GridImage(im,parent=self.parent)
            else:
                self.image.image=im
##            self.parent.backgroundFlag=True

    def reload_orientation(self):
        '''Loads the orientation from a save string'''
        o=self.orientation
        self.orientation=[0,0,0]
        for i in range(o[0]):
            self.Rotate()
        for j in range(o[1]):
            self.Flip('horizontal')
        for k in range(o[2]):
            self.Flip('vertical')
            
    def bind(self,callback,to='events',**kwargs):
        '''Sets a binding much as Cell does, but also routes to 'button_press' if a normal binding fails'''
        try:
            super().bind(callback,to=to,**kwargs)
        except KeyError:
            super().bind(callback,to='button_presses',**kwargs)
            
    def call(self,trigger,ob,cell=None,mode='append',lock=False):
        '''Calls the event bindings for the trigger on the object provided'''
        
        if cell is None:
            cell=self
        try:
            v=cell.events[trigger]
        except KeyError:
            src=cell.button_presses                    
        else:
            src=cell.events
        
        if trigger=='a_button':
            for x in cell.obs:
                super().call(trigger,ob,cell=x,source=x.events,mode=mode,lock=lock)

        return super().call(trigger,ob,cell=cell,source=src,mode=mode,lock=lock)
        
    def change_type(self,name,source=None,
            orientation=None,clear_obs=False):
        '''Changes the type of the cell'''
        i,j=self.pos
        if source is None:
            try:
                source=self.source
            except AttributeError:
                source=None
        if orientation is None:
            orientation=self.orientation
        obs=self.obs
        events=self.events;base=self.base_events
        self.__init__(name,self.parent,i,j,source=source,
                      orientation=orientation)
                      
        for key in events:
            for e in events[key]:
                if not str(e) in base:
                    self.events[key].append(e)
                                
        if not clear_obs:
            for x in self.obs:
                self.append(x)

        self.Draw()

    def colorize(self,color_ranges=None,colors=None,reload=False):
        '''Colorizes the cell
Loads parent tint colors and color ranges by default''' 
        if color_ranges is None:
            color_ranges=self.color_ranges
        if colors is None:
            colors=self.parent.tint_colors
        if not colors is None and not self.image is None:
            if reload:
                self.image.reload()
            self.image.reset()
            self.image.color_ranges(*zip(color_ranges,colors),
                                    keep_shading=False)
            self.image.set_base_image()
    
    def reload(self):
        '''Just reinitializes'''
        i,j=self.pos
        name=self.name
        source=self.source
        root=self.parent
        obs=self.obs
        events=self.events;base=self.base_events
        self.__init__(name,root,i,j,source=source,orientation=self.orientation)
        for x in obs:
            self.append(x)
        for key in events:
            for e in events[key]:
                if not str(e) in base:
                    self.events[key].append(e)
            
            
    def Flip(self,mode):
        '''Flips the image and bindings'''
        if not self.image is None:
            self.image.Flip(mode)
            self.Background()
        if mode=='horizontal':
            cycle=('up','down')
            paired=('down','up')
            self.orientation[1]=(1+self.orientation[1])%2
        elif mode=='vertical':
            cycle=('up','down')
            paired=('down','up')
            self.orientation[2]=(1+self.orientation[2])%2
        for ext in ('_enter','_exit'):
            it=zip(cycle,paired)
            store=self.events[cycle[0]+ext]            
            for now,then in zip(cycle,paired):
                now=now+ext;then=then+ext
                evs=self.events[then]
                for ev in evs:
                    ev.t=now
                self.events[now]=evs
            for ev in store:
                ev.t=cycle[-1]+ext
            self.events[cycle[-1]+ext]=store
            
    def Rotate(self):
        '''Rotates the image and bindings'''
        self.orientation[0]=(self.orientation[0]+1)%4
        if not self.image is None:
            self.image.Rotate(90)
            self.Background()
        cycle=('up','right','down','left')
        paired=('right','down','left','up')
        for ext in ('_enter','_exit'):
            it=zip(cycle,paired)
            store=self.events[cycle[0]+ext]            
            for now,then in zip(cycle,paired):
                now=now+ext;then=then+ext
                evs=self.events[then]
                for ev in evs:
                    ev.t=now
                self.events[now]=evs
            for ev in store:
                ev.t=cycle[-1]+ext
            self.events[cycle[-1]+ext]=store
        
    def get_props(self,name,source=None):
        '''Gets all the properties and bindings from a file'''
        self._events=[]
        self._buttons=[]
        split=':'
        initkeys={'spaces':'space'}
        nopars=lambda l:l.replace('(','').replace(')','')
        strip=lambda l:l.strip()
        splitstrip=lambda l:[x.strip() for x in nopars(l).split(',')]

        
        def triggersplit(text):
            text=text.strip().replace('(','').replace(')','')
            i=iter(text.split(','))
            for k in i:
                self._events.append(k)
        def asplit(text):
            text=text.strip().replace('(','').replace(')','')
            i=iter(text.split(','))
            for k in i:
                self._buttons.append(k)
        if source is None:
            source=self.source
        propskeys={'events':triggersplit,'tiletype':strip,'buttons':asplit}
        p=os.path.join(self.dir,'props.txt')
        
        try:
            props=open(p)
        except:
            props=open(p,'w+')
            self.props['space']=1
            self.tiletype=name.lower()
            props.write('tiletype: {}\nspaces: {}'.format(self.tiletype,1))
        else:
            for line in props:
                
                if 'draw_mode:' in line:
                    mode=line.split(':')[1].strip()
                    self._draw_mode=mode
                    continue
                for k,n in tuple(initkeys.items()):
                    if k in line:
                        v=line.split(split)[1].strip()
                        try:
                            v=int(v)
                        except ValueError:
                            print(v)
                        self.props[n]=v
                        del initkeys[k]
                        
                for k,f in tuple(propskeys.items()):
                    if k in line:
                        v=f(line.split(split)[1])
                        setattr(self,k,v)
                        del propskeys[k]
                        
        finally:
            props.close()
            
    def load_events(self):
        '''Loads the events from a file'''
        
        for event in self._events:
            trigger,frequency,call=event.split()
            self.bind(self.translate_event(call),frequency=float(frequency),trigger=trigger,name=call)
            
        for event in self._buttons:
            name,call=event.split()
            self.bind(self.translate_event(call),frequency=1.0,trigger=name,name=call,to='button_presses')
            
    def clear_events(self,trigger=None):
        '''Removes all the events'''
        if trigger is None:
            super().clear_events()
            self.button_presses={'a_button':[],'b_button':[],'start':[],'select':[]}
        elif trigger in self.button_presses.keys():
            self.button_presses[trigger]=[]

    def set_message(self,text,cell=None,ob=None,trigger=None):
        '''Creates a message'''
        if cell is None:
            cell=self
        self.parent.CreateMessage(text,cell,ob,trigger)
    create_message=set_message
    
    def call_event(self,event,arg=None,ob=None,cell=None,trigger=None):
        if cell is None:
            cell=self
        return self.translate_event(event,argument=arg)(cell,ob,trigger)
        
    def string_set(self,string):
        '''Resets the cell from a string'''
        orientation,rest=string.split('.',1)
        name=rest.split('[')[0]
        try:
            source,name=name.split('/')
        except:
            source=None
        self.change_type(name,source=source,orientation=eval(orientation))

    def translate_event(self,event_string,argument=None):
        return translate_event(event_string,self.event_library,argument=argument)
    
    @classmethod
    def FromString(cls,parent,string,ignore_errors=False):
        '''Takes a cell formatted line orientation.name[cell]((trigger fq)&(trigger fq)&...)'''

##        ind=string.index('[')
##        name=string[:ind]
##        rest=string[ind+1:]
        try:
            orientation,string=string.split('.',1)
        except ValueError:
            string=string;orientation=0
        else:
            orientation=eval(orientation)
        name,rest=string.split('[',1)
        try:
            source,name=name.split('/')
        except ValueError:
            source=None
            name=name
        ind=rest.index(']')
        cell=rest[:ind]
        rest=rest[ind+1:]
        try:
            ind=rest.index('(')
        except ValueError:
            bindings=[]
            links=rest.strip()[1:-1].split('&')
        else:
            rest=rest.strip('()')
            bindings=rest.split('&')
            
        i,j=(int(x) for x in cell.split(','))
        try:
            self=cls(name,parent,i,j,source=source,orientation=orientation)
        except FileNotFoundError:
            tb.print_exc()
            self=cls('Blank',parent,i,j,source=source,orientation=orientation)

        cleared=[]
        for b in bindings:
            b=b.strip()
            if b:
                bits=b.split('*')
                try:
                    trigger,fq,event=bits
                except ValueError:
                    try:
                        trigger,event=bits
                    except ValueError:
                        continue
                    fq=1.0
                if not trigger in cleared:
                    self.clear_events(trigger)
                    cleared.append(trigger)
                self.bind(self.translate_event(event),frequency=float(fq),trigger=trigger,name=event)

        return self
    

    def save_string(self):
        '''Generates the save string for writing in tile files'''

        extraEvents=[]
        for s in (self.events,self.button_presses):
            for x,y in s.items():
                for e in y:
                    e=str(e)
                    if e not in self.base_events:
##                            print(e,self.base_events)
                        extraEvents.append(str(e))
        extraEvents='&'.join(extraEvents)
        if extraEvents:
            extraEvents='({})'.format(extraEvents)
        links=''
        name='{}/{}'.format(self.source,self.lookup_name)
        return '{0}.{1}[{2[0]!s},{2[1]!s}]{3}{4}'.format(self.orientation,name,self.pos,extraEvents,links)

    
    def __str__(self):
        return '{0}[{1[0]!s},{1[1]!s}]#{2!s}'.format(self.tiletype,self.pos,self.orientation)
