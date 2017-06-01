refresh_before_calling=False
def event(cell,ob,trigger,arg):
    '''Starts a battle with the first trainer in cell'''
    game=cell.parent
    trainer1=ob.trainer
    trainer2=None
    for o in cell:
        if hasattr(o,'trainer'):
            if not o.trainer is None:
                trainer2=o.trainer
                break
    if not trainer2 is None:
        game.StartBattle(trainer1,trainer2)    
    yield 'break'
