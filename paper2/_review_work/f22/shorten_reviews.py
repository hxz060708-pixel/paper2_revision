from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import json, sys

ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).resolve().parent
new={
2:[
"Although the references include recent papers, the Introduction could better compare this work with closely related approaches. Please discuss recent studies on event-triggered IT-2 fuzzy control and secure or fault-tolerant control. Explain how the combined attack/failure setting and derivative-dependent regional design relate to these studies, using only supported distinctions.",
"Sections 2.3 and 2.4 introduce the deception signal and actuator-failure model separately. Please clarify how the corrupted sampled state and actuator mode enter the control loop in the model. Add a concise bridging paragraph before the substitution leading to the closed-loop dynamics in Eq. (15).",
"Remark 3.1 introduces the two-sided FMF-dependent looped functional, but its motivation needs clarification. Since the control input is updated according to sampled information, the system state continues to evolve between consecutive sampling instants. Please clarify why a looped functional is suitable for describing this inter-sample behavior, how the sampling-interval-dependent terms are incorporated, and why membership-function-related information is included in the functional. A concise explanation of these design choices and their benefits would help readers understand the theoretical framework.",
"The manuscript uses symbols for lower and upper firing strengths, normalized membership functions, actuator-failure matrices, and region-dependent controller gains. Please define these quantities at first use and distinguish related symbols.",
"The manuscript presents a PMSM example and a second numerical IT-2 fuzzy system, but their complementary purposes need further clarification. Please explain what the engineering-motivated example illustrates and what the second model configuration adds. Connect state responses, control input, threshold evolution, and transmission statistics to specific claims.",
"The manuscript needs careful language revision to improve grammar and logical flow. Several technical concepts appear in quick succession, particularly in the Abstract and Section 2. Please review sentence transitions, abbreviation consistency, and isolated grammar errors.",
"The Conclusion should clearly distinguish current results from possible extensions. Please state the specified state-feedback and attack/fault assumptions underlying this analysis, and connect future work on output feedback or more general attack models to these assumptions. Distinguish established results from directions that remain open.",
],
3:[
"The Introduction lists the contributions, but links among the combined system model, adaptive event-triggering mechanism, derivative-dependent regional conditions, and LMI-based synthesis need clarification. Each contribution should state a distinct methodological element and explain its role in the overall framework. A cohesive transition from the research gap to the contributions would clarify how the components fit together.",
"The theoretical analysis is followed by numerical examples illustrating the proposed control strategy. Please clarify this transition by indicating which features of the proposed framework the examples illustrate, such as closed-loop state behavior and event-triggered transmission. A short introductory paragraph at the beginning of the numerical section would help readers connect the theoretical development with the results presented below.",
"Figure 12 presents the membership-function derivative and control input, but their significance needs clarification. Please clarify how the derivative information relates to the region-dependent design and what the control-input trajectory indicates about controller behavior. A concise discussion connecting these observations to the closed-loop response plots would improve interpretation.",
"Please improve English throughout the manuscript. The Abstract should clearly progress from the problem setting to the method, theoretical result, and numerical validation. The Introduction should provide smooth transitions from the literature review to the stated contributions.",
"Please check simulation-figure readability, including axis labels, units, legends, and consistency between plotted quantities and captions. Discuss the main observations rather than merely repeating captions.",
"The numerical examples illustrate the proposed controller's behavior under selected simulation settings. Please clarify how the observed trajectories relate to the stated control objectives, while distinguishing numerical illustration from the theoretical guarantee established by the theorem. This would improve the precision and clarity of numerical interpretation.",
"Please compare the proposed framework with recent, directly related work, stating only clearly supported methodological distinctions. The Introduction already cites recent studies; clarify how the combined attack/failure setting and membership-function-derivative-dependent regional conditions relate to the closest existing methods.",
]}
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
for ri,texts in new.items():
    path=ROOT/'filally_22'/f'审稿意见{ri}'/'01_审稿意见.docx'
    with ZipFile(path) as z: tree=E.fromstring(z.read('word/document.xml'))
    ps=tree.find(W+'body').findall(W+'p')
    for i,t in enumerate(texts,1):
        old=''.join(n.text or '' for n in ps[i+1].iter(W+'t'))
        print(f'R{ri}.{i}: {len(old.split())} -> {len(t.split())}; removed {len(old.split())-len(t.split())}')
        assert len(old.split())-len(t.split()) == 10

ending_old='After reading, the primary features and contributions of this article are sound compared to some existing publications. However, the following aspects should be seriously considered to improve the presentation quality of this investigation.'
ending_new='The topic investigated in this manuscript is of interest, and the proposed control framework offers useful insights into the considered problem. However, several aspects require further clarification and discussion to strengthen the presentation of the results.'
responses_path=WORK/'responses.json'
responses=json.loads(responses_path.read_text(encoding='utf-8'))
for ri,texts in new.items():
    folder=ROOT/'filally_22'/f'审稿意见{ri}'
    path=folder/'01_审稿意见.docx'
    with ZipFile(path) as z: parts={n:z.read(n) for n in z.namelist()}
    tree=E.fromstring(parts['word/document.xml'])
    ps=tree.find(W+'body').findall(W+'p')
    overview=''.join(n.text or '' for n in ps[1].iter(W+'t')).replace(ending_old,ending_new)
    for p,text in [(ps[1],overview)]+list(zip(ps[2:9],texts)):
        nodes=list(p.iter(W+'t'))
        nodes[0].text=text
        for n in nodes[1:]: n.text=''
    parts['word/document.xml']=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
    import io
    buf=io.BytesIO()
    with ZipFile(buf,'w',ZIP_DEFLATED) as z:
        for name,data in parts.items(): z.writestr(name,data)
    content=buf.getvalue()
    destinations=[path,folder/'01_审稿意见_结尾已更新.docx']
    saved=[]
    for dest in destinations:
        try:
            dest.write_bytes(content)
            saved.append(dest)
            print('SAVED',dest,flush=True)
        except PermissionError:
            print('LOCKED',dest,flush=True)
    if path not in saved:
        dest=folder/'01_审稿意见_精简版.docx'
        dest.write_bytes(content)
        print('LATEST',dest,flush=True)
    else:
        print('LATEST',path,flush=True)
    r=next(r for r in responses if r['reviewer']==ri)
    r['overview']=overview
    for i,text in enumerate(texts,1): r['items'][i-1]['comment']=f'{i}. '+text
responses_path.write_text(json.dumps(responses,ensure_ascii=False,indent=2),encoding='utf-8')
builder=WORK/'build_pdfs.py'
source=builder.read_text(encoding='utf-8').replace('for r in reviews:', 'for r in reviews[1:]:',1)
exec(compile(source,str(builder),'exec'),{'__file__':str(builder),'__name__':'__main__'})

