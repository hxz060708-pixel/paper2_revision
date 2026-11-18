from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
import io,json

WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[1]
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
comment='The proposed looped functional depends on fuzzy membership functions. Could the authors explain what advantages this dependence offers over a membership-independent construction, particularly in exploiting membership-derivative information for stability analysis and regional controller synthesis?'
response=('Thank you for this question. Membership dependence allows the matrices in the functional to retain information about the active fuzzy-rule weights. Unlike a membership-independent matrix, a membership-weighted matrix changes with these weights, and its derivative explicitly contains terms involving the membership-function derivatives. In the proposed analysis, the signs of these derivatives define regional matrix constraints. This allows the stability conditions to use both the membership values and their variation, thereby connecting the functional construction with regional controller synthesis.\n\n'
'The looped terms additionally describe the state evolution between sampling instants while satisfying the endpoint-matching property used in the analysis. These two aspects serve complementary purposes: membership dependence retains fuzzy-model information, whereas the looped construction incorporates inter-sample information. Their combination provides a structured basis for deriving the sufficient stability and synthesis conditions. It does not, by itself, establish that the conditions are less conservative than every membership-independent alternative; such a quantitative claim would require a matched comparison.')
folder=ROOT/'filally_22/审稿意见3';path=folder/'01_审稿意见.docx'
with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
tree=E.fromstring(parts['word/document.xml']);body=tree.find(W+'body');ps=body.findall(W+'p')
assert len(ps)==9
p=deepcopy(ps[-1]);p.attrib.clear()
rpr=deepcopy(p.find(W+'r').find(W+'rPr'))
for child in list(p):
    if child.tag!=W+'pPr':p.remove(child)
run=E.SubElement(p,W+'r');run.append(rpr);E.SubElement(run,W+'t').text=comment
body.insert(list(body).index(ps[-1])+1,p)
parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
buf=io.BytesIO()
with ZipFile(buf,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
try:path.write_bytes(buf.getvalue());print('SAVED',path,flush=True)
except PermissionError:
    alt=folder/'01_审稿意见_新增第8条.docx';alt.write_bytes(buf.getvalue());print('SAVED',alt,flush=True)
alias=folder/'01_审稿意见_结尾已更新.docx'
if alias.exists():
    try:alias.write_bytes(buf.getvalue())
    except PermissionError:print('ALIAS LOCKED',alias.name,flush=True)
rp=WORK/'responses.json';reviews=json.loads(rp.read_text(encoding='utf-8'))
review=next(r for r in reviews if r['reviewer']==3)
assert len(review['items'])==7
review['items'].append({'id':'R3.8','comment':'8. '+comment,'response':response,'changes':[],
    'response_only_note':'本条依据现有隶属函数加权矩阵、导数符号区域约束及looped functional的采样区间结构作解释，不新增论文正文修改或比较仿真。'})
rp.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
builder=WORK/'build_pdfs.py';source=builder.read_text(encoding='utf-8').replace('for r in reviews:', 'for r in reviews[2:3]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})
