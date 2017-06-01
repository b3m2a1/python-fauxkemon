
def effect(attackORitem,user,target,damage,arg=None):
    '''This is an effect to recover a percentage of the target's hp'''

    damage=-arg*target.max_hp
    messages=['{} recovered health!'.format(user.name)]
    animations=[]
    
    return (damage,messages,animations)
    
    