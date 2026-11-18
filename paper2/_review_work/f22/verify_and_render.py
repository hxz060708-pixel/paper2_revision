from pathlib import Path
import json,re,hashlib,difflib
from zipfile import ZipFile
from xml.etree import ElementTree as E
import fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent;OUT=ROOT/'filally_22';REV=OUT/'paper2';QA=WORK/'qa';QA.mkdir(exist_ok=True)
m=json.loads((WORK/'manifest.json').read_text(encoding='utf-8'));reviews=json.loads((WORK/'source_reviews.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,h in m['source_hashes'].items():assert sha(ROOT/'paper2'/name)==h,name
orig=(ROOT/'paper2/paper2.tex').read_text(encoding='utf-8');accepted=(WORK/'accepted_content.tex').read_text(encoding='utf-8');marked=(REV/'paper2.tex').read_text(encoding='utf-8')
eqs=lambda s:[x.group(0) for x in re.finditer(r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}',s,re.S)]
assert eqs(orig)==eqs(accepted)

def accept(s):
    out='';i=0
    while i<len(s):
        mat=re.match(r'\\rev(del|add)\{',s[i:])
        if not mat:out+=s[i];i+=1;continue
        k=i+mat.end();start=k;depth=1
        while depth:
            if s[k]=='{' and s[k-1]!='\\':depth+=1
            elif s[k]=='}' and s[k-1]!='\\':depth-=1
            k+=1
        if mat.group(1)=='add':out+=s[start:k-1]
        i=k
    return out
body=marked.split('\\begin{document}',1)[1]
body=re.sub(r'\\label\{rev:M\d+\}','',body)
body=body.replace(r'\revfigure{actuator_fault.pdf}',r'\includegraphics[width=0.9\textwidth]{figs/actuator_fault.pdf}').replace(r'\revfigure{2_actuator_fault.pdf}',r'\includegraphics[width=0.9\textwidth]{figs/2_actuator_fault.pdf}')
assert accept(body)==accepted.split('\\begin{document}',1)[1],'Marked-to-clean reconstruction differs.'
for p in m['patches']:
    assert orig[p['start']:p['end']]==p['old'],p['id']
    assert '\\label{rev:'+p['id']+'}' in marked.splitlines()[p['marked_line']-1],p['id']

W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
for src in reviews:
    i=src['reviewer'];dest=OUT/f'审稿意见{i}/01_审稿意见.docx'
    with ZipFile(dest) as z:
        ps=E.fromstring(z.read('word/document.xml')).find(W+'body').findall(W+'p')
        ts=[''.join(t.text or '' for t in p.iter(W+'t')) for p in ps]
        assert ts[:2]+[f'{j}. '+x for j,x in enumerate(ts[2:],1)]==src['paragraphs']
        assert len(ps)==9
    assert sha(Path(src['source']))==src['sha256']
stats={};warnings=[]
pdfs=list(OUT.glob('审稿意见*/*.pdf'))+[REV/'paper2.pdf',REV/'paper2_clean.pdf']
for index,path in enumerate(pdfs):
    tag=f'pdf{index+1}';target=QA/tag;target.mkdir(exist_ok=True)
    d=fitz.open(path);texts=[];pageimages=[]
    for j,page in enumerate(d):
        text=page.get_text();texts.append(text)
        assert '\ufffd' not in text,(path,j,'replacement character')
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if x0<0 or x1>page.rect.width+1 or y0<0 or y1>page.rect.height+1:
                        warnings.append({'file':str(path),'page':j+1,'text':span['text'],'bbox':span['bbox']})
        png=target/f'page-{j+1:03d}.png';page.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(png);pageimages.append(png)
    if '审稿意见' in str(path.parent):
        ri=int(path.parent.name[-1]);alltext=''.join(texts)
        assert all(f'R{ri}.{n}' in alltext for n in range(1,8))
        if path.name.startswith('03'):
            expected=[p['id'] for p in m['patches'] if any(cid.startswith(f'R{ri}.') for cid in p['ids'])]
            assert all(cid in alltext for cid in expected)
        assert all(len(t.strip())>110 for t in texts),(path,'near-empty page')
    for start in range(0,len(pageimages),9):
        batch=pageimages[start:start+9];rows=(len(batch)+2)//3
        contact=Image.new('RGB',(1530,735*rows),'#e7e7e7');draw=ImageDraw.Draw(contact)
        for k,png in enumerate(batch):
            im=Image.open(png);im.thumbnail((500,700))
            x=(k%3)*510;y=(k//3)*735
            contact.paste(im,(x+5,y+25));draw.text((x+8,y+5),f'{tag} page {start+k+1}',fill='black')
        contact.save(QA/f'{tag}-contact-{start//9+1}.png')
    stats[str(path.relative_to(OUT))]={'tag':tag,'pages':len(d),'text_lengths':[len(t) for t in texts]}
    print(tag,path.name,len(d),flush=True)
(WORK/'verification.json').write_text(json.dumps({'original_files_unchanged':True,'displayed_math_blocks_unchanged':len(eqs(orig)),'marked_to_clean_exact':True,'review_comments_exact':21,'changes':len(m['patches']),'pdfs':stats,'page_bounds_warnings':warnings,'word_visual_status':'Unavailable: missing bundled soffice; Word COM denied.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Bounds warnings',len(warnings))
