
def effect(attackORitem,target,user,damage,arg=None):
    '''This is an effect to apply the paralysis status'''
    
    return target.call_effect('status_apply',target,user,damage,'paralysis')
    
    