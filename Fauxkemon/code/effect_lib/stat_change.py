'''stat_change'''
def effect(attackORitem,target,user,damage,arg=None):
    '''This is a battle effect to change a pokemon's battle stats

arg is required to be a (stat,amount) pair

It tracks the current state of the target pokemon's stats and does stuff u no?
'''

    damage=0
    messages=[]
    animations=[]
    (stat,amount)=arg
    
    v,q=target.battle_stats[stat]
    base=target.stats[stat] if stat in target.stats else 1
    if isinstance(amount,float):
        target.battle_stats[stat]=int(amount*base)
        messages.append("{pokemon.name}'s {stat} {adj} by {perc} percent!".format(target,stat,
            'fell' if amount < 1 else 'rose', int(100*amount)))
    elif amount > 0:                        
        if amount+q>6:
            amount=-1
        v=int((1.25)*amount*base)
        q+=amount
        if amount==1:
            target.battle_stats[stat]=[v,q]
            messages.append("{}'s {} rose".format(target.name,stat))
        elif amount>1:
            target.battle_stats[stat]=[v,q]
            messages.append("{}'s {} sharply rose".format(target.name,stat))                                      
        else:
            messages.append('{} cannot go any higher'.format(stat))
    elif amount < 0:
        if amount+q<-6:
            amount=-amount
        v=int((.75)*abs(amount)*base)
        q+=amount
        if amount==-1:
            target.battle_stats[stat]=[v,q]
            messages.append("{}'s {} fell".format(target.name,stat))
            animations.append('slow_shake_horizontal')
        elif amount<-1:
            target.battle_stats[stat]=[v,q]
            messages.append("{}'s {} sharply fell".format(target.name,stat))                                      
        else:
            messages.append('{} cannot go any lower'.format(stat))
    
    return (damage,messages,animations)
    
    
