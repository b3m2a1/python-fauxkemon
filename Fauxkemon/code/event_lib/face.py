def event(char,ob,trigger,arg):
    
    for r in char.face(ob):
        yield 'draw'
        
    yield 'done'
