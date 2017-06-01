'''stat_change'''
def effect(attackORitem,target,user,damage,arg=None):
    '''This is a battle effect to change a pokemon's battle stats

arg is required to be a (stat,amount) pair

It tracks the current state of the target pokemon's stats and does stuff u no?
'''
    
    messages=[];animations=[]
    if isinstance(arg,int):
        damage=arg
        if arg>0:
            messages.append('{} recovered {} HP!'.format(target,arg))
        elif arg<0:
            pass
#             messages.append('{} was hurt'.format(target,arg))
        else:
            messages.append('It had no effect...')
    else:
        if damage>0:
            damage=arg*damage
            messages.append('{} was hurt by {}!'.format(target.name,attackORitem.name))
        else:
            damage=target.max_hp*arg
            messages.append('{} recovered health!'.format(target.name))
    return (damage,messages,animations)
    
    
