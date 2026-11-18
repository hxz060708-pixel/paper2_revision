from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
from docx import Document
import json,re,hashlib,subprocess,os,sys
ROOT=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent
REF=ROOT/'新+/Review Comments on TR-2026-312.docx'
sources=json.loads((WORK/'source_reviews.json').read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
reference_hash=sha(REF.read_bytes())
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
with ZipFile(REF) as z:parts={n:z.read(n) for n in z.namelist()}
rt=E.fromstring(parts['word/document.xml']);body=rt.find(W+'body');paras=body.findall(W+'p');sect=deepcopy(body.find(W+'sectPr'))
styles=E.fromstring(parts['word/styles.xml'])
title=next((s for s in styles.findall(W+'style') if s.find(W+'name') is not None and s.find(W+'name').get(W+'val','').lower()=='title'),None)
if title is None:
    title=E.SubElement(styles,W+'style',{W+'type':'paragraph',W+'styleId':'ReviewTitle'})
    E.SubElement(title,W+'name',{W+'val':'Title'})
title_id=title.get(W+'styleId')
def filled(proto,text,is_title=False):
    p=deepcopy(proto);p.attrib.clear();ppr=p.find(W+'pPr');rp=deepcopy(p.find(W+'r').find(W+'rPr'))
    for e in list(p):
        if e is not ppr:p.remove(e)
    if is_title:
        ps=ppr.find(W+'pStyle')
        if ps is not None:ppr.remove(ps)
        ppr.insert(0,E.Element(W+'pStyle',{W+'val':title_id}))
    color=rp.find(W+'color')
    if color is None:color=E.SubElement(rp,W+'color')
    color.attrib.clear();color.set(W+'val','000000')
    r=E.SubElement(p,W+'r');r.append(rp)
    E.SubElement(r,W+'t',{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=text
    return p

inventory={n:{'sha256':sha(b),'bytes':len(b),'policy':'editable' if n in ['word/document.xml','word/styles.xml','docProps/core.xml','docProps/app.xml'] else 'preserve'} for n,b in parts.items()}
(WORK/'template_TR_parts.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
contract=f'''# Template contract
Reference: {REF}
SHA256: {sha(REF.read_bytes())}
One section. A4 11906 by 16838 twips. Top/bottom margins 1440; left/right margins 1800. Original sectPr preserved byte-for-byte in canonical XML.
Title: centered, Times New Roman 15 pt bold. Body: Times New Roman 12 pt, justified. Comments: Times New Roman 12 pt, justified, List Paragraph style a9, numId 1 and level 0. Retain the original paragraph properties, default spacing, list indent, and numbering definitions. No generic spacing preset.
Content flow: title, overview, seven numbered comments. Source slots: word/document.xml body p[1] title, p[2] overview, p[3] through p[9] numbered comments. Final empty p[10] is omitted. Seven comment patterns are cloned one-to-one. Source equation runs belong to the old text and are replaced; their unused package parts and relationships remain intact.
New content authority: 新+ three latest review files. Exact wording and punctuation preserved. Manual number prefixes are represented by the source automatic numbering. The title uses a named Title style without altering the retained direct appearance.
Preserve all other package parts; scrub inherited unrelated author/title metadata. No headers, tables, or extra sections are added. Source template bytes remain unchanged.
Renderer: packaged renderer cannot run because bundled soffice.exe is missing. Native Word export was attempted and returned E_ACCESSDENIED. Page visuals remain unverified; structural and text checks are performed and the limitation will be disclosed.
'''
(WORK/'artifact.md').write_text(contract,encoding='utf-8')
for src in sources:
    newrt=deepcopy(rt);newb=newrt.find(W+'body')
    for el in list(newb):newb.remove(el)
    texts=src['paragraphs']
    newb.append(filled(paras[0],texts[0],True));newb.append(filled(paras[1],texts[1]))
    for j,txt in enumerate(texts[2:]):newb.append(filled(paras[j+2],re.sub(r'^\d+\.\s*','',txt)))
    newb.append(deepcopy(sect))
    modified=dict(parts)
    modified['word/document.xml']=E.tostring(newrt,xml_declaration=True,encoding='UTF-8',standalone=True)
    modified['word/styles.xml']=E.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True)
    core=E.fromstring(parts['docProps/core.xml'])
    for e in core:
        if E.QName(e).localname in ['creator','lastModifiedBy','title','subject','description','keywords','category']:e.text=''
    modified['docProps/core.xml']=E.tostring(core,xml_declaration=True,encoding='UTF-8',standalone=True)
    app=E.fromstring(parts['docProps/app.xml'])
    for e in app:
        if E.QName(e).localname in ['Pages','Words','Characters','CharactersWithSpaces','Paragraphs','Lines','TotalTime']:e.text='0'
    modified['docProps/app.xml']=E.tostring(app,xml_declaration=True,encoding='UTF-8',standalone=True)
    dest=ROOT/'filally_22'/f"审稿意见{src['reviewer']}"/'01_审稿意见.docx'
    with ZipFile(dest,'w',ZIP_DEFLATED) as z:
        for n,b in modified.items():z.writestr(n,b)
    with ZipFile(dest) as z:assert all(z.read(n)==parts[n] for n,v in inventory.items() if v['policy']=='preserve')
    doc=Document(dest);actual=[p.text for p in doc.paragraphs]
    assert actual[:2]+[f'{i}. '+s for i,s in enumerate(actual[2:],1)]==texts
    assert doc.paragraphs[0].runs[0].font.size.pt==15
    print('TR template applied, exact text verified:',src['reviewer'])
assert sha(REF.read_bytes())==reference_hash
renderer=Path("C:/Users/zh'x/.codex/plugins/cache/openai-primary-runtime/documents/26.1017.22136/skills/documents/render_docx.py")
env=dict(os.environ);env['TEMP']=env['TMP']=str(WORK)
for i in range(1,4):
    p=ROOT/'filally_22'/f'审稿意见{i}'/'01_审稿意见.docx'
    r=subprocess.run([sys.executable,str(renderer),str(p),'--output_dir',str(WORK/f'TR_word_render_{i}')],env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45)
    (WORK/f'TR_word_render_{i}.log').write_text(r.stdout+r.stderr,encoding='utf-8')
    print('Render attempt',i,r.returncode)
