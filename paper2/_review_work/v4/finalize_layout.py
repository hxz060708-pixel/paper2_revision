from pathlib import Path
import json,re,difflib
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'_review_work'/'v4';OUT=ROOT/'paper2_审稿意见'/'按师兄模板重做';REV=OUT/'paper2_修改副本'
p=REV/'paper2.tex';s=p.read_text(encoding='utf-8')
old=r'\caption{Evolution of the actuator fault mode $r(t)$.}'
new=r'\caption{Actuator-failure mode $r(t)$.}'
assert s.count(old)==2
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
m=json.loads((WORK/'revision_manifest.json').read_text(encoding='utf-8'))
m['changes'].append(dict(ids=['R1.5'],location='Figs. 7 and 13, compact captions',old=old,new=new,count=2))
for c in m['changes']:c['revised_lines']=[s[:x.start()].count('\n')+1 for x in re.finditer(re.escape(c['new']),s)]
(WORK/'revision_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
original=(ROOT/'paper2'/'paper2.tex').read_text(encoding='utf-8')
(OUT/'paper2_修改对照.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='original/paper2.tex',tofile='paper2_修改副本/paper2.tex')),encoding='utf-8')
