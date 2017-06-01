def event(cell,ob,trigger,arg):
    c=ob.ahead(0)
    if c.tiletype!='water':
        ob.change_icon(ob.kind)
    yield 'done'
