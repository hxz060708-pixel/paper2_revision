"""Run the current Library helper using NTFS alternate streams for xattrs."""
from pathlib import Path
import os,re,runpy,sys
if os.name=='nt' and not hasattr(os,'setxattr'):
    def stream(path,name):
        if not re.fullmatch(r'user\.library-[a-z-]+',name):
            raise ValueError('Unexpected Library attribute name')
        return Path(str(path)+':'+name)
    os.setxattr=lambda path,name,value:stream(path,name).write_bytes(value)
    os.getxattr=lambda path,name:stream(path,name).read_bytes()
helper=Path(__file__).with_name('library_file_transfer.py')
sys.argv[0]=str(helper)
runpy.run_path(str(helper),run_name='__main__')
