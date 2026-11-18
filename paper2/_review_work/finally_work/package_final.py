from pathlib import Path
import json,zipfile,hashlib
from pypdf import PdfReader
from docx import Document

root=Path(__file__).resolve().parents[2]
work=root/'_review_work'/'finally_work'
out=root/'finally'
verification=json.loads((work/'verification.json').read_text(encoding='utf-8'))
data=json.loads((work/'content.json').read_text(encoding='utf-8'))
for index,p in enumerate(sorted(out.glob('*.docx'))):
    doc=Document(p)
    assert len(doc.paragraphs)==8
    assert all('major' not in q.text.lower() for q in doc.paragraphs)
    assert all(q.text for q in doc.paragraphs)
for p in out.glob('*.pdf'):
    reader=PdfReader(p)
    assert len(reader.pages)==(11 if p.name.startswith('01_') else 6)
    txt=''.join(page.extract_text() for page in reader.pages)
    assert '\\ref{' not in txt and '\\eqref{' not in txt
    if p.name.startswith('05_'):
        assert 'actuator_fault.pdf' in txt
    if p.name.startswith('06_'):
        assert 't_k' not in txt
verification['visual_review']={
    'language':list(range(1,12)),
    'reviewer_1':list(range(1,7)),
    'reviewer_2':list(range(1,7)),
    'reviewer_3':list(range(1,7)),
    'paper_direct':list(range(13,21)),
    'paper_pixel_identical_to_previously_reviewed':list(range(1,13)),
    'word':'Content, OOXML formatting and document structure verified; page rendering unavailable because soffice is absent.'
}
verification['final_pdf_sha256']={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*.pdf') if p.parent==out or p.name=='paper2.pdf'}
(work/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
excluded={'.aux','.blg','.fdb_latexmk','.fls','.log','.out','.spl'}
files=[p for p in sorted(out.rglob('*')) if p.is_file() and p.suffix not in excluded]
archive=root/'finally_完整包.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,'finally/'+p.relative_to(out).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.infolist())==len(files)
print(json.dumps({'archive':str(archive),'files':len(files),'bytes':archive.stat().st_size,'word_reports':3,'response_pdfs':3,'language_pdf_pages':11,'revised_paper_pages':20},ensure_ascii=False))
