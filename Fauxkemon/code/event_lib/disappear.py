refresh_before_calling=False
def event(ob,blump,trigger,arg):
    '''Deletes the object ob'''
    for o in ob.delete():
        yield o