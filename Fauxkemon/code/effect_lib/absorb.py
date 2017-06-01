def effect(attackORitem,user,target,damage,arg=None):
    '''This is an effect for target to absorb damage done'''

    damage=-damage*arg
    messages=['{} absorbed health from {}'.format(user.name, target.name)]
    animations=[]
    
    return (damage,messages,animations)