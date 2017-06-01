def event(called_on,called_from,trigger,arg):
    called_on.current.remove(called_on)
    called_on.current.space+=called_on.size
    yield 'done'
    
