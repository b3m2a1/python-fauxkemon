def event(cell,ob,trigger,arg):
    if arg is None:
        arg='Main'
    ob.change_icon(arg)
    yield 'done'
