from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import json

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[1]
changes={
2: ('Please explain why their combined presence motivates analysis of the resulting closed-loop stability and H∞ performance.', 'Could the authors further clarify why these three factors need to be considered simultaneously and how their combined effects influence closed-loop stability and H∞ performance?'),
3: ('Clarify methodological distinctions supported by the cited literature rather than simply adding references.', 'Could the authors further clarify the methodological differences between the proposed approach and the most closely related studies? Please support these distinctions with the cited literature rather than simply adding references.'),
4: ('Please explain how the threshold dynamics should be read together with the triggering inequality and state error.', 'How do the adaptive threshold dynamics interact with the triggering condition and state error, particularly under different initial conditions?'),
5: ('Please explain how the regional conditions enter controller synthesis, while retaining the existing theorem conditions and proof.', 'Could the authors explain how the signs of the membership-function derivatives determine the regional constraints and how these constraints are incorporated into controller synthesis? Please retain the existing theorem conditions and proof.'),
6: ('Please explain this trend in relation to the adaptive threshold and triggering condition under the tested settings.', 'Could the authors explain why the packet count increases and the saving rate decreases as σ rises, and how this trend relates to the adaptive threshold and triggering condition under the tested settings?'),
}
path=ROOT/'filally_22/审稿意见1/01_审稿意见.docx'
with ZipFile(path) as z:
    parts={n:z.read(n) for n in z.namelist()}
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
tree=E.fromstring(parts['word/document.xml'])
paras=tree.find(W+'body').findall(W+'p')
for n,(old,new) in changes.items():
    nodes=list(paras[n+1].iter(W+'t'))
    text=''.join(t.text or '' for t in nodes)
    if old not in text: raise ValueError(f'第{n}条待替换内容不匹配')
    nodes[0].text=text.replace(old,new,1)
    for t in nodes[1:]: t.text=''
parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
response_path=WORK/'responses.json'
reviews=json.loads(response_path.read_text(encoding='utf-8'))
for n,(old,new) in changes.items():
    item=reviews[0]['items'][n-1]
    if old not in item['comment']: raise ValueError(f'第{n}条PDF数据不匹配')
    item['comment']=item['comment'].replace(old,new,1)
with ZipFile(path,'w',ZIP_DEFLATED) as z:
    for n,b in parts.items(): z.writestr(n,b)
response_path.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
print('审稿意见1：第2、3、4、5、6条问句已写入Word。',flush=True)
builder=WORK/'build_pdfs.py'
source=builder.read_text(encoding='utf-8').replace('for r in reviews:', 'for r in reviews[:1]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})
