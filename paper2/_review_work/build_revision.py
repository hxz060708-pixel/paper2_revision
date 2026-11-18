from pathlib import Path
import re, json, shutil, hashlib, difflib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper2_审稿意见'
REV = OUT / 'paper2_修改副本'
WORK = ROOT / '_review_work'
OUT.mkdir(exist_ok=True)
WORK.mkdir(exist_ok=True)
if REV.exists():
    raise RuntimeError('Refusing to overwrite an existing revision directory')
REV.mkdir()
source = ROOT / 'paper2'
for name in ['paper2.tex', 'ref2.bib']:
    shutil.copy2(source/name, REV/name)
shutil.copytree(source/'figs', REV/'figs')
original = (source/'paper2.tex').read_text(encoding='utf-8')
text = original
changes=[]

def replace(old, new, cid, location, count=1):
    global text
    actual = text.count(old)
    assert actual == count, (cid, location, actual, old[:100])
    text=text.replace(old,new)
    changes.append(dict(id=cid, location=location, old=old, new=new, count=count))

abstract = r'''This article addresses adaptive event-triggered control for interval type-2 (IT-2) fuzzy cyber-physical systems (CPSs) subject to stochastic deception attacks and Markov-type actuator failures. An adaptive event-triggered mechanism (AETM) adjusts the transmission threshold using state-error information to reduce redundant communication. Deception attacks are described by a Bernoulli process, and actuator failures are represented by Markov switching fault matrices. These components are incorporated into a unified closed-loop model. The signs of the membership-function derivatives define operational regions for a region-dependent fuzzy controller. Within this framework, the controller gains and event-triggering weight matrices are jointly designed. A two-sided looped functional dependent on fuzzy membership functions (FMFs) incorporates membership information and sampled-data dynamics. Sufficient conditions for asymptotic stability with a prescribed $\mathrm{H}_\infty$ disturbance attenuation level are formulated as linear matrix inequalities (LMIs). A permanent magnet synchronous motor example and a numerical IT-2 fuzzy example illustrate the control responses and the reduction in data transmissions.'''
old_abstract = re.search(r'\\begin\{abstract\}\s*(.*?)\s*\\end\{abstract\}',text,re.S).group(1)
replace(old_abstract, abstract, 'R1.1/R1.3', 'Abstract')

replacements = [
('Applications of CPSs span intelligent transportation, smart grids, and advanced aviation','Applications of CPSs include intelligent transportation, smart grids, and aviation', 'Introduction paragraph 1',1),
('are two common cyber threats to CPSs..','are two common cyber threats to CPSs.','Introduction paragraph 3',1),
('their\nflexibility is improved, but several network-induced constraints are also\nintroduced.','they gain communication flexibility but also face network-induced constraints.','Introduction paragraph 3',1),
('IT-2 fuzzy\nCPSs under coupled cyber and physical anomalies remains insufficiently developed.','IT-2 fuzzy\nCPSs under concurrent cyber and physical anomalies warrants further investigation.','Introduction paragraph 2',1),
('However, conventional static ETMs use fixed\nthresholds and cannot adapt well to state fluctuations caused by attacks,\ndisturbances, or actuator anomalies.','However, conventional static ETMs use fixed thresholds, which do not adjust online to state fluctuations caused by attacks, disturbances, or actuator anomalies.','Introduction paragraph 4',1),
('By adjusting the threshold online according to real-time state-error information, the proposed mechanism reduces redundant transmissions while maintaining the desired control performance.','This online adjustment reduces redundant transmissions while supporting the prescribed control objective.','Introduction contribution 2',1),
('In networked control systems (NCSs), continuous data transmission often leads to network congestion and unnecessary waste of limited communication bandwidth. To alleviate the communication burden while preserving the desired control performance and avoiding unnecessary transmissions, an AETM is deployed along the sensor-to-controller communication path.','In networked control systems (NCSs), frequent data transmission can cause network congestion and consume limited communication bandwidth. An AETM is therefore introduced in the sensor-to-controller channel to reduce unnecessary transmissions while supporting the desired control performance.','Section 2.2 opening',1),
('the transmitted data is compromised by the attacker','the transmitted data are compromised by the attacker','Section 2.3 Bernoulli description',1),
('Different from Denial-of-Service attacks that aim to block communication channels','Unlike denial-of-service attacks, which block communication channels','Section 2.3 Remark 2.3',1),
('For compact representation, the following notations are introduced:','For compactness, the following notation is introduced:','Section 3 notation',1),
(r'closed-loop IT-2 fuzzy CPSs \eqref{eq:closed_loop} is',r'closed-loop IT-2 fuzzy system \eqref{eq:closed_loop} is','Section 3 system terminology',3),
(r'condition \eqref{shucr1} guarantee',r'condition \eqref{shucr1} guarantees','Proof of Theorem 3.1',1),
('The open-loop system exhibits a clear divergent behavior','The open-loop system exhibits divergent behavior','Example 2 discussion',1),
('offers the same communication-efficiency advantage.','reduces transmissions relative to sending every candidate sample.','Example 2 closing discussion',1),
]
for a,b,loc,n in replacements:
    replace(a,b,'R1.1',loc,n)

