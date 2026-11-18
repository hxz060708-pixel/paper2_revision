from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from pypdf import PdfReader
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'_review_work'/'v4';OUT=ROOT/'paper2_审稿意见'/'按师兄模板重做';REV=OUT/'paper2_修改副本'
verification=json.loads((WORK/'verification.json').read_text(encoding='utf-8'))
manifest=json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
for name,v in manifest['source_hashes'].items():assert hashlib.sha256((ROOT/'paper2'/name).read_bytes()).hexdigest()==v
pdf=PdfReader(REV/'paper2.pdf');assert len(pdf.pages)==21
aux=(REV/'paper2.aux').read_text(encoding='utf-8')
for key,num,page in [('fig6','7','15'),('fig13','13','18'),('fig12','12','18'),('sec5','5','18')]:
    assert re.search(r'\\newlabel\{'+key+r'\}\{\{'+num+r'\}\{'+page+r'\}',aux)
log=(REV/'paper2.log').read_text(encoding='utf-8',errors='replace')
assert 'Overfull' not in log and 'undefined' not in log
verification.update(pdf_visual_pages_reviewed=list(range(1,22)),final_pdf_sha256=hashlib.sha256((REV/'paper2.pdf').read_bytes()).hexdigest(),word_visual_qa=False)
(WORK/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
notes=OUT/'00_阅读说明与修改对应.txt'
notes.write_text(notes.read_text(encoding='utf-8')+'\n最终检查：论文 PDF 共21页，所有页已查看；图7与图13图注已缩短，避免并排图注靠得过近。原有参考文献条目不在本轮全面著录核对范围内。\n',encoding='utf-8')
files=sorted(OUT.glob('*.docx'))+[notes,OUT/'paper2_修改对照.diff']
files += [REV/n for n in ['paper2.tex','ref2.bib','paper2.pdf','paper2.bbl']]
files += sorted(p for p in (REV/'figs').iterdir() if p.is_file())
archive=OUT.parent/'paper2_按师兄模板重做_完整包.zip'
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
    for p in files:z.write(p,'paper2_按师兄模板重做/'+p.relative_to(OUT).as_posix())
with ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(files)
print(json.dumps(dict(archive=str(archive),size=archive.stat().st_size,files=len(files),documents=6,pdf_pages=21),ensure_ascii=False))
