import math,random

def catch_algorithm(pokemon,ball):
    '''Should return an effect_tuple as any other item would

The return value should be 'caught' if the pokemon is caught and anything string otherwise.

This one mimics the catch algorithm found here: http://www.dragonflycave.com/mechanics/gen-i-capturing
'''
    try:
        catch_rate=float(ball.catch_rate)
    except AttributeError:
        if ball.name=='PokeBall':
            catch_rate=0
        elif ball.name=='Great Ball':
            catch_rate=55
        elif ball.name in ('Ultra Ball','Safari Ball'):
            catch_rate=105
        elif ball.name=='Master Ball':
            catch_rate=255
        else:
            catch_rate=0
            
    caught='caught'
    messages=[]
    catch_string='{} was caught!'.format(pokemon.name)
    animations=[]
    wobbles=4
    
    try:
        catchable=pokemon.catchable#for those special pokemans
    except AttributeError:
        catchable=True
    try:
        wild=pokemon.original_trainer is None
    except AttributeError:
        wild=True
    
    if not wild:
        caught='not wild'
        messages.append('Theif! You have been warned, beware. That Pokemon has a trainer, there.')
    elif not catchable:
        caught='not catchable'
        messages.append("It dodged the ball thrown! This Pokemon can't be caught!")
    else:
        R1=random.randint(0,255-catch_rate)
        S=pokemon.status;S=S[1]._short_string if not (S=='OK' or S[1] is None) else 'OK'
        S=(0 if S=='OK' else
            25 if S in ('FRZ','SLP') else
            12)
        R1-=S
        if R1<=0:
            messages.append(catch_string)
        else:
            F=int((255*pokemon.max_health)/(8 if ball.name=='Great Ball' else 12))
            hp_fac=max(int(pokemon.health/4),1)
            F=min(F/hp_fac,255)
            R2=random.randint(0,255)
            if pokemon.catch_rate>=R1 and R2<=F:
                messages.append(catch_string)
            else:
                W=int(pokemon.catch_rate*100/(255-catch_rate)*F)
                W+=(0 if S==0 else
                    10 if S==25 else
                    5)
                if W<10:
                    caught='missed'
                    messages.append('The ball missed the Pokemon!')
                    wobbles=0
                elif W<30:
                    caught='darn'
                    messages.append('Darn! The Pokemon broke free!')
                    wobbles=1
                elif W<70:
                    caught='aww'
                    messages.append("Aww! It appeared to be caught!")
                    wobbles=2
                else:
                    caught='shoot'
                    messages.append("Shoot! It was so close too!")
                    wobbles=3            
    animations.append('catch_animation[{}]'.format(wobbles))
    return (caught,messages,animations)
