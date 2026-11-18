from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
import json,io

WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[1]
rp=WORK/'responses.json';reviews=json.loads(rp.read_text(encoding='utf-8'))
language_changes=next(r for r in reviews if r['reviewer']==1)['items'][0]['changes']
data=[
{
'comment':'Some expressions are conversational or insufficiently precise for an academic article. Please revise the language, particularly in the Abstract, Introduction, and Conclusion, to use a more formal academic style, consistent technical terminology, and appropriately qualified statements about the results.',
'response':'Thank you for this comment. We have revised the Abstract, Introduction, and Conclusion to improve academic tone, precision, and consistency. The Abstract now presents the problem, method, sufficient conditions, and numerical illustrations in a clearer order. General expressions have been replaced with descriptions of the specific mechanisms; for example, the discussion of fixed thresholds now states that they do not adjust online to the relevant fluctuations. We have also corrected grammatical errors and clarified abbreviations. The Conclusion describes the numerical results as illustrations under the selected settings and states the assumptions of the analysis, avoiding claims that go beyond the established results.',
'changes':language_changes,
'revision_plan':'改摘要、引言和结论的语言，不改公式。将泛泛、口语化的评价改为具体技术描述；统一术语和缩写；将数值结果表述为所选条件下的展示。详细版逐项列出实际措辞和标点改动。'
},
{
'comment':'The literature review would benefit from more recent studies closely related to secure IT-2 fuzzy control, adaptive event-triggered transmission, and actuator failures. Please supplement the relevant references and briefly compare their modeling assumptions and control strategies with those of this manuscript, rather than only expanding the reference list.',
'response':'Thank you for this suggestion. We have added two recent, directly relevant studies and expanded the comparison before the contribution list. Liu et al. (2025) consider discrete-time IT-2 fuzzy systems under deception attacks using torus-event-triggered sliding-mode control. Chandrasekar et al. (2026) investigate adaptive event-triggered asynchronous control of uncertain IT-2 fuzzy Markov jump systems under deception attacks. We also discuss the existing attack/failure study by Chen et al. (2023). The revised paragraph distinguishes our continuous-time formulation, Markov-type actuator effectiveness, and membership-derivative-based regional synthesis. It explains the connections without claiming that combining attacks and failures, or using adaptive event triggering alone, is new.',
'changes':['M08'],
'revision_plan':'在引言贡献列表之前加入相关工作比较段，并补入两条近期文献。比较对象、时间模型、攻击/故障设置和控制结构；保留对已有联合攻击/故障研究的承认，不使用没有文献依据的“首次”表述。'
},
{
'comment':'The manuscript considers deception attacks, actuator failures, and communication limitations within one framework. Could the authors explain why their interaction warrants a joint analysis, and how these factors affect the information received by the controller and the control action applied to the plant?',
'response':'Thank you for this question. We have added a motivation paragraph explaining the roles of the three factors in the feedback loop. Deception attacks can corrupt the sampled information used by the controller, while actuator failures alter the effectiveness of the resulting control input. Event-triggered transmission retains the last transmitted sample between releases, so the controller also operates with a sampling error. The plant therefore evolves under a control action influenced simultaneously by the available sample, possible data corruption, and actuator effectiveness. The added paragraph explains why these interacting effects motivate a joint stability and disturbance-attenuation analysis under the specified models.',
'changes':['M07'],
'revision_plan':'在引言的执行器故障讨论之后补一段联合研究动机，按“采样信息被篡改—控制作用受故障影响—两次传输间保留旧样本”的闭环关系说明三者的联系。沿用现有模型，不追加新模型或仿真。'
},
{
'comment':'The manuscript employs a two-sided looped functional incorporating fuzzy membership information. Could the authors explain how the looped structure captures inter-sample dynamics and what additional benefits the membership-dependent terms bring to the stability analysis?',
'response':'Thank you for this question. The two-sided looped structure uses the elapsed and remaining parts of a sampling interval, together with state and state-derivative information, to describe evolution between sampling instants. The auxiliary looped terms satisfy the endpoint-matching property used in the analysis, allowing this inter-sample information to enter the functional framework. Membership dependence provides complementary information: the weighted matrices retain the active fuzzy memberships, and their derivatives involve membership-function derivatives. The regional constraints exploit the signs of these derivatives in the stability and synthesis conditions. We have expanded Remark 3.1 to explain these roles separately and then their combination. This explanation identifies the information used by the construction without claiming an unverified quantitative advantage over all alternative functionals.',
'changes':['M33'],
'revision_plan':'扩充Remark 3.1：先解释已过去/剩余采样时间、V2/V3/V4中的状态与积分项以及端点匹配，再解释隶属函数加权矩阵和导数符号约束的作用。说明分析中的未来端点量不是控制器所需的额外测量，不新增保守性比较实验。'
},
{
'comment':'Remark 2.2 gives an equilibrium value for the adaptive threshold, but its interpretation could be clearer. How does the initial threshold relative to this equilibrium affect its evolution, and what role does the sampling error play? Please relate the explanation to the stated adaptation law and triggering condition.',
'response':'Thank you for this question. We have clarified the interpretation of the existing adaptation law in Remark 2.2. For a positive threshold and nonzero sampling error, the threshold increases when it is below 1/sigma and decreases when it is above 1/sigma. Its derivative is zero when the error is zero or the threshold equals 1/sigma. The weighted error magnitude scales the rate of adjustment. For fixed sampled state, error, and weighting matrix, a larger threshold makes the triggering inequality harder to satisfy. We also explain that actual transmission times depend on the joint evolution of these quantities, so the equilibrium alone does not imply the same trajectory or communication savings for every initial condition.',
'changes':['M17','M18'],
'revision_plan':'修正参数sigma的解释，并扩充Remark 2.2，分别说明初始阈值位于平衡值上方、下方及误差为零时的情况，再联系触发不等式。保留原自适应律，不改公式，也不把特定仿真趋势说成普遍保证。'
},
{
'comment':'The regional matrix constraints are selected according to the signs of the membership-function derivatives. Could the authors explain how a derivative-sign pattern determines the directions of these inequalities? One representative example would help clarify their role in the stability analysis and controller synthesis.',
'response':'Thank you for this suggestion. We have added an explanation after the regional controller and triggering definitions in Remark 2.4. For example, a nonpositive membership-function derivative multiplied by a positive semidefinite matrix difference gives a negative semidefinite term; for a positive derivative, reversing the matrix inequality produces the same sign. We also explain why the R2-related inequality has the opposite orientation, as the analysis requires a nonnegative derivative for that weighted matrix. Collecting these choices gives the constraint set for each region, which is imposed together with the synthesis LMIs. This addition explains the existing constraints without altering the theorem or proof.',
'changes':['M26'],
'revision_plan':'在Remark 2.4的区域控制器和触发矩阵定义后补一个代表性符号乘积说明，用P矩阵差解释不等式方向，并交代R2项方向相反的原因。随后说明各约束如何组成区域集合并与LMI联合使用；不变动定理约束。'
},
{
'comment':'The Conclusion should state the scope and limitations of the results more explicitly. Please identify the assumptions on state availability, deception attacks, and actuator-failure transitions, and explain how these assumptions motivate future work on output feedback or more general network conditions.',
'response':'Thank you for this comment. We have revised the final paragraph of the Conclusion to state that the analysis uses state feedback, Bernoulli-modeled deception attacks satisfying the prescribed signal bound, and Markov-type actuator failures with known transition rates. The conclusions are presented within these assumptions. Observer-based output feedback is identified as a future direction when full-state measurements are unavailable. Denial-of-service attacks and partially unknown transition rates are also identified as extensions requiring additional modeling and analysis. The paragraph now separates the scope of the established results from these open directions.',
'changes':['M58'],
'revision_plan':'重写结论最后一段：先列出状态反馈、伯努利攻击及其幅值约束、已知转移率三项适用前提，再对应提出输出反馈、DoS攻击和部分未知转移率等未来方向，不将未完成的扩展写成已有成果。'
}
]
review=next(r for r in reviews if r['reviewer']==3)
review['items']=[dict(d,id=f'R3.{i}',comment=f"{i}. "+d['comment']) for i,d in enumerate(data,1)]
folder=ROOT/'filally_22/审稿意见3';path=folder/'01_审稿意见.docx'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
tree=E.fromstring(parts['word/document.xml']);body=tree.find(W+'body');ps=body.findall(W+'p')
assert len(ps)>=9
prototype=deepcopy(ps[2]);insert_at=list(body).index(ps[2])
for p in ps[2:]:body.remove(p)
for i,d in enumerate(data):
    p=deepcopy(prototype);p.attrib.clear()
    rpr=deepcopy(p.find(W+'r').find(W+'rPr'))
    for el in list(p):
        if el.tag!=W+'pPr':p.remove(el)
    run=E.SubElement(p,W+'r');run.append(rpr);E.SubElement(run,W+'t').text=d['comment']
    body.insert(insert_at+i,p)
parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
buffer=io.BytesIO()
with ZipFile(buffer,'w',ZIP_DEFLATED) as z:
    for n,b in parts.items():z.writestr(n,b)
try:path.write_bytes(buffer.getvalue());print('SAVED',path,flush=True)
except PermissionError:
    path=folder/'01_审稿意见_重新整理版.docx';path.write_bytes(buffer.getvalue());print('SAVED',path,flush=True)
for name in ['01_审稿意见_结尾已更新.docx','01_审稿意见_新增第8条.docx']:
    alias=folder/name
    if alias.exists():
        try:alias.write_bytes(buffer.getvalue())
        except PermissionError:print('ALIAS LOCKED',alias.name,flush=True)
rp.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
mp=WORK/'manifest.json';manifest=json.loads(mp.read_text(encoding='utf-8'))
for p in manifest['patches']:
    p['ids']=[cid for cid in p['ids'] if not cid.startswith('R3.')]
    p['ids'] += [it['id'] for it in review['items'] if p['id'] in it['changes']]
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
builder=WORK/'build_pdfs.py';source=builder.read_text(encoding='utf-8')
source=source.replace("if cid in ['R1.3','R2.1','R3.7']:","if 'M08' in it['changes']:")
source=source.replace("if cid=='R3.5':","if it.get('include_figure_edits', False):")
needle="            arr.append(P('修改位置' if related else '回复说明','sub'))"
replacement="            if it.get('revision_plan'):\n                arr.append(P('具体改法','sub'));arr.append(P(it['revision_plan'],'cn'))\n"+needle
assert needle in source;source=source.replace(needle,replacement,1)
builder.write_text(source,encoding='utf-8')
source=source.replace('for r in reviews:', 'for r in reviews[2:3]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})
print('Reviewer 3 rebuilt: seven comments, seven responses, seven revision plans.',flush=True)
