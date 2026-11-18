from pathlib import Path
import json,re,difflib
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'_review_work'/'finally_work';OUT=ROOT/'finally';REV=OUT/'paper2_修改副本'
m=json.loads((WORK/'manifest.json').read_text(encoding='utf-8'))
old=(ROOT/'paper2'/'paper2.tex').read_text(encoding='utf-8');new=(REV/'paper2.tex').read_text(encoding='utf-8')
occ=[]
for c in m['changes']:
    for q in re.finditer(re.escape(c['old']),old):occ.append((q.start(),q.end(),c))
occ.sort(key=lambda x:x[0]);assert all(a[1]<=b[0] for a,b in zip(occ,occ[1:]))
offset=0
for c in m['changes']:c['revised_lines']=[]
for start,end,c in occ:
    pos=start+offset;assert new[pos:pos+len(c['new'])]==c['new'],c['location']
    c['revised_lines'].append(new[:pos].count('\n')+1)
    offset+=len(c['new'])-(end-start)
lang=sorted([c for c in m['changes'] if 'language_id' in c],key=lambda c:c['original_lines'][0])
for i,c in enumerate(lang,1):c['language_id']=f'L{i:02d}'
(WORK/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')

aux=(REV/'paper2.aux').read_text(encoding='utf-8')
labels={a:(b,c) for a,b,c in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{([^}]+)',aux)}
pages=[''.join(p.extract_text().split()) for p in PdfReader(REV/'paper2.pdf').pages]
def pageof(phrase):
    needle=''.join(phrase.split());hits=[i+1 for i,t in enumerate(pages) if needle in t]
    assert hits,(phrase,);return hits[0]
def cfind(part):return next(c for c in m['changes'] if part in c['location'])
def addpart(c):
    if c['new'].endswith(c['old']):return c['new'][:-len(c['old'])].strip()
    if c['new'].startswith(c['old']):return c['new'][len(c['old']):].strip()
    return c['new']
previous=json.loads((ROOT/'_review_work'/'v4'/'document_content.json').read_text(encoding='utf-8'))
orders=[[0,5,1,2,3,4],[0,5,2,1,None,4],[0,5,1,2,3,4]]
items=[]
for ri in range(3):
    block=[]
    for ci,idx in enumerate(orders[ri]):
        item={'id':f'R{ri+1}.{ci+1}'}
        if idx is not None:
            for field in ['comments','responses','titles','template_basis']:
                item[field.rstrip('s') if field!='template_basis' else field]=previous[field][ri][idx]
        block.append(item)
    items.append(block)

# Keep the report comments short and concrete; English and literature come first in all three.
items[1][4].update(comment='The respective purposes of the two examples could be stated more clearly. Please briefly explain what the PMSM example and the second numerical example illustrate at the beginning of Section 4.',title='两个算例的作用',template_basis='新+第2份第5条；MATH 模板中的仿真解释建议。')
items[1][5]['comment']='The discussion in Remark 2.2 could be made easier to follow. Please briefly explain how the adaptive threshold in Eq. (6) relates to the transmission condition in Eq. (5).'
items[0][2]['comment']='The practical motivation could be made more concrete. Please relate the joint consideration of deception attacks, actuator failures, and communication limitations to the PMSM example.'
items[0][3]['comment']='The meaning of some design parameters could be explained more clearly. In particular, please clarify the roles of ξ_1 and ξ_2 in Theorem 3.2.'

language_response='We have edited the Abstract, Introduction, model description, and Conclusion for grammar, sentence structure, and consistent terminology. For example, "the transmitted data is" has been changed to "the transmitted data are", "K_n denote" to "K_n denotes", and "condition ... guarantee" to "condition ... guarantees". The Abstract and the opening conclusion paragraph have also been made more concise. All 17 language-edit entries, covering 19 replacement locations, are listed with the original text, revised text, and complete changes in the accompanying language comparison.'
reference_response='We have added two recent, directly related studies as References [34] and [35]. A new paragraph before the contribution statement explains their connection to event-triggered secure fuzzy control and identifies the model setting and membership-function-derivative-based design considered in the present paper. Both references are cited in the text, and their bibliographic details have been checked against the publisher records.'
for ri in range(3):
    items[ri][0]['response']=language_response
    items[ri][1]['response']=reference_response
items[0][2]['response']='We have added a paragraph linking the joint problem setting to the PMSM example. It explains that deception attacks affect the transmitted current and angular-velocity measurements, actuator degradation reduces the effective control input, and the event trigger limits transmissions. This gives a concrete engineering interpretation of the modeled requirements for data integrity, actuator reliability, and communication efficiency.'
items[0][3]['response']='We have added an explanation immediately before Theorem 3.2. The prescribed scalars ξ_1 and ξ_2 specify the proportionality relations Q_2 = ξ_1 Q_1 and Q_3 = ξ_2 Q_1 in the variable transformation. They are fixed during each LMI feasibility solve, and different choices may affect feasibility. The text now distinguishes these synthesis parameters from physical plant and attack parameters.'
items[0][4]['response']='We have removed the duplicated full stop after "CPSs" in the Introduction. We also corrected subject-verb agreement in the transmitted-data and controller-gain descriptions and in the proof text. The exact changes and their locations are included in the language comparison.'
items[0][5]['response']='We have changed the vertical-axis title from "Operation models" to "Operating modes" in both Figs. 7 and 13. Their captions have also been shortened to "Actuator-failure mode r(t)". The switching traces, axis ticks, time intervals, and reported results are unchanged.'
items[1][2]['response']='We have added a short paragraph immediately after Eq. (15). It explains that the Bernoulli variable selects the state information received by the controller, while the actuator-effectiveness matrix changes the input delivered to the plant. The paragraph therefore distinguishes the information channel from the actuation channel and identifies the corresponding terms in the existing closed-loop model.'
items[1][3]['response']='We have expanded Remark 3.1 to explain the roles of the functional components. The FMF-weighted matrices retain membership dependence; the elapsed and remaining interval lengths incorporate sampling information. The two integrals in V_3 use derivative information on either side of the current time, the augmented-vector terms in V_2 and V_4 add interval information, and V_5 incorporates the adaptive threshold. These explanations refer to the functional already defined in the manuscript.'
items[1][4]['response']='We have revised the opening paragraph of Section 4. It now states that the PMSM example provides an engineering context and reports communication counts for different values of σ, whereas the second example uses a different IT-2 fuzzy model with fixed design parameters. It also identifies the state, input, threshold, actuator-mode, and transmission results used to illustrate the closed-loop behavior.'
items[1][5]['response']='We have expanded Remark 2.2 and refined the description of σ below Eq. (6). For a positive threshold and nonzero triggering error, the update increases the threshold below 1/σ and decreases it above 1/σ. The update is zero when the error is zero or the threshold equals 1/σ. The text relates this adjustment to Eq. (5) and explains that the transmission count depends on the evolving state, error, and threshold.'
items[2][2]['response']='We have expanded the discussion before Table 1. Under the reported settings, increasing σ from 4 to 20 increases transmissions from 85 to 164, while the equilibrium threshold 1/σ decreases from 0.25 to 0.05. The text relates a smaller threshold to easier satisfaction of the triggering condition for fixed sampled state, error, and weighting matrix. It also makes clear that the observed count depends on the closed-loop trajectory and threshold evolution.'
items[2][3]['response']='We have defined the saving rate using the reported event-triggered and time-triggered counts over the same interval. The first table row gives (1 − 85/400) × 100% = 78.75%; all four rows give 78.75%, 71.75%, 66.00%, and 59.00%. In Example 2, 65 transmissions out of 400 candidates give 83.75%, so the previous value of 83.79% has been corrected. The reported transmission counts are unchanged.'
items[2][4]['response']='We have expanded the discussion and caption of Fig. 12. The blue curve shows the control input, while the black curve shows the membership-function derivative. The input illustrates the actuation generated by feedback, and the derivative sign provides the regional switching information in Remark 2.4. The text relates their approach to zero to the settling state responses and explains the purpose of showing the two quantities together.'
items[2][5]['response']='We have revised the final conclusion paragraph to state that the current formulation uses state feedback, a specified deception-signal bound, and known Markov transition rates. We then connect the future directions to these assumptions: observer-based output feedback when all states are not measured, DoS attacks, and partially unknown transition rates. This clarifies the scope of the current results before discussing possible extensions.'

lit=cfind('paragraph immediately before the contributions')
mot=cfind('following the actuator-failure')
scalar=cfind('immediately before Theorem')
fun=cfind('explanation of the functional')
model=cfind('immediately after Eq.')
adapt=cfind('comparison with a fixed')
trend=cfind('discussion immediately before Table')
rate=cfind('Example 2, communication')
fig=cfind('interpretation of Fig.')
scope=cfind('Conclusion, final')
examples=cfind('Section 4, opening')
for ri in range(3):
    items[ri][0].update(location='Abstract, Introduction, Sections 2 and 3, Example 2, and Conclusion.',cn='先看 01_语言修改逐字对照.pdf。该文件完整列出 L01-L17 的原文、改文、逐词增删和原稿/修改稿源码行号。',quotes=[('Example language edits','the transmitted data is → the transmitted data are\nK_n denote → K_n denotes\ncondition ... guarantee → condition ... guarantees')])
    items[ri][1].update(location=f'Introduction, p. {pageof("Recent work has")}, before the contribution statement; References [34] and [35], p. {pageof("100003")}.',cn='在引言贡献列表前增加文献讨论，并在 ref2.bib 增加两条记录。三份回复共同对应这一处修改，不重复添加。',quotes=[('Added paragraph',addpart(lit))] if ri==0 else [('Corresponding manuscript sentence',addpart(lit).split('The present study')[1].join(['The present study','']))])
items[0][2].update(location=f'Introduction, p. {pageof("The PMSM example in Section")}, following the actuator-failure motivation paragraph.',cn='新增工程背景段，把三类因素分别落到 PMSM 的测量、输入和通信环节。',quotes=[('Added text',mot['new'].split('\n\n')[1])])
items[0][3].update(location=f'Section 3, p. {pageof("The prescribed scalars")}, immediately before Theorem 3.2.',cn='只说明现有 ξ 参数在变量变换中的含义，不要求参数优化或新增理论推导。',quotes=[('Added text',addpart(scalar))])
items[0][4].update(location=f'Introduction, p. {pageof("two common cyber threats")}; additional language locations in L01-L17.',cn='重复句号对应语言对照中的 L05；其他主谓一致问题也逐处列出。',quotes=[('Before','are two common cyber threats to CPSs..'),('After','are two common cyber threats to CPSs.')])
items[0][5].update(location=f'Fig. 7, p. {labels["fig6"][1]}, and Fig. 13, p. {labels["fig13"][1]}.',cn='对应 figs/actuator_fault.pdf 和 figs/2_actuator_fault.pdf。轴标题替换前后作过像素比对；轴标题区域以外保持一致。',quotes=[('Axis title before','Operation models'),('Axis title after','Operating modes'),('Revised captions','Actuator-failure mode r(t).')])
items[1][2].update(location=f'Section 2.4, p. {pageof("The two uncertainty sources")}, immediately after Eq. (15).',cn='把新增解释放在模型公式之后；不采用新+第2份第2条中跑题的文献回复。',quotes=[('Added text',addpart(model))])
items[1][3].update(location=f'Remark 3.1, p. {pageof("In particular, the FMF")}.',cn='解释已有泛函各项使用的信息，不要求证明新定理或补充优越性对比。',quotes=[('Added text',addpart(fun))])
items[1][4].update(location=f'Section 4, p. {labels["sec4"][1]}, opening paragraph.',cn='用一段话说明两个算例各自展示什么；没有新增实验或声称两个算例证明普遍适用性。',quotes=[('Replacement paragraph',examples['new'])])
items[1][5].update(location=f'Section 2.2, p. {pageof("For comparison, a fixed")}, sentence below Eq. (6) and Remark 2.2.',cn='阈值如何变化直接按原式(6)解释，再与式(5)联系；公式本身不改。',quotes=[('Sentence below Eq. (6)',cfind('sentence after Eq. (6)')['new']),('Revised end of Remark 2.2',adapt['new'])])
items[2][2].update(location=f'Example 1, pp. {pageof("In Table 1")}-{labels["tab:sigma_effect"][1]}, paragraph before Table 1.',cn='只解释现有四组 σ 设置下的计数趋势，不把它写成通用规律或控制性能定量对比。',quotes=[('Added discussion',trend['new'].split('\n')[0])])
items[2][3].update(location=f'Example 1, p. {pageof("The saving rate is calculated")}, before Table 1; Example 2, p. {pageof("83.75")}, final paragraph.',cn='基准为稿件报告的400次候选发送；四组表格比例逐项核算。算例二将83.79%改为83.75%。',quotes=[('Definition and table calculations',trend['new'].split('\n')[1]),('Corrected Example 2 text',rate['new'])])
items[2][4].update(location=f'Fig. 12 and its discussion, p. {labels["fig12"][1]}.',cn='解释两条曲线各自表示什么，并在图注标明蓝线/黑线；曲线本身不变。',quotes=[('Revised discussion',fig['new']),('Revised caption',cfind('Fig. 12 caption')['new'])])
items[2][5].update(location=f'Conclusion, p. {labels["sec5"][1]}, final paragraph.',cn='原文已有未来工作；本次在它之前明确当前状态反馈、攻击界和转移率条件。',quotes=[('Replacement paragraph',scope['new'])])

for block in items:
    for it in block:
        it['changes']=[c['change_id'] for c in m['changes'] if it['id'] in c['ids']]
        assert it['changes'] or it['id']=='R1.6'

reasons={
'Abstract':('摘要长句与组织顺序','把背景长句压缩为机制的直接描述，统一 attack/failure 的表述，明确已有分区设计。此项含结构重排和方法信息明确化，不把所有改动都当作语法错误。'),
'Introduction paragraph 1':('应用范围措辞','span 改为 include；删除不必要的 advanced，使列举更直接。'),
'Introduction paragraph 2':('研究空缺措辞','coupled 改为 concurrent，强调同时存在；不足判断改为 warrants further investigation。完整句主语为 secure and reliable control，因此使用 warrants。'),
'Introduction paragraph 3':('句式或标点','重复句号删除一个；被动且冗长的 flexibility is improved 改为直接表达 gain communication flexibility。下方按具体原片段列出。'),
'Introduction paragraph 4':('固定阈值表述','把 cannot adapt well 的效果判断改为 do not adjust online 的机制描述。'),
'Introduction contribution 2':('贡献描述精简','用 This online adjustment 承接前句已有阈值更新说明，减少重复；其余替换词全部列在增删表中。'),
'Section 2.2 opening':('通信机制段落精简','continuous 改为 frequent，避免把离散采样发送称为连续发送；删除重复的通信负担表达。'),
'Section 2.3 Bernoulli description':('data 的主谓一致','is 改为 are，与本稿将 data 作为复数的用法一致。'),
'Section 2.3 Remark 2.3':('比较结构','Different from 改为 Unlike，并整理定语从句和逗号，使比较关系更自然。'),
'Section 2.4, controller-rule description':('单个规则增益的主谓一致','K_n 指第 n 条规则的一个增益矩阵，denote 改为 denotes；gains 改为 gain，并明确 for rule n。'),
'Section 3 notation':('notation 的用法','For compact representation 改为 For compactness；将此处集合性 notation 用单数形式，are 改为 is。'),
'Section 3 system terminology':('单个闭环系统称谓','将 CPSs 改为 system，与单个闭环模型及后面的 is 对应。实际改动三处，三个源码行号均列出。'),
'Proof of Theorem 3.1':('condition 的主谓一致','主语 condition 为单数，guarantee 末尾增加 s，改为 guarantees。'),
'Example 2 discussion':('冗余修饰','删除 a clear，直接写 exhibits divergent behavior。'),
'Example 2 closing discussion':('通信优势表述具体化','把笼统的 same communication-efficiency advantage 改成相对每个候选样本都发送的基准，明确比较对象。'),
'Conclusion paragraph 1':('结论句式精简','将连续的被动长句改为较短的主动/直接陈述，保留原有方法要素。逐词表列出每处删除、增加和替换。')}
for c in lang:
    c['title_cn'],c['reason_cn']=reasons[c['location']]
    if c['location']=='Introduction paragraph 3':
        if 'CPSs..' in c['old']:
            c['title_cn']='重复句号'
            c['reason_cn']='删除 CPSs 后多出的第二个句号；其余词保持不变。'
        else:
            c['title_cn']='被动长句改为直接表达'
            c['reason_cn']='their flexibility is improved 改为 they gain communication flexibility；后半句用 face constraints 表达遇到约束，删去重复的被动结构。'
data=dict(overviews=previous['overviews'],reviewers=items,language=lang,labels=labels,manuscript_pages=len(pages))
(WORK/'content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

readme='''finally 阅读顺序

1. 先看 01_语言修改逐字对照.pdf。17项语言修改覆盖19处实际替换；每项都有原文、改后全文、完整增删词表、原因及原稿和修改稿的源码行号。
2. 再看三份最终版 Word。每份6条；第1条为英文，第2条为近期文献，其余4条分别展开。
3. 三份“回复与修改位置”PDF逐条列出英文意见、英文答复、中文修改说明、实际正文改文和位置。
4. paper2_修改副本 是与这些回复一致的论文副本。08_全部修改精确对照.txt 保存源代码原文与改文，便于逐字搜索核对。

新+材料的取舍
新+不是全部太难。联合动机、两个算例的作用、已有曲线的解释、结论范围，均可利用现有内容补充。涉及分区条件如何进入综合、整套符号系统审查和可复现实验步骤的宽泛要求，本轮没有采用；避免把简单说明扩大成新的证明或实验任务。
新+第2份第2条要求说明 Eq. (15) 的模型过渡，但所附PDF回答成了文献比较。最终版已改为与两个反馈环节对应的模型解释。
主要仍沿用 SMCA、AMC、ESWA、MATH 模板的语气和问题粒度；新+仅提供合适的具体问题。

文件对应与核对边界
三份语言意见对应同一批修改；三份文献意见也对应同一处文献补充。没有为了三个审稿人重复改写正文。
这些是供作者审阅的拟定审稿意见和对应回复，不代表实际外审结果。本轮没有重新运行仿真或重证定理。节省率按已有计数核算；65/400对应83.75%。原始paper2未覆盖。
Word按原模板保留字体、页面和编号，内容及文档结构已核对。当前缺少Word转页组件，无法完成Word分页视觉核验。PDF均单独排版和核验，不是假称由Word成功转换。
'''
(OUT/'00_阅读顺序与新加材料取舍.txt').write_text(readme,encoding='utf-8')
raw=['全部修改精确对照\n原稿：paper2/paper2.tex\n修改稿：finally/paper2_修改副本/paper2.tex\n这里保留完整LaTeX原文与改文，包括标点及源码换行。\n']
for c in m['changes']:
    raw.extend([f"{c['change_id']}  {' / '.join(c['ids'])}  {c.get('language_id','')}\n{c['location']}\n原稿起始行 {c['original_lines']}；修改稿起始行 {c['revised_lines']}\n",'【原文】\n'+c['old']+'\n','【改文】\n'+c['new']+'\n\n'])
for c in m['figure_edits']:raw.append(f"图文件 {c['file']}：{c['old']} → {c['new']}\n")
oldbib=(ROOT/'paper2'/'ref2.bib').read_text(encoding='utf-8');newbib=(REV/'ref2.bib').read_text(encoding='utf-8');assert newbib.startswith(oldbib)
raw.append('\n【ref2.bib 新增完整记录】\n'+newbib[len(oldbib):])
(OUT/'08_全部修改精确对照.txt').write_text('\n'.join(raw),encoding='utf-8')
print(json.dumps(dict(language_entries=len(lang),language_locations=sum(c['count'] for c in lang),reviewers=3,comments=18,pdf_pages=len(pages)),ensure_ascii=False))
