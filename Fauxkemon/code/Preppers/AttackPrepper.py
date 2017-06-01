from ._shared import *
        
class AttackPrepper:

    atk_link='http://bulbapedia.bulbagarden.net/wiki/{}_(move)'
    gen_link='http://bulbapedia.bulbagarden.net/wiki/{}_(move)#In_other_generations'
    img_link='http://bulbapedia.bulbagarden.net/wiki/File:{}_I.png'
    png_link='http://cdn.bulbagarden.net/upload/{}/{}{}/{}_I.png'
    eff_link='http://bulbapedia.bulbagarden.net/wiki/{}_(move)#Effect'
    
    test_keys=string.digits+string.ascii_lowercase
    
    def __init__(self,base=None,to_where=None,file_src=None):
        if base is None:
            base='~/Desktop'
        self.src=base
        if to_where is None:
            to_where=self.src
        self.to=to_where
        if file_src is None:
            file_src='~/Documents/Python/Projects/Fauxkemon/Source Data/Attacks'
        self.files=file_src
        self.look_up=None

    def collect_attacks(self,file,out_ext='attack_folder'):
        out_dir=os.path.join(self.to,out_ext)
        in_file=os.path.join(self.src,file)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        form_lam=lambda k:(lambda v:('{}: {}'.format(k,v.lower())))
        name_lam=lambda k:(lambda v:('#{}: {}#'.format(k,v)))
        def acc_pro(k,v):
            try:
                v=float(v.strip('%'))/100
            except:
                v=1
            return '{}: {}'.format(k,v)
        acc_lam=lambda k:lambda v:acc_pro(k,v)
        format_keys={x:None for x in ('NUM','NAME','TYPE','EFF','CAT','PP','POW','PRI','ACC')}
        write_map={'NAME':name_lam('MOVE'),
                   'TYPE':form_lam('type'),
                   'CAT':form_lam('mode'),
                   'POW':form_lam('attack'),
                   'ACC':acc_lam('hit_rate'),
                   'PP':form_lam('pp'),
                   'EFF':'effect: none_0',
                   'PRI':'priority: 1'}
        write_order=('NAME','TYPE','CAT','POW','EFF','ACC','PRI','PP')

        prop_num=-1
        with open(in_file) as src:
            for line in src:
                line=line.strip()
                if line:
                    bits=line.split()
                    if '#FORMAT' in bits[0]:
                        for k in bits:
                            format_keys[k]=prop_num
                            prop_num+=1
                        break
            for line in src:
                line=line.strip()
                if line:
                    bits=line.split()
                    fkn=format_keys['NAME']
                    if len(bits)>prop_num:
                        flarp=1+fkn+len(bits)-prop_num
                        atk_name=' '.join(bits[fkn:flarp])
                        bits=bits[:fkn]+[atk_name]+bits[flarp:]
                    name=bits[fkn]
##                    print(name)
                    with open(os.path.join(out_dir,name+'.txt'),'w+') as atk:
                        for k in write_order:
                            v=format_keys[k]
                            if v is None:
                                atk.write(write_map[k]+'\n')
                            else:
                                atk.write(write_map[k](bits[v].strip('*'))+'\n')

    def load_status_moves(self,status_move_file,dir_ext):
        atk_dir=os.path.join(self.to,dir_ext)
        in_file=os.path.join(self.src,status_move_file)
        format_keys={x:None for x in ('NAME','TYPE','EFF','CAT','POW','ACC','PP')}
        order=[]
        prop_num=0
        with open(in_file) as data:
            for line in data:
                line=line.strip()
                if line:
                    bits=line.split()
                    if '#FORMAT' in bits[0]:
                        for k in bits[1:]:
                            format_keys[k]=prop_num
                            order.append(k)
                            prop_num+=1
                        break
            assert order==['NAME','TYPE','CAT','POW','ACC','PP','EFF']
            for line in data:
                line=line.strip()
                if line:
                    bits=line.split()
                    effect_flag=False
                    i=0
                    for b in bits:
                        try:
                            int(b)
                        except ValueError:
                            if effect_flag:
                                rest=bits[:i]
                                effect=bits[i:]
                                break
                        else:
                            effect_flag=True
                        i+=1
##                    print(rest,effect)
##                    prop_num=prop_num-1
                    if len(rest)>prop_num-1:
                        for i in range(1+len(rest)-prop_num):
                            rest[0]+=' '
                            rest[0]+=rest.pop(1)
                    name=rest[format_keys['NAME']]
                    try:
                        f=self.find_attack(name,atk_dir)
                    except FileNotFoundError:
                        print('No: '+name)
                        continue
                    s=self.complex_effect_parse(effect)
                    if not s is None:
                        bck=os.path.join(atk_dir,name+'_old')
                        shutil.copy(f,bck)
    ##                    try:
                        with open(bck) as old:
                            with open(f,'w+') as new:
                                for line in old:
                                    l=line.strip()
                                    if l:
                                        bits=line.split(':',1)
                                        if 'effect' in bits[0]:
                                            if 'none_0' in bits[1]:
                                                new.write('effect:{}\n'.format(s))
                                            else:
                                                new.write(line)
                                        else:
                                            new.write(line)
                        os.remove(bck)
