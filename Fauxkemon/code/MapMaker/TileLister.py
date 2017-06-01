from .Shared import *

class TileLister(tk.Listbox):
    def __init__(self,root,source=None,**kwargs):
        f=tk.Frame(root)
        super().__init__(f,**kwargs)
        r=root
        while not hasattr(r,'Deselect'):
            r=r.master
        self.root=r
        sc=tk.Scrollbar(f,command=self.yview)
        self.config(yscrollcommand=sc.set)
        self.insert('end','No Selection')
        self.insert('end','Select Tiles')
        self.bind('<Button-1>',lambda e:self.after_idle(self.tileset))
        self.trf=None
        tls=os.listdir(tiles)
        if source is None:
            source=tls[0]
            if not os.path.isdir(os.path.join(tiles,source)):
                source=tls[1]
        self.src=tk.StringVar(value=source)
        ops=[]
        for i in range(len(tls)):
            r=self.source_test(tls[i])
            if r:
                ops.append(r)
        self.reload()
        self.ops=tk.OptionMenu(f,self.src,*ops,command=lambda *e:self.reload())
        self.ops.grid(row=0,column=0,columnspan=2,sticky='ew')                                                                          
        self.grid(row=1,column=0,sticky='nsew')
        sc.grid(row=1,column=1,sticky='ns')
        f.grid_rowconfigure(1,weight=1)
        self.pack=f.pack

    @property
    def source(self):
        return self.src.get()

    def source_test(self,x):
        f=os.path.join(tiles,x)
        ret=False
        if os.path.isdir(f):
            ret=x
            
        return ret

    def tile_test(self,x,source=''):
        f=os.path.join(source,x)
        ret=False
        if os.path.isdir(f):
            ret=x
            self.type_refs[ret]='tile'
        else:
            f,e=os.path.splitext(x)
            if e in ('tlf','.tlf'):
                ret=os.path.basename(f)
                self.type_refs[ret]='composite'
                
        return ret
            
    def tileset(self):
        e=self.get('anchor')
        toSet=e
        self.trf=None
        if toSet=='No Selection':
            toSet=None
        elif toSet=='Select Tiles':
            toSet='Select'
        elif toSet=='Blank':
            self.trf='tile'
        else:
            self.trf=self.type_refs[e]
        self.tile=toSet
        
        self.root.Deselect()
            
    def reload(self):
        self.type_refs={}
        self.delete(0,'end')
        self.insert('end','No Selection')
        self.insert('end','Select Tiles')
        sp=os.path.join(tiles,self.source)
        for x in os.listdir(sp):
            r=self.tile_test(x,sp)
            if r:
                self.insert('end',r)
        self.insert('end','Blank')
        self.tile=None
        if hasattr(self.root,'selected'):
            self.root.Deselect()
