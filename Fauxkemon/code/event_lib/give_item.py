def event(reciever,giver,trigger,arg):
    
    reciever=reciever.trainer
    try:
        giver=giver.trainer
    except AttributeError:
        give_flag=True
    else:
        give_flag=arg in giver.inventory if not giver is None else True
    
    if give_flag and not reciever is None:
        reciever.get_item(arg)       
        
    yield 'done'
    
