from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import json, re, runpy

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
sources = json.loads((WORK/'source_reviews.json').read_text(encoding='utf-8'))
replacements = {}
for src in sources:
    path = ROOT/'filally_22'/f"审稿意见{src['reviewer']}"/'01_审稿意见.docx'
    with ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    tree = E.fromstring(parts['word/document.xml'])
    pairs = {}
    for text in src['paragraphs'][2:]:
        number, heading, body = re.match(r'^(\d+\.\s*)([^.]+\.\s*)(.*)$', text, re.S).groups()
        pairs[heading+body] = body
        replacements[text] = number+body
    changed = 0
    for p in tree.iter(W+'p'):
        nodes = list(p.iter(W+'t'))
        old = ''.join(n.text or '' for n in nodes)
        if old in pairs:
            nodes[0].text = pairs[old]
            for n in nodes[1:]:
                n.text = ''
            changed += 1
    if changed:
        parts['word/document.xml'] = E.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
        with ZipFile(path, 'w', ZIP_DEFLATED) as z:
            for name, data in parts.items():
                z.writestr(name, data)
    print(f"审稿意见{src['reviewer']}：已删除 {changed} 个开头短句", flush=True)

response_path = WORK/'responses.json'
responses = json.loads(response_path.read_text(encoding='utf-8'))
for review in responses:
    for item in review['items']:
        item['comment'] = replacements.get(item['comment'], item['comment'])
response_path.write_text(json.dumps(responses, ensure_ascii=False, indent=2), encoding='utf-8')
runpy.run_path(str(WORK/'build_pdfs.py'), run_name='__main__')