recent = r'''Recent work has further developed event-triggered security control for IT-2 fuzzy systems. Liu et al.\ \cite{liuTorusEventBased2025} combined a two-threshold torus-event-triggering protocol with sliding-mode control for discrete-time IT-2 fuzzy systems under deception attacks. Chandrasekar et al.\ \cite{chandrasekarAdaptiveEvent2026} investigated adaptive event-triggered asynchronous control of uncertain IT-2 fuzzy Markov jump systems, using a hidden Markov model to describe the mismatch between plant and controller modes. These studies provide relevant developments in communication scheduling and attack-resilient fuzzy control. The present study focuses on continuous-time IT-2 fuzzy CPSs with Bernoulli deception attacks and Markov-type actuator failures, and organizes the controller and triggering design around the signs of the membership-function derivatives.'''
anchor='Building on the above discussion, this study addresses adaptive event-triggered'
replace(anchor,recent+'\n\n'+anchor,'R1.2','Introduction paragraph immediately before the contributions')

overview=r'''This section develops the analysis and synthesis conditions in three stages. Theorem~\ref{thm1} gives sufficient stability and $\mathrm{H}_\infty$ performance conditions for the closed-loop model. Theorem~\ref{thm2} introduces transformed decision variables to express the joint design of the controller gains and event-triggering weight matrix. Theorem~\ref{thm3} then bounds the actuator-failure uncertainty and yields deterministic LMIs for numerical synthesis. This sequence connects the performance analysis to the gain and triggering-matrix calculations used in the examples.'''
replace(r'This section presents the main results. On the basis of the established system model, an appropriate Lyapunov functional is constructed to obtain sufficient criteria guaranteeing the asymptotic stability and prescribed $\mathrm{H}_\infty$ performance of the closed-loop system.',overview,'R1.4','Section 3 opening paragraph')

examples=r'''Two examples illustrate complementary aspects of the proposed scheme. Example~\ref{exm1} uses a permanent magnet synchronous motor (PMSM) model to provide an engineering context and reports transmission counts for several values of $\sigma$. Example~\ref{exm2} considers a different IT-2 fuzzy model under a fixed parameter setting. In both examples, the state responses, control inputs, actuator-failure modes, adaptive thresholds, and transmission intervals illustrate the closed-loop behavior and communication activity.'''
# The second example has no explicit label in the original; add a stable label.
example_starts = list(re.finditer(r'\\begin\{example\}(?:\\label\{[^}]+\})?',text))
assert len(example_starts)==2
second = example_starts[1].group()
if second == r'\begin{example}':
    pos=example_starts[1].start()
    text=text[:pos]+text[pos:].replace(second,second+r'\label{exm2}',1)
    changes.append(dict(id='R1.5',location='Example 2 label',old=second,new=second+r'\label{exm2}',count=1))
elif second != r'\begin{example}\label{exm2}':
    label=re.search(r'\\label\{([^}]+)\}',second).group(1)
    examples=examples.replace('exm2',label)
replace('This section considers an engineering-motivated example and a numerical simulation study to assess the effectiveness and applicability of the developed control scheme.',examples,'R1.5','Section 4 opening paragraph')

