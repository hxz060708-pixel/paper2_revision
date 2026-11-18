from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
from docx import Document
import json, hashlib, re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'paper2_审稿意见'
WORK=ROOT/'_review_work'
REF=next((ROOT/'论文审稿参考').rglob('Comment on SMCA-25-06-2213.docx'))
REFERENCE_HASH=hashlib.sha256(REF.read_bytes()).hexdigest()
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
with ZipFile(REF) as z:
    parts={n:z.read(n) for n in z.namelist()}
root=ET.fromstring(parts['word/document.xml'])
body=root.find(W+'body')
paras=body.findall(W+'p')
sect=deepcopy(body.find(W+'sectPr'))
title_pattern=deepcopy(paras[0]); body_pattern=deepcopy(paras[1]); list_pattern=deepcopy(paras[3])
styles=ET.fromstring(parts['word/styles.xml'])
title_style=next((s for s in styles.findall(W+'style') if (s.find(W+'name') is not None and s.find(W+'name').get(W+'val','').lower()=='title')),None)
if title_style is None:
    title_id='ReviewTitle'
    title_style=ET.SubElement(styles,W+'style',{W+'type':'paragraph',W+'styleId':title_id})
    ET.SubElement(title_style,W+'name',{W+'val':'Title'})
    ET.SubElement(title_style,W+'qFormat')
else: title_id=title_style.get(W+'styleId')

