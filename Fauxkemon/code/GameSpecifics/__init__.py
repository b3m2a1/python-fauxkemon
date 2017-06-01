import os,sys

new_d=os.path.join(os.path.dirname(__file__),game_source)
sys.path.insert(0,new_d)

try:
    from battle_statuses import *
    from catch_algorithm import *
    from effect_calculator import *
except:
    raise
finally:
    sys.path.pop(0)
