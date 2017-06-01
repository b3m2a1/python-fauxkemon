from Fauxkemon.code.State.base_modules import *

project_title='Fauxkemon'
base=os.getcwd()
if not os.path.basename(base)==project_title:
    base=os.path.join(base,project_title)

character_path='Characters'
poke_path='Pokemon'
map_path='Maps'
save_path='Save-State'
tile_path='Tiles'
data_source='Source Data'
code_path='code'
game_path='Games'
attack_path='Attacks'
trainer_path='Trainers'
item_path='Items'
event_lib='event_lib'
eff_lib='effect_lib'
animation_path='battle_animations'
sprite_extension='__trainer_sprites__'
game_spec_data='GameSpecifics'
misc_path='misc'

fauxkemon_directories={
    'base':base,
    'data':('base',data_source),
    'characters':('data',character_path),
    'pokemon':('data',poke_path),
    'maps':('data',map_path),
    'saves':('games',save_path),
    'tiles':('data',tile_path),
    'code':('base',code_path),
    'events':('code',event_lib),
    'animations':('code',animation_path),
    'attacks':('data',attack_path),
    'games':('base',game_path),
    'trainers':('data',trainer_path),
    'trainer_sprites':('trainers',sprite_extension),
    'items':('data',item_path),
    'game_specifics':('code',game_spec_data),
    'misc':('data',misc_path),
    'battle_effects':('code',eff_lib)
    }

def getdir(name):
    d=fauxkemon_directories[name]
    if not isinstance(d,str):
        p=getdir(d[0])
        d=os.path.join(p,d[1])
    return d

Loader=PathLoader()
