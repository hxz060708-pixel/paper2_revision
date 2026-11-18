from pathlib import Path
import json, re, shutil, hashlib, difflib

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '_review_work' / 'v2'
OUT = ROOT / 'paper2_审稿意见' / '第二版_结合模板'
REV = OUT / 'paper2_修改副本'
WORK.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
if REV.exists():
    raise RuntimeError('Revision copy already exists; edit the existing copy deliberately.')
REV.mkdir()
SOURCE = ROOT / 'paper2'
shutil.copytree(SOURCE / 'figs', REV / 'figs')
original = (SOURCE / 'paper2.tex').read_text(encoding='utf-8')
text = original
old_manifest = json.loads((ROOT / '_review_work' / 'revision_manifest.json').read_text(encoding='utf-8'))
changes = []

def replace(old, new, cid, location, count=1):
    global text
    assert text.count(old) == count, (cid, location, text.count(old))
    text = text.replace(old, new)
    changes.append(dict(id=cid, location=location, old=old, new=new, count=count))

# Reuse only checked language edits and the verified literature addition.
# The rejected theorem overview and example-overview comments are omitted.
for c in old_manifest['changes']:
    if c['id'] in ('R1.1', 'R1.1/R1.3', 'R1.2'):
        replace(c['old'], c['new'], 'R1.1' if c['id']=='R1.1/R1.3' else c['id'], c['location'], c['count'])
replace('where $K_n$ denote the controller gains to be designed.',
        'where $K_n$ denotes the controller gain for rule $n$.',
        'R1.1', 'Section 2.4 controller-rule description')

motivation = r'''The PMSM example in Section~\ref{sec4} provides an engineering illustration of these coupled requirements. In this model, deception attacks affect the transmitted current and angular-velocity measurements, actuator degradation reduces the effective control input, and the event-triggering mechanism limits data transmissions. Considering these effects together connects the controller design to the simultaneous requirements of data integrity, actuator reliability, and communication efficiency in a networked motor drive.'''
anchor = 'communication resources.\n\nLyapunov--Krasovskii'
replace(anchor, 'communication resources.\n\n'+motivation+'\n\nLyapunov--Krasovskii',
        'R1.3', 'Introduction, after the actuator-failure motivation paragraph')

fault_meaning = r'''Here, each diagonal entry of $F_i$ represents the fraction of the commanded input delivered by the corresponding actuator in mode $i$: a value of one denotes full effectiveness, a value between zero and one denotes partial loss of effectiveness, and zero denotes complete loss. The matrices $F_{i0}$ and $F_{i1}$ contain the midpoints and half-widths of the admissible effectiveness intervals, respectively; $V_i$ describes the normalized deviations within these intervals.'''
anchor = r'Then, $V_i^\mathrm{T}V_i \le I$ holds.'
replace(anchor, anchor+'\n'+fault_meaning, 'R1.4', 'Section 2.4, after the definitions below Eq. (12)')
fault_example = r'''For this single-input example, these values give $F_1\in[0.8,1.0]$ and $F_2\in[0.6,1.0]$. Thus, modes 1 and 2 allow up to $20\%$ and $40\%$ loss of actuator effectiveness, respectively; neither interval includes complete actuator loss.'''
anchor = 'for mode 2. In addition, the external disturbance is specified by'
replace(anchor, 'for mode 2. '+fault_example+'\nIn addition, the external disturbance is specified by',
        'R1.4', 'Example 1, actuator-failure parameter paragraph')

