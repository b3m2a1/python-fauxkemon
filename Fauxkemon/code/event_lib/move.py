import math
refresh_before_calling=False
def event(cell,ob,trigger,arg):
    '''Should the character to the specified cell, if possible

Try to have it work by walking'''
    
    p=0#ob.standpause
    def move_iter(q,p=p):
        for i in range(abs(q)):
            for o in ob.move():
                if not o in ('break','done'):
                    yield o
                else:
                    yield 'draw'
            if i>1:
                yield p
                
    if isinstance(arg,int):
        to=ob.ahead(arg)
        if arg<0:
            list(ob.turn(180))
        for o in move_iter(arg):
            yield o
            
    else:
        if isinstance(arg,str):
            arg=(arg,1)
        
        t=0 if arg[1]>0 else 180
        if isinstance(arg[0],str):            
            ar=arg[0].lower()
            if arg=='left':
                t+=90
            elif arg=='right':
                t+=270
            elif arg=='back':
                t+=180
            else:
                t=0
            if t>0:
                list(ob.turn(t))
            for o in move_iter(arg[1]):
                yield o 
            
        else:
            
            f=ob.orientation
            j,i=arg
            #O IS FACING RIGHT
            #270 IS FACING DOWN
            if f=='back':#FACING UP
                if j>0:
                    mode=(0,1)
                else:
                    mode=(1,0)
            elif 'left':#FACING LEFT
                if i<0:
                    mode=(0,1)
                else:
                    mode=(1,0)
            elif 'down':#FACING DOWN
                if j<0:
                    mode=(0,1)
                else:
                    mode=(1,0)
            else:#FACING RIGHT
                if i>0:
                    mode=(0,1)
                else:
                    mode=(1,0)
            
            if mode==(0,1):#JUST SWAPS HOW THE MOVEMENTS ARE DONE
                if i<0:
                    ob.orientation='left'
                elif i>0:
                    ob.orientation='right'
                for o in move_iter(i):
                    yield o      
                
                if j<0:
                    ob.orientation='back'
                elif j>0:
                    ob.orientation='front'
                for o in move_iter(j):
                    yield o 
                        
            else:
                if j<0:
                    ob.orientation='back'
                elif j>0:
                    ob.orientation='front'
                for o in move_iter(j):
                    yield o 
                                        
                if i<0:
                    ob.orientation='left'
                elif i>0:
                    ob.orientation='right'
                for o in move_iter(i):
                    yield o 
            
    yield 'done'
