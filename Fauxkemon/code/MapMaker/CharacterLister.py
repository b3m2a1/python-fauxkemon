from .Shared import *
chars=getdir('characters')

class CharacterLister(tk.Listbox):
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
        self.insert('end','Select Characters')
        if source is None:
            sources=os.listdir(chars)
            source=sources[0]
            if not os.path.isdir(os.path.join(chars,source)):
                source=sources[1]
        sp=os.path.join(chars,source)
        self.src=tk.StringVar(value=source)
        for x in os.listdir(sp):
            p=os.path.join(sp,x)
            if os.path.isdir(p):
                self.insert('end',x)
        self.char=None
        self.bind('<Button-1>',lambda e:self.after_idle(self.charset))
        ops=[x for x in os.listdir(chars) if os.path.isdir(os.path.join(chars,x))]
        self.ops=tk.OptionMenu(f,self.src,*ops,command=lambda *e:self.reload())
        self.reload()
        self.ops.grid(row=0,column=0,columnspan=2,sticky='ew')                                                                          
        self.grid(row=1,column=0,sticky='nsew')
        sc.grid(row=1,column=1,sticky='ns')
        f.grid_rowconfigure(1,weight=1)

        self.pack=f.pack

    @property
    def source(self):
        return self.src.get()
            
    def charset(self):
        e=self.get('anchor')
        toSet=e
        if toSet=='No Selection':
            toSet=None
        elif toSet=='Select Characters':
            toSet='Select'
        self.char=toSet
        self.root.Deselect()
            
    def reload(self):
        self.delete(0,'end')
        self.insert('end','No Selection')
        self.insert('end','Select Characters')
        sp=os.path.join(chars,self.source)
        for x in os.listdir(sp):
            p=os.path.join(sp,x)
            if os.path.isdir(p):
                self.insert('end',x)
        self.char=None
##        self.root.Deselect()
