def event(cell,ob,trigger,arg):
    '''tries to call the same sequence on the cell found arg away from cell.
    
If arg is None, it goes twice the distance from ob to cell
If arg is 3 elements long, it calls the trigger specified as the 3rd element'''
    i,j=cell.pos
    if arg is None:
        i1,j1=ob.cell
        ahead_i=i-i1
        ahead_j=j-j1
    else:
        ahead_i=arg[0];ahead_j=arg[1]
        if len(arg)>2:
            trigger=arg[2]    
    
    try:
        callable=cell.parent[i+ahead_i,j+ahead_j]
    except IndexError:
        pass
    else:
        callable.call(trigger,ob)#,mode='add')
        callable.parent.step()
    
    yield 'draw'