from ._shared import *

class ItemPrepper:

    basic_format=(
        '#{}#',
        'buy: {}',
        'sell: {}',
        'type: basic',
        'battle: {}',
        'uses: 1',
        'map: {}'
        )
    ball_format=(
        '#{}#',
        'buy: {}',
        'sell: {}',
        'type: ball',
        'uses: 1',
        'battle: {}'
        )
    key_format=(
        '#{}#',
        'buy: {}',
        'sell: {}',
        'type: key',
        'uses: -',
        'map: {}'
        )
    tm_format=(
        '#{}#',
        'buy: {}',
        'sell: {}',
        'type: tm',
        'uses: {}',
        'map: teach_{}'
        )
    def __init__(self,base=None,to_where=None,file_src=None):
        if base is None:
            base='~/Desktop'
        self.src=base
        if to_where is None:
            to_where=self.src
        self.to=to_where
        if file_src is None:
            file_src='~/Documents/Python/Projects/Fauxkemon/Source Data/Items'
        self.files=file_src
        self.look_up=None
    def parse_items(self,file_name,to='Pokemon Yellow',key='basic'):
        p_dir=os.path.join(self.src,to)
        try:
            os.mkdir(p_dir)
        except OSError:
            pass
        file=os.path.join(self.src,file_name)
        if key=='basic':
            self.parse_basic(file,to)
        elif key=='tm':
            self.parse_tm(file,to)
        elif key=='hm':
            self.parse_hm(file,to)
        elif key=='ball':
            self.parse_ball(file,to)

    def parse_basic(self,file,to):
        def make_file(prop_list):
            name,c,p,w,e=prop_list
            i_file=os.path.join(self.src,to,string.capwords(name))
            format_strings=self.basic_format
            try:
                int(c)
            except ValueError:
                format_strings=self.key_format
            try:
                int(p)
            except ValueError:
                format_strings=self.key_format
            
            with open(i_file,'w+') as to_write:
                strings=[]
                I=iter((name,c,p,e))
                v=next(I)
                for s in format_strings:
                    try:
                        s=s.format(v)
                    except:
                        pass
                    else:
                        try:
                            v=next(I)
                        except:
                            pass
                    strings.append(s)
                to_write.write('\n'.join(strings))
        with open(file) as data:
            props=[]
            name_flag=False
            for line in data:
                line=line.strip()
                if line:
                    try:
                        key,value=line.split(':')
                    except:
                        value=line
                        if name_flag:
                            props[-1]+=value
                            continue
                        name_flag=True
                    else:
                        value=value.replace('$','')
                    props.append(value)
                else:
                    make_file(props)
                    props=[]
                    name_flag=False
    def parse_ball(self,file,to):
        def make_file(prop_list):
            name,c,p,w,e=prop_list
            i_file=os.path.join(self.src,to,string.capwords(name))
            format_strings=self.ball_format            
            with open(i_file,'w+') as to_write:
                strings=[]
                I=iter((name,c,p,e))
                v=next(I)
                for s in format_strings:
                    try:
                        s=s.format(v)
                    except:
                        pass
                    else:
                        try:
                            v=next(I)
                        except:
                            pass
                    strings.append(s)
                to_write.write('\n'.join(strings))

        with open(file) as src:
            props=[]
            name_flag=False
            for line in src:
                line=line.strip()
                if line:
                    try:
                        key,value=line.split(':')
                    except:
                        value=line
                        if name_flag:
                            props[-1]+=value
                            continue
                        name_flag=True
                    else:
                        value=value.replace('$','')
                    props.append(value)
                else:
                    make_file(props)
                    props=[]
                    name_flag=False
    def parse_tm(self,file,to):
        def make_file(prop_list):
            name,m,p=prop_list
            i_file=os.path.join(self.src,to,name.upper())
            format_strings=self.tm_format            
            with open(i_file,'w+') as to_write:
                strings=[]
                I=iter((name,p,'500','1',m))
                v=next(I)
                for s in format_strings:
                    try:
                        s=s.format(v)
                    except:
                        pass
                    else:
                        try:
                            v=next(I)
                        except:
                            pass
                    strings.append(s)
                to_write.write('\n'.join(strings))

        with open(file) as src:
            for line in src:
                line=line.strip()
                if line:
                    line=[x.strip() for x in line.split('-')]
                    if len(line)<4:
                        line.append('2000')
                    line.pop(2)
                    make_file(line)
    def parse_hm(self,file,to):
        def make_file(prop_list):
            name,m=prop_list
            i_file=os.path.join(self.src,to,name.upper())
            format_strings=self.tm_format            
            with open(i_file,'w+') as to_write:
                strings=[]
                I=iter((name,'-','-','-',m))
                v=next(I)
                for s in format_strings:
                    try:
                        s=s.format(v)
                    except:
                        pass
                    else:
                        try:
                            v=next(I)
                        except:
                            pass
                    strings.append(s)
                to_write.write('\n'.join(strings))

        with open(file) as src:
            flag=True
            for line in src:
                line=line.strip()
                if line:
                    if flag:
                        line=[x.strip() for x in line.split('-')]
                        make_file(line)
                        flag=False
                else:
                    flag=True