sha=lambda b:hashlib.sha256(b).hexdigest()
inventory={n:dict(size=len(b),sha256=sha(b),policy='editable' if n in ['word/document.xml','word/styles.xml','docProps/core.xml','docProps/app.xml'] else 'preserve') for n,b in parts.items()}
(WORK/'template_parts.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
geometry=ET.tostring(sect,encoding='unicode')
(WORK/'artifact.md').write_text(f'''# Review document template contract
Reference: {REF}
SHA256: {sha(REF.read_bytes())}
Sections: 1. A4 11906 x 16838 twips. Top/bottom margins 1440; left/right 1800.
Reference title: centered Times New Roman 14 pt bold. Body and numbered comments: Times New Roman 12 pt. Black text. Numbered paragraphs reuse source numId 1 and style a7.
Content flow: title, overview, six numbered paragraphs. Original eight review paragraphs, blank separators, and embedded equation runs are replacement slots, not retained prose.
Stable locators: word/document.xml / w:document/w:body/w:p[1] title; p[2] overview; first numbered paragraph p[4] repeated for six comments. sectPr is preserved.
Response: the same page geometry and type family, with bold comment/response labels and explicit page breaks between pairs of comments. Chinese check page uses Microsoft YaHei for East Asian glyphs.
All original textual content slots are replaced. No tables, headers, footers, comments, or page fields are added. Original unused relationship-backed equation assets and all preserve-only package parts stay byte-identical.
Intentional adaptation: named Title paragraph style; consistent 6 pt paragraph spacing and 1.15 line spacing; numbered comments remain together. Report uses 12 pt source body; long response uses the same 12 pt.
Verification: template-render attempted using packaged render_docx.py; blocked by missing soffice.exe. Native Word automation is denied in this session. Visual page verification remains pending. Text, XML, preserved parts, paragraph geometry, and source hashes will be checked programmatically.
''',encoding='utf-8')

def paragraph(text,kind='body',bold=False,italic=False,after=120):
    proto={'title':title_pattern,'number':list_pattern}.get(kind,body_pattern)
    p=deepcopy(proto)
    for k in list(p.attrib): del p.attrib[k]
    ppr=p.find(W+'pPr')
    if ppr is None: ppr=ET.SubElement(p,W+'pPr')
    for e in list(p):
        if e is not ppr: p.remove(e)
    for tag in ['spacing','keepNext','keepLines','pBdr']:
        for e in ppr.findall(W+tag):ppr.remove(e)
    ET.SubElement(ppr,W+'spacing',{W+'after':str(after),W+'line':'276',W+'lineRule':'auto'})
    ET.SubElement(ppr,W+'keepLines')
    if kind in ['title','label']: ET.SubElement(ppr,W+'keepNext')
    if kind=='title':
        old=ppr.find(W+'pStyle')
        if old is not None:ppr.remove(old)
        ppr.insert(0,ET.Element(W+'pStyle',{W+'val':title_id}))
    if kind=='label': bold=True
    r=ET.SubElement(p,W+'r'); rp=ET.SubElement(r,W+'rPr')
    ET.SubElement(rp,W+'rFonts',{W+'ascii':'Times New Roman',W+'hAnsi':'Times New Roman',W+'cs':'Times New Roman',W+'eastAsia':'Microsoft YaHei'})
    if bold or kind=='title': ET.SubElement(rp,W+'b')
    if italic: ET.SubElement(rp,W+'i')
    ET.SubElement(rp,W+'color',{W+'val':'000000'})
    size='28' if kind=='title' else '24'
    ET.SubElement(rp,W+'sz',{W+'val':size}); ET.SubElement(rp,W+'szCs',{W+'val':size})
    ET.SubElement(r,W+'t',{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=text
    return p

def pagebreak():
    p=ET.Element(W+'p');r=ET.SubElement(p,W+'r');ET.SubElement(r,W+'br',{W+'type':'page'});return p

def write_doc(name,elements):
    dest=OUT/name
    rt=deepcopy(root);b=rt.find(W+'body')
    for item in list(b): b.remove(item)
    for e in elements:b.append(e)
    b.append(deepcopy(sect))
    modified=dict(parts)
    modified['word/document.xml']=ET.tostring(rt,encoding='UTF-8',xml_declaration=True,standalone=True)
    modified['word/styles.xml']=ET.tostring(styles,encoding='UTF-8',xml_declaration=True,standalone=True)
    core=ET.fromstring(parts['docProps/core.xml'])
    for e in core:
        local=ET.QName(e).localname
        if local in ['creator','lastModifiedBy']:e.text=''
        elif local in ['title','subject','description','keywords','category']:e.text=''
        elif local=='revision':e.text='1'
    modified['docProps/core.xml']=ET.tostring(core,encoding='UTF-8',xml_declaration=True,standalone=True)
    app=ET.fromstring(parts['docProps/app.xml'])
    for e in app:
        if ET.QName(e).localname in ['Pages','Words','Characters','CharactersWithSpaces','Paragraphs','Lines','TotalTime']:e.text='0'
    modified['docProps/app.xml']=ET.tostring(app,encoding='UTF-8',xml_declaration=True,standalone=True)
    with ZipFile(dest,'w',ZIP_DEFLATED) as z:
        for n,data in modified.items():z.writestr(n,data)
    # The structure, section geometry, and preserve-only parts are verified.
    with ZipFile(dest) as z:
        assert all(z.read(n)==parts[n] for n in parts if inventory[n]['policy']=='preserve')
        actual_sect=ET.fromstring(z.read('word/document.xml')).find(W+'body').find(W+'sectPr')
        assert ET.tostring(actual_sect,method='c14n',exclusive=True)==ET.tostring(sect,method='c14n',exclusive=True)
    doc=Document(dest)
    assert doc.paragraphs[0].style.name=='Title'
    assert 'SMCA-25-06-2213' not in '\n'.join(p.text for p in doc.paragraphs)
    return dest

comments=[
'The English presentation could be further improved. Please polish the grammar, sentence structure, punctuation, and terminology throughout the manuscript, particularly in the Abstract, Introduction, and Conclusion, to enhance clarity and readability.',
'The references could be further updated with recent studies directly related to secure event-triggered control of interval type-2 fuzzy systems. A brief discussion of their connections with the present work would help clarify the research context.',
'The title emphasizes membership-function-derivative-dependent switching. Please state this feature more explicitly in the Abstract and briefly explain its role in the controller and triggering-parameter design.',
'The relationships among Theorems 3.1, 3.2, and 3.3 could be made easier to follow. A short overview at the beginning of Section 3 explaining the role of each theorem would improve the presentation.',
'The two examples illustrate the method from different perspectives. Please briefly explain their respective purposes at the beginning of Section 4, including the engineering role of the PMSM example and the role of the second fuzzy-system example.',
'Please define the communication saving rate explicitly and explain how the percentages in Table 1 and Example 2 are calculated from the reported transmission counts. This would make the communication-efficiency results easier to interpret.'
]
overview='This paper studies adaptive event-triggered control for interval type-2 fuzzy cyber-physical systems subject to deception attacks and Markov-type actuator failures. It combines membership-function derivative information, a region-dependent fuzzy controller, and a looped-functional approach, with a PMSM example and a numerical example. The topic is relevant to secure networked control. The following comments are intended to improve the clarity and presentation of the manuscript.'
report=[paragraph('Comments on paper2','title'),paragraph(overview)]
report.extend(paragraph(c,'number') for c in comments)
report_path=write_doc('01_审稿意见_Reviewer1.docx',report)

manifest=json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
changes=manifest['changes']
find=lambda id,loc=None:next(c for c in changes if id in c['id'] and (not loc or loc in c['location']))
def plain(t):
    t=t.replace(r'\mathrm{H}_\infty','H∞').replace(r'\mathrm{H}_{\infty}','H∞')
    t=re.sub(r'\\ref\{thm([123])\}',lambda m:'3.'+m.group(1),t)
    t=t.replace(r'\ref{exm1}','1').replace(r'\ref{exm2}','2').replace(r'\ref{tab:sigma_effect}','1')
    t=t.replace(r'\sigma','σ').replace(r'\%','%').replace(r'\times','×')
    t=t.replace(r'N_{\mathrm{TT}}','N_TT').replace(r'N_{\mathrm{ET}}','N_ET')
    t=re.sub(r'\\cite\{liuTorusEventBased2025\}','[Liu et al., 2025]',t)
    t=re.sub(r'\\cite\{chandrasekarAdaptiveEvent2026\}','[Chandrasekar et al., 2026]',t)
    t=t.replace(r'\ ',' ').replace('$','').replace('~',' ')
    return t

locations={
'R1.1':'Abstract; Section 1; Sections 2.2 and 2.3; Section 3; Example 2; Conclusion.',
'R1.2':'Section 1, p. 2, paragraph immediately before the contribution statement; References [34] and [35].',
'R1.3':'Abstract, p. 1, sentences describing the operational regions and joint design.',
'R1.4':'Section 3, p. 6, opening paragraph.',
'R1.5':'Section 4, p. 12, opening paragraph.',
'R1.6':'Example 1, p. 15, paragraph immediately before Table 1; Example 2, p. 17, final paragraph.'}

responses=[
'We have edited the prose for grammar, punctuation, sentence length, and consistent terminology. The Abstract and the first paragraph of the Conclusion have been rewritten more concisely. We also corrected the duplicated full stop after “CPSs” in the Introduction, changed “the transmitted data is” to “the transmitted data are” in Section 2.3, and corrected “condition ... guarantee” to “condition ... guarantees” in the proof of Theorem 3.1. Singular references to the closed-loop system have been standardized. These are language edits; the displayed mathematical expressions are unchanged.',
'We have added two recent studies and a paragraph explaining their relevance. Liu et al. (2025) address discrete-time IT-2 fuzzy systems with torus-event-triggered sliding-mode control under deception attacks. Chandrasekar et al. (2026) consider adaptive event-triggered asynchronous control of uncertain IT-2 fuzzy Markov jump systems. The added paragraph relates these developments to the continuous-time model and membership-function-derivative-based design considered here. Both references have been added to the bibliography and cited in the Introduction.',
'We have revised the Abstract to state explicitly how the derivative sign information defines the operational regions and how this relates to the design. The added description is quoted below. It reflects the region-dependent formulation already presented in the manuscript.',
'We have replaced the opening paragraph of Section 3 with an overview of the three stages: performance analysis in Theorem 3.1, transformed variables for joint controller and triggering-matrix design in Theorem 3.2, and deterministic synthesis conditions after bounding actuator-failure uncertainty in Theorem 3.3. This overview makes the sequence explicit before the detailed notation and results.',
'We have expanded the opening of Section 4 to distinguish the purposes of the two examples. The PMSM model provides an engineering context and reports communication counts for several values of the triggering parameter. The second example illustrates the scheme for a different IT-2 fuzzy model with a fixed parameter setting. The revised paragraph also identifies the common quantities displayed in the figures.',
'We have defined the saving rate as (1 − N_ET/N_TT) × 100%, where N_TT and N_ET denote the reported baseline and event-triggered transmission counts over the same interval. We added the calculation for the first row of Table 1. Its four rows give 78.75%, 71.75%, 66.00%, and 59.00%, respectively. In Example 2, the reported counts of 65 and 400 give 83.75%; the percentage has been corrected from 83.79% to 83.75%. The reported transmission counts are unchanged.'
]

response=[paragraph('Response to Reviewer 1','title'),paragraph('We thank the reviewer for the suggestions on presentation and clarity. Below, each comment is followed by the corresponding response and the location of the changes in the revised manuscript.')]
for i,(comment,answer) in enumerate(zip(comments,responses),1):
    if i in (3,5):response.append(pagebreak())
    response.append(paragraph('Comment '+str(i),'label'))
    response.append(paragraph(comment,italic=True))
    response.append(paragraph('Response','label'))
    response.append(paragraph(answer))
    response.append(paragraph('Location: '+locations['R1.'+str(i)]))
    if i==2:
        response.append(paragraph('Added references','label'))
        response.append(paragraph('X. Liu, Z. Ling, and Y. Zhang. Torus-Event-Based Sliding Mode Control for Networked Interval Type-2 Fuzzy Systems Under Deception Attacks. International Journal of Network Dynamics and Intelligence 4(1) (2025), 100003. DOI: 10.53941/ijndi.2025.100003.'))
        response.append(paragraph('A. Chandrasekar, W.-J. Chang, T. Radhika, S. Santhosh Kumar, and M. S. Aslam. Adaptive event triggering asynchronous control for interval type-2 fuzzy Markov jump systems with uncertainties and deception attacks. Complex & Intelligent Systems 12 (2026), 59. DOI: 10.1007/s40747-025-02172-5.'))
    if i==3:
        response.append(paragraph('Revised text','label'))
        response.append(paragraph('The signs of the membership-function derivatives define operational regions for a region-dependent fuzzy controller. Within this framework, the controller gains and event-triggering weight matrices are jointly designed.'))
    if i in (4,5):
        response.append(paragraph('Revised text','label'))
        response.append(paragraph(plain(find('R1.'+str(i))['new'])))
    if i==6:
        response.append(paragraph('Revised text in Example 2','label'))
        response.append(paragraph(plain(find('R1.6','Example 2')['new'])))
response.append(pagebreak())
response.append(paragraph('中文核对与修改对应','title'))
response.append(paragraph('本轮为第一份意见草稿及对应修改，便于作者和审阅者逐项核对。六条意见均已落实到 paper2_修改副本；原始 paper2 文件未改。'))
for i in range(1,7):
    titles=['英文表达','更新近期文献','摘要中的方法特色','三个定理的关系','两个算例的作用','通信节省率说明']
    response.append(paragraph('R1.'+str(i)+'  '+titles[i-1],'label'))
    selected=[c for c in changes if 'R1.'+str(i) in c['id']]
    lines=sorted(set(n for c in selected for n in c['revised_lines']))
    response.append(paragraph('对应修改稿 paper2.tex 源码行：'+', '.join(map(str,lines))+'。'))
response.append(paragraph('核对说明','label'))
response.append(paragraph('新增两篇文献的作者、题目、卷期或文章号及 DOI 已与出版社页面核对；引言已实际引用。2026 年文献的在线发表日为 2025 年 12 月 1 日，正式卷年为 2026，按正式卷年著录。'))
response.append(paragraph('通信比例按稿件已有计数核算：65/400 对应节省 83.75%。本轮没有重新运行仿真，也没有重新统计原始触发记录；回复只说明文字修改和基于已报告计数的计算。'))
response.append(paragraph('这份回复用于当前六条表达与说明意见的核对，不包含定理重证或新增实验的完成声明。最终使用前请核对论文题名、投稿编号及审阅者实际意见。'))
response_path=write_doc('02_逐点回复_Reviewer1.docx',response)

report_text=[p.text for p in Document(report_path).paragraphs]
reply_text=[p.text for p in Document(response_path).paragraphs]
assert sum(c in report_text for c in comments)==6
assert all(c in reply_text for c in comments)
assert sha(REF.read_bytes())==REFERENCE_HASH
(WORK/'document_content.json').write_text(json.dumps(dict(comments=comments,overview=overview,responses=responses,locations=locations,report=str(report_path),response=str(response_path)),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(report=str(report_path),response=str(response_path),comments=6,word_render='pending_missing_libreoffice'),ensure_ascii=False))
