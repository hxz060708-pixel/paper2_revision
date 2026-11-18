from pathlib import Path
import json,re,hashlib,subprocess,os,sys
from docx import Document
ROOT=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent
writer=(ROOT/'_review_work/build_documents.py').read_text(encoding='utf-8').split('\ncomments=[',1)[0]
writer=writer.replace('ROOT=Path(__file__).resolve().parents[1]','ROOT=Path(__file__).resolve().parents[2]').replace("WORK=ROOT/'_review_work'","WORK=ROOT/'_review_work'/'f22'")
exec(compile(writer,'template_writer','exec'),globals())
sources=json.loads((WORK/'source_reviews.json').read_text(encoding='utf-8'))
for src in sources:
    OUT=ROOT/'filally_22'/f"审稿意见{src['reviewer']}"
    paras=[paragraph(src['paragraphs'][0],'title'),paragraph(src['paragraphs'][1])]
    paras += [paragraph(re.sub(r'^\d+\.\s*','',s),'number') for s in src['paragraphs'][2:]]
    dest=write_doc('01_审稿意见.docx',paras)
    texts=[p.text for p in Document(dest).paragraphs]
    reconstructed=texts[:2]+[f'{i}. '+s for i,s in enumerate(texts[2:],1)]
    assert reconstructed==src['paragraphs']
    assert hashlib.sha256(Path(src['source']).read_bytes()).hexdigest()==src['sha256']
    print('Exact review text preserved:',src['reviewer'])

a=(WORK/'artifact.md').read_text(encoding='utf-8')
a=a.replace('six numbered paragraphs','seven numbered paragraphs').replace('repeated for six comments','repeated for seven comments')
a += '\nCurrent source: 新+ latest three reports. All title, overview and comment wording is preserved exactly; manual number prefixes are represented using the retained template’s automatic numbering. All three have nine content paragraphs. No request to shorten or rewrite comments.\n'
(WORK/'artifact.md').write_text(a,encoding='utf-8')

renderer=Path("C:/Users/zh'x/.codex/plugins/cache/openai-primary-runtime/documents/26.1017.22136/skills/documents/render_docx.py")
env=dict(os.environ);env['TEMP']=env['TMP']=str(WORK)
for i in range(1,4):
    p=ROOT/'filally_22'/f'审稿意见{i}'/'01_审稿意见.docx'
    r=subprocess.run([sys.executable,str(renderer),str(p),'--output_dir',str(WORK/f'word_render_{i}')],env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45)
    (WORK/f'word_render_{i}.log').write_text(r.stdout+r.stderr,encoding='utf-8')
    print('Word render:',i,r.returncode,'missing_soffice=', 'soffice.exe was not found' in r.stderr)
