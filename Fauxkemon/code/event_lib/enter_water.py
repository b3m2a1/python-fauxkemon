def event(cell,ob,trigger,arg):
#     cell.space+=1
    if ob.trainer is None or arg==True:
        for x in ob.move(iconchange='Water'):
            yield x
    yield 'done'
