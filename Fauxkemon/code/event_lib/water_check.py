def event(cell,ob,trigger,arg):
    ret=None
    if ob.icon.lower()!='water':
        list(ob.call_event('repel'))
    yield 'done'
