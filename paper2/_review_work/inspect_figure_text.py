from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import ContentStream
root=Path(__file__).resolve().parents[1]
for name in ['actuator_fault.pdf','2_actuator_fault.pdf','2_h1_dot_and_ut.pdf']:
    r=PdfReader(root/'paper2'/'figs'/name); p=r.pages[0]
    print('\nFILE',name)
    def visitor(text,cm,tm,font,size):
        if text.strip(): print(repr(text), 'cm',cm,'tm',tm,'font',font.get('/BaseFont') if font else None,'size',size)
    p.extract_text(visitor_text=visitor)
    if 'fault' in name:
        for i,(args,op) in enumerate(ContentStream(p.get_contents(),r).operations):
            if op in (b'Tj',b'TJ'): print(i,op,repr(args))
