refresh_before_calling=False
def event(cell,ob,trigger,arg):
    '''Has the map set the flag in arg'''
    game_map=cell.parent
    game_map.set_flag(arg)
    yield 'done'
