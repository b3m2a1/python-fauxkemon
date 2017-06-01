from Fauxkemon.code.State.file_sources import *

e_lib=getdir('events')

def null_event(*a):
    yield None

class LibraryEvent:
    '''An event translated from the event library'''
    def __init__(self,event,name,arg=None,df=False,verbose=False):
        self.event=event
        self.df_flag=df
        self.verbose=verbose
        self.name=name
        self.arg=arg
        self.generator_expr=None
        
    def __call__(self,cell,ob,trigger):
        event=self.event(cell,ob,trigger,self.arg)
        if type(event).__name__=='generator' and self.df_flag:
            def draw_first_event(event=event):
                yield 'draw'
                for e in event:
                    yield e
            event=draw_first_event()
        self.generator_expr=event
        return self
    
    def __iter__(self):
        return self
        
    def __next__(self):
        if self.verbose:
            print(self.name)
        return next(self.generator_expr)       
        
    def __repr__(self):
        return '{}_{}'.format(self.name,
            'processing' if not self.generator_expr is None else 'unqueued'
            )
    @classmethod
    def from_event_string(cls,eventstring,event_library=e_lib,argument=None):

        if eventstring.strip():
            L=Loader
            bits=eventstring.lower().strip().split('[')
            try:
                name,arg=bits
                arg=arg.strip(']').strip()
                try:
                    arg=eval(arg)
                except:
                    pass
            except:
                name=bits[0]
                arg=None
            if arg is None:
                arg=argument
            events=event_library
            p=os.path.join(events,name+'.py')
            if os.path.exists(p):
                m=L.load_module(p)
                e=m.event
                try:
                    df=m.refresh_before_calling
                except AttributeError:
                    df=False
                try:
                    vb=m.run_verbose
                except:
                    vb=False
                ret=LibraryEvent(e,name,arg=arg,df=df)
            else:
                def ret(cell,ob,trigger,e=eventstring):
                    print(e)
                    return null_event()
                ret=LibraryEvent(ret,name,df=False)
        else:
            ret=LibraryEvent(null_event,'No Event',df=False)
        return ret

translate_event=LibraryEvent.from_event_string