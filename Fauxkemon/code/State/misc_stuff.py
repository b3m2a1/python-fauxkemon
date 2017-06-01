from Fauxkemon.code.State.base_modules import *

def idNo(length):
    from random import choice
    from string import digits
    return ''.join((choice(digits) for i in range(length) ))

def key_wait(widget,*keys):
    wait_var=tk.BooleanVar(value=False)
    D=TemporaryBinding('<Destroy>',command=lambda *e,w=wait_var:w.set(True))
    bindings=[D]
    def wait_cmd(event=None,w=wait_var,wid=widget,b_keys=bindings):
        w.set(True)
        for B in b_keys:
            B.remove(wid)
    for key in keys:
        if key:
            B=TemporaryBinding(key)
            B.command=wait_cmd            
            bindings.append(B)
            B.apply(widget,0)
    D.apply(widget)
    widget.focus_set()
    widget.wait_variable(wait_var)
