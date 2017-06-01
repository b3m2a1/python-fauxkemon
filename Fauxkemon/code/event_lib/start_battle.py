refresh_before_calling=True
def event(enemy,player,trigger,arg):
    '''This is an event to be called from an enemy character to start a battle with the trainer in player'''

    if not (player.trainer is None or not enemy.trainer):
        win=enemy.parent.StartBattle(player.trainer,enemy.trainer)
        if not arg is None and win=='won':
            player.parent.set_flag(arg)
            
    yield 'continue'
