#Fauxkemon's __init__
import os,sys
f_path = os.path.dirname(os.path.dirname(__file__))
if not f_path in sys.path:
    sys.path.insert(0,f_path)
del f_path
import Fauxkemon.code
