from pathlib import Path
import json, re, hashlib, difflib
ROOT=Path(__file__).resolve().parents[1]
REV=ROOT/'paper2_审稿意见'/'paper2_修改副本'
OUT=REV.parent
WORK=ROOT/'_review_work'
p=REV/'paper2.tex';text=p.read_text(encoding='utf-8')
old=r'\bibliographystyle{elsarticle-num}'
new=r'\setlength{\bibsep}{0pt}'+'\n'+old
assert new not in text
text=text.replace(old,new)
p.write_text(text,encoding='utf-8')
b=REV/'ref2.bib';bib=b.read_text(encoding='utf-8')
for title in ['Torus-Event-Based Sliding Mode Control for Networked Interval Type-2 Fuzzy Systems Under Deception Attacks','Adaptive event triggering asynchronous control for interval type-2 fuzzy Markov jump systems with uncertainties and deception attacks']:
    assert 'title = {'+title+'}' in bib
    bib=bib.replace('title = {'+title+'}','title = {{'+title+'}}')
b.write_text(bib,encoding='utf-8')
manifest=json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
manifest['layout_adjustments']=['Reference list inter-entry spacing set to 0 pt to avoid a final page containing only one entry; reference font size unchanged.','Capitalization of both newly added article titles preserved in BibTeX.']
(WORK/'revision_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
original=(ROOT/'paper2'/'paper2.tex').read_text(encoding='utf-8')
diff=''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='original/paper2.tex',tofile='paper2_修改副本/paper2.tex'))
(OUT/'paper2_修改对照.diff').write_text(diff,encoding='utf-8')
# Verify unchanged original files, all displayed mathematical environments, and all source figures.
for n,digest in manifest['source_hashes'].items():assert hashlib.sha256((ROOT/'paper2'/n).read_bytes()).hexdigest()==digest
pat=r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}'
old_math=[m.group() for m in re.finditer(pat,original,re.S)]
new_math=[m.group() for m in re.finditer(pat,text,re.S)]
assert old_math==new_math
for f in (ROOT/'paper2'/'figs').iterdir():
    if f.is_file():assert f.read_bytes()==(REV/'figs'/f.name).read_bytes()
notes='''paper2 第一份审稿意见及修改包

先看：01_审稿意见_Reviewer1.docx
逐条核对：02_逐点回复_Reviewer1.docx（含英文回复和中文修改位置）
论文副本：paper2_修改副本/paper2.tex 与 paper2.pdf
文字差异：paper2_修改对照.diff

本轮六条意见：英文表达、补充近期相关文献、摘要中的导数分区思路、三个定理的关系、两个算例的作用、通信节省率的定义和计算。

已完成：正文文字修改；加入两篇真实近期文献及引言讨论；按已有计数校正 65/400 对应的通信节省率为 83.75%；逐条回复与改动对应；修改副本 LaTeX 编译。正文显示公式和原始图文件均保留；原 paper2 的 tex、bib、PDF 文件哈希未变。

本轮没有重新运行仿真或独立重证定理。传输计数沿用原稿，不声称已核查原始仿真记录。此包是供作者和审阅者核对的第一份意见及回复草稿。

Word 已完成正文、编号、XML 和模板页面参数核对。自动逐页视觉预览未完成：本环境缺少 LibreOffice，Word 自动化启动被拒绝。因此打开 Word 后仍需看一次分页；不应把文件结构校验当成逐页视觉校验。

新增文献来源
Liu, Ling and Zhang (2025), International Journal of Network Dynamics and Intelligence 4(1), 100003.
https://doi.org/10.53941/ijndi.2025.100003
Chandrasekar et al. (2026), Complex & Intelligent Systems 12, 59.
https://doi.org/10.1007/s40747-025-02172-5
后者在线发表于 2025-12-01，正式卷年为 2026，采用正式卷年。
'''
(OUT/'00_阅读说明.txt').write_text(notes,encoding='utf-8')
print(json.dumps({'displayed_math_blocks_unchanged':len(old_math),'original_hashes_unchanged':True,'figure_files_unchanged':True},ensure_ascii=False))
