from Fauxkemon.code.State import *

items=getdir('items')

class ItemClass:
    _loaded_items={}
    def __init__(self,name,source,version=base_game_source):
        self.file=os.path.join(source,version,name+'.txt')
        self.name=os.path.splitext(os.path.basename(self.file))[0]
        self.prices={'buy':0,'sell':0}
        self.effects={}
        self.uses=0
        self.type=None
        self.load()
                            
    @property
    def battle_usable(self):
        return 'battle' in self.effects

    def open(self):
        from GeneralTools.PlatformIndependent import open_file
        open_file(self.file)

    def load(self):
        with open(self.file) as data:
            mode='effects'
            for line in data:
                line=line.strip()
                if line:
                    if '#PROPERTIES#' in line:
                        mode='props'
                    elif '#EFFECTS#' in line:
                        mode='effects'
                    elif '#'==line[0]:
                        pass
                    else:
                        key,value=[x.strip() for x in line.split(':')]
                        if key in self.prices:
                            self.prices[key]=int(value)
                        elif 'type' in key:
                            self.type=value
                        elif 'uses' in key:
                            try:
                                value=int(value)
                            except ValueError:
                                value=None
                            self.uses=value
                        elif mode=='props':
                            setattr(self,key,value)
                        else:
                            self.effects[key]=process_effect(value)

    def edit(self,root=None):
        T=tk.Toplevel(root)
        R=RichText(T)
        R.pack(fill='both',expand=True)
        with open(self.file) as data:
            R.Append(data.read())
        
        def save(event=None,R=R,S=self):
            text=R.get('all').strip()
            if text:
                with open(S.file,'w+') as out:
                    out.write(text)
            S.load()
        T.protocol('WM_DELETE_WINDOW',lambda T=T,s=self:(save(),s.load(),T.destroy()))
        
    def use(self,user,target,context='map'):
        
        try:
            eff=self.effects[context]
        except KeyError:
            R=None
        else:
            R=eff(self,user,target,0)
        return R
                        
def Item(name,source=items):
    file=os.path.join(source,name)
    try:
        I=ItemClass._loaded_items[file]
    except KeyError:
        I=ItemClass(name,source)
        ItemClass._loaded_items[file]=I
    return I
    
