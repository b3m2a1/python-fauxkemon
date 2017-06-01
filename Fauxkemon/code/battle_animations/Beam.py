import math

class BeamAnimation:
    
    def __init__(self,animation,frame,step_rate=5):

        self.animation=animation
        self.animation.delete('all')
        self.step_rate=step_rate
        self.frame=frame
        self.image_link='Beam.png'
        self.ob1=None
        self.beam=None
        self.beam_image=None
        self.ob2=None
        self.step=0
        self.step_total=0
        self.base=None
        self.move_vector=None
        self.calculate_vector(animation,frame)
        
    def calculate_vector(self,a=None,f=None):
        
        vector=self.animation.vector
        self.animation.pass_obs=[]
        try:
            self.ob1=self.animation.pass_obs[0]
       	except IndexError:
            self.ob1=self.animation.add_file(.1,.9,'Pikachu',mode='frac',anchor='center')
        try:
             self.ob2=self.animation.pass_obs[1]
        except IndexError:
             self.ob2=self.animation.add_file(.9,.1,'Raichu',mode='frac',anchor='center')
        ob1,ob2=(self.ob1,self.ob2)
        self.base=base=self.frame.bbox(ob1)
        x1,y1,x2,y2=base
        #I=self.frame.image_hooks[ob1]
        #w,h=I.dimensions
        #x1+=w/2#;y1+=h
        #x1+=10
        #y1+=-20
        x3,y3,x4,y4=self.frame.bbox(ob2)
        x=x3-x2;y=y4-y1
        self.start_vector=vector(x2,y1)
        self.current_vector=vector(x2,y1)
        self.move_vector=move_vector=vector(x,y)
        self.step_total=int(move_vector.magnitude/self.step_rate)
        self.move_vector=move_vector.unit_vector
##        self.step_total=5
        

    def make_beam(self,a=None,f=None):
        
        ob1=self.ob1;ob2=self.ob2
        o=self.frame.coords(self.ob1)
        self.beam=beam=self.animation.add_file(o[0],o[1],'Beam.png',anchor='ne')
        self.beam_image=self.frame.image_hooks[self.beam]
        angle=self.animation.vector(1,0).angle(self.move_vector)
        w1,h1=self.beam_image.dimensions
        w2=w1*math.sin(angle)
        h2=h1*math.cos(angle)
        self.beam_image.rotate(angle,expand=True)
##        self.current_vector[0]+=(w1-w2)/2
        self.current_vector+=(h1/2,(h2-h1)/2)
        self.frame.coords(self.beam,*self.current_vector)
        self.beam_image.set_base_image()
        self.frame.tag_lower(beam,ob1)
        self.frame.display_rectangle(beam,.99)
        self.image_width=self.beam_image.width

    def move_beam(self,a=None,f=None,steps=None):
        if steps is None:
            steps=self.step_rate
        self.current_vector+=self.move_vector*steps
        x,y=self.current_vector
        self.frame.coords(self.beam,int(x),int(y))
        self.step+=1
        v_w=abs(self.current_vector[0]-self.start_vector[0])
        q=v_w/self.image_width
        self.animation.revert_ob(self.beam)
        self.frame.display_rectangle(self.beam,1-q)
        self.frame.tint_ob(self.beam,g=100)
##        self.frame.hold_update(100)
    
    def end(self,a=None,f=None):
        self.frame.delete('all')

def load_animation(animation,parent):
    A=BeamAnimation(animation,parent)
    return [A.make_beam]+[A.move_beam]*A.step_total+[A.end]

























