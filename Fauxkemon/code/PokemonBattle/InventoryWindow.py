from .config import *
from ..DataTypes import Item,ItemClass

#Needs a serious revamp
#Allow for automatic return of the appropriate item
#Add in support for standardizing

class InventoryWindow(tk.Frame):

    def __init__(self,root,inventory,controller=None,**kwargs):
    
        super().__init__(root,**kwargs)
        Standardizer.standardize(self,'battle')
        
        if controller is None:
            controller=self.master
        self.controller=controller
        
        if not isinstance(inventory,dict):
            if hasattr(inventory,'count'):
                inventory={x:inventory.count(x) for x in set(inventory)}
            else:
                new={}
                for x in inventory:
                    try:
                        new[x]+=1
                    except AttributeError:
                        new[x]=1
                inventory=new
        
        self.inventory=inventory
        self.selected=None
        self.list_box=None# FormattingGrid(self,columns=2,
#             active=Standardizer.standard_select,
#             inactive=Standardizer.standard_frame,
#             selectable=True)
        self.sb_frame=None
        self.anchor_point=None
        self.bindings=pan_bindings=(Binding('<Up>',lambda e:self.pan(-1)),
                      Binding('<Down>',lambda e:self.pan(1)))
        self.bind('<Expose>',self.select)
        
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        for b in pan_bindings:
            b.apply(self)
        self.load()
    
    @property
    def current_item(self):
        item=self.list_box.get('current').item
        if not item is None:
            item=Item(item['text'])
        return item
        
    def pan(self,q):
        ap=self.list_box.focus_point[0]
        ap=ap+q
        if ap>=0:
            try:
                w=self.list_box.get(ap,0)
            except IndexError:
                pass
            else:
                if not w is self.list_box.Empty:
                    self.select(widget=w)
                    mx,my,MX,MY=self.list_box.display_rectangle
                    if ap<my or ap>=my+4:
                        self.set_view(q,increment=True)

    def deselect(self):
        
        ap=self.selected.anchor_point
        
    def select(self,event=None,widget=None):
        if not widget is None:
            w=widget
        else:
            w=event.widget
        if w is self:
            w=self.list_box.get(*self.list_box.focus_point)
        if not self.selected is None:
            self.deselect()
        self.selected=w
        w.focus_set()

    def cget(self,option):
        try:
            r=super().cget(option)
        except TclError:
            r=self.controller.cget(option)
        return r

    def adjust(self,item,amt=None):
        if amt is None:
            if isinstance(item,int):
                amt=item
                item=self.current_item
        item=item.name if isinstance(item,ItemClass) else item    
        try:
            self.inventory[item]+=-(amt)
        except TypeError:
            pass
        self.load()
        
    def set_view(self,my,offset='',increment=False):
        mx,min_y,MX,MY=self.list_box.display_rectangle
        if not offset=='':
            my=offset
        if isinstance(my,str):
            my=float(my)
        if increment:
            my=min_y+my
        elif isinstance(my,float):
            if my>=0:
                self.list_box.SetView(rel_y=my)
                mx,my,MX,MY=self.list_box.display_rectangle
        if my>=0:
            r,c=self.list_box.commands.dimensions
            MY=my+4
            if MY>=r:
                MY=r
                my=max(MY-4,0)
            self.list_box.SetView(my=my,MY=MY)
            r,c=self.list_box.commands.dimensions
            self.sb.set(my/r,MY/r)
##        self.list_box.display_rectangle=(0,1,3,5)
        
    def load(self):

        if not self.list_box is None:
            self.list_box.destroy()
        if not self.sb_frame is None:
            self.sb_frame.destroy()
        try:
            self.list_box=FormattingGrid(self,rows=0,columns=1,
                active=Standardizer.standard_select,
                inactive=Standardizer.config_map['battle'],
                selectable=True)
        except:
            pass
        else:
            self.list_box.display_rectangle=(0,0,1,4)
            self.sb_frame=tk.Frame(self)
            self.sb=tk.Scrollbar(self.sb_frame,command=self.set_view)
            self.sb.pack(fill='both',expand=True)
            self.sb.activate('slider')
            
            def fake_event(key,sel,self=self):
                self.focus_set()
                self.after_idle(lambda:sel.event_generate(key))
            cur=0   
            for x,q in self.inventory.items():
                if q>0:
                    sel=self.list_box.AddFormat(UniformityFrame)
                    
                    sel.gridConfig(sticky='nsew',ipady=2)
                    sel.item=tk.Label(sel,text=x);sel.anchor_point=cur
                    sel.item.grid(row=0,column=0,sticky='w')
                    
                    sel.quantity=tk.Label(sel,text='x {}'.format(q))
                    sel.quantity.grid(row=0,column=1,sticky='e')
                    
                    sel.grid_columnconfigure(0,weight=1)
                    
                    for w in (sel.item,sel.quantity):
                        w.bind('<Button-1>',lambda e,s=sel,self=self:self.select(widget=s))
                        sel.do_not_configure(w,'relief')
                    a_press='<KeyPress-{}>'.format(self.controller.a_button)
                    b_press='<KeyPress-{}>'.format(self.controller.b_button)
                    sel.bind(a_press,lambda e,a=a_press:fake_event(a_press,sel))
                    sel.bind(b_press,lambda e,a=b_press:fake_event(b_press,sel))
                    Standardizer.standardize(sel,sel.item,sel.quantity,'battle')
                    for b in self.bindings:
                        b.apply(sel)
                    cur+=1
            
            close=self.list_box.AddFormat(tk.Label,text='Close');close.grid_config(sticky='w',ipady=2)
            close.item=None;close.quantity=None;close.anchor_point=cur
            close.bind('<Button-1>',lambda e,s=close,self=self:self.select(widget=s))
            a_press='<KeyPress-{}>'.format(self.controller.a_button)
            b_press='<KeyPress-{}>'.format(self.controller.b_button)
            close.bind(a_press,lambda e,a=a_press:fake_event(a_press,close))
            close.bind(b_press,lambda e,a=b_press:fake_event(b_press,close))
            for b in self.bindings:
                b.apply(close)
            
                    
#             self.list_box.grid_columnconfigure(1,minsize=50)
            self.list_box.configure_rows(weight=1,minsize=25)
            self.list_box.grid_configure(mode='row',sticky='nsew')
            
            self.list_box.grid(row=0,column=0,sticky='nsew')
            self.sb_frame.grid(row=0,column=1,sticky='ns')
            self.set_view(0)

            if self.anchor_point is None:
                self.select(widget=self.list_box.get(0,0))
