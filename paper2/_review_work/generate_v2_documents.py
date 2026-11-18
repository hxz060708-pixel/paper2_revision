from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
# Reuse the template-preserving OOXML writer from the previous task.
writer = (ROOT/'_review_work'/'build_documents.py').read_text(encoding='utf-8').split('\ncomments=[',1)[0]
writer = writer.replace("OUT=ROOT/'paper2_审稿意见'", "OUT=ROOT/'paper2_审稿意见'/'第二版_结合模板'")
writer = writer.replace("WORK=ROOT/'_review_work'", "WORK=ROOT/'_review_work'/'v2'")
exec(compile(writer, 'retained_template_writer', 'exec'), globals())
content = json.loads((WORK/'document_content.json').read_text(encoding='utf-8'))
manifest = json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
comments = content['comments']

base_paragraph = paragraph
def paragraph(text, *args, **kwargs):
    text = text.replace('sigma', 'σ').replace('+/-', '±')
    p = base_paragraph(text, *args, **kwargs)
    r = p.find(W+'r')
    rp = deepcopy(r.find(W+'rPr'))
    p.remove(r)
    # Keep mathematical subscripts as Word text formatting, not underscores.
    for token in re.split(r'(F_i[01]?|V_i)', text):
        if not token:
            continue
        if re.fullmatch(r'[FV]_i[01]?', token):
            segments = [(token[0],False),(token[2:],True)]
        else:
            segments = [(token,False)]
        for value, sub in segments:
            run = ET.SubElement(p,W+'r')
            prop = deepcopy(rp)
            if sub:
                ET.SubElement(prop,W+'vertAlign',{W+'val':'subscript'})
                ET.SubElement(prop,W+'i')
            run.append(prop)
            ET.SubElement(run,W+'t',{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=value
    return p

report = [paragraph('Comments on paper2','title'), paragraph(content['overview'])]
for c in comments:
    report.append(paragraph(c,'number'))
report_path = write_doc('01_审稿意见_Reviewer1_第二版.docx',report)

response = [paragraph('Response to Reviewer 1','title'), paragraph('We thank the reviewer for the constructive suggestions. Each comment is reproduced below, followed by our response and the corresponding revision location.')]
for idx in range(6):
    if idx in (2,4):
        response.append(pagebreak())
    response.extend([
        paragraph('Comment '+str(idx+1),'label'),
        paragraph(comments[idx],italic=True),
        paragraph('Response','label'),
        paragraph(content['responses'][idx]),
        paragraph('Location: '+content['locations'][idx])
    ])
    if idx==1:
        response.append(paragraph('Added references','label'))
        response.append(paragraph('X. Liu, Z. Ling, and Y. Zhang. Torus-Event-Based Sliding Mode Control for Networked Interval Type-2 Fuzzy Systems Under Deception Attacks. International Journal of Network Dynamics and Intelligence 4(1) (2025), 100003. DOI: 10.53941/ijndi.2025.100003.'))
        response.append(paragraph('A. Chandrasekar, W.-J. Chang, T. Radhika, S. Santhosh Kumar, and M. S. Aslam. Adaptive event triggering asynchronous control for interval type-2 fuzzy Markov jump systems with uncertainties and deception attacks. Complex & Intelligent Systems 12 (2026), 59. DOI: 10.1007/s40747-025-02172-5.'))
    if idx==2:
        response.append(paragraph('Added text','label'))
        response.append(paragraph(content['motivation'].replace(r'Section~\ref{sec4}','Section 4')))
    if idx==5:
        response.append(paragraph('Revised caption for Figure 8','label'))
        response.append(paragraph('Adaptive threshold δ(t) for σ = 4 and sampling period h = 0.05 s. The equilibrium threshold is 1/σ = 0.25.'))

response.append(pagebreak())
response.append(paragraph('中文核对与修改对应','title'))
response.append(paragraph('本版共六条意见，已逐项落实到同目录的 paper2_修改副本。英文回复中的修改均可在副本内核对。'))
checks = [
    ('英语润色','缩短摘要、引言和结论中的长句；修正重复句号、主谓一致等问题。'),
    ('近期文献','引言新增两篇相关研究并说明联系；参考文献同步补齐作者、卷期、文章号与 DOI。'),
    ('应用背景','在引言中联系 PMSM 算例，说明传输数据受攻击、执行器效能降低和通信受限在模型中的位置。'),
    ('故障参数','补充 F_i0 为区间中点、F_i1 为半宽的物理解释；例 1 两模式的效能范围分别为 [0.8, 1.0] 和 [0.6, 1.0]。'),
    ('表 1 的趋势','结合 1/σ 解释已报告的发送次数变化；明确该解释以给定状态、误差和权重为条件，不把表中趋势写成所有设置下的必然规律。'),
    ('图注信息','在图 8、9、14、15 中补充 σ 和采样周期；两幅阈值图注补充相应的 1/σ 数值。')
]
for i,(title, explanation) in enumerate(checks,1):
    selected = [c for c in manifest['changes'] if c['id']=='R1.'+str(i)]
    lines = sorted(set(n for c in selected for n in c['revised_lines']))
    response.append(paragraph('R1.'+str(i)+'  '+title,'label'))
    response.append(paragraph(explanation+' 对应 paper2.tex 源码行：'+', '.join(map(str,lines))+'。'))
response.append(paragraph('补充核对','label'))
response.append(paragraph('根据稿件已有计数，例 2 的 65/400 对应节省率 83.75%，已将原文 83.79% 校正；发送次数未变。本轮没有重新运行仿真，也未重新验证全部定理，因此回复没有作这些完成声明。'))
response_path = write_doc('02_逐点回复_Reviewer1_第二版.docx',response)

def visible(s):
    return s.replace('sigma','σ').replace('F_i0','Fi0').replace('F_i1','Fi1').replace('F_i','Fi').replace('V_i','Vi').replace('+/-','±')
rtext=[p.text for p in Document(report_path).paragraphs]
atext=[p.text for p in Document(response_path).paragraphs]
assert all(visible(c) in rtext and visible(c) in atext for c in comments)
assert len([p for p in report if p.find('.//'+W+'numPr') is not None])==6
assert hashlib.sha256(REF.read_bytes()).hexdigest()==REFERENCE_HASH
(WORK/'artifact.md').write_text((WORK/'artifact.md').read_text(encoding='utf-8')+'\nSecond version content: language, recent literature, PMSM motivation, actuator-effectiveness parameters, Table 1 trend, and figure captions. The original paper and previous version are preserved. Response uses three English page groups and a Chinese cross-check page. Native Word subscripts are used for actuator symbols.\n',encoding='utf-8')
print(json.dumps(dict(report=str(report_path),response=str(response_path),comments=6,word_render='not_yet_rendered'),ensure_ascii=False))
