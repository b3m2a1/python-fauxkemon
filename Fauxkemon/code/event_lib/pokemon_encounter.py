refresh_before_calling=True
def event(cell,ob,trigger,arg):

    if ob.trainer is None:
        yield 'break'
    else:
        if arg is None:
            
            pokemon=cell.parent.encounterable_pokemon(cell.tile_type)
        else:
            from Fauxkemon.code import Pokemon
            pokemon=Pokemon.get_pokemon(arg)
            
        if not pokemon is None:
            team2=[pokemon]
            team1=ob.trainer
            
            cell.parent.button_bind('disabled')
            cell.parent.flash(length=100,delay=250,times=4)
            cell.parent.StartBattle(team1,team2)
            
        yield 'done'
            
