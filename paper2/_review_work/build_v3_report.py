from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'_review_work'/'v3'
OUT=ROOT/'paper2_审稿意见'/'第三版_意见正文'
WORK.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
writer=(ROOT/'_review_work'/'build_documents.py').read_text(encoding='utf-8').split('\ncomments=[',1)[0]
writer=writer.replace("OUT=ROOT/'paper2_审稿意见'", "OUT=ROOT/'paper2_审稿意见'/'第三版_意见正文'")
writer=writer.replace("WORK=ROOT/'_review_work'", "WORK=ROOT/'_review_work'/'v3'")
exec(compile(writer,'retained_template_writer','exec'),globals())

overview='This paper investigates adaptive event-triggered control for interval type-2 fuzzy cyber-physical systems subject to deception attacks and actuator failures. A switching design based on membership-function-derivative information is developed, and a two-sided FMF-dependent looped functional is employed to derive LMI-based control conditions. The proposed approach is illustrated through a PMSM example and a numerical example. The topic is relevant to secure networked control. However, the following points should be addressed to improve the presentation of the manuscript.'
comments=[
'The manuscript requires careful editing to improve English grammar and sentence structure. Some sentences are overly complex or awkwardly phrased, which may hinder comprehension for international readers. Professional language polishing is recommended.',
'The Introduction should better explain the practical significance of considering deception attacks and actuator failures simultaneously under limited communication resources. The authors are encouraged to connect this combined setting more closely with the engineering application considered in the paper.',
'The problem formulation involves several components, including IT-2 fuzzy modeling, adaptive triggering, deception attacks, and actuator failures. Please add an explanatory remark to clarify how these components are connected in the closed-loop model, so that the modeling framework is easier to follow.',
'Why is a two-sided FMF-dependent looped functional adopted in this work? In addition to the brief discussion in Remark 3.1, please provide a more intuitive explanation of the roles of membership-function dependence and the two-sided sampling-interval structure.',
'The discussion of the numerical examples could be strengthened. Please explain more clearly how the state responses, adaptive-threshold evolution, and communication savings together illustrate the effects of the proposed controller and triggering mechanism.',
'It is suggested that the authors include more recent studies closely related to secure event-triggered control and fault-tolerant control of IT-2 fuzzy systems. The distinctions and connections between these studies and the proposed method should also be discussed.'
]
paragraphs=[paragraph('Comments on paper2','title'),paragraph(overview)]
paragraphs.extend(paragraph(c,'number') for c in comments)
dest=write_doc('01_审稿意见_Reviewer1_第三版.docx',paragraphs)
actual=[p.text for p in Document(dest).paragraphs]
assert all(c in actual for c in comments)
assert len([p for p in paragraphs if p.find('.//'+W+'numPr') is not None])==6
(WORK/'report_content.json').write_text(json.dumps(dict(overview=overview,comments=comments,file=str(dest)),ensure_ascii=False,indent=2),encoding='utf-8')
(WORK/'comment_basis.json').write_text(json.dumps([
{'id':'R1.1','template':'SMCA comment 1 / AMC comment 1','paper':'Abstract, Introduction, grammar examples recorded in the reading notes','action':'Language editing; no claim of professional editing already performed.'},
{'id':'R1.2','template':'SMCA comment 2 / AMC comment 2 / ESWA motivation comments','paper':'Introduction already discusses the joint setting; Example 1 provides the PMSM application','action':'Strengthen the application connection without claiming that motivation is entirely absent.'},
{'id':'R1.3','template':'ESWA model-description comments','paper':'Sections 2.1-2.4 and the combined closed-loop model','action':'Add a concise conceptual remark based on the existing equations; no new implementation assumption.'},
{'id':'R1.4','template':'ESWA looped-functional rationale comment / short-review method rationale questions','paper':'Remark 3.1 and the functional construction in Theorem 3.1','action':'Extend the intuitive explanation; do not assert numerical superiority or request rederivation.'},
{'id':'R1.5','template':'MATH numerical-result discussion / ESWA more detailed simulation description','paper':'Existing state, control, threshold, and transmission results in both examples','action':'Explain the existing observations; no new experiment or unreported quantitative result.'},
{'id':'R1.6','template':'SMCA comment 8 / AMC comment 8','paper':'Current references already include recent works','action':'Add closely related recent studies; do not claim most citations are outdated.'}
],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'comments':6},ensure_ascii=False))
