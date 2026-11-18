from pathlib import Path
import json,re,io
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream,FloatObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent
REV=ROOT/'filally_22/paper2'
m=json.loads((WORK/'manifest.json').read_text(encoding='utf-8'))
t=(REV/'paper2.tex').read_text(encoding='utf-8')
lines=t.splitlines(keepends=True)
# Put a stable location label on the source line of each edit, without changing pagination.
if '\\label{rev:M01}' not in t:
    for p in reversed(m['patches']):
        i=p['marked_line']-1
        assert i<len(lines)
        lines[i]='\\label{rev:'+p['id']+'}'+lines[i]
t=''.join(lines)
bibmark=r'''
\usepackage{etoolbox}
\AtBeginDocument{%
  \let\revieworiginalbibitem\bibitem
  \renewcommand{\bibitem}[2][]{%
    \ifreviewmarkup
      \ifstrequal{#2}{liuTorusEventBased2025}{\color{revisiongreen}}{%
        \ifstrequal{#2}{chandrasekarAdaptiveEvent2026}{\color{revisiongreen}}{\normalcolor}}%
    \fi
    \revieworiginalbibitem[#1]{#2}}
}
'''
if '\\revieworiginalbibitem' not in t:
    t=t.replace('\\begin{document}',bibmark+'\n\\begin{document}',1)
if '\\revieworiginalbibitem' not in m['config']:
    for p in m['patches']:p['marked_line']+=bibmark.count('\n')+1
    m['config']+=bibmark
for key in ['del','add']:
    t=t.replace('\\long\\def\\rev'+key+'#1{','\\DeclareRobustCommand{\\rev'+key+'}[1]{')
    m['config']=m['config'].replace('\\long\\def\\rev'+key+'#1{','\\DeclareRobustCommand{\\rev'+key+'}[1]{')
(REV/'paper2.tex').write_text(t,encoding='utf-8')
(WORK/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')

pdfmetrics.registerFont(TTFont('LabelArial','C:/Windows/Fonts/arial.ttf'))
for name in ['actuator_fault.pdf','2_actuator_fault.pdf']:
    r=PdfReader(ROOT/'paper2/figs'/name);p=r.pages[0]
    cs=ContentStream(p.get_contents(),r)
    start=next(i for i,(a,op) in enumerate(cs.operations) if op==b'Tj' and str(a[0])=='\x0f')
    ids=[i for i,(a,op) in enumerate(cs.operations) if i>=start and op==b'Tj'][:16]
    expected='\x0f\x10\x04\x11\x12\x13\x02\x14\x15\x05\x03\x14\x16\x04\x17\x07'
    assert ''.join(str(cs.operations[i][0][0]) for i in ids)==expected
    # Preserve every original operator and glyph; insert only color operators around the old label.
    ops=list(cs.operations)
    ops.insert(ids[-1]+1,([FloatObject(0)],b'g'))
    ops.insert(ids[0],([FloatObject(190/255),FloatObject(0),FloatObject(0)],b'rg'))
    cs.operations=ops;p.replace_contents(cs)
    w=PdfWriter();out=w.add_blank_page(width=float(p.mediabox.width)+24,height=float(p.mediabox.height))
    out.merge_translated_page(p,24,0)
    buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(float(out.mediabox.width),float(out.mediabox.height)))
    c.setFillColorRGB(0,115/255,35/255);c.setFont('LabelArial',12)
    c.translate(10.5,241.8);c.rotate(90);c.drawCentredString(0,0,'Operating modes');c.save();buf.seek(0)
    out.merge_page(PdfReader(buf).pages[0])
    with (REV/'figs'/name).open('wb') as f:w.write(f)
    text=PdfReader(REV/'figs'/name).pages[0].extract_text()
    assert 'Operationmodels' in ''.join(text.split()) and 'Operatingmodes' in ''.join(text.split()),repr(text)
    m['figure_edits'][0 if name=='actuator_fault.pdf' else 1]['note']='原坐标标题完整保留并标红；新增正确标题置于加宽的左边距并标绿；原曲线路径、数据及坐标刻度保持不变。清洁版使用纠正后的坐标标题。'

(WORK/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'filally_22/全部修改精确记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('Added source location labels, reference colors, and red/green axis labels.')
