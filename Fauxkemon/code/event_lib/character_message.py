def event(char,ob,trigger,arg):
    
    '''cell_message, but for ob'''
    import os
    
    d=char.dir
    if arg is None:
        arg='default'
        
    f=os.path.join(d,arg+'.txt')
    if not os.path.exists(f):
        with open(f,'w+') as file:
            file.write('Hi. This is the default character message.')
            
    with open(f) as file:
        text=file.read().strip()
    
    if isinstance(char,type(ob)):
        cell=char.ahead(0)
    else:
        cell=char
    
    if hasattr(cell,'trainer'):
        text=text.replace('<character_flag>',str(cell.trainer))
    
    for o in ob.face(char):
        if not o in ('break','done'):
            yield o
            
    char.parent.CreateMessage(text,cell,ob)
    
    yield 'done'
