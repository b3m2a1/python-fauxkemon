refresh_before_calling=False
def event(cell,ob,trigger,arg):
    '''Has the map remove the flag in arg'''
    game_map=cell.parent
    game_map.remove_flag(arg)
    yield 'done'
