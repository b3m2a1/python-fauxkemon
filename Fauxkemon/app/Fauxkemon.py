import shim, sys, os

from GUITools import *

gid=sys.argv[2] if len(sys.argv)>2 else ''
if not gid.strip():
    gid=None
    vid=None
else:
    vid=sys.argv[3]
    if not vid.strip():
        vid='Pokemon Yellow'

import Fauxkemon

# from Fauxkemon.code.GameInterface import GameRoot

Fauxkemon.code.GameRoot().mainloop()
