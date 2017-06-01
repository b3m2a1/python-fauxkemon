from ._shared import *

class PokemonPrepper:

    def __init__(self,base=None,to_where=None,file_src=None):
        if base is None:
            base='~/Desktop'
        self.src=base
        if to_where is None:
            to_where=self.src
        self.to=to_where
        if file_src is None:
            file_src='~/Documents/Python/Projects/Fauxkemon/Source Data/Pokemon'
        self.files=file_src

    def sprite_save(self,mode='back',source=None,to=None):
        if source is None:
            source=self.src
        if to is None:
            to=self.to
        for f in os.listdir(source):
            n,e=os.path.splitext(f)
            try:
                int(n)
            except:
                continue
            if e=='.png':
                d=os.path.join(to,n+'_')
                os.mkdir(d)
                f=os.path.join(source,f)
                shutil.copy(f,os.path.join(d,mode+'.png'))
                os.remove(f)

    def grid_chop(self,file_name,mode='row',**kwargs):
        if mode=='row':
            self.grid_chop_row(file_name,**kwargs)
        else:
            self.grid_chop_col(file_name,**kwargs)
            
    def grid_chop_row(self,file_name,to=None,grid_key=None,sensitivity=(1.5,1),
                  left_pad=0,right_pad=0,top_pad=0,bottom_pad=0,min_size=30):

        from GUITools.ImageTools import ImageWrapper

        if grid_key is None:
            grid_key=lambda p:(all((b<10 for b in p[:3])) and b[3]>100)
        if to is None:
            to=self.to
        else:
            to=os.path.join(self.src,to)
        im_f=os.path.join(self.src,file_name)
        I=ImageWrapper(im_f)
        #find horizontals first
        #then within each horiztonal, find the verticals
        #each time a grid is found, save that fucker.
        w=I.width
        c_it=I.col_iter(end=w//2,step=7)
        if sensitivity[0] is None:
            col_sensitvity=None
        else:
            col_sensitvity=w//(2*7*sensitivity[0])
        positions={}
        hors=[]
        for col in c_it:
            last=-1
            for p,pos in col:
                x,y=pos
                if grid_key(p):
                    if (y-last)>2:
                        try:
                            positions[y]+=1
                        except KeyError:
                            positions[y]=1
                    last=y
                #counts the black spots. Then max over these to, hopefully, get gridlines
        max_count=max((count for y,count in positions.items()))
        if col_sensitvity is None:
            col_sensitvity=max_count-1
        for y,count in positions.items():
            if count>max_count-col_sensitvity:
                hors.append(y)
        hors.extend((top_pad,I.height-bottom_pad))
        hors=sorted(hors)
        l=len(hors)
        to_remove=[]
        for i in range(l-1):
            y=hors[i]
            y2=hors[i+1]
            if y2-y<min_size:
                if i>1 and i+1<l:
                    y3=hors[i-1]
                    try:
                        y4=hors[i+2]
                    except IndexError:
                        to_remove.append(y2)
                        continue
                    
                    if (y3-y)<(y4-y2):
                        to_remove.append(y)
                    else:
                        to_remove.append(y2)
        for x in to_remove:
            hors.remove(x)

        row_sensitvity=3*sensitivity[1]
        l=len(hors)

        verts=[]
        it_1=iter(hors[:-1])
        it_2=iter(hors[1:])
        for y1,y2 in zip(it_1,it_2):
            r_it=I.row_iter(start=y1+1,end=y2-1,step=3)
            grid_lines=[]
            positions={}
            for row in r_it:
                last=-1
                for p,pos in row:
                    if grid_key(p):
                        x,y=pos
                        try:
                            positions[x]+=1
                        except KeyError:
                            positions[x]=1
            try:
                max_count=max((count for x,count in positions.items()))
            except ValueError:
                continue
            for x,count in positions.items():
                if count>max_count-(y2-y1)//row_sensitvity:
                    grid_lines.append(x)
            verts.append(sorted(grid_lines))
            del grid_lines
        last_h=0
        grid=[(x,v) for x,v in zip(hors[1:],verts)]
        n=1
        last_h=0
        for h,vs in grid:
            last_v=left_pad
            for v in vs:
                name='{}.png'.format(n)
                new=I.copyrectangle(last_v+1,last_h+1,v,h)
                new.save(os.path.join(to,name))
                last_v=v
                n+=1
            last_h=h

    def grid_chop_col(self,file_name,to=None,grid_key=None,sensitivity=(1.5,1),
                  left_pad=0,right_pad=0,top_pad=0,bottom_pad=0,min_size=30):

        from GUITools.ImageTools import ImageWrapper

        if grid_key is None:
            grid_key=lambda p:(all((b<10 for b in p[:3])) and b[3]>100)
        if to is None:
            to=self.to
        else:
            to=os.path.join(self.src,to)
        im_f=os.path.join(self.src,file_name)
        I=ImageWrapper(im_f)
        #find verticals first
        #then within each vertical, find the horizontals
        #each time a grid is found, save that fucker.
        h=I.height
        c_it=I.row_iter(end=h//2,step=7)
        if sensitivity[0] is None:
            row_sensitvity=None
        else:
            row_sensitvity=h//(2*7*sensitivity[0])
        positions={}
        hors=[]
        for col in c_it:
            last=-1
            for p,pos in col:
                y,x=pos
                if grid_key(p):
                    if (y-last)>2:
                        try:
                            positions[y]+=1
                        except KeyError:
                            positions[y]=1
                    last=y
                #counts the [grid_key returns true] spots. Then max over these to, hopefully, get gridlines
        max_count=max((count for y,count in positions.items()))
        if row_sensitvity is None:
            row_sensitvity=max_count-1
        for y,count in positions.items():
            if count>max_count-row_sensitvity:
                hors.append(y)
        hors.extend((left_pad,I.width-right_pad))
        hors=sorted(hors)
        l=len(hors)
        to_remove=[]
        for i in range(l-1):
            y=hors[i]
            y2=hors[i+1]
            if y2-y<min_size:
                if i>1 and i+1<l:
                    y3=hors[i-1]
                    try:
                        y4=hors[i+2]
                    except IndexError:
                        to_remove.append(y2)
                        continue
                    
                    if (y3-y)<(y4-y2):
                        to_remove.append(y)
                    else:
                        to_remove.append(y2)
        for x in to_remove:
            hors.remove(x)

        col_sensitvity=3*sensitivity[1]
        l=len(hors)

        verts=[]
        it_1=iter(hors[:-1])
        it_2=iter(hors[1:])
        for y1,y2 in zip(it_1,it_2):
            r_it=I.col_iter(start=y1+1,end=y2-1,step=3)
            grid_lines=[]
            positions={}
            for row in r_it:
                last=-1
                for p,pos in row:
                    if grid_key(p):
                        y,x=pos
                        try:
                            positions[x]+=1
                        except KeyError:
                            positions[x]=1
            try:
                max_count=max((count for x,count in positions.items()))
            except ValueError:
                continue
            for x,count in positions.items():
                if count>max_count-(y2-y1)//col_sensitvity:
                    grid_lines.append(x)
            verts.append(sorted(grid_lines))
            del grid_lines
        last_h=0
        grid=[(x,v) for x,v in zip(hors[1:],verts)]
        n=1
        last_h=0
        for h,vs in grid:
            last_v=top_pad
            for v in vs:
                name='{}.png'.format(n)
                new=I.copyrectangle(last_h,last_v,h,v)
                new.save(os.path.join(to,name))
                last_v=v+1
                n+=1
            last_h=h+1
            
    def sprite_merge(self,dir1,dir2,new,source=None,to=None):
        if source is None:
            source=self.src
        if to is None:
            to=self.to
        new=os.path.join(to,new)
        dir1=os.path.join(source,dir1)
        dir2=os.path.join(source,dir2)
        for x in os.listdir(dir1):
            d1=os.path.join(dir1,x)
            if os.path.isdir(d1):
                d2=os.path.join(dir2,x)
                if os.path.isdir(d2):
                    d3=os.path.join(new,x)
                    if not os.path.exists(d3):
                        os.mkdir(d3)
                    for f in os.listdir(d1):
                        shutil.copy(os.path.join(d1,f),os.path.join(d3,f))
                    for f in os.listdir(d2):
                        shutil.copy(os.path.join(d2,f),os.path.join(d3,f))

    def undo(self,folder):
        folder=os.path.join(self.src,folder)
        for d in folder:
            d=os.path.join(folder,d)
            bck=os.path.join(d,'backup.txt')
            fil=os.path.join(d,'props.txt')
            if os.path.exists(bck) and os.path.exists(fil):
                shutil.copy(bck,fil)
                
    def format_files(self,folder,name_file):
        folder=os.path.join(self.src,folder)
        name_file=os.path.join(self.src,name_file)
##        dir_iter=iter((x for x in os.listdir(folder) if os.path.isdir(os.path.join(folder,x))))

        file_params=(
                '#PROPERTIES (height in m, weight in kg)#',
                'type:',
                'height:',
                'weight:',
                'evolution:',
                'catch_rate:',
                '#BASESTATS#',
                'HP:',
                'attack:',
                'defense:',
                'special_attack:',
                'special_defense:',
                'speed:',
                '#MOVELIST#'
                     )
                     
        with open(name_file) as names:
            name_iter=iter(names)
            
            line_form={'NUM':[],'NAME':[],'TYPE':[]}
            for line in name_iter:
                l=line.split()
##                print(l)
                i=0
                if '#FORMAT' in l[0]:
                    for n in l[1:]:
##                        print(n)
                        line_form[n.strip()].append(i)
                        i+=1
                    break
##            print(line_form)
            name_ind=line_form['NAME'][0]
            num_ind=line_form['NUM'][0]
            type_inds=line_form['TYPE']
            for line in name_iter:
                l=line.split()
                n=l[name_ind]
                num=l[num_ind].strip('#')
                num=str(int(num))
                fo=os.path.join(folder,'{}_'.format(num))
                new=os.path.join(folder,'{}_{}'.format(num,n))
                if os.path.exists(fo) or os.path.exists(new):
                    try:
                        shutil.copytree(fo,new)
                    except FileNotFoundError:
                        pass
                    f=os.path.join(new,'props.txt')
                    l=line.split()
                    if os.path.exists(f):
                        bck=os.path.join(new,'backup.txt')
                        shutil.copy(f,bck)
                        with open(bck) as old:
                            with open(f,'w') as out:
                                to_write=list(file_params)
                                lines=[]
                                for line in old:
                                    for x in to_write:
                                        if line[:len(x)]==x:
                                            lines.append(line)
                                            to_remove=x
                                            break
                                    else:
                                        lines.append(line)
                                    if to_remove:
                                        to_write.remove(to_remove)
                                        to_remove=None
                                for x in to_write:
                                    i=file_params.index(x)
                                    lines.insert(i,x+'\n')
                                out.write(''.join(lines))
                                        
                                        
                    else:
                        with open(f,'w+') as out:
                            types=[]
                            for t in type_inds:
                                try:
                                    types.append(l[t].lower())
                                except IndexError:
                                    pass
                            lines=list(file_params);lines[1]='type:{}'.format(','.join(types))
                            out.write('\n'.join(lines))
                    try:
                        shutil.rmtree(fo)
                    except FileNotFoundError:
                        pass

    def find_pokemon(self,num_name,where=None,mode='dir'):
        learnset='http://bulbapedia.bulbagarden.net/wiki/{}_(Pok%C3%A9mon)/Generation_I_learnset'
        if where is None:
            where=self.src
        try:
            i=int(num_name)
            m_val=0
            num_name=str(i)
        except ValueError:
            m_val=1
        
        for x in os.listdir(where):
            f=os.path.join(where,x)
            if os.path.isdir(f):
                num,name=chk=x.split('_',1)
                if chk[m_val]==num_name:
                    if mode=='dir':
                        return f
                    elif mode=='learnset':
                        return learnset.format(name)
        else:
            raise FileNotFoundError('No pokemon found from {}'.format(num_name))
                
    def fill_stats(self,src_dir,file,source=None):

        #works as follows
        #find file format
        #get num and name
        #find props.txt
        #get stats
        #add where appropriate
        if source is None:
            source=self.src
        src_dir=os.path.join(source,src_dir)
        file=os.path.join(source,file)
        
        with open(file) as specs:
            format_keys={x:None for x in ('NAME','NUM','HP','ATK',
                                          'DEF','SPC','SPD')}
            key_map={'attack':'ATK','HP':'HP','defense':'DEF',
                     'special_attack':'SPC','special_defense':'SPC',
                     'speed':'SPD','BASESTATS':None}
            write_order=('HP','attack','defense','special_attack','special_defense',
                         'speed')
            for line in specs:
                l=iter(line.split())
                i=0
                if '#FORMAT' in next(l):
                    for p in l:
                        format_keys[p]=i
                        i+=1
                    break
                
            for line in specs:
                l=line.split()
                num=l[format_keys['NUM']]
                try:
                    p=self.find_pokemon(num,src_dir)
                except FileNotFoundError:
                    print(num)
                    continue
                prop_f=os.path.join(p,'props.txt')
                bck=os.path.join(p,'backup.txt')
                shutil.copy(prop_f,bck)
                s_flag=True
                with open(prop_f,'w+') as new:
                    with open(bck,'r') as old:
                        for subline in old:
                            if 'BASESTATS' in subline:
                                if s_flag:
                                    s_flag=False
                                    new.write(subline)
                                    for k in write_order:
                                        to=key_map[k]
                                        i=format_keys[to]
                                        new.write('{}: {}\n'.format(k,l[i]))
                            for k,form in key_map.items():
                                if k in subline:
##                                    new.write('{}:{}\n'.format(k,l[format_keys[form]]))
                                    break
                            else:
                                new.write(subline)

    def get_catchrates(self,poke_dir,catch_file):
        source=os.path.join(self.src,poke_dir)
        catch_file=os.path.join(self.src,catch_file)

        format_keys={'NAME':None,'NUM':None,'CAT':None}
        with open(catch_file) as src:
            for line in src:
                line=line.strip()
                if line:
                    bits=iter(line.split())
                    form=next(bits)
                    i=0
                    if '#FORMAT' in form:
                        for p in bits:
                            format_keys[p]=i
                            i+=1
                        prop_num=i
                        break
            for line in src:
                line=line.strip()
                if line:
                    bits=line.split()
                    nkey=format_keys['NAME']
                    if len(bits)>prop_num:
                        diff=len(bits)-prop_num
                        for i in range(diff):
                            bits.pop(nkey)
                        name=[]
                        for i in range(diff):
                            name.append(bits.pop(nkey))
                        name=' '.join(name)
                        bits.insert(nkey,name)
                        bits.insert(nkey,name)
                    name=bits[nkey]
                    num=bits[format_keys['NUM']]
                    catch_rate=bits[format_keys['CAT']].strip('*')
                    p=self.find_pokemon(name,where=source)
                    props=os.path.join(p,'props.txt')
                    bck=os.path.join(p,'backup.txt')
                    shutil.copy(props,bck)
                    key='catch_rate'
                    with open(bck) as old:
                        with open(props,'w') as new:
                            for line in old:
                                if key in line:
                                    new.write('{}: {}\n'.format(key,catch_rate))
                                else:
                                    new.write(line)
                        
        
    def fill_moveset(self,moveset_file,source=None,where=None):
        if source is None:
            source=self.src
        if where is None:
            where='Pokemon Yellow'
        where=os.path.join(self.src,where)
        f=os.path.join(source,moveset_file)
        def fill_moves(p_dir,iterator,prop_num):
            file=os.path.join(p_dir,'props.txt')
            bck=os.path.join(p_dir,'backup.txt')
            shutil.copy(file,bck)
            added=set()
            with open(file,'w+') as new:
                with open(bck) as old:
                    for line in old:
                        if '#MOVELIST#' in line:
                            new.write(line.strip()+'\n')
                            for line in iterator:
                                bits=line.split()
                                level=bits[0]
                                move=' '.join(bits[1:2+len(bits)-prop_num])
                                if 'Start' in level:
                                    level='0'
                                else:
                                    lev=''
                                    for b in level:
                                        if b.isdigit():
                                            lev+=b
                                        else:
                                            break
                                    level=lev
                                if not move in added:
                                    new.write('{} {}\n'.format(level,move))
                                    added.add(move)
                            break
                        else:
                            new.write(line)
                                          
                                    
        with open(f) as data:
            name_line=next(data)
            name=name_line.split()[0]
            p=self.find_pokemon(name,where)
            for line in data:
                bits=line.split()
                if 'Level' in bits[0]:
                    fill_moves(p,data,len(bits))
        return name
        

    def move_interface(self,where=None,root=None):
        from GeneralTools.PlatformIndependent import open_file
        
        if where is None:
            where='Pokemon Yellow'
        if root is None:
            processing=P=tk.Tk()
        else:
            processing=P=root
##        print(root)
        processing.title('Press to process file')
        E=tk.Entry(P)
        D=tk.Entry(P)
        D.insert(0,where)
        E.insert(0,'to_fill_moveset.txt')
        n=1
        where=self.src
        def open_next(where=where):
            nonlocal n
            w=os.path.join(where,'Pokemon Yellow')
            f=self.find_pokemon(n,where=w,mode='learnset')
            open_file(f,'Google Chrome')
            n+=1
            
        def lamb(event=None):
            B['text']=self.fill_moveset(E.get(),where=D.get())
            open_next()
            
        B=tk.Button(P,text='Click to Process',command=lamb)
        #B.did=tk.Label(P,text='-')
        E.grid(columnspan=2);D.grid(columnspan=2);B.grid(row=2,column=0)#;B.did.grid(row=2,column=0)