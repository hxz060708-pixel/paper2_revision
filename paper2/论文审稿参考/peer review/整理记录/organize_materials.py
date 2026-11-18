from pathlib import Path
import json
import hashlib
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = Path('C:/Users/mech-mind/AppData/Local/Temp/peer-review-inventory-20261021.json')
records = json.loads(INVENTORY.read_text(encoding='utf-8'))

groups = [
 ('01_论文与意见配对/01_JSCE-24-0030_入门示例', 'JSCE-24-0030', '时滞神经网络的动态输出反馈异步控制', '论文25页＋Word意见＋PDF意见', '先看此组：意见仅3条，容易理解结构。Word与PDF正文经去除空白和列表编号后相同。', ['JSCE-24-0030_Proof_hi.pdf','peer review on JSCE.docx','peer review on JSCE-24-0030.pdf']),
 ('01_论文与意见配对/02_SMCA-25-06-2213_具体问题示例', 'SMCA-25-06-2213', '时滞T-S模糊系统的指数镇定', '论文12页＋Word意见', '学习意见如何定位到引理、不等式、推导和仿真图。原意见的数学判断仍须回原文核验。', ['SMCA-25-06-2213_Proof_hi(1).pdf','Comment on SMCA-25-06-2213.docx']),
 ('01_论文与意见配对/03_AMC-D-25-04496_方法与实验', 'AMC-D-25-04496', '广义神经网络的有限时间概率镇定', '论文32页＋Word意见', '关注研究动机、参数含义、公式、推导衔接与仿真；意见要求是否适用，应依据论文范围判断。', ['AMC-D-25-04496 (1).pdf','Comment on AMC-D-25-04496.docx']),
 ('01_论文与意见配对/04_MATH-8993_公式与图示', 'MATH-8993', '带时滞和脉冲的Clifford值BAM神经网络', '论文23页＋Word意见', '学习从公式括号、定义顺序、收敛时间解释和图形表现提出问题。PDF虽叫peer-review，内容是论文。', ['Math-8993-peer-review (1).pdf','comment on MATH-8993.docx']),
 ('01_论文与意见配对/05_ISATRANS-D-22-00600_表达与格式', 'ISATRANS-D-22-00600', '汽车防抱死系统的模糊自适应PID控制', '论文26页＋PDF意见', '原意见文件名漏了稿号开头的I；正文稿号和主题均可配对。没有找到正式Word意见，只有锁文件。', ['ISATRANS-D-22-00600_reviewer.pdf','peer review on SATRANS-D-22-00600.pdf']),
 ('01_论文与意见配对/06_0189_中文示例', '0189', '分布式驱动电动汽车操纵稳定性分层控制', '论文6页＋中文Word意见', '可先用中文理解总评和分条问题；现有意见较概括，学习时要补充具体位置与证据。', ['0189.pdf','Comment On _on_0189.docx']),
 ('01_论文与意见配对/07_0292_简短英文示例', '0292', '分布式驱动电动汽车轮胎力估计', '论文6页＋英文Word意见', '比较模型方法与机器学习方法；现有意见偏语言、动机和文献，不代表方法已被充分验证。', ['0292.pdf','Comment On _on_0292.docx']),
 ('02_只有审稿意见/01_ESWA-D-22-07284_四份不同文本', 'ESWA-D-22-07284', 'IT2模糊半马尔可夫系统的异步采样控制', '3份Word意见＋1份PDF意见；缺论文', '四份文本内容不同，保留全部；编号1、2不代表审稿人编号，无法确认提交版本或先后关系。', ['1.docx','2.docx','Comment On ESWA-D-22-07284.docx','Comments on ESWA-D-22-07284.pdf']),
 ('02_只有审稿意见/02_OPENMATH-D-22-00217_不同结论对照', 'OPENMATH-D-22-00217', '两类Fermat型常微分方程的整函数解', '3份PDF报告；缺论文', '一份建议小修，一份推荐发表并列出修改，一份建议拒稿。不能判断它们是否来自同一轮或不同审稿人。', ['Referee report of  OPENMATH-D-22-00217 by BINBIN HU and LIU YANG ..pdf','Report-OPENMATH-D-22-00217.pdf','The report on the paper with reference OPENMATH-D-22-00217.pdf']),
 ('02_只有审稿意见/03_FSS-D-21-00117_理论问题示例', 'FSS-D-21-00117', '船舶电力推进系统的模糊采样容错控制', '1份PDF意见；缺论文', '包括保守性、求解复杂度、定理和导数可计算性的质疑。技术问题与末尾小修结论需要分开理解。', ['1_Comment On FSS-D-21-00117.pdf']),
 ('02_只有审稿意见/04_六篇短评合集_稿号未注明', '六篇短评合集', '控制、无人机、视觉、导航等六个主题', '1份Word合集；缺对应论文和稿号', '原名Distributed H.docx，不是一篇完整论文；已改为能说明内容的名称。适合看提问角度，不适合直接照抄。', ['Distributed H.docx']),
 ('03_只有论文/01_RNC-23-0196_缺对应意见', 'RNC-23-0196', '半马尔可夫执行器故障下的IT2模糊容错控制', '论文30页；缺对应意见', '与ESWA、FSS题材相近，但稿号不同；没有足够依据认定为同一论文或转投版本。', ['RNC-23-0196_Proof_hi.pdf']),
]