##                    except:
##                        raise
##                    finally:
####                        shutil.copy(bck,f)
####                        os.remove(bck)
####                        raise
                                
    def format_moves(self,dir_ext):
        keys=('type','mode','attack','effect','hit_rate','hits','turns','priority','pp')
        formatting={'type':'-','mode':'-','attack':'-','effect':'none_0',
                    'hit_rate':'1','priority':1,'pp':0,'hits':1,'turns':1}
        atk_dir=os.path.join(self.to,dir_ext)
        for f in os.listdir(atk_dir):
            f=self.find_attack(f,atk_dir)
            n,e=os.path.splitext(f)
            if e=='.txt':
                do=False
                try:
                    with open(f,encoding='utf-8') as src:
                        lines=[]
                        i=0
                        for l in src:
                            lines.append(l)
                            i+=1
                            if '#MOVE' in l:
                                do=True
                                break
                        if do:
                            start=i
                            to_do=list(keys)
                            extras=[]
                            for line in src:
                                i+=1
                                try:
                                    k,v=line.split(':',1)
                                except ValueError:
                                    continue
                                if k in to_do:
                                    to_do.remove(k)
                                else:
                                    extras.append(i)
                                lines.append(line)
                            for k in to_do:
                                i=keys.index(k)
                                for x in extras:
                                    if x<=i:
                                        i=x+1
                                lines.insert(i+1,'{}:{}\n'.format(k,formatting[k]))
##                        print(''.join(lines))
                    with open(f,'w+') as out:
                        out.write(''.join(lines))
##                            raise
                except UnicodeDecodeError:
                    print(f)
                    raise
                            
                        
        
    def load_effects(self,effect_file,dir_ext):
        atk_dir=os.path.join(self.to,dir_ext)
        in_file=os.path.join(self.src,effect_file)
        format_keys={x:None for x in ('NAME','TYPE','EFF','CAT','CHANCE')}
        order=[]
        prop_num=0
        with open(in_file) as data:
            for line in data:
                line=line.strip()
                if line:
                    bits=line.split()
                    if '#FORMAT' in bits[0]:
                        for k in bits[1:]:
                            format_keys[k]=prop_num
                            order.append(k)
                            prop_num+=1
                        break
            assert order==['NAME','TYPE','CAT','CHANCE','EFF']
            for line in data:
                line=line.strip()
                if line:
                    bits=line.split()
                    i=0
                    for b in bits:
                        i+=1
                        if '%' in b:
                            effect=bits[i:][:]
                            rest=bits[:i]
                            break
                    else:
                        print(line)
                        raise
                    if len(rest)>prop_num-1:
                        name=' '.join(rest[:])
                        for i in range(1+len(rest)-prop_num):
                            rest[0]+=' '
                            rest[0]+=rest.pop(1)
                    name=rest[format_keys['NAME']]
                    chance=rest[format_keys['CHANCE']]
                    chance=float(chance.strip('%'))/100
                    effect=self.parse_effect(effect)
                    effect='{}_{}'.format(effect,chance)
                    try:
                        file=self.find_attack(name,atk_dir)
                    except:
                        continue
                    else:
                        hold_file=os.path.join(atk_dir,name+'_old.txt')
                        shutil.copy(file,hold_file)
                        with open(hold_file) as hf:
                            with open(file,'w+') as old:
                                for line in hf:
                                    s=line.split(':',1)
                                    if s[0]=='effect':
                                        old.write('effect:{}\n'.format(effect))
                                    else:
                                        old.write(line)
                        os.remove(hold_file)

    def complex_effect_parse(self,effect_list):
        #fields_to_fille=['obj','direction','what','quantity']
