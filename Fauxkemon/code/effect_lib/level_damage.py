
def effect(attackORitem,target,user,damage,arg=None):
    '''This is an effect for all those attacks that do damage equal to the user's level'''
    
    
    damage=user.level
    messages=[]
    animations=[]
    
    return (damage,messages,animations)