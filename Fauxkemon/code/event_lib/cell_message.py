def event(cell,ob,trigger,arg):
    import os
    d=cell.dir
    if arg is None:
        arg='message'
    text='Welcome to the world of Fauxkemon!'
    if isinstance(arg,str):
        f=os.path.join(d,arg+'.txt')
        if not os.path.exists(f):
            with open(f,'w+') as file:
                file.write(text)
        else:
            with open(f) as file:
                text=file.read().strip()
    
    cell.parent.CreateMessage(text,cell,ob,trigger)
    
    yield 'done'