##        next=random.choice([
        next_key='next'
        fields={'obj':False,
               'direction':False,
               'quantity':False,
                'stat':False,
               'hits':False,
               'what':False}
        key={'obj':
             {'user':'user','inflicts':'target','opponent':'target','target':'target'},
             'direction':
             {'lower':'-','raise':'+','receives':'-','inflicts':'-','recover':'+'},
             'quantity':
              {'sharply':'2','half':'.5','recoil':'.25','quarter':'.25',int:int},
             'hits':
              {'hits':next_key,'hits twice':2,'hits 2-5':'2-5'},
             'stat':
             {'hp':'hp','special':next_key,'defense':'defense','attack':'attack',
              'special defense':'special_defense','special attack':'special_attack',
              'accuracy':'accuracy','speed':'speed'},
             'what':
             {'faints':'faints','damage':'dmg','hp':next_key,'hp inflicted':'dmg',
              'confuse':'confuse','paralyze':'paralysis','burn':'burn','freeze':'freeze',
              'poison':'poison','badly':next_key,'badly poisions':'toxic','flinch':'flinch',
              'switch':'switch','sleep':'sleep'}
             }
        E=iter((x.lower().strip('.') for x in effect_list))
        for e in E:
            #figure out the object
            for f,v in fields.items():
                if v is False:
                    key_map=key[f]
                    for k,v in key_map.items():
                        if isinstance(k,str):
                            if k in e:
                                while v==next_key:
                                    try:
                                        k+=' '+next(E)
                                    except StopIteration:
                                        v=False
                                    else:
                                        try:
                                            v=key_map[k]
                                        except KeyError:
                                            v=False
                                fields[f]=v
                                break
                        else:
                            try:
                                v(e)
                            except ValueError:
                                continue
                            else:
                                fields[f]=e
                                break
        if fields['direction'] is not False and fields['quantity'] is False:
            fields['quantity']='1'
        if fields['obj'] is False:
            string=None
        else:
            string=fields['obj']+'_'
            flag=False
            for x in ('stat','direction','quantity','what'):
                if fields[x] is not False:
                    flag=True
                    string+=fields[x]
            if not flag:
                string=None
        return string

                
    def simple_effect_parse(self,effect_list):
        effect=effect_list
        b=effect[0]
        if b in ('Lowers','Raises'):
            obj=effect[1:3]
            how_much=effect[-2]
            stat=effect[3:-3]
            stat='_'.join(stat).lower()                
            if b=='Lowers':
                op='-'
            else:
                op='+'
            if 'target' in obj[1]:
                obj='target'
            else:
                obj='user'
            return '{}_{}{}{}'.format(obj,stat,op,how_much)
        
        elif b in ('Inflicts',):
            obj=effect[-2:]
            if 'target' in obj[1]:
                obj='target'
            else:
                obj='user'
            what=effect[1:-3]
            what=[x.strip(',').lower() for x in what if not x=='or']
            return '{}_{}'.format(obj,'|'.join(what))
        else:
##            print(effect_list)
            return 'none'
                            
                        

    def find_attack(self,name,directory):
        file=os.path.join(directory,name)
        if not os.path.exists(file):
            c=name.count(' ')
            if c==0:
                i=1
                for x in name[1:]:
                    if x.isupper():
                        new=name[:i]+' '+name[i:]
                        file=os.path.join(directory,new+'.txt')
                        break
                    i+=1
        if not os.path.exists(file):
            new=name.replace(' ','')
            file=os.path.join(directory,new+'.txt')
        if not os.path.exists(file):
            new=name.replace('-',' ')
            file=os.path.join(directory,new+'.txt')
        if os.path.exists(file):
            return file
        else:
            raise FileNotFoundError('No attack {}'.format(name))
    
    def open_move(self,name,mode='img'):
        from GeneralTools.PlatformIndependent import open_file

        link=[None,None]        
        if mode=='img':
            link[0]=self.img_link.format(name)
        elif mode=='eff':
            link=self.eff_link.format(name)
        elif mode=='png':
            P=mp.Pool(5,maxtasksperchild=5)
            P.break_flag=False
            def pool_back(R,P=P):
                l=R
                P.terminate()
                P.break_flag=True
                open_file(l,'Google Chrome')
            for x in self.test_keys:
                for y in self.test_keys:
##                    for z in self.test_keys:
                    l=self.png_link.format(x,x,y,name)
##                        l=self.png_link.format(1,1,'b','Tackle')
                    P.apply_async(pool_call_function,(l,),callback=pool_back)
##                        if P.break_flag:
##                            break
                    if P.break_flag:
                        break
                if P.break_flag:
                    link=P.link
                    break
                            
                        
        else:
            link[0]=self.atk_link.format(name)
        if link[0]:
            open_file(link[0],'Google Chrome')

    def attack_browser(self,dir_name,root=None):
        fo=os.path.join(self.src,dir_name)
        if root is None:
            processing=P=tk.Tk()
        else:
            processing=P=root
        P.title('Attack Browser')
        L=tk.Listbox(P)
        var=tk.StringVar(value='img')
        C=tk.OptionMenu(P,var,'img','eff','atk','tm','png')
        for f in os.listdir(fo):
            n,e=os.path.splitext(f)
            if n and e=='.txt':
                L.insert('end',n)
        def cmd(E=None,P=P):
            P.S.open_move(L.get('anchor'),mode=var.get())
                          
        B=tk.Button(P,text='open attack',command=cmd)
        L.bind('<Double-Button-1>',cmd)
        L.bind('<Return>',cmd)
        P.S=self
        P.v=var;P.C=C;P.L=L
        C.pack()
        L.pack()
        B.pack()

def pool_call_function(link):
    urllib.request.urlopen(link)
    return link