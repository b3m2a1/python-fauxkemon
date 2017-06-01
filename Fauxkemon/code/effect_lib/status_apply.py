
def effect(attackORitem,target,user,damage,arg=None):
    '''This is an effect to apply a status to a Pokemon'''
    from Fauxkemon.code.State import BattleEffect    
    
    add_status=BattleEffect(arg)
    
    insert=2 if add_status.battle_only else 1
    status=[None,None,None] if target.status=='OK' else target.status
    
    damage=0
    animations=[]
    if status[insert] is None:
        status[insert]=add_status
        messages=[add_status.apply(target)]
        target.status_set(status)
    else:
        messages=['It had no effect...']
        
            
    
    return (damage,messages,animations)