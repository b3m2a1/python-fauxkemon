
def effect(attackORitem,user,target,damage,arg=None):
    '''This is an effect for target to take recoil damage'''

    damage=damage*arg
    messages=['{} was hurt by recoil'.format(user.name)]
    animations=[]
    
    return (damage,messages,animations)
    
    