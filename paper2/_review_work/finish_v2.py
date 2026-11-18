from pathlib import Path
import re,json,difflib
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'_review_work'/'v2'
OUT=ROOT/'paper2_审稿意见'/'第二版_结合模板'
REV=OUT/'paper2_修改副本'
tex=REV/'paper2.tex'
s=tex.read_text(encoding='utf-8')
manifest=json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
old=r'\end{minipage}'+'\n'+ '\t'+r'\begin{minipage}'
new=r'\end{minipage}\hfill'+'\n'+ '\t'+r'\begin{minipage}'
n=s.count(old)
assert n==6,n
s=s.replace(old,new)
manifest['changes'].append(dict(id='R1.6',location='Spacing between paired simulation figures',old=old,new=new,count=n))
for c in manifest['changes']:
    c['revised_lines']=[s[:m.start()].count('\n')+1 for m in re.finditer(re.escape(c['new']),s)]
    if c['location']=='Section 2.4, after the definitions below Eq. (12)':
        c['location']='Section 2.4, after the definitions below Eq. (13)'
tex.write_text(s,encoding='utf-8')
(WORK/'revision_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
original=(ROOT/'paper2'/'paper2.tex').read_text(encoding='utf-8')
(OUT/'paper2_修改对照.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='original/paper2.tex',tofile='paper2_修改副本/paper2.tex')),encoding='utf-8')
print('Added consistent spacing to six paired figure groups.')
