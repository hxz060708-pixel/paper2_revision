from pathlib import Path
import json, hashlib
from docx import Document
import fitz

ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).resolve().parent
data=[]
for i in range(1,4):
    p=ROOT/'新+'/f'审稿意见_{i}'/'审稿意见.docx'
    doc=Document(p)
    data.append({'reviewer':i,'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'paragraphs':[x.text for x in doc.paragraphs]})
(WORK/'source_reviews.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['2_h1_dot_and_ut.pdf','actuator_fault.pdf','2_actuator_fault.pdf','x(t).pdf','2_x(t).pdf']:
    p=ROOT/'paper2'/'figs'/name
    d=fitz.open(p)
    print(name,repr(d[0].get_text()))
    d[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(WORK/(name[:-4]+'.png'))
print('saved source reviews and figure previews')
