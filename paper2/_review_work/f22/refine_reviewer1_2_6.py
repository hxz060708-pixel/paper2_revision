from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
import io,json

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[1]
path=ROOT/'filally_22/审稿意见1/01_审稿意见.docx'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
tree=E.fromstring(parts['word/document.xml'])
ps=tree.find(W+'body').findall(W+'p')
p2=ps[3]
first=next(p2.iter(W+'t'))
short='The motivation for jointly considering deception attacks, actuator failures, and communication limitations needs clarification. These factors affect interconnected closed-loop components: attacks may corrupt sampled information, actuator failures may alter the effective control input, and event-triggered transmission limits unnecessary data exchange. Could the authors clarify why these factors require simultaneous consideration and how their combined effects influence closed-loop stability and'
assert len(first.text.split())-len(short.split())==10
first.text=short
# Leave the existing H-infinity equation and its surrounding runs intact.
p6=ps[7]
chunks=[]
for el in p6:
    if el.tag==W+'pPr':continue
    if el.find('.//'+W+'object') is not None:
        chunks.append('σ')
    else:chunks.append(''.join(n.text or '' for n in el.iter(W+'t')))
full=''.join(chunks)
assert full.count('σ')==3
props=deepcopy(ps[6].find(W+'pPr'))
for el in list(p6):p6.remove(el)
p6.append(props)
for i,part in enumerate(full.split('σ')):
    if i:
        r=E.SubElement(p6,W+'r');rp=E.SubElement(r,W+'rPr')
        E.SubElement(rp,W+'rFonts',{W+'ascii':'Times New Roman',W+'hAnsi':'Times New Roman',W+'cs':'Times New Roman'})
        E.SubElement(rp,W+'i');E.SubElement(rp,W+'color',{W+'val':'000000'})
        E.SubElement(rp,W+'sz',{W+'val':'24'})
        E.SubElement(r,W+'t').text='σ'
    if part:
        r=E.SubElement(p6,W+'r');rp=E.SubElement(r,W+'rPr')
        E.SubElement(rp,W+'rFonts',{W+'ascii':'Times New Roman',W+'hAnsi':'Times New Roman',W+'cs':'Times New Roman'})
        E.SubElement(rp,W+'color',{W+'val':'000000'});E.SubElement(rp,W+'sz',{W+'val':'24'})
        E.SubElement(r,W+'t',{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=part
parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
buffer=io.BytesIO()
with ZipFile(buffer,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
try:
    path.write_bytes(buffer.getvalue())
except PermissionError:
    path=path.with_name('01_审稿意见_第2与6条已更新.docx')
    path.write_bytes(buffer.getvalue())
print('SAVED',path,flush=True)
rp=WORK/'responses.json'
reviews=json.loads(rp.read_text(encoding='utf-8'))
reviews[0]['items'][1]['comment']='2. '+short+' H∞ performance?'
reviews[0]['items'][5]['comment']='6. '+full
rp.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
builder=WORK/'build_pdfs.py'
source=builder.read_text(encoding='utf-8').replace('for r in reviews:', 'for r in reviews[:1]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})
