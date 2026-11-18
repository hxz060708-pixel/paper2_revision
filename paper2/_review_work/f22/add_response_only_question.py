from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
import json,io

WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[1]
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
comment='The framework involves both membership-derivative-dependent regional selection and Markov-type actuator-failure switching. Could the authors clarify the distinct roles of these two mechanisms and explain how they are jointly accounted for in the stability analysis?'
response=('Thank you for this question. These mechanisms describe different aspects of the existing model. '
'Regional selection is determined by the sign pattern of the membership-function derivatives. It selects the regional fuzzy gains K_n^l and the associated derivative-sign constraints C_l. '
'In contrast, the Markov process describes stochastic changes in actuator effectiveness through the mode-dependent matrix F_i and transition rates lambda_ij. '
'The regional index l and actuator-mode index i therefore have different meanings; the regions are not identified with the Markov failure modes. '
'In the stability analysis, the regional constraints control the signs of the membership-derivative terms in the functional derivative, whereas Markov transitions contribute the generator term involving the sum of lambda_ij P_jh. '
'The existing sufficient conditions are imposed for each actuator mode, fuzzy-rule combination, and regional constraint set, so both mechanisms are included in the same analysis. '
'This explanation follows the existing controller formulation and theorem conditions; no additional manuscript modification is needed for this comment.')
folder=ROOT/'filally_22/审稿意见2';path=folder/'01_审稿意见.docx'
with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
tree=E.fromstring(parts['word/document.xml']);body=tree.find(W+'body');ps=body.findall(W+'p')
assert len(ps)==8,'Expected six existing comments'
p=deepcopy(ps[-1]);p.attrib.clear()
rpr=deepcopy(p.find(W+'r').find(W+'rPr'))
for el in list(p):
    if el.tag!=W+'pPr':p.remove(el)
r=E.SubElement(p,W+'r');r.append(rpr);E.SubElement(r,W+'t').text=comment
body.insert(list(body).index(ps[-1])+1,p)
parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
out=io.BytesIO()
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for n,b in parts.items():z.writestr(n,b)
for dest in [path,folder/'01_审稿意见_结尾已更新.docx']:
    try:dest.write_bytes(out.getvalue());print('SAVED',dest,flush=True)
    except PermissionError:
        fallback=folder/'01_审稿意见_新增第7条.docx';fallback.write_bytes(out.getvalue());print('SAVED',fallback,flush=True)
rp=WORK/'responses.json';reviews=json.loads(rp.read_text(encoding='utf-8'))
review=next(r for r in reviews if r['reviewer']==2)
assert len(review['items'])==6
review['items'].append({'id':'R2.7','comment':'7. '+comment,'response':response,'changes':[],
    'response_only_note':'本条只在回复中解释现有的区域选择、执行器故障模式及稳定性分析之间的关系，不新增论文正文修改。依据为现有控制器定义、区域约束及含马尔可夫转移率的泛函分析。'})
rp.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
builder=WORK/'build_pdfs.py';source=builder.read_text(encoding='utf-8')
source=source.replace("arr.append(P('修改位置','sub'))", "arr.append(P('修改位置' if related else '回复说明','sub'))")
needle="arr.append(P('；'.join(f\"{p['id']}（红绿稿第 {p['marked_page']} 页，清洁稿第 {p['clean_page']} 页）\" for p in related),'small'))"
replacement="arr.append(P('；'.join(f\"{p['id']}（红绿稿第 {p['marked_page']} 页，清洁稿第 {p['clean_page']} 页）\" for p in related) if related else it['response_only_note'],'small'))"
assert needle in source;source=source.replace(needle,replacement)
needle="        detailed.append(P('逐项修改','sub'))"
replacement="        if not related:\n            continue\n"+needle
assert needle in source;source=source.replace(needle,replacement)
builder.write_text(source,encoding='utf-8')
source=source.replace('for r in reviews:', 'for r in reviews[1:2]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})
