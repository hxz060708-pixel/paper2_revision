from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
import json,io

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[1]
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
changes={
2:{
1:"The literature review would benefit from more up-to-date coverage of secure control for IT-2 fuzzy cyber-physical systems, adaptive event-triggered control, and actuator-failure compensation. Could the authors include more recent, closely related studies to strengthen the research motivation and clarify the methodological distinctions and connections between this work and existing approaches?",
2:"Sections 2.3 and 2.4 introduce the deception signal and actuator-failure model separately. Could the authors clarify how the corrupted sampled state and actuator mode enter the control loop? Please add a concise bridging paragraph before the substitution leading to the closed-loop dynamics in Eq. (15).",
3:"Remark 3.1 introduces the two-sided FMF-dependent looped functional, but its motivation needs clarification. Although the control input is updated using sampled information, the system state evolves between sampling instants. Could the authors explain why this functional suits inter-sample behavior, how sampling-interval-dependent terms are incorporated, and why membership-function-related information is included? A concise explanation of these design choices and their benefits would clarify the theoretical framework.",
5:"The manuscript presents a PMSM example and a second numerical IT-2 fuzzy system, but their complementary purposes need further clarification. What does the engineering-motivated example illustrate, and what does the second model configuration add? Please connect state responses, control input, threshold evolution, and transmission statistics to specific claims.",
7:"The Conclusion should clearly distinguish current results from possible extensions. Could the authors state the underlying state-feedback and attack/fault assumptions and relate future work on output feedback or more general attack models to these assumptions? Please distinguish established results from directions that remain open.",
},
3:{
1:"The Introduction lists the contributions, but links among the combined system model, adaptive event-triggering mechanism, derivative-dependent regional conditions, and LMI-based synthesis need clarification. Could the authors explain each contribution's distinct methodological role in the overall framework? A cohesive transition from the research gap to the contributions would clarify how the components fit together.",
2:"The theoretical analysis is followed by numerical examples illustrating the proposed control strategy. Which features of the proposed framework do the examples illustrate, particularly regarding closed-loop state behavior and event-triggered transmission? A short introductory paragraph at the beginning of the numerical section would help readers connect the theoretical development with the results presented below.",
3:"Figure 12 presents the membership-function derivative and control input, but their significance needs clarification. How does the derivative information relate to the region-dependent design, and what does the control-input trajectory indicate about controller behavior? A concise discussion connecting these observations to the closed-loop response plots would improve interpretation.",
6:"The numerical examples illustrate the proposed controller's behavior under selected simulation settings. How do the observed trajectories relate to the stated control objectives, and how should these numerical illustrations be distinguished from the theoretical guarantee established by the theorem? This would improve the precision and clarity of numerical interpretation.",
7:"Please compare the proposed framework with recent, directly related work, stating only clearly supported methodological distinctions. How do the combined attack/failure setting and membership-function-derivative-dependent regional conditions relate to the closest existing methods? Please clarify these connections using the recent studies already cited in the Introduction.",
}}
response_path=WORK/'responses.json'
reviews=json.loads(response_path.read_text(encoding='utf-8'))
for ri in (2,3):
    folder=ROOT/'filally_22'/f'审稿意见{ri}'
    path=folder/'01_审稿意见.docx'
    with ZipFile(path) as z: parts={n:z.read(n) for n in z.namelist()}
    tree=E.fromstring(parts['word/document.xml']);body=tree.find(W+'body')
    ps=body.findall(W+'p')
    assert len(ps)==9
    if ri==2:
        assert 'symbols' in ''.join(t.text or '' for t in ps[5].iter(W+'t'))
    for index,new in changes[ri].items():
        p=ps[index+1]
        rpr=p.find(W+'r').find(W+'rPr')
        rpr=deepcopy(rpr) if rpr is not None else E.Element(W+'rPr')
        for child in list(p):
            if child.tag!=W+'pPr':p.remove(child)
        run=E.SubElement(p,W+'r');run.append(rpr)
        E.SubElement(run,W+'t',{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=new
    keep=[1,2,3,5,6,7] if ri==2 else list(range(1,8))
    if ri==2:body.remove(ps[5])
    # Original automatic numbering continues through the retained paragraphs.
    parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
    out=io.BytesIO()
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    for dest in (path,folder/'01_审稿意见_结尾已更新.docx'):
        try:
            dest.write_bytes(out.getvalue());print('SAVED',dest,flush=True)
        except PermissionError:
            alt=folder/'01_审稿意见_问句已更新.docx'
            alt.write_bytes(out.getvalue());print('LOCKED',dest,'SAVED',alt,flush=True)
    review=next(r for r in reviews if r['reviewer']==ri)
    previous=review['items']
    assert len(previous)==7
    review['items']=[]
    for num,oldnum in enumerate(keep,1):
        item=previous[oldnum-1]
        item['id']=f'R{ri}.{num}'
        content=''.join(t.text or '' for t in ps[oldnum+1].iter(W+'t'))
        item['comment']=f'{num}. '+content
        review['items'].append(item)
    print('COMMENTS',ri,len(review['items']),flush=True)
response_path.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
# Keep the source-change index aligned with the new reviewer-2 numbering.
mp=WORK/'manifest.json';manifest=json.loads(mp.read_text(encoding='utf-8'))
mapping={'R2.4':None,'R2.5':'R2.4','R2.6':'R2.5','R2.7':'R2.6'}
for patch in manifest['patches']:
    patch['ids']=[mapping.get(cid,cid) for cid in patch['ids'] if mapping.get(cid,cid) is not None]
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
builder=WORK/'build_pdfs.py'
source=builder.read_text(encoding='utf-8')
source=source.replace('本文逐条对应新+中的最新七条意见。','本文逐条对应当前同目录 Word 中的审稿意见。')
builder.write_text(source,encoding='utf-8')
source=source.replace('for r in reviews:', 'for r in reviews[1:]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})
