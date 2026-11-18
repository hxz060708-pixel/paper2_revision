from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from pypdf import PdfReader
from docx import Document
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'paper2_审稿意见'
WORK=ROOT/'_review_work'
REV=OUT/'paper2_修改副本'
content=json.loads((WORK/'document_content.json').read_text(encoding='utf-8'))
manifest=json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
report=Document(content['report']); reply=Document(content['response'])
report_text='\n'.join(p.text for p in report.paragraphs)
reply_text='\n'.join(p.text for p in reply.paragraphs)
assert all(report_text.count(c)==1 and reply_text.count(c)==1 for c in content['comments'])
assert not any(x in report_text+reply_text for x in ['AUTHOR_INPUT_NEEDED','[INSERT','SMCA-25-06-2213'])
numbered=[p for p in report.paragraphs if p._p.xpath('./w:pPr/w:numPr')]
assert len(numbered)==6
pdf=PdfReader(REV/'paper2.pdf')
assert len(pdf.pages)==19
pages=[p.extract_text() for p in pdf.pages]
checks={1:'The signs of the membership-function derivatives',2:'Recent work',6:'three stages',12:'complementary',15:'saving rate',17:'83.75%',19:'10.1007/s40747-025-02172-5'}
for page,needle in checks.items():
    assert needle.lower().replace(' ','') in pages[page-1].lower().replace(' ','').replace('\n',''),(page,needle)
for n,h in manifest['source_hashes'].items():assert hashlib.sha256((ROOT/'paper2'/n).read_bytes()).hexdigest()==h
tex=(REV/'paper2.tex').read_text(encoding='utf-8')
for c in manifest['changes']:
    assert c['new'] in tex
    assert c['revised_lines']==[tex[:m.start()].count('\n')+1 for m in re.finditer(re.escape(c['new']),tex)]
log=(REV/'paper2.log').read_text(encoding='utf-8',errors='replace')
assert not re.search(r'(^!|undefined references|Citation .* undefined|Overfull)',log,re.M)
orig_bib=(ROOT/'paper2'/'ref2.bib').read_text(encoding='utf-8')
revised_bib=(REV/'ref2.bib').read_text(encoding='utf-8')
assert revised_bib.startswith(orig_bib)
final=dict(comment_count=6,review_response_comment_identity=True,numbered_items=6,manuscript_pages=19,source_location_checks=True,original_files_unchanged=True,compile_success=True,unresolved_citations=False,word_visual_qa='NOT COMPLETED: no LibreOffice executable; Word COM access denied',existing_bibliography_warnings='29 original bibliography entries have issue numbers but no volume. New entries are complete; original entries were not changed.',new_references=manifest['new_references'])
(WORK/'verification.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
note=OUT/'00_阅读说明.txt'
t=note.read_text(encoding='utf-8')
t+='\n编译补充：修改稿为 19 页，无未解析引用。原有书目仍有 29 条缺少卷号的 BibTeX 提示，本轮未全面补齐原有书目信息；新加两条的卷号、文章号和 DOI 完整。\n'
note.write_text(t,encoding='utf-8')
archive=OUT/'paper2_第一份审稿与修改包.zip'
files=[OUT/'00_阅读说明.txt',Path(content['report']),Path(content['response']),OUT/'paper2_修改对照.diff',REV/'paper2.tex',REV/'ref2.bib',REV/'paper2.pdf']+sorted((REV/'figs').glob('*'))
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
    for f in files:
        if f.is_file():z.write(f,str(f.relative_to(OUT)).replace('\\','/'))
with ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(dict(archive=str(archive),size=archive.stat().st_size,files=len(files),verification=final),ensure_ascii=False))
