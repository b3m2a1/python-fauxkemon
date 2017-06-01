from ._shared import *

class TilePrepper:
    def __init__(self,base=None,to_where=None,file_src=None):
        if base is None:
            base='~/Desktop'
        self.src=base
        if to_where is None:
            to_where=self.src
        self.to=to_where
        if file_src is None:
            file_src='~/Documents/Python/Projects/Fauxkemon/Source Data/Tiles'
        self.files=file_src
        
    def process(self,src=None,ext=None,to=None,make_bw=False):
        if src is None:
            src=self.src
        if not ext is None:
            src=os.path.join(src,ext)
        if not to is None:
            to=os.path.join(src,to)
        else:
            to=src
        for file in os.listdir(src):
            n,e=os.path.splitext(file)
            if 'png' in e:
                f_src=os.path.join(src,file)
                dirp=os.path.join(to,n)
                to_f=os.path.join(dirp,'background.png')
                try:
                    shutil.copy(f_src,to_f)
                except FileNotFoundError:
                    os.mkdir(dirp)
                    shutil.copy(f_src,to_f)
                    if make_bw:
                        self.process_bw(to_f)
                os.remove(f_src)

    def process_bw(self,file):
        try:
            from GUITools.ImageTools import ImageWrapper
        except ImportError:
            pass
        else:
            I=ImageWrapper(file)
            I.black_and_white()
            try:
                I.save()
            except KeyError:
                I.save(file,'png')
    def file_format(self,src=None):
        if src is None:
            src=self.src
        for f in os.listdir(src):
            j=os.path.join(src,f)
            if os.path.isdir(j):
                if not 'props.txt' in os.listdir(j):
                    for t in os.listdir(self.files):
                        t_src=os.path.join(self.files,t)
                        tile_dir=os.path.join(t_src,f)
                        if os.path.exists(tile_dir):
                            tile_props=os.path.join(tile_dir,'props.txt')
##                            print(tile_props)
                            if os.path.exists(tile_props):
                                end=os.path.join(j,'props.txt')
##                                print(end)
                                shutil.copy(tile_props,end)