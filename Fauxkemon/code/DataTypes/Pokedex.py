
class Pokedex:
    '''Combines Pokedex and PC storage'''
    
    def __init__(self,dir,game_source=base_game_source):
        self.in_game_pokemon={}#fill this from the pokemon directory
        self.seen=set()
        self.dir=os.path.join(dir,'Pokedex_Save_Folder')
        self.pokemon={}#Should map IDs to pokemon
        self.load()
    
    @property
    def seen_count(self):
        return len(self.seen)
        
    @property
    def caught_count(self):
        i=0
        for f in os.path.listdir(self.dir):
            try:
                base,rest=f.split(w)
            except ValueError:
                continue
            if base in self.in_game_pokemon:
                i+=1
        return i
        
    def save_to_folder(self,dir=None):
        if dir is None:
            dir=self.dir   
        elif dir!=self.dir:
            dir=os.path.join(dir,'Pokedex_Save_Folder')
            self.dir=dir
        
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)
        for f in 
        
        
    def save_pokemon(self,pokemon):
        pokemon.save(self.dir)
        
    def retrieve(self,pokemon_id):
        pass
    
    def deposit(self,pokemon):
        pass
    
    def PCInterface(self,pokemon):
        pass
    
    def MapInterface(self,pokemon):
        pass
        