trend = r'''In the reported simulations, increasing $\sigma$ from 4 to 20 increases the transmitted packet count from 85 to 164. This trend is consistent with the role of $\sigma$ in \eqref{eq:adaptive_law}: its equilibrium threshold $1/\sigma$ decreases from 0.25 to 0.05. For fixed sampled state, error, and weighting matrix, a smaller $\delta(t)$ lowers the right-hand threshold in the triggering comparison \eqref{eq:Event_TR_1}, making transmission easier to trigger. This explains the direction of the observed trend; the actual transmission count also depends on the closed-loop trajectory and the evolution of the threshold.'''
metric = r'''The saving rate is calculated as $(1-N_{\mathrm{ET}}/N_{\mathrm{TT}})\times100\%$, where $N_{\mathrm{ET}}$ and $N_{\mathrm{TT}}$ are the reported AETM and time-triggered transmission counts over the same simulation interval. The four settings in Table~\ref{tab:sigma_effect} therefore give saving rates of $78.75\%$, $71.75\%$, $66.00\%$, and $59.00\%$, respectively.'''
replace('These results confirm that the proposed AETM significantly reduces the number of data transmissions.',
        trend+'\n'+metric, 'R1.5', 'Example 1, discussion immediately before Table 1')
replace(r'only 65 transmissions are triggered out of 400 candidate sampling instants, yielding a communication saving rate of $83.79\%$.',
        r'65 transmissions are triggered out of the reported 400 candidate sampling instants, yielding a communication saving rate of $(1-65/400)\times100\%=83.75\%$.',
        'Additional proofreading', 'Example 2, saving-rate percentage checked against the reported counts')

# Caption changes use figure labels, not figure numbers guessed from source order.
captions = {
    'fig7': r'Adaptive threshold $\delta(t)$ for $\sigma=4$ and sampling period $h=0.05$~s. The equilibrium threshold is $1/\sigma=0.25$.',
    'fig8': r'Release instants and inter-event intervals for $\sigma=4$ and sampling period $h=0.05$~s.',
    'fig14': r'Adaptive threshold $\delta(t)$ for $\sigma=10$ and sampling period $h=0.05$~s. The equilibrium threshold is $1/\sigma=0.1$.',
    'fig15': r'Release instants and inter-event intervals for $\sigma=10$ and sampling period $h=0.05$~s.',
}
for label, caption in captions.items():
    match = re.search(r'\\caption\{([^\n]+)\}(\s*\\label\{'+label+r'\})', text)
    assert match, label
    replace(match.group(0), r'\caption{'+caption+'}'+match.group(2), 'R1.6', 'Caption '+label)

bib_original = (SOURCE/'ref2.bib').read_text(encoding='utf-8')
bib_verified = (ROOT/'paper2_审稿意见'/'paper2_修改副本'/'ref2.bib').read_text(encoding='utf-8')
assert bib_verified.startswith(bib_original)
(REV/'ref2.bib').write_text(bib_verified, encoding='utf-8')
(REV/'paper2.tex').write_text(text, encoding='utf-8')
for c in changes:
    c['revised_lines'] = [text[:m.start()].count('\n')+1 for m in re.finditer(re.escape(c['new']), text)]
manifest = dict(source_hashes=old_manifest['source_hashes'], changes=changes,
                new_references=old_manifest['new_references'])
