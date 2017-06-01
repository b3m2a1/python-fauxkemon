'''This is a shimming module that sets up sys to load the appropriate modules'''

import os, sys

d=os.path.dirname(__file__)
code_dir=os.path.join(os.path.dirname(d),'code')

if not ( 
    os.path.exists(os.path.join(code_dir,'GUITools')) or 
    os.path.exists(os.path.join(code_dir,'GUITools.py')) 
    ):
    for i in range(1):
        try:
            sys.path.remove(d)
        except ValueError:
            pass
        d=os.path.dirname(d)

    base_dir=os.path.dirname(d)
    os.chdir(base_dir)

    sys.path.insert(0,base_dir)
    sys.path.insert(0,os.path.dirname(base_dir))