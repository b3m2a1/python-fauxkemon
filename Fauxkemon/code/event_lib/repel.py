def event(cell,ob,trigger,arg):
    c=cell.parent.cellget(ob.cell)
    if c is cell:
        c.remove(ob,triggers=())
        c.space+=ob.size
    c=ob.ahead(-1)
    c.append(ob,triggers=())
    ob.cell[:]=c.pos
    ob.center_view()
    yield 'break'
    
