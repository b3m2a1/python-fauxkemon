
def effect(attackORitem,target,user,damage,arg=None):
    '''This is an effect to be used by an attack or item on a pokemon or its enemy

attackORitem is the attack or item to be used
target is the pokemon targeted by this effect
user is the user of this effect: this will be either the pokemon using the attack or the trainer using the item
arg is an optional argument

The return value should be the following tuple:
    
    (damage,status,messages,animations)

where:

damage is the damage done by the effect:
    - Negative for recovery and positive for damage.
status is any statuses that should be applied:
    - Stat changes can be accessed through the stat_change effect. Just remember to add these messages to the the message list
    - Statuses can be called via apply_status. Remember to add these statuses to the list.
message is the set of messages to apply afterwards
animations is the set of battle animations to call after setting the message. Simply specify these by name and they'll be applied sequentially.
'''

    damage=0
    status=[]
    messages=[]
    animations=[]
    
    return (damage,status,messages,animations)
    
    