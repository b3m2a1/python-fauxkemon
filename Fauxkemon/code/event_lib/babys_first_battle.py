refresh_before_calling=True
run_verbose=True
def event(char,ob,trigger,arg):
    '''This event starts that first battle with the rival'''

    if not ob.trainer is None:
        if len(ob.trainer.pokemon)==0:
            for o in char.call_event('character_message','talk_to_oak',cell=char,ob=ob):
                yield o
        else:
            
            for o in char.call_event('character_message','start_babys_first_battle',cell=char,ob=ob):
                if not o in ('break','done'):
                    yield o
            char.parent.set_flag('first_battle')
            
            
    yield 'break'
