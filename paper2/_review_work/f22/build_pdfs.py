from pathlib import Path
import json,re,html,difflib,collections
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,CondPageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent;OUT=ROOT/'filally_22';REV=OUT/'paper2'
m=json.loads((WORK/'manifest.json').read_text(encoding='utf-8'));reviews=json.loads((WORK/'responses.json').read_text(encoding='utf-8'))
for name,file in [('CN','msyh.ttc'),('CNB','msyhbd.ttc'),('EN','times.ttf'),('ENB','timesbd.ttf'),('ENI','timesi.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file,subfontIndex=0))
pdfmetrics.registerFontFamily('CN',normal='CN',bold='CNB',italic='CN',boldItalic='CNB')
pdfmetrics.registerFontFamily('EN',normal='EN',bold='ENB',italic='ENI',boldItalic='ENB')
st={
'title':ParagraphStyle('title',fontName='CNB',fontSize=17,leading=24,spaceAfter=12),
'head':ParagraphStyle('head',fontName='CNB',fontSize=12,leading=18,spaceBefore=11,spaceAfter=7,keepWithNext=True),
'sub':ParagraphStyle('sub',fontName='CNB',fontSize=10,leading=15,spaceBefore=7,spaceAfter=5,keepWithNext=True),
'cn':ParagraphStyle('cn',fontName='CN',fontSize=10,leading=15.5,spaceAfter=7,wordWrap='CJK'),
'small':ParagraphStyle('small',fontName='CN',fontSize=8.5,leading=12.8,spaceAfter=6,wordWrap='CJK'),
'en':ParagraphStyle('en',fontName='EN',fontSize=11.6,leading=16,spaceAfter=9),
'comment':ParagraphStyle('comment',fontName='ENI',fontSize=11.3,leading=15.5,spaceAfter=10),
'code':ParagraphStyle('code',fontName='CN',fontSize=8.4,leading=13,spaceAfter=7,wordWrap='CJK'),
'ops':ParagraphStyle('ops',fontName='CN',fontSize=8.4,leading=13,spaceAfter=5,wordWrap='CJK'),
}
esc=lambda s:html.escape(s).replace('\n','<br/>')
def P(s,k='en'):return Paragraph(esc(s),st[k])
def footer(label):
    def f(c,d):
        c.setFont('CN',8);c.setFillColor(colors.HexColor('#666666'))
        c.drawString(44,25,label);c.drawRightString(A4[0]-44,25,str(d.page))
    return f
def build(path,story,label):
    SimpleDocTemplate(str(path),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=42,bottomMargin=43,title=label,author='',pageCompression=1).build(story,onFirstPage=footer(label),onLaterPages=footer(label))

aux={name:(REV/(name+'.aux')).read_text(encoding='utf-8') for name in ['paper2','paper2_clean']}
def read_pages(text):
    result={}
    for match in re.finditer(r'\\newlabel\{rev:(M\d+)\}\{',text):
        pos=match.end();assert text[pos]=='{';depth=1;pos+=1
        while depth:
            if text[pos]=='{':depth+=1
            elif text[pos]=='}':depth-=1
            pos+=1
        assert text[pos]=='{';end=text.index('}',pos)
        result[match.group(1)]=int(text[pos+1:end])
    return result
pages={name:read_pages(t) for name,t in aux.items()}
labels={a:(b,c) for a,b,c in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{([^}]+)\}',aux['paper2_clean'])}
for p in m['patches']:
    p['marked_page']=pages['paper2'][p['id']];p['clean_page']=pages['paper2_clean'][p['id']]
assert len(pages['paper2'])==len(m['patches'])
patches={p['id']:p for p in m['patches']}

def grouped(items):
    groups=collections.OrderedDict()
    for p in items:groups.setdefault((p['old'],p['new'],p['reason']),[]).append(p)
    return list(groups.values())

def loc(group):
    return '；'.join(f"{p['id']}：原稿第 {p['original_line']} 行，红绿稿第 {p['marked_line']} 行／第 {p['marked_page']} 页，清洁稿第 {p['clean_page']} 页" for p in group)

def marked(text,other,side):
    a,b=(text,other) if side=='old' else (other,text)
    chunks=[]
    for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
        part=a[i:j] if side=='old' else b[k:l]
        if not part:continue
        body=html.escape(part).replace('\n','<br/>').replace('\t','&#160;&#160;&#160;&#160;')
        if tag!='equal':body='<font color="'+('#BE0000' if side=='old' else '#007323')+'">'+body+'</font>'
        chunks.append(body)
    return Paragraph(''.join(chunks) or '（无）',st['code'])

def literal(s):
    # JSON quoting makes all line breaks, tabs, quotes and backslashes explicit.
    return html.escape(json.dumps(s,ensure_ascii=False)).replace(' ','&#160;')

def operations(old,new):
    result=[]
    opcodes=difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes()
    reconstructed=''.join(old[i:j] if tag=='equal' else new[k:l] for tag,i,j,k,l in opcodes)
    assert reconstructed==new
    for tag,i,j,k,l in opcodes:
        if tag=='equal':continue
        oldpart=old[i:j];newpart=new[k:l]
        if tag=='insert':where=f'在原文第 {i+1} 个字符之前插入' if i<len(old) else '在原文末尾插入'
        else:where=f'原文第 {i+1} 至 {j} 个字符'
        line=html.escape(where)+'：'
        if oldpart:line+='删除 <font color="#BE0000">'+literal(oldpart)+'</font>'
        if oldpart and newpart:line+='；'
        if newpart:line+='新增 <font color="#007323">'+literal(newpart)+'</font>'
        result.append(Paragraph(line,st['ops']))
    return result

sources=[
('Liu et al. 2025','Torus-Event-Based Sliding Mode Control for Networked Interval Type-2 Fuzzy Systems Under Deception Attacks','https://www.sciltp.com/journals/ijndi/articles/2504000064','10.53941/ijndi.2025.100003'),
('Chandrasekar et al. 2026','Adaptive event triggering asynchronous control for interval type-2 fuzzy Markov jump systems with uncertainties and deception attacks','https://link.springer.com/article/10.1007/s40747-025-02172-5','10.1007/s40747-025-02172-5'),
('Chen et al. 2023','Probabilistic Event-Triggered Policy for Extended Dissipative Finite-Time Control of MJSs under Cyber-Attacks and Actuator Failures','https://www.uvic.ca/research/labs/acipl/publications/index.php','10.1109/TAC.2023.3246429')]

for r in reviews:
    ri=r['reviewer'];folder=OUT/f'审稿意见{ri}'
    story=[P(f'审稿意见{ri} 逐条回复','title'),P('本文逐条对应当前同目录 Word 中的审稿意见。下列英文回复均以同目录上一级 paper2 副本中的实际改动为依据。修改位置同时给出红绿稿与清洁稿页码。','cn')]
    detailed=[P(f'审稿意见{ri} 回复与逐字修改','title'),P('本文件包含完整审稿意见、英文回复、修改位置、原文与改文，以及逐字符增删记录。三位审稿人的意见共同落实在同一个 paper2 副本中；一处修改可以同时回应多条意见。','cn'),P('阅读方法','head'),P('红绿稿 paper2/paper2.tex 与 paper2.pdf：红色保留拟删除或替换的原文，绿色显示新增内容，黑色为未改内容。paper2_clean.pdf 供连贯阅读。本文代码片段中的 LaTeX 命令原样保留，可据此定位和编辑。字符位置从各条“原文”片段的第 1 个字符计数，包含空格和标点；增删记录采用 JSON 字符串形式，\\n 表示换行、\\t 表示制表符、\\\\ 表示一个反斜杠。每条操作都相对于原片段定位，不依次改变后续位置。','cn'),P('页码来自本次编译结果。源码行号指 paper2/paper2.tex（红绿稿）；原稿行号指本任务开始时的 paper2/paper2.tex。重复意见涉及的修改在本 PDF 首次完整列出，后续给出对应修改编号，避免遗漏或使用不同版本。','cn')]
    seen=set()
    for it in r['items']:
        cid=it['id'];related=[patches[c] for c in it['changes']]
        for arr in [story,detailed]:
            arr.append(CondPageBreak(150))
            arr.append(P(cid+' 审稿意见','head'));arr.append(P(it['comment'],'comment'))
            arr.append(P('Response','sub'));arr.append(P(it['response']))
            if it.get('revision_plan'):
                arr.append(P('具体改法','sub'));arr.append(P(it['revision_plan'],'cn'))
            arr.append(P('修改位置' if related else '回复说明','sub'))
            arr.append(P('；'.join(f"{p['id']}（红绿稿第 {p['marked_page']} 页，清洁稿第 {p['clean_page']} 页）" for p in related) if related else it['response_only_note'],'small'))
        if not related:
            continue
        detailed.append(P('逐项修改','sub'))
        for group in grouped(related):
            fresh=[p for p in group if p['id'] not in seen]
            if not fresh:
                detailed.append(P('同一修改已在本文件前文完整列出：'+', '.join(p['id'] for p in group)+'。','small'));continue
            p=group[0];seen.update(x['id'] for x in group)
            detailed.append(CondPageBreak(130))
            detailed.append(P(' / '.join(x['id'] for x in group)+' '+p['location'],'sub'))
            detailed.append(P(loc(group),'small'));detailed.append(P('修改理由：'+p['reason'],'cn'))
            if p['kind']=='insert':detailed.append(P('插入定位：置于以下原文之前（定位句本身不删除）：'+p['anchor'],'code'))
            detailed.append(P('原文 完整保留','sub'));detailed.append(marked(p['old'],p['new'],'old'))
            detailed.append(P('改文 完整文本','sub'));detailed.append(marked(p['new'],p['old'],'new'))
            detailed.append(P('逐字符增删','sub'));detailed.extend(operations(p['old'],p['new']))
        if 'M08' in it['changes']:
            detailed.append(P('新增参考文献及核对依据','sub'))
            detailed.append(P('ref2.bib 原有内容逐字保留，以下两条完整追加在文件末尾；正文引用与编译后的编号自动对应。Chen 等人的条目原稿已有，本次只加强正文比较。','cn'))
            detailed.append(P(m['bib_addition'],'code'))
            for author,title,url,doi in sources:
                detailed.append(P(author+'. '+title+'. DOI: '+doi,'en'))
                detailed.append(Paragraph('<link href="'+html.escape(url,quote=True)+'" color="#1E4E79">'+html.escape(url)+'</link>',st['small']))
            detailed.append(P('Chandrasekar 等的在线发表日期为 2025 年 12 月 1 日，正式卷期为 2026 年第 12 卷、文章 59；BibTeX 使用正式卷期年份 2026。','cn'))
        if it.get('include_figure_edits', False):
            detailed.append(P('图内文字修改','sub'))
            for fig in m['figure_edits']:
                detailed.append(P('figs/'+fig['file'],'sub'));detailed.append(P(fig['note'],'cn'))
                detailed.append(P('原文：Operation models；改文：Operating modes。','code'))
                detailed.extend(operations(fig['old'],fig['new']))
            detailed.append(P('仅调整图文和图间距，不重新生成仿真数据。红绿版在原矢量图左侧增加 24 pt 留白放置绿色标题，原错误标题完整保留并标红。清洁版显示正确标题。','cn'))
    build(folder/'02_审稿意见怎么回复.pdf',story,f'审稿意见{ri} 逐条回复')
    detailed.append(PageBreak());detailed.append(P('修改完整性与阅读说明','title'))
    detailed.append(P('本组意见对应的全部修改编号：'+', '.join(sorted(seen))+'.','cn'))
    detailed.append(P('上述“原文／改文／逐字符增删”描述论文内容层面的编辑。额外加入的红绿标记命令、定位标签和清洁版入口只用于核对与编译，不作为论文研究内容。原有显示公式、定理约束和仿真数值不因这些标记而改变。页码、引文编号、交叉引用及行号会因排版变化而重新生成。','cn'))
    detailed.append(P('标记与定位规则','head'))
    detailed.append(P('每一处变动在 TeX 中使用 \\revdel{原文} 和／或 \\revadd{改文}；新增块仅使用后者。\\label{rev:Mxx} 是修改定位标签。两张坐标文字调整图由 \\revfigure 按标注版或清洁版选择。下面完整列出导言区支持代码。','cn'))
    detailed.append(P(m['config'],'code'))
    detailed.append(P('清洁版入口 paper2_clean.tex 的完整内容','sub'));detailed.append(P((REV/'paper2_clean.tex').read_text(encoding='utf-8'),'code'))
    build(folder/'03_怎么回复与怎么改动_逐字对照.pdf',detailed,f'审稿意见{ri} 回复与逐字修改')
    print('Built reviewer PDFs',ri,flush=True)
(WORK/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'全部修改精确记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
