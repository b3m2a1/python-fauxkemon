from Fauxkemon.code.State import *
from Fauxkemon.code.Map import Map
from Fauxkemon.code.DataTypes import Trainer,Pokemon

games=getdir('games')
maps=getdir('maps')
trainers=getdir('trainers')
            
class GameFolder(Session):
    def __init__(self,file_key=None,name='Name',
                 root=None,game_source='Pokemon Yellow'):
        
        
        self.ext=game_source
        self.root=root
        self.save_flag=True
        
        if file_key is None:
            self.player_name=(idNo(6),name)
            file_key='{}_{}'.format(*self.player_name)
            self.save_flag=False
        else:
            self.player_name=file_key.split('_',1)
        
        if not os.path.exists(os.path.join(games,game_source)):
            os.mkdir(os.path.join(games,game_source))
            
        super().__init__(name=str(file_key),
                         location=os.path.join(games,game_source))
    
    @property
    def map(self):
        f=self['Map.pmp']
        if not f:
            f=self.MakeFile('Map','.pmp')
            #extend to allow for different start-point choices
            load=os.path.join(maps,self.ext,'Pallet Town.pmp')
            M=Map.LoadFromFile(self.root,load)
            M.destroy()
            M.character.trainer=self.load_trainer()
            f=self[f]
            M.file=f
            M.Save()
        return f
    @property
    def pokedex(self):
        p=Pokedex(self.dir,self.ext)
        return p
    @property
    def ID(self):
        return self.player_name[0]
    @property
    def trainer(self):
        f=self['Trainer_{}.txt'.format(self.ID)]
        if not f:
            f=self.MakeFile('Trainer_{}'.format(self.ID),'.txt')
            load=os.path.join(trainers,self.ext,'default.txt')
            T=self.load_trainer(load)
            f=self['Trainer_{}.txt'.format(self.ID)]
            T.file=f
            T.save()
        return f
    
    def load_trainer(self,f=None):
        if f is None:
            f=self.trainer
        s,chaff=os.path.split(f)
        source,chaff=os.path.split(s)
        source=os.path.basename(source)
#         with open(se lf.flags) as flag_set:
#             flag_set=eval(flag_set.read())
        T=Trainer(file=f,source=source,pokedex=True)
        T.ID,T.name=self.player_name
        T.game_name=self.player_name
        return T
                   
    @property
    def pokemon(self):
        return self.pokedex.dir

    @property
    def flags(self):
        f=self['flags.txt']
        if not f:
            self.MakeFile('flags','.txt')
            f=self['flags.txt']
            with open(f,'w+',encoding='utf-8') as flags:
                flags.write("['game_start']")
        return f
    
    def get_flags(self):
        with open(self.flags,encoding='utf-8') as flag_set:
            eval(flag_set.read())
            
    def __del__(self):
        if not self.save_flag:
            shutil.rmtree(self.foldername)
##        super().__del__
