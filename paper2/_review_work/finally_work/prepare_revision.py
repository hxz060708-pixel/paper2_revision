from pathlib import Path
import json,shutil,re,hashlib,difflib
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'_review_work'/'finally_work'; OUT=ROOT/'finally'; REV=OUT/'paper2_修改副本'
SOURCE=ROOT/'paper2'; PREV=ROOT/'paper2_审稿意见'/'按师兄模板重做'/'paper2_修改副本'
assert not OUT.exists(),'Do not overwrite an existing finally folder.'
REV.mkdir(parents=True)
oldm=json.loads((ROOT/'_review_work'/'v4'/'revision_manifest.json').read_text(encoding='utf-8'))
for name,sha in oldm['source_hashes'].items():assert hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()==sha
original=(SOURCE/'paper2.tex').read_text(encoding='utf-8'); text=original
mapping={'R1.1':'R1.1','R1.2':'R1.3','R1.3':'R1.4','R1.4':'R1.5','R1.5':'R1.6','R1.6':'R1.2','R2.1':'R2.1','R2.2':'R2.4','R2.3':'R2.3','R2.5':'R2.6','R2.6':'R2.2','R3.1':'R3.1','R3.2':'R3.3','R3.3':'R3.4','R3.4':'R3.5','R3.5':'R3.6','R3.6':'R3.2','Layout':'Layout'}
changes=[];li=0
for c in oldm['changes']:
    if c['ids']==['R2.4']:continue
    c=dict(c);c['ids']=[mapping[x] for x in c['ids']]
    assert text.count(c['old'])==c['count'],c['location']
    c['original_lines']=[original[:m.start()].count('\n')+1 for m in re.finditer(re.escape(c['old']),original)]
    assert len(c['original_lines'])==c['count'],c['location']
    text=text.replace(c['old'],c['new'])
    if 'R1.1' in c['ids']:
        li+=1;c['language_id']=f'L{li:02d}'
    c['change_id']=f'M{len(changes)+1:02d}'
    changes.append(c)
old='This section considers an engineering-motivated example and a numerical simulation study to assess the effectiveness and applicability of the developed control scheme.'
new=r'''Two examples illustrate complementary aspects of the proposed scheme. Example~\ref{exm1} uses a permanent magnet synchronous motor (PMSM) model to provide an engineering context and reports transmission counts for several values of $\sigma$. Example~\ref{exm2} considers a different IT-2 fuzzy model under a fixed parameter setting. In both examples, the state responses, control inputs, actuator-failure modes, adaptive thresholds, and transmission intervals illustrate the closed-loop behavior and communication activity.'''
assert text.count(old)==1;text=text.replace(old,new)
changes.append(dict(ids=['R2.5'],location='Section 4, opening paragraph',old=old,new=new,count=1,original_lines=[original[:original.index(old)].count('\n')+1],change_id=f'M{len(changes)+1:02d}'))
for c in changes:
    c['revised_lines']=[text[:m.start()].count('\n')+1 for m in re.finditer(re.escape(c['new']),text)]
    assert len(c['revised_lines'])>=c['count'],c['location']
(REV/'paper2.tex').write_text(text,encoding='utf-8')
shutil.copy2(PREV/'ref2.bib',REV/'ref2.bib');shutil.copytree(PREV/'figs',REV/'figs')
figs=[]
for c in oldm['figure_edits']:
    c=dict(c);c['ids']=['R1.6'];figs.append(c)
m=dict(source_hashes=oldm['source_hashes'],changes=changes,figure_edits=figs,new_references=oldm['new_references'],language_records=li)
(WORK/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'paper2_修改对照.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='original/paper2.tex',tofile='finally/paper2_修改副本/paper2.tex')),encoding='utf-8')
print(json.dumps(dict(output=str(OUT),language_records=li,changes=len(changes)),ensure_ascii=False))