renames = {
 '1.docx':'ESWA-D-22-07284_意见文本_原1.docx',
 '2.docx':'ESWA-D-22-07284_意见文本_原2.docx',
 'Distributed H.docx':'六篇论文短评合集_原Distributed H.docx',
}
by_name = {Path(r['path']).name:r for r in records}
assert len(by_name)==len(records), 'Ambiguous original filenames'
plan=[]
for folder,code,topic,contents,note,names in groups:
 for name in names:
  r=by_name[name]
  plan.append({'old_path':r['path'],'new_path':str(Path(folder)/renames.get(name,name)),'sha256':r['sha256'],'bytes':r['bytes']})
for name,folder in [('注意要点.txt','04_原有经验笔记'),('~$er review on SATRANS-D-22-00600.docx','99_Word临时锁文件')]:
 r=by_name[name];plan.append({'old_path':r['path'],'new_path':str(Path(folder)/name),'sha256':r['sha256'],'bytes':r['bytes']})
assert len(plan)==len(records)==27
def inside(relative):
 p=(ROOT/relative).resolve()
 assert p.is_relative_to(ROOT) and p!=ROOT
 return p
for entry in plan:
 src=inside(entry['old_path']); dst=inside(entry['new_path'])
 assert src.is_file() and not dst.exists(), (src,dst)
 assert hashlib.sha256(src.read_bytes()).hexdigest()==entry['sha256'], src
