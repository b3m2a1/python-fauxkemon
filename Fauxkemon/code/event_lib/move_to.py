refresh_before_calling=False
def event(cell,ob,trigger,arg):
    '''Moves to a position'''
    
    if isinstance(arg,type(cell)):
        arg=arg.pos
    elif isinstance(arg,type(ob)):
        arg=arg.cell
    I,J=arg
    i,j=ob.cell
    i=I-i
    j=J-j
    for o in ob.call_event('move',(i,j)):
        yield o

    yield 'done'