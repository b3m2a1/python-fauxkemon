def event(cell,ob,trigger,arg):
    c=cell.parent.cellget(ob.cell)
        
    if arg is None:
        arg=2
    
    i=0
    for x in ob.hop(arg):
        yield 'draw'
        yield x
        i+=1

    #yield 'done'
