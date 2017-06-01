#PuffAnimation.py animation loader

#This file needs to define either a function, load animation,
#or an iterable, animation
#
#The function load_animation takes an animation instance and an animation frame
#and optional arguments and keywords and must return an iterable of functions
#in no arguments.
#
#The animation iterable is an iterable of functions in no arguments
#
#If load_animation is defined the animation_instance calls it and
#adds the functions produced to its call list
#
#Otherwise if animation is defined the animation_instance adds the functions
#in the iterable to its call list

##DEFINE VIA ITERABLE##
#animation=()

##DEFINE VIA FUNCTION##
class Puff:
    
    def __init__(self,animation_instance,animation_frame,center_ob_id=None):
        
        self.animation=animation_instance
        self.frame=animation_frame
        if center_ob_id is None:
            center_ob_id=self.animation.add_file(.5,.5,'Pokeball',mode='frac')
        elif not isinstance(center_ob_id,(int,str)):
            center_ob_id=center_ob_id[0]
        self.ob=center_ob_id
        self.current=None
        self.pos=0
        
    def find_center(self):
#        points=self.frame.bbox(self.ob)
#        x=sum( (p for p,i in zip(points,range(len(points))) if i%2==1))/2
#        y=sum( (p for p,i in zip(points,range(len(points))) if i%2==0))/2
        self.center=self.frame.coords(self.ob)#(x,y)
        
    def load_images(self):
        import os
        
        self.dir=os.path.join(self.frame.image_source,'Puff')
        puffs=sorted(os.listdir(self.dir))
        self.puffs=[os.path.join(self.dir,p) for p in puffs if os.path.splitext(p)[1]=='.png']
        self.num=len(self.puffs)
   
    def puff(self,*a,**k):
        
        if self.current is not None:
                self.animation.delete(self.current)
                
        if self.pos<self.num:
            puff=self.puffs[self.pos]
            self.current=self.animation.add_file(self.center[0],self.center[1],puff)
            self.pos+=1
        
        
def load_animation(animation_instance,animation_frame,center_ob_id=None):
   
    A=Puff(animation_instance,animation_frame,center_ob_id)
    A.find_center();A.load_images();
    
    animation=[A.puff]*(A.num+1)#+[lambda *a,anm=animation_instance:anm.delete('all')]
    
    return animation






