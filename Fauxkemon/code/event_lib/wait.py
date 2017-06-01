def event(cell,ob,trigger,arg):
    if arg is None:
        arg=.1
    else:
        arg=float(arg)
    yield arg
    yield 'done'