(ROOT/'整理记录'/'原位置与新位置.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
for entry in plan:
 src=inside(entry['old_path']); dst=inside(entry['new_path'])
 dst.parent.mkdir(parents=True,exist_ok=True)
 src.rename(dst)
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==entry['sha256']
for rel in ['新建文件夹/peer-review','新建文件夹/评审','新建文件夹']:
 p=inside(rel)
 if p.exists() and not any(p.iterdir()):p.rmdir()

def link(label,rel):
 return f'[{label}](<{quote(str(rel).replace(chr(92),"/"),safe="/._-")}>)'
def item_link(name):
 entry=next(e for e in plan if Path(e['old_path']).name==name)
 return link(renames.get(name,name),entry['new_path'])

intro='''# 审稿资料导读

这批文件是多篇论文的审稿资料合集。最适合用它学习：一份意见如何组织、怎样找到具体问题，以及作者怎样把问题落实成修改。它不是已经配齐的“投稿—评审—回复—修订—录用”全过程记录。

**建议先看 JSCE，再看 SMCA，最后对照 OPENMATH。** 先理解结构，再学习具体定位，最后看不同结论如何依赖不同依据。

## 整理后有什么

| 目录 | 内容 | 用法 |
|---|---|---|
| 01_论文与意见配对 | 7组，共15个原文件 | 一边看论文，一边核对意见 |
| 02_只有审稿意见 | 4组，共9个原文件 | 3个稿号案例和1个六篇短评合集 |
| 03_只有论文 | RNC，共1个原文件 | 等找到对应意见后再补配 |
| 04_原有经验笔记 | 注意要点，共1个原文件 | 师兄留下的格式、逻辑、摘要提醒 |
| 99_Word临时锁文件 | 1个162字节的隐藏锁文件 | 不是正式意见正文，已保留 |
| 整理记录 | 原位置、新位置及校验信息 | 追溯本次移动和重命名 |

原有27个文件全部保留，内容未改；只有3个含义不明的Word文件改了名称。文件名中的年份、文件修改时间不能证明审稿轮次或提交状态。本文页数为PDF文件总页数，可能包含封面，与正文页码不同。

## 先分清四种材料

| 材料 | 谁写、做什么 | 本文件夹情况 |
|---|---|---|
| 论文送审稿 | 作者呈现研究问题、方法和结果 | 有8份可识别论文PDF |
| 审稿意见 | 审稿人说明评价、疑问及修改要求 | 有多份；是否正式提交无法从文件确认 |
| 作者回复信 | 作者逐条回答收到的意见，指出证据和修改位置 | 未识别出单独文件 |
| 修改稿和编辑决定信 | 展示实际修改，以及编辑作出的处理决定 | 未识别出单独文件 |

意见末尾写“可接受”或“小修”只是该文本的建议，不能当成期刊最终决定。作者自查可以参考这些材料；如需向期刊提供作者评估，应标明作者身份与用途，不能冒充独立审稿意见。

## 按这个顺序读

1. **JSCE：看懂一份意见。** 先看PDF意见，再对照论文。它的结构是研究概述、总体评价、3条问题、结尾建议。问题涉及缩写首次定义、研究动机和公式排版。概述篇幅偏长，学习时不必照搬这个长度。
2. **SMCA：学习把问题写具体。** 看意见怎样定位到Lemma 1、不等式(7)、代入推导和Example 1。注意：这是原意见提出的问题，不等于本次整理已验证了公式错误。
3. **OPENMATH：看同一稿号的不同评价。** 把三份报告并排阅读，区分语言修订、论证疑问和影响结论的问题。没有原稿，暂时无法判断哪一份技术判断正确。
4. **ESWA：比较表达，但不要当作版本历史。** 3份Word与1份PDF不是简单重复；不同文本连示例数量的描述也有差别。缺原稿，不能确定哪份更准确、哪份最后提交。
5. **回到自己的论文。** 使用根目录的《论文自查工作表》，先记录能核验的问题，再写修改计划。不要为了凑条数搬用其他论文的技术批评。

## 每个案例在哪里

以下标题和文件都可点击。各组的“适合学什么”是整理说明，不是对原论文的重新审稿。
'''
parts=[intro]
for folder,code,topic,contents,note,names in groups:
 parts.append(f'\n### {code}　{topic}\n\n**材料：** {contents}。\n\n**阅读提示：** {note}\n\n')
 parts.extend(f'- {item_link(n)}\n' for n in names)
parts.append('''
## 看意见时应该学什么

一条有用的问题通常能说清：**位置 → 发现的情况 → 为什么影响理解或结论 → 应补充或修改什么。**

| 常见的笼统说法 | 在自己的论文中应核查的内容 | 下一步动作 |
|---|---|---|
| 创新不够清楚 | 与最接近的工作相比，改变了哪项假设、方法或能力 | 写出差异，并给出理论或实验依据 |
| 动机不清楚 | 实际场景中的限制，是否确实需要本文的方法 | 补充问题背景和研究范围，避免夸大应用 |
| 方法描述不够详细 | 参数、符号、输入输出、算法步骤和假设是否完整 | 补定义、步骤或必要说明 |
| 证明不严谨 | 哪一步推导无法从前提得到，是否存在反例 | 逐步核验；若影响结论，应先处理理论问题 |
| 实验不充分 | 关键主张有没有对应指标、合理基线和一致的比较条件 | 补适用的对照、消融或复现实验，不机械加实验 |
| 图表不清楚 | 坐标、单位、图例、工况和误差表达能否支持解读 | 修改图表并解释主要现象 |
| 文献需要更新 | 是否遗漏直接相关工作，差异是否说明 | 补真正相关的文献，不以年份或数量代替相关性 |
| 英文和格式需改 | 哪一句不清、哪个符号不一致、哪条格式不符合要求 | 记录具体位置并统一修订 |

**示范，仅说明自查方法，不是在评价你的论文：**

“实验不充分”可以细化为：“论文声称降低计算开销，但现有结果只报告精度。请核查是否已有相同硬件与输入规模下的运行时间；如没有，应补充比较，或收窄关于计算效率的表述。”

先按“是否影响结论成立”区分实质问题与表述问题，再安排修改。不能因为某份范例结尾写了“小修”，就把证明缺口、关键对照缺失等问题也视作小修。

## 这些范例不要原样照搬

- 部分英文意见自身存在语法问题，适合学提问方式，不适合当作标准英语模板。
- 不少意见重复使用“语言、动机、文献”三类泛化建议；没有具体依据时，不能证明论文存在对应问题。
- 部分意见开头高度肯定数学正确性，后面又提出证明疑问。阅读时应检验评价和问题是否一致。
- FSS报告提出了导数可计算性的质疑，末尾仍建议小修。这是需要回原稿判断严重程度的例子，不应照搬其处理结论。
- “首行缩进两个字符”“近三年参考文献”等范例要求不自动适用于所有英文期刊。实际格式以目标期刊要求为准。
- Word中的部分数学表达属于公式对象，纯文本读取可能漏掉。遇到缺符号或含义不清的句子，请打开原Word核对，不能据抽取文字认定原文件缺失。

## 六篇短评合集的内容索引

| 顺序 | 主题 | 原短评主要提问方向 |
|---|---|---|
| 1 | 多区域负荷频率控制中的攻击检测 | distributed的含义，模拟退火的选择依据 |
| 2 | Voronoi势场无人机覆盖路径规划 | 覆盖路径与一般路径规划的区别，相关文献 |
| 3 | 弱监督目标定位的高分辨率类激活映射 | 特征相加与相乘融合的选择依据 |
| 4 | 基于新息序列的自适应卡尔曼滤波与故障检测 | 引言中的创新点，结论中的未来工作 |
| 5 | 频域重参数化YOLO医学目标检测 | 傅里叶卷积对边界和纹理的作用 |
| 6 | VSFNet遥感图像语义分割 | 两级多尺度融合结构的设计理由 |

## 整理范围

本次核对了所有独立意见文本、经验笔记以及论文题目、稿号和主题，用于文件配对与导读；没有逐式复核所有论文，也没有验证意见是否被期刊采纳。不根据文件名猜测审稿人身份、最终稿或轮次。未找到字节完全一致的重复文件，因此未删除任何原文件。

后续如果拿到作者回复信、修订稿或决定信，放回相应稿号文件夹，就能继续补成完整案例。
''')
(ROOT/'00_先看这里_资料导读.md').write_text(''.join(parts),encoding='utf-8')
table=['# 原文件整理清单\n\n整理日期：2026-10-21。27个原文件移动后SHA-256全部匹配；原内容未改。\n\n| 原位置 | 新位置 |\n|---|---|\n']
for e in plan:table.append(f"| {e['old_path']} | {e['new_path']} |\n")
(ROOT/'整理记录'/'文件移动清单.md').write_text(''.join(table),encoding='utf-8')
print(json.dumps({'files_moved':len(plan),'all_hashes_match':True,'guide':str(ROOT/'00_先看这里_资料导读.md')},ensure_ascii=False))
