from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import ContentStream
from PIL import Image, ImageChops
from docx import Document
import json,re,hashlib,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'_review_work'/'v4'; OUT=ROOT/'paper2_审稿意见'/'按师兄模板重做'; REV=OUT/'paper2_修改副本'
src=(ROOT/'paper2'/'paper2.tex').read_text(encoding='utf-8')
new=(REV/'paper2.tex').read_text(encoding='utf-8')
m=json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,v in m['source_hashes'].items():assert sha(ROOT/'paper2'/name)==v
pattern=r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}'
math=lambda s:[x.group(0) for x in re.finditer(pattern,s,re.S)]
assert math(src)==math(new)
changed_figures={x['file'] for x in m['figure_edits']}
other_figures=0
for p in (ROOT/'paper2'/'figs').iterdir():
    if p.is_file() and p.name not in changed_figures:
        assert sha(p)==sha(REV/'figs'/p.name),p.name
        other_figures+=1

log=(REV/'paper2.log').read_text(encoding='utf-8',errors='replace')
assert not re.search(r'Overfull|undefined references|undefined citations|LaTeX Warning:.*undefined',log)
texts=[' '.join(p.extract_text().split()) for p in PdfReader(REV/'paper2.pdf').pages]
assert len(texts)==21
checks={2:['The PMSM example','Recent work has'],4:['For comparison, a fixed','The update is zero'],6:['The two uncertainty sources'],11:['In particular, the FMF','The prescribed scalars'],13:['For offline synthesis'],16:['The saving rate is calculated','In Table 1'],18:['In Fig. 12','83.75','The present formulation'],21:['100003','02172']}
for page,terms in checks.items():
    for t in terms:assert t in texts[page-1],(page,t)
aux=(REV/'paper2.aux').read_text(encoding='utf-8')
for key,num,page in [('fig6','7','15'),('fig13','13','18'),('fig12','12','18'),('thm2','3.2','11'),('eq:closed_loop','15','6')]:
    assert re.search(r'\\newlabel\{'+key+r'\}\{\{'+num+r'\}\{'+page+r'\}',aux),(key,num,page)
assert '83.79' not in new

# Ensure the original plotted geometry is unchanged by the PDF label edit.
poppler=Path(r'C:\Users\zh\x') # replaced by the runtime-owned absolute path below
poppler=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
if not poppler.exists():
    poppler=Path("C:/Users/zh'x/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe")
plots={}
for name in sorted(changed_figures):
    paths=[]
    for suffix,base in [('orig',ROOT/'paper2'),('rev',REV)]:
        output=WORK/(Path(name).stem+'-'+suffix)
        subprocess.run([str(poppler),'-png','-r','144','-singlefile',str(base/'figs'/name),str(output)],check=True,capture_output=True)
        paths.append(output.with_suffix('.png'))
    a,b=[Image.open(p).convert('RGB') for p in paths]
    assert a.size==b.size
    # Exclude only the leftmost 14 PDF points containing the changed axis title.
    box=(28,0,a.width,a.height)
    assert ImageChops.difference(a.crop(box),b.crop(box)).getbbox() is None,name
    plots[name]={'all_pixels_outside_axis_title_identical':True}

renderer=Path("C:/Users/zh'x/.codex/plugins/cache/openai-primary-runtime/documents/26.1017.22136/skills/documents/render_docx.py")
render_results=[]
for p in sorted(OUT.glob('*.docx')):
    d=Document(p)
    assert len(d.sections)==1
    assert not any('SMCA-25' in x.text for x in d.paragraphs)
    res=subprocess.run([sys.executable,str(renderer),str(p),'--output_dir',str(WORK/('render-'+p.stem))],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45)
    output=res.stdout+'\n'+res.stderr
    (WORK/(p.stem+'-render.log')).write_text(output,encoding='utf-8')
    render_results.append({'file':p.name,'returncode':res.returncode,'missing_soffice':'soffice' in output.lower()})
    print(p.name,'render status',res.returncode,flush=True)
result=dict(original_files_unchanged=True,displayed_math_blocks_unchanged=len(math(src)),other_figure_files_unchanged=other_figures,changed_figure_checks=plots,pdf_pages=21,latex_references_resolved=True,comments=18,word_render=render_results)
(WORK/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
