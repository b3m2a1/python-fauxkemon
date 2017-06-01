
class PokeBallAnimation:

    def __init__(self,animation,frame):
        self.animation=animation
        self.frame=frame
        self.add_file(.5,.5,'PokeBall')
   
    def __getattr__(self,attr):
        return getattr(self.animation,'attr')

