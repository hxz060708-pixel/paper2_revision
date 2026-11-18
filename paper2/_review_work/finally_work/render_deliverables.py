from pathlib import Path
import json,re,html,difflib,subprocess,sys
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,KeepTogether,CondPageBreak,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'_review_work'/'finally_work';OUT=ROOT/'finally'
data=json.loads((WORK/'content.json').read_text(encoding='utf-8'))
manifest=json.loads((WORK/'manifest.json').read_text(encoding='utf-8'))
writer=(ROOT/'_review_work'/'build_documents.py').read_text(encoding='utf-8').split('\ncomments=[',1)[0]
writer=writer.replace('ROOT=Path(__file__).resolve().parents[1]','ROOT=Path(__file__).resolve().parents[2]').replace("OUT=ROOT/'paper2_审稿意见'","OUT=ROOT/'finally'").replace("WORK=ROOT/'_review_work'","WORK=ROOT/'_review_work'/'finally_work'")
exec(compile(writer,'retained_template_writer','exec'),globals())
base_paragraph=paragraph
def paragraph(text,*args,**kwargs):
    p=base_paragraph(text,*args,**kwargs);run=p.find(W+'r');props=deepcopy(run.find(W+'rPr'));p.remove(run)
    for token in re.split(r'([ξQhVK]_[1-5n])',text):
        if not token:continue
        pairs=[(token[0],False),(token[2:],True)] if re.fullmatch(r'[ξQhVK]_[1-5n]',token) else [(token,False)]
        for val,sub in pairs:
            rr=ET.SubElement(p,W+'r');rp=deepcopy(props)
            if sub:ET.SubElement(rp,W+'vertAlign',{W+'val':'subscript'})
            rr.append(rp);ET.SubElement(rr,W+'t',{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=val
    return p

for ri,items in enumerate(data['reviewers'],1):
    report=[paragraph(f'Comments on paper2 Reviewer {ri}','title'),paragraph(data['overviews'][ri-1])]
    report += [paragraph(it['comment'],'number') for it in items]
    p=write_doc(f'0{ri+1}_审稿意见_Reviewer{ri}_最终版.docx',report)
    actual=[q.text for q in Document(p).paragraphs]
    normal=lambda s:re.sub(r'([ξQhVK])_([1-5n])',r'\1\2',s)
    assert all(normal(it['comment']) in actual for it in items)

for name,file in [('CN','msyh.ttc'),('CNBold','msyhbd.ttc'),('EN','times.ttf'),('ENBold','timesbd.ttf'),('ENItalic','timesi.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file,subfontIndex=0))
pdfmetrics.registerFontFamily('EN',normal='EN',bold='ENBold',italic='ENItalic',boldItalic='ENBold')
pdfmetrics.registerFontFamily('CN',normal='CN',bold='CNBold',italic='CN',boldItalic='CNBold')
sty={
 'title':ParagraphStyle('title',fontName='CNBold',fontSize=17,leading=24,spaceAfter=13),
 'head':ParagraphStyle('head',fontName='CNBold',fontSize=12,leading=17,spaceBefore=9,spaceAfter=7,keepWithNext=True),
 'label':ParagraphStyle('label',fontName='CNBold',fontSize=9.7,leading=14,spaceBefore=7,spaceAfter=4,keepWithNext=True),
 'tablelabel':ParagraphStyle('tablelabel',fontName='CNBold',fontSize=9.7,leading=14,spaceBefore=7,spaceAfter=4,keepWithNext=False),
 'cn':ParagraphStyle('cn',fontName='CN',fontSize=9.6,leading=14.6,spaceAfter=7,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='CN',fontSize=8.5,leading=12,spaceAfter=5,wordWrap='CJK',textColor=colors.HexColor('#444444')),
 'en':ParagraphStyle('en',fontName='EN',fontSize=11.2,leading=14.7,spaceAfter=8),
 'comment':ParagraphStyle('comment',fontName='ENItalic',fontSize=11,leading=14.5,spaceAfter=9),
 'quote':ParagraphStyle('quote',fontName='EN',fontSize=10.5,leading=13.8,spaceAfter=7,leftIndent=8,rightIndent=6),
 'cell':ParagraphStyle('cell',fontName='EN',fontSize=10.2,leading=13.2),
 'thead':ParagraphStyle('thead',fontName='CNBold',fontSize=9.2,leading=13,textColor=colors.white),
}
labels=data['labels']
def plain(tex):
    s=tex
    s=re.sub(r'\\eqref\{([^}]+)\}',lambda m:'('+labels[m.group(1)][0]+')',s)
    s=re.sub(r'\\ref\{([^}]+)\}',lambda m:labels[m.group(1)][0],s)
    s=re.sub(r'\\cite\{liuTorusEventBased2025\}','[34]',s);s=re.sub(r'\\cite\{chandrasekarAdaptiveEvent2026\}','[35]',s)
    s=s.replace(r'\mathrm{H}_{\infty}','H∞').replace(r'\mathrm{H}_\infty','H∞')
    s=s.replace(r'\dot{h}', 'ḣ').replace(r'\bar{\theta}','θ̄')
    for a,b in [(r'\sigma','σ'),(r'\delta','δ'),(r'\xi','ξ'),(r'\theta','θ'),(r'\times','×'),(r'\%','%')]:s=s.replace(a,b)
    s=re.sub(r'\\mathrm\{([^}]+)\}',r'\1',s)
    s=re.sub(r'_\{([^}]+)\}',r'_\1',s)
    if s.startswith(r'\caption{'):s=s[len(r'\caption{'):-1]
    s=s.replace(r'\ ',' ').replace('$','').replace('~',' ')
    return ' '.join(s.split())
def markup(s):
    s=html.escape(s)
    s=re.sub(r'(?<![A-Za-z])([A-Za-zξθδ][\u0300-\u036f]*)_(ET|TT|[0-9]+|[A-Za-z])',r'\1<sub>\2</sub>',s)
    # The derivative dot is rendered explicitly above h by the font; use conventional dh/dt wording in PDF quotes if needed.
    return s
def P(s,kind='en',tex=False):return Paragraph(markup(plain(s) if tex else s).replace('\n','<br/>'),sty[kind])
def footer(label):
    def f(canvas,doc):
        canvas.setFont('CN',8);canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawString(48,28,label);canvas.drawRightString(A4[0]-48,28,str(doc.page))
    return f
def build(name,story,label):
    doc=SimpleDocTemplate(str(OUT/name),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=42,bottomMargin=43,title=label,author='',pageCompression=1)
    doc.build(story,onFirstPage=footer(label),onLaterPages=footer(label))

def word_edits(before,after):
    tokens=lambda s:re.findall(r"\s+|[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:\.\d+)?|[^\s]",s)
    a,b=tokens(before),tokens(after);assert ''.join(a)==before and ''.join(b)==after
    ops=difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes();changes=[];rebuilt=[]
    for tag,i,j,k,l in ops:
        rebuilt.extend(a[i:j] if tag=='equal' else b[k:l])
        if tag!='equal':
            old,new=''.join(a[i:j]),''.join(b[k:l])
            if old.strip()!=new.strip():changes.append((old.strip(),new.strip()))
    assert ''.join(rebuilt)==after
    return changes
def char_mark(old,new,which):
    if not (old if which=='old' else new):return '<font name="CN" color="#666666">（无）</font>'
    out=[]
    for tag,i,j,k,l in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes():
        s=old[i:j] if which=='old' else new[k:l]
        if not s:continue
        value=markup(s)
        if tag!='equal':value=('<font color="#9B2828"><strike>'+value+'</strike></font>') if which=='old' else ('<font color="#164E80"><u>'+value+'</u></font>')
        out.append(value)
    return ''.join(out)

story=[P('语言修改逐字对照','title'),P('本文件先处理语言修改。17项条目覆盖19处实际替换；每项完整显示原文与改文，并逐项列出删词、增词、替换词和标点变化。红色删除线表示删去的字符，蓝色下划线表示加入的字符。','cn'),P('正文中的数学符号按常规形式显示；源码换行折叠为空格。完整 LaTeX 字符及换行见 08_全部修改精确对照.txt。定位使用两个 paper2.tex 文件的实际源码行号，不把源码行号当作 PDF 行号。','small')]
diff_records=[]
for c in data['language']:
    before,after=plain(c['old']),plain(c['new']);edits=word_edits(before,after)
    diff_records.append(dict(id=c['language_id'],before=before,after=after,edits=edits))
    story.append(CondPageBreak(145))
    story.append(P(c['language_id']+'  '+c['title_cn'],'head'))
    story.append(P(c['location'],'small'))
    story.append(P('原稿源码起始行：'+', '.join(map(str,c['original_lines']))+'；修改稿源码起始行：'+', '.join(map(str,c['revised_lines']))+'。','small'))
    story.append(P('修改原因：'+c['reason_cn'],'cn'))
    story.extend([P('原文全文或完整定位片段','label'),P(before,'en'),P('改后全文或完整对应片段','label'),P(after,'en'),CondPageBreak(65),P('全部增删明细','tablelabel')])
    rows=[[P('项','thead'),P('删除或替换前','thead'),P('增加或替换后','thead')]]
    for i,(a,b) in enumerate(edits,1):rows.append([P(str(i),'cell'),Paragraph(char_mark(a,b,'old'),sty['cell']),Paragraph(char_mark(a,b,'new'),sty['cell'])])
    t=Table(rows,colWidths=[25,237,237],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#424B55')),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#D9D9D9')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7FA')]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.extend([t,Spacer(1,10)])
build('01_语言修改逐字对照.pdf',story,'paper2 语言修改逐字对照')
(WORK/'language_diff.json').write_text(json.dumps(diff_records,ensure_ascii=False,indent=2),encoding='utf-8')

byid={c['change_id']:c for c in manifest['changes']}
for ri,items in enumerate(data['reviewers'],1):
    story=[]
    for ci,it in enumerate(items,1):
        if ci>1:story.append(PageBreak())
        story.append(P(f'Reviewer {ri} 回复与修改位置','title'))
        story.append(P(it['id']+'  '+it['title'],'head'))
        story.extend([P('审稿意见','label'),P(it['comment'],'comment'),P('英文回复','label'),P(it['response'],'en'),P('修改位置','label'),P(it['location'],'en'),P(it['cn'],'cn')])
        if ci!=1:
            for key in it['changes']:
                c=byid[key]
                story.append(P(c['change_id']+'：原稿源码 '+', '.join(map(str,c['original_lines']))+'；修改稿源码 '+', '.join(map(str,c['revised_lines']))+'。','small'))
        for title,quote in it['quotes']:
            story.append(P(title,'label'))
            for q in (quote.splitlines() if title=='Example language edits' else [quote]):
                story.append(P(q,'quote',tex=True))
        if ci==2:story.append(P('文献核对：Liu 等 (2025)，DOI 10.53941/ijndi.2025.100003；Chandrasekar 等 (2026)，DOI 10.1007/s40747-025-02172-5。','small'))
    build(f'0{ri+4}_回复与修改位置_Reviewer{ri}.pdf',story,f'paper2 Reviewer {ri} 逐点回复')

print(json.dumps(dict(word_reports=3,response_pdfs=3,language_pdf=1,word_changes=sum(len(d['edits']) for d in diff_records)),ensure_ascii=False))
