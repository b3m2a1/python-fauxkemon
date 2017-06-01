def event(cell,ob,trigger,arg):
    '''Gives the pokemon specified by arg'''

    if not (ob.trainer is None or arg is None):
        if isinstance(arg,str):
            import string
            arg=string.capwords(arg)
        cell.parent.CreateMessage('Got {}!'.format(arg))
        if isinstance(arg,(str,int)):
            arg=(arg,)
        r=ob.trainer.add_pokemon(arg,screen=cell.parent)
        if r:
            pass
    yield 'continue'
