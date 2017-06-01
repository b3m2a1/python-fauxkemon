def event(cell,ob,trigger,arg):
    '''This heals the pokemon in ob.trainer.
    
if arg is 'full' it heals health, status and pp
if arg is 'hp' it heals health
if arg is 'status' it heals status
if arg is 'pp' it heals pp'''
    
    if arg is None:
        arg='full'
    
    t=ob.trainer
    if not t is None:
        for p in t.load_pokemon():
            p.restore(arg)
    
    yield 'done'