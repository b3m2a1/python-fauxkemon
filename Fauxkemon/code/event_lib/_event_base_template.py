refresh_before_calling=False
def event(cell,ob,trigger,arg):
    '''This is an event to be loaded from the event library. 

cell is the cell the event is called from
ob is the object the event is called on
trigger is the trigger that called the event
arg is the argument. Use a tuple to pass multiple arguments. If not argument is passed, this default to None.

To get the map, use cell.parent
To get the trainer, use ob.trainer. Beware that this can be None.

Events are generator objects, so don't use return, but rather yield

yielding 'break' will prevent any other events from being called
yielding 'draw' will cause the map to be redrawn
yielding a float or integer will cause the game to pause for that many milliseconds

Setting refresh_before_calling to True before defining the event will cause the map to be redrawn before the event is called, which can be particularly useful for events that are called upon entering a cell as then the character will appear to truly enter the cell, rather than freezing just outside of it.

Note that if trigger is a_button, cell could potentially be a character, as an a_button call on a cell is passed down to all of the objects in the cell
'''
    game_map=cell.parent
    create_message=cell.create_message
    trainer=ob.trainer
    call_object_event=ob.call_event#this returns an iterator
    call_cell_event=cell.call_event#as does this
    yield 'continue'
