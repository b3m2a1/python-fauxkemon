def event(cell,ob,trigger,arg):
    current=cell.parent
    which=arg
    current.ExitMap(which,ob)
    yield 'break'
