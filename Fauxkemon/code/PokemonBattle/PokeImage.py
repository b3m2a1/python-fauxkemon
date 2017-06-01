from .config import *

class PokeImage:
    
    def __init__(self,root,pokemon,mode,**kwargs):
    
        self.parent=self.canvas=self.battle=root
        self.pokemon=P=pokemon
        self.canvas_obs=None
        if mode==root.enemy_key:
            img='front'
            
        else:
            img='back'
        self.image=self.im=ImageWrapper(os.path.join(P.dir,img+'.png'))
        if img=='front':
            self.image.transpose('flip horizontal')
            self.image.set_base_image()

        self.original=self.image.image
        self.mode=mode
        self.info_tab=UniformityFrame(root,
                                      bg=battle_screen_bg)
        h1,h2=(self.pokemon.health,self.pokemon.max_health)
        barmode='pill'
        self.bar=FillBar(self.info_tab,h1,h2,width=100,height=15,
                         bg=battle_screen_bg,
                         color=battle_screen_hb_color,
                         mode=barmode)
        
        self.poke_name=tk.Label(self.info_tab,
                                text=self.pokemon.name,
                                bg=battle_screen_bg,
                                fg=battle_screen_fg)
        
        self.poke_name.pack(side='top',anchor='w')
        self.poke_level=tk.Label(self.info_tab,text=':L{}'.format(self.pokemon.level))
        self.poke_level.pack(side='top')
        self.bar.pack(side='top')
        Standardizer.standardize_recursive(self.info_tab,'battle')
        if self.mode==root.enemy_key:
            self.draw_anchors=('ne','nw')
            self.health_label=None
        else:
            self.health_label=tk.Label(self.info_tab,text='{: >3}/{: >3}'.format(h1,h2))
            self.health_label.pack(side='top')
            self.draw_anchors=('sw','se')
            Standardizer.standardize_recursive(self.health_label,'battle')
        

    def draw(self,x,y,X,Y,padx=0,pady=0,**kwargs):
        
        a1,a2=self.draw_anchors
        self.p_img=self.image.Tk
        self.canvas_obs=[
            self.canvas.create_image(x+padx,y,anchor=a1,image=self.p_img,**kwargs),
            self.canvas.create_window(X-padx,Y+pady,anchor=a2,window=self.info_tab)
            ]
        
    def set_image(self,img=None):
        if img is None:
            img=self.image.Tk
        self.canvas.itemconfig(self.canvas_obs[0],image=img)
        
    def update(self,change_max=False):
        
        m=self.bar.val
        end=to=self.pokemon.health
        inc=-1
        if m<to:
            inc=1
        to+=inc
        
        H=self.health_label
        if not H is None:
            H.config(text='{: >3}/{: >3}'.format(self.pokemon.health,self.pokemon.max_health))

        i=m
        for i in range(m,to,inc):
            self.bar.update(i)
            self.battle.hold_update(5)
        self.bar.val=i
