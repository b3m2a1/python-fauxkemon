def event(cell,ob,trigger,arg):
    if arg is None:
        arg='Dirt'
    cell.change_type(arg,source=cell.source)
    yield 'break'
