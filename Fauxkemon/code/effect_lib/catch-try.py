
def effect(ball,target,user,damage,arg=None):
    '''This is an effect to try to catch a Pokemon'''
    
    from Fauxkemon.code.State import CatchAlgorithm
    
    c=CatchAlgorithm()
    return c(target,ball)
    