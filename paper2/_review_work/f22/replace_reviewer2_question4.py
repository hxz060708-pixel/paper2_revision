from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
import json,io

WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[1]
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
comment='The attack model uses a Bernoulli variable together with a state-dependent bound on the deception signal. Could the authors clarify what these two components represent and how their roles differ?'
response=('Thank you for this question. The Bernoulli variable describes whether the transmitted state information is replaced by a deception signal. Its mean specifies the probability of this replacement: a value of zero for the variable corresponds to normal transmission, while a value of one corresponds to replacement by the false signal. '
'The state-dependent bound instead restricts the admissible magnitude of that false signal. For each state component, the positive coefficient L_k bounds the magnitude of the corresponding deception-signal component relative to the magnitude of that state component. It is neither an attack probability nor a fixed absolute amplitude limit. '
'Thus, the Bernoulli model describes attack occurrence, whereas the bound describes the allowed signal magnitude when an attack occurs. This distinction follows directly from the existing attack model and its bounded-signal assumption.')
folder=ROOT/'filally_22/审稿意见2';path=folder/'01_审稿意见.docx'
with ZipFile(path) as z: parts={n:z.read(n) for n in z.namelist()}
tree=E.fromstring(parts['word/document.xml']);ps=tree.find(W+'body').findall(W+'p')
assert len(ps)==9
p=ps[5]
assert 'PMSM' in ''.join(t.text or '' for t in p.iter(W+'t'))
rpr=deepcopy(p.find(W+'r').find(W+'rPr'))
for el in list(p):
    if el.tag!=W+'pPr':p.remove(el)
r=E.SubElement(p,W+'r');r.append(rpr);E.SubElement(r,W+'t').text=comment
parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
out=io.BytesIO()
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for n,data in parts.items():z.writestr(n,data)
try:path.write_bytes(out.getvalue());print('SAVED',path,flush=True)
except PermissionError:
    fallback=folder/'01_审稿意见_第4条已替换.docx';fallback.write_bytes(out.getvalue());print('SAVED',fallback,flush=True)
for name in ['01_审稿意见_结尾已更新.docx','01_审稿意见_新增第7条.docx']:
    dest=folder/name
    if dest.exists():
        try:dest.write_bytes(out.getvalue())
        except PermissionError:print('ALIAS LOCKED',name,flush=True)
rp=WORK/'responses.json';reviews=json.loads(rp.read_text(encoding='utf-8'))
review=next(r for r in reviews if r['reviewer']==2)
item=next(it for it in review['items'] if it['id']=='R2.4')
item.update(comment='4. '+comment,response=response,changes=[],response_only_note='本条依据现有欺骗攻击模型及其信号有界假设作解释，不新增算例、仿真或论文正文修改。')
rp.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
mp=WORK/'manifest.json';manifest=json.loads(mp.read_text(encoding='utf-8'))
for p in manifest['patches']:p['ids']=[cid for cid in p['ids'] if cid!='R2.4']
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
builder=WORK/'build_pdfs.py'
source=builder.read_text(encoding='utf-8').replace('for r in reviews:', 'for r in reviews[1:2]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})