(WORK/'revision_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2),encoding='utf-8')
(OUT/'paper2_修改对照.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='original/paper2.tex', tofile='paper2_修改副本/paper2.tex')),encoding='utf-8')

comments = [
    'The manuscript requires further editing to improve English grammar and sentence structure. Some sentences in the Abstract and Introduction are overly long and could be expressed more clearly. Careful language polishing is recommended.',
    'The literature discussion could be strengthened by including additional recent studies on secure event-triggered control of interval type-2 fuzzy systems. Please briefly explain their connections with the present work to better establish the research context.',
    'The practical motivation could be made more concrete. The authors are encouraged to relate the simultaneous consideration of deception attacks, actuator failures, and limited communication resources to the PMSM application presented in Example 1.',
    'The physical meaning of the actuator-failure parameters could be explained more clearly. In particular, please clarify what F_i0 and F_i1 represent and what actuator-effectiveness ranges correspond to the values used in Example 1.',
    'In Table 1, the number of transmitted packets increases as sigma increases. Please add a brief explanation of this trend and relate it to the adaptive threshold in Eq. (6).',
    'Some simulation captions are rather brief. Please indicate the corresponding sigma and sampling-period settings in Figs. 8-9 and 14-15, so that the threshold and transmission plots can be interpreted more easily.'
]
overview = 'This paper investigates adaptive event-triggered control for interval type-2 fuzzy cyber-physical systems under deception attacks and actuator failures. A membership-function-derivative-dependent switching design is combined with a looped-functional approach to obtain conditions for the joint design of the controller and triggering mechanism. A PMSM example and a numerical example illustrate the proposed method. The topic is relevant to secure networked control. The following minor comments are offered to improve the clarity and presentation of the manuscript.'
responses = [
    'Thank you for this suggestion. We have revised the Abstract and the opening paragraph of the Conclusion, shortened long sentences in the Introduction and Section 2.2, and corrected grammar and punctuation in the main text. For example, the duplicated full stop after "CPSs" has been removed, "the transmitted data is" has been changed to "the transmitted data are", and "condition ... guarantee" has been corrected to "condition ... guarantees". These edits improve the expression without changing the displayed mathematical statements.',
    'We have added two relevant recent studies to the Introduction and bibliography: Liu et al. (2025) on torus-event-based sliding-mode control under deception attacks, and Chandrasekar et al. (2026) on adaptive event-triggered asynchronous control of uncertain IT-2 fuzzy Markov jump systems. The new paragraph explains their connection to communication scheduling and secure fuzzy control, and then identifies the continuous-time model and membership-function-derivative-based design considered in this manuscript.',
    'We have added a paragraph in the Introduction connecting the problem formulation to the PMSM example. It explains that the attack model affects transmitted current and angular-velocity measurements, the actuator-failure model reduces the applied control input, and the event trigger limits data transmissions. This makes the engineering motivation more explicit using the application already considered in the manuscript.',
    'We have added a physical interpretation in Section 2.4. Each diagonal entry of F_i is an actuator-effectiveness factor. F_i0 contains the interval midpoints and F_i1 the half-widths, while V_i specifies the normalized deviations. We have also explained the values in Example 1: 0.9 +/- 0.1 gives the interval [0.8, 1.0], and 0.8 +/- 0.2 gives [0.6, 1.0]. These intervals allow up to 20% and 40% loss of effectiveness, respectively, and exclude complete actuator loss. The parameter values and uncertainty model are unchanged.',
    'We have expanded the discussion of Table 1. In the reported simulations, increasing sigma from 4 to 20 increases the transmission count from 85 to 164. Meanwhile, the equilibrium threshold 1/sigma decreases from 0.25 to 0.05. For fixed sampled state, error, and weighting matrix, a smaller threshold makes the triggering inequality easier to satisfy. The revised text links this property to the observed trend and notes that the actual count also depends on the closed-loop trajectory and threshold evolution. The existing transmission counts are unchanged.',
    'We have expanded the four captions. Figs. 8-9 now specify sigma = 4 and h = 0.05 s; Figs. 14-15 specify sigma = 10 and h = 0.05 s. The threshold captions also give the corresponding equilibrium values, 0.25 and 0.1. These settings are taken from the existing descriptions of Examples 1 and 2. The plotted results are unchanged.'
]
locations = [
    'Abstract; Introduction; Sections 2.2-2.4; proof of Theorem 3.1; Example 2; Conclusion.',
    'Introduction, paragraph beginning "Recent work has further developed"; the two added entries in the bibliography.',
    'Introduction, paragraph beginning "The PMSM example in Section".',
    'Section 2.4, paragraph beginning "Here, each diagonal entry"; Example 1, paragraph specifying the actuator-failure parameters.',
    'Example 1, discussion immediately before Table 1.',
    'Captions of Figs. 8, 9, 14, and 15.'
]
content = dict(comments=comments, overview=overview, responses=responses, locations=locations,
               motivation=motivation, fault_meaning=fault_meaning, fault_example=fault_example, trend=trend)
(WORK/'document_content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(revision=str(REV),comments=len(comments),changes=len(changes)),ensure_ascii=False))
