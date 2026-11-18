from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageDraw
from docx import Document
import re, json, hashlib

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'_review_work'/'v2'
OUT=ROOT/'paper2_审稿意见'/'第二版_结合模板'
REV=OUT/'paper2_修改副本'
src=(ROOT/'paper2'/'paper2.tex').read_text(encoding='utf-8')
new=(REV/'paper2.tex').read_text(encoding='utf-8')
manifest=json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,v in manifest['source_hashes'].items():
    assert sha(ROOT/'paper2'/n)==v,n
for p in (ROOT/'paper2'/'figs').iterdir():
    if p.is_file():
        assert sha(p)==sha(REV/'figs'/p.name),p.name
pattern=r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}'
eqs=lambda s:[m.group(0) for m in re.finditer(pattern,s,re.S)]
assert eqs(src)==eqs(new)
log=(REV/'paper2.log').read_text(encoding='utf-8',errors='replace')
assert 'Overfull' not in log and 'undefined references' not in log and 'undefined citations' not in log
aux=(REV/'paper2.aux').read_text(encoding='utf-8')
labels={}
for k in ['sec4','eq:adaptive_law','F_i01','fig7','fig8','fig14','fig15','tab:sigma_effect']:
    m=re.search(r'\\newlabel\{'+re.escape(k)+r'\}\{\{([^}]+)\}\{([^}]+)',aux)
    assert m,k
    labels[k]={'number':m.group(1),'page':m.group(2)}
assert labels['eq:adaptive_law']['number']=='6'
assert [labels[k]['number'] for k in ('fig7','fig8','fig14','fig15')]==['8','9','14','15']
pdf=PdfReader(REV/'paper2.pdf')
texts=[p.extract_text() for p in pdf.pages]
(WORK/'revised_pdf_text.txt').write_text('\n\n'.join('PAGE '+str(i+1)+'\n'+s for i,s in enumerate(texts)),encoding='utf-8')
terms=['The PMSM example','Here, each diagonal entry','these values give','In the reported simulations','Recent work has further','83.75','0.05 s']
locations={term:[i+1 for i,s in enumerate(texts) if term in s] for term in terms}
assert all(locations[t] for t in terms if t!='0.05 s')
verify=dict(pages=len(pdf.pages),displayed_math_blocks_unchanged=len(eqs(src)),original_hashes_unchanged=True,figures_unchanged=True,labels=labels,text_pages=locations,word_visual_qa=False)
(WORK/'verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2),encoding='utf-8')
images=sorted(WORK.glob('paper-*.png'))
if images:
    thumbs=[]
    for i,p in enumerate(images):
        im=Image.open(p).convert('RGB')
        im.thumbnail((270,382))
        tile=Image.new('RGB',(290,410),'#eeeeee')
        tile.paste(im,((290-im.width)//2,20))
        ImageDraw.Draw(tile).text((10,5),'Page '+str(i+1),fill='black')
        thumbs.append(tile)
    sheet=Image.new('RGB',(290*5,410*((len(thumbs)+4)//5)),'white')
    for i,im in enumerate(thumbs):sheet.paste(im,((i%5)*290,(i//5)*410))
    sheet.save(WORK/'paper-contact.png')
print(json.dumps(verify,ensure_ascii=False))