metric=r'''For the communication comparison, let $N_{\mathrm{TT}}$ denote the number of candidate packets transmitted by the time-triggered baseline and $N_{\mathrm{ET}}$ the number transmitted by the AETM over the same reported interval. The saving rate is calculated as $(1-N_{\mathrm{ET}}/N_{\mathrm{TT}})\times100\%$. For example, the first row of Table~\ref{tab:sigma_effect} gives $(1-85/400)\times100\%=78.75\%$. The reported counts therefore quantify the fraction of transmissions avoided relative to sending every candidate sample.'''
replace('These results confirm that the proposed AETM significantly reduces the number of data transmissions.',metric,'R1.6','Example 1 paragraph before Table 1')
replace(r'only 65 transmissions are triggered out of 400 candidate sampling instants, yielding a communication saving rate of $83.79\%$.',r'65 transmissions are triggered out of the reported 400 candidate sampling instants. Using the same definition as in Example~\ref{exm1}, the saving rate is $(1-65/400)\times100\%=83.75\%$.','R1.6','Example 2 final paragraph')

conclusion=r'''This study has considered adaptive event-triggered $\mathrm{H}_{\infty}$ control of IT-2 fuzzy CPSs subject to stochastic deception attacks and Markov-type actuator failures. The AETM updates its threshold using state-error information to reduce redundant transmissions. Membership-function derivative information defines operational regions for the fuzzy control design. An FMF-dependent looped functional is used to formulate sufficient stability and performance conditions. The controller gains and event-triggering weight matrices are jointly determined through LMIs, with a bounding technique used to handle actuator-failure uncertainty.'''
old_conclusion=re.search(r'\\section\{Conclusion\} \\label\{sec5\}\n(.*?)\n\n',text,re.S).group(1)
replace(old_conclusion,conclusion,'R1.1','Conclusion paragraph 1')

bibnew=r'''

@article{liuTorusEventBased2025,
  author = {Liu, Xingwang and Ling, Zhi and Zhang, Yang},
  title = {Torus-Event-Based Sliding Mode Control for Networked Interval Type-2 Fuzzy Systems Under Deception Attacks},
  journal = {International Journal of Network Dynamics and Intelligence},
  year = {2025},
  volume = {4},
  number = {1},
  pages = {100003},
  doi = {10.53941/ijndi.2025.100003}
}

@article{chandrasekarAdaptiveEvent2026,
  author = {Chandrasekar, A. and Chang, Wen-Jer and Radhika, T. and Santhosh Kumar, S. and Aslam, Muhammad Shamrooz},
  title = {Adaptive event triggering asynchronous control for interval type-2 fuzzy Markov jump systems with uncertainties and deception attacks},
  journal = {Complex \& Intelligent Systems},
  year = {2026},
  volume = {12},
  pages = {59},
  doi = {10.1007/s40747-025-02172-5}
}
'''
original_bib=(source/'ref2.bib').read_text(encoding='utf-8')
(REV/'ref2.bib').write_text(original_bib+bibnew,encoding='utf-8')
(REV/'paper2.tex').write_text(text,encoding='utf-8')
for c in changes:
    # Verified source-line locators, including repeat occurrences where applicable.
    c['revised_lines']=[text[:m.start()].count('\n')+1 for m in re.finditer(re.escape(c['new']),text)]

manifest=dict(source_hashes={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ['paper2.tex','ref2.bib','paper2.pdf']},changes=changes,new_references=[dict(key='liuTorusEventBased2025',url='https://www.sciltp.com/journals/ijndi/articles/2504000064',doi='10.53941/ijndi.2025.100003'),dict(key='chandrasekarAdaptiveEvent2026',url='https://link.springer.com/article/10.1007/s40747-025-02172-5',doi='10.1007/s40747-025-02172-5')])
(WORK/'revision_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
diff=''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='original/paper2.tex',tofile='paper2_修改副本/paper2.tex'))
(OUT/'paper2_修改对照.diff').write_text(diff,encoding='utf-8')
print(json.dumps({'revision':str(REV),'change_groups':len(changes),'new_references':2},ensure_ascii=False))
