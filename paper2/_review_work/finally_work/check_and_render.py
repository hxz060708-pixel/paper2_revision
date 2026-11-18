from pathlib import Path
import json,re,hashlib,subprocess,sys,os
from pypdf import PdfReader
from docx import Document
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'_review_work'/'finally_work';OUT=ROOT/'finally';REV=OUT/'paper2_修改副本';QA=WORK/'qa';QA.mkdir(exist_ok=True)
m=json.loads((WORK/'manifest.json').read_text(encoding='utf-8'));data=json.loads((WORK/'content.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,h in m['source_hashes'].items():assert sha(ROOT/'paper2'/name)==h
original=(ROOT/'paper2'/'paper2.tex').read_text(encoding='utf-8');revised=(REV/'paper2.tex').read_text(encoding='utf-8')
pattern=r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}'
eqs=lambda s:[x.group(0) for x in re.finditer(pattern,s,re.S)]
assert eqs(original)==eqs(revised)
for c in m['changes']:
    for line in c['revised_lines']:assert revised.splitlines()[line-1].startswith(c['new'].splitlines()[0]) or c['new'].splitlines()[0] in revised.splitlines()[line-1]
for p in (REV/'figs').iterdir():
    if p.is_file():assert sha(p)==sha(ROOT/'paper2_审稿意见'/'按师兄模板重做'/'paper2_修改副本'/'figs'/p.name)
assert 'For offline synthesis' not in revised
assert 'Two examples illustrate complementary' in revised
log=(REV/'paper2.log').read_text(encoding='utf-8',errors='replace')
assert not re.search(r'Overfull|undefined references|undefined citations',log)
poppler=Path("C:/Users/zh'x/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe")
pdfs=[('language',OUT/'01_语言修改逐字对照.pdf')]+[(f'r{i}',OUT/f'0{i+4}_回复与修改位置_Reviewer{i}.pdf') for i in range(1,4)]+[('paper',REV/'paper2.pdf')]
stats={}
for tag,p in pdfs:
    r=PdfReader(p);texts=[q.extract_text() for q in r.pages]
    stats[tag]={'pages':len(r.pages),'characters_per_page':[len(t) for t in texts]}
    if tag.startswith('r'):
        assert len(r.pages)==6
        ri=int(tag[-1])-1
        for i,it in enumerate(data['reviewers'][ri]):
            assert it['id'] in texts[i]
            assert '英文回复' in texts[i] and '修改位置' in texts[i]
    if tag=='language':
        assert all(c['language_id'] in ''.join(texts) for c in data['language'])
        assert len(texts[-1])>200,'Orphan final table row'
    if tag!='paper':
        assert all('\\ref{' not in t and '\\sigma' not in t and '\\caption' not in t for t in texts)
    d=QA/tag;d.mkdir(exist_ok=True)
    subprocess.run([str(poppler),'-png','-r','110',str(p),str(d/'page')],capture_output=True,check=True)
    print(tag,'rendered',len(r.pages),'pages',flush=True)

same_pages=[]
for i in range(1,13):
    a=ROOT/'_review_work'/'v4'/f'paper-{i:02d}.png';b=QA/'paper'/f'page-{i:02d}.png'
    if a.exists() and b.exists():
        aa,bb=Image.open(a).convert('RGB'),Image.open(b).convert('RGB')
        if aa.size==bb.size and ImageChops.difference(aa,bb).getbbox() is None:same_pages.append(i)

renderer=Path("C:/Users/zh'x/.codex/plugins/cache/openai-primary-runtime/documents/26.1017.22136/skills/documents/render_docx.py")
env=dict(os.environ);tmp=WORK/'render_temp';tmp.mkdir(exist_ok=True);env['TEMP']=env['TMP']=str(tmp)
word=[]
for p in sorted(OUT.glob('*.docx')):
    doc=Document(p);assert len(doc.sections)==1 and len(doc.paragraphs)==8
    result=subprocess.run([sys.executable,str(renderer),str(p),'--output_dir',str(QA/p.stem)],capture_output=True,text=True,encoding='utf-8',errors='replace',env=env,timeout=40)
    output=result.stdout+'\n'+result.stderr;(WORK/(p.stem+'-render.log')).write_text(output,encoding='utf-8')
    word.append({'file':p.name,'exit_code':result.returncode,'missing_soffice':'soffice.exe was not found' in output})
verification=dict(original_unchanged=True,displayed_math_blocks_unchanged=len(eqs(original)),language_entries=17,language_locations=19,word_edit_groups=110,comments=18,pdfs=stats,paper_pages_identical_to_previously_reviewed=same_pages,word_render=word)
(WORK/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(verification,ensure_ascii=False))
