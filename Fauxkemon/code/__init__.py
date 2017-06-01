#Fauxkemon.code's __init__
import os,sys

f_path=os.path.dirname(os.path.dirname(os.path.dirname((__file__))))
if not f_path in sys.path:
    sys.path.insert(f_path,0)
del f_path

from .GameInterface import *
