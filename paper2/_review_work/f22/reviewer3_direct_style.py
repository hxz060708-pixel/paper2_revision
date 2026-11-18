from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
import json,io

WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[1]
rp=WORK/'responses.json';reviews=json.loads(rp.read_text(encoding='utf-8'))
third=next(r for r in reviews if r['reviewer']==3)
old={it['id']:deepcopy(it) for it in third['items']}
assert len(old)==7
def inherited(cid,comment):
    item=deepcopy(old[cid]);item['comment']=comment;return item
items=[
inherited('R3.1','The manuscript requires further editing to improve English grammar, sentence structure, and readability. Some expressions are informal or awkwardly phrased, particularly in the Abstract and Introduction. Careful language polishing is recommended to ensure clear and consistent academic expression.'),
inherited('R3.3','Why is it necessary to consider deception attacks, actuator failures, and communication limitations together? The Introduction should explain their interaction in the feedback loop more clearly and strengthen the practical motivation for the proposed framework.'),
inherited('R3.5','The interpretation of the adaptive-threshold parameter in Remark 2.2 is not sufficiently clear. Please explain its relationship with the equilibrium threshold and how the threshold evolves from different initial values under the influence of the sampling error.'),
inherited('R3.4','The manuscript employs a two-sided looped functional incorporating fuzzy membership information. Could the authors explain how the looped structure captures inter-sample dynamics and what additional benefits the membership-dependent terms bring to the stability analysis?'),
inherited('R3.6','The connection between the membership-function derivatives and the regional matrix constraints needs further explanation. How do the derivative signs determine the directions of the matrix inequalities? A representative example would help readers understand the regional controller design.'),
{
'comment':'The interpretation of the LMI-based conditions could be clearer. Please explain the distinction between the closed-loop stability requirement and the prescribed disturbance-attenuation performance, and relate this explanation to the existing definition and theorem.',
'response':'Thank you for this suggestion. We have added an interpretation after Theorem 3.1 and its proof, referring to the two requirements in Definition 2.1. Stability concerns the unforced closed loop with zero external disturbance. The prescribed H-infinity performance concerns the expected output-energy bound relative to disturbance energy for square-integrable disturbances under the stated zero-initial-condition convention. We explain that the output and performance-level terms enter the same sufficient-condition framework. We also clarify that infeasibility of these sufficient conditions alone does not establish instability. This explanation supplements the existing theorem without changing its conditions or proof.',
'changes':['M32'],
'revision_plan':'在定理3.1及其证明之后补一段解释，对应定义2.1区分无扰动稳定性与零初始条件下的能量衰减指标；说明LMI只是充分条件。沿用现有公式与证明。'
},
{
'comment':'Please check the presentation of the simulation figures, including axis labels, units, caption terminology, and the spacing between adjacent figures. The plotted quantities should be clearly identified, and their descriptions should be consistent throughout the manuscript.',
'response':'Thank you for this comment. We have revised the presentation of the existing figures. The actuator-mode axis wording has been corrected from "Operation models" to "Operating modes", and the corresponding captions now use consistent actuator-failure terminology. The caption of Figure 12 identifies the control input and membership-function derivative by their respective curve colors. We have added spacing between adjacent figure panels and explained the time units and normalized model quantities in the numerical section. These changes improve presentation without altering the simulation data.',
'changes':['M36','M39','M40','M41','M42','M48','M49','M50','M51','M52'],
'include_figure_edits':True,
'revision_plan':'修正两幅模式图的坐标文字，统一相关图注，明确图12中两条曲线的颜色与变量；给并排图加入间隔，在数值部分说明时间单位和归一化模型量。图中原文字在红绿稿中保留红色，新文字显示绿色，不重做仿真。'
},
inherited('R3.2','The literature review would benefit from broader coverage of recent advances in secure IT-2 fuzzy control and event-triggered control. The authors are encouraged to include more relevant studies published within the past three years to strengthen the research motivation and clarify the distinctions and connections between this work and existing methods.')
]
for i,item in enumerate(items,1):item['id']=f'R3.{i}';item['comment']=f'{i}. '+item['comment']
third['items']=items
folder=ROOT/'filally_22/审稿意见3';path=folder/'01_审稿意见.docx'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
tree=E.fromstring(parts['word/document.xml']);body=tree.find(W+'body');ps=body.findall(W+'p')
assert len(ps)==9
prototype=deepcopy(ps[2]);idx=list(body).index(ps[2])
for p in ps[2:]:body.remove(p)
for i,item in enumerate(items):
    p=deepcopy(prototype);p.attrib.clear();rpr=deepcopy(p.find(W+'r').find(W+'rPr'))
    for child in list(p):
        if child.tag!=W+'pPr':p.remove(child)
    run=E.SubElement(p,W+'r');run.append(rpr);E.SubElement(run,W+'t').text=item['comment'].split('. ',1)[1]
    body.insert(idx+i,p)
parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
buf=io.BytesIO()
with ZipFile(buf,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
try:path.write_bytes(buf.getvalue());print('SAVED',path,flush=True)
except PermissionError:
    fallback=folder/'01_审稿意见_简洁评审版.docx';fallback.write_bytes(buf.getvalue());print('SAVED',fallback,flush=True)
for name in ['01_审稿意见_结尾已更新.docx','01_审稿意见_重新整理版.docx','01_审稿意见_新增第8条.docx']:
    alias=folder/name
    if alias.exists():
        try:alias.write_bytes(buf.getvalue())
        except PermissionError:print('ALIAS LOCKED',name,flush=True)
rp.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
mp=WORK/'manifest.json';manifest=json.loads(mp.read_text(encoding='utf-8'))
for patch in manifest['patches']:
    patch['ids']=[cid for cid in patch['ids'] if not cid.startswith('R3.')]
    patch['ids'] += [it['id'] for it in items if patch['id'] in it['changes']]
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
builder=WORK/'build_pdfs.py';source=builder.read_text(encoding='utf-8').replace('for r in reviews:', 'for r in reviews[2:3]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})
print('第三篇8条已重写，回复及具体改法已同步。',flush=True)
