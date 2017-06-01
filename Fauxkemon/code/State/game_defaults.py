from Fauxkemon.code.State.base_modules import *

screen_tile_range=(9,9)
cell_pixels=(16,16)
screen_cell_scale=(3,3)
standard_screen_dimensions=tuple((int(r*p*q) for r,p,q in zip(
    screen_tile_range, cell_pixels, screen_cell_scale
    )))
tile_colorizing_ranges=((200,235),(150,200))
character_colorizing_ranges=((130,200),(200,235))
character_positioning=(0,.75)
a_button='a'
b_button='b'
start_button='space'
party_size=6


poke_font_config={
    'family':'PT Mono',
    'size':20
    }
def PokeFont(conf=poke_font_config):
    return FontObject(conf)

class StandardizerClass:
    
    standard_frame_color='white'
    standard_frame_style='flat'
    standard_font_color='black'
    standard_border_width=2
    standard_border_color='black'
    standard_border_style='ridge'
    standard_font=poke_font_config
    battle_font=poke_font_config.copy();battle_font['size']=12

    standard_frame={'bg':standard_frame_color,
                    'relief':standard_frame_style,
                    'fg':standard_font_color,
                    'font':standard_font,
                    'highlightthickness':0,
                    'cursor':'arrow'
                    }
    standard_battle=standard_frame.copy()
    standard_battle['font']=battle_font
    standard_border={'bd':standard_border_width, 
                     'bg':standard_border_color,
                     'relief':standard_border_style}
    standard_select={'fg':'blue',
                    'bg':'grey95',
                    'bd':2,
                    'relief':'ridge'}
    def __init__(self):
        self.tracking={}
    @property
    def configuration_map(self):
        return {'frame':self.standard_frame,
                'border':self.standard_border,
                'select':self.standard_select,
                'battle':self.standard_battle}
    config_map=configuration_map
    def standardize(self,*widgets,conf='frame',standardize=None):
        if isinstance(widgets[-1],str):
            conf=widgets[-1]
            widgets=widgets[:-1]
        conf_key=conf
        conf=self.configuration_map[conf]
        if 'font' in conf:
            if isinstance(conf['font'],(dict,tuple)):
                font_base=PokeFont(conf['font'])
                conf['font']=PokeFont(font_base)
                if font_base is self.standard_font:
                    type(self).standard_font=self.standard_font=conf['font']
                elif font_base is self.battle_font:
                    type(self).battle_font=self.battle_font=conf['font']
        if widgets==():
            widgets=self.tracking
        for w in widgets:
            self.tracking[str(w)]=w
            try:
                keys=w.config()
            except:
                del self.tracking[str(w)]
            else:
                if standardize is None or type(w)==standardize or isinstance(w,standardize):
                    cd={k if k in keys else None:conf[k] for k in conf}
                    if None in cd:
                        del cd[None]
                    w.config(**cd)
                    if len(widgets)==1:
                        return cd
    
    def standardize_recursive(self,widget,conf='frame',standardize=None):
        self.standardize(widget,conf=conf,standardize=standardize)
        for child in widget.children.values():
            self.standardize_recursive(child,standardize=standardize,conf=conf)
                    
    def config(self,conf='frame',**kw):
        conf_d=self.configuration_map[conf]
        conf_d.update(kw)
        self.standardize(conf=conf)
        
Standardizer=StandardizerClass()
def BorderedFrame(root,cls=tk.Frame,**kw):
    kw=dict(Standardizer.standard_border,**kw)
    return cls(root,**kw)
    

