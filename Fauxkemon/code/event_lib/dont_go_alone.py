refresh_before_calling=True
def event(cell,ob,trigger,arg):
    '''Event to call Professor Oak to give starter. Too lazy to do the full version, so you just get a Pikachu.
'''
    if not ob.trainer is None:
        if len(ob.trainer.pokemon)==0:
            ob.create_message('''
Professor Oak: It's dangerous to go alone.
#PAUSE 1000
---NEW MESSAGE---
Professor Oak: Meet me at my lab
#DELAY 250
#CMD
move[-1]
#CMD
''')        
            if not cell.parent.menu is None:
                cell.parent.menu.destroy()

    yield 'break'
