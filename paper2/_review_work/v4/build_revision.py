from pathlib import Path
import re, json, shutil, hashlib, difflib, io
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, ByteStringObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'_review_work'/'v4'
OUT=ROOT/'paper2_审稿意见'/'按师兄模板重做'
REV=OUT/'paper2_修改副本'
SOURCE=ROOT/'paper2'
assert not REV.exists(), 'Do not overwrite an existing revision.'
REV.mkdir(parents=True)
shutil.copytree(SOURCE/'figs',REV/'figs')
original=(SOURCE/'paper2.tex').read_text(encoding='utf-8')
text=original
prior=json.loads((ROOT/'_review_work'/'revision_manifest.json').read_text(encoding='utf-8'))
changes=[]

def replace(old,new,ids,location,count=1):
    global text
    assert text.count(old)==count,(ids,location,text.count(old))
    text=text.replace(old,new)
    changes.append(dict(ids=ids,location=location,old=old,new=new,count=count))

for c in prior['changes']:
    if c['id'] in ('R1.1','R1.1/R1.3','R1.2'):
        ids=['R1.6','R2.6','R3.6'] if c['id']=='R1.2' else ['R1.1','R2.1','R3.1']
        if 'CPSs..' in c['old']: ids=ids+['R1.4']
        replace(c['old'],c['new'],ids,c['location'],c['count'])
replace('where $K_n$ denote the controller gains to be designed.',
        'where $K_n$ denotes the controller gain for rule $n$.',
        ['R1.1','R2.1','R3.1'],'Section 2.4, controller-rule description')

motivation=r'''The PMSM example in Section~\ref{sec4} provides an engineering illustration of these joint requirements. In this model, deception attacks affect the transmitted current and angular-velocity measurements, actuator degradation reduces the effective control input, and the event-triggering mechanism limits data transmissions. Considering these effects together connects the control problem to data integrity, actuator reliability, and communication efficiency in a networked motor drive.'''
anchor='communication resources.\n\nLyapunov--Krasovskii'
replace(anchor,'communication resources.\n\n'+motivation+'\n\nLyapunov--Krasovskii',
        ['R1.2'],'Introduction, following the actuator-failure motivation paragraph')

scalars=r'''The prescribed scalars $\xi_1$ and $\xi_2$ are synthesis parameters that impose the proportionality relations $Q_2=\xi_1Q_1$ and $Q_3=\xi_2Q_1$ in the variable transformation below. They are not physical parameters of the plant or the attack model. Their values are fixed in each LMI feasibility problem, and different choices may affect feasibility.'''
anchor=r'\begin{thm}\label{thm2}'
replace(anchor,scalars+'\n'+anchor,['R1.3'],'Section 3, immediately before Theorem 3.2')

functional=r'''In particular, the FMF-weighted matrices retain the dependence on the fuzzy memberships, while $d_1(t)$ and $d_2(t)$ describe the elapsed and remaining portions of the sampling interval. The two integrals in $V_3(t)$ use the state derivative on the left and right of the current time, respectively. The augmented-vector terms in $V_2(t)$ and $V_4(t)$ provide additional sampling-interval information, and $V_5(t)$ includes the adaptive threshold in the analysis. These terms explain how membership information, intersample behavior, and threshold adaptation enter the functional.'''
anchor=r'Furthermore, this methodological framework is not restricted to the current system and can be extended to other networked or sampled-data systems.'
replace(anchor,functional+'\n'+anchor,['R2.2'],'Remark 3.1, explanation of the functional components')

model=r'''The two uncertainty sources enter different parts of the feedback path. The Bernoulli variable $\theta(t_kh)$ selects whether the controller receives the transmitted state or the deception signal. The matrix $F_i$ then represents the effectiveness of the actuator applying the computed control input. Thus, the attack changes the information used by the controller, whereas the actuator failure changes the input delivered to the plant; both effects appear explicitly in \eqref{eq:closed_loop}.'''
anchor='where $h_m$ and $h_n$ denote $h_m(x(t))$ and $h_n(x(t))$, respectively.'
replace(anchor,anchor+'\n'+model,['R2.3'],'Section 2.4, immediately after Eq. (15)')

workflow=r'''For offline synthesis, first specify the plant matrices, the attack bound $L$, the actuator-effectiveness intervals, and the Markov transition rates, and fix $h$, $\bar{\theta}$, $\sigma$, $\gamma$, $\xi_1$, $\xi_2$, and $\tau$. Next, solve the feasibility conditions of Theorem~\ref{thm3}, including the applicable sign conditions $\mathcal{C}_l$ and the stated requirements for the Markov modes and fuzzy-rule pairs. From a feasible solution, recover the controller gains as $K_n=\widetilde{K}_n\widetilde{N}^{-1}$ and the triggering matrix as $S=\widetilde{N}^{-\mathrm{T}}\widetilde{S}\widetilde{N}^{-1}$. The latter follows directly from $\widetilde{S}=\widetilde{N}^{\mathrm{T}}S\widetilde{N}$ in the proof of Theorem~\ref{thm2}. If the problem is infeasible for the selected scalars, this choice does not provide a feasible design under these sufficient conditions; it does not by itself establish that no stabilizing controller exists.'''
anchor=r'\section{Numerical Examples}\label{sec4}'
replace(anchor,workflow+'\n\n'+anchor,['R2.4'],'End of Section 3, offline synthesis paragraph')

replace(r'Here, $\sigma>0$ governs the convergence speed of $\delta(t)$.',
        r'Here, $\sigma>0$ sets the equilibrium threshold $1/\sigma$ and influences the adaptive response.',
        ['R2.5'],'Section 2.2, sentence after Eq. (6)')
adaptive=r'''For comparison, a fixed-threshold trigger keeps its threshold constant regardless of the current error. Here, for $\delta(t)>0$ and nonzero triggering error, \eqref{eq:adaptive_law} increases $\delta(t)$ when $\delta(t)<1/\sigma$ and decreases it when $\delta(t)>1/\sigma$. The update is zero when the error is zero or $\delta(t)=1/\sigma$. For fixed sampled state, error, and weighting matrix, a larger threshold makes the transmission condition in \eqref{eq:Event_TR_1} harder to satisfy. The communication outcome nevertheless depends on the joint evolution of the state, error, and threshold.'''
anchor='When the triggering error is small, the update of $\delta(t)$ is weakened, thereby avoiding unnecessary fluctuations of the threshold and reducing redundant data transmissions.'
replace(anchor,'When the triggering error is small, the update of $\delta(t)$ is weakened.\n'+adaptive,
        ['R2.5'],'Remark 2.2, comparison with a fixed-threshold trigger')

trend=r'''In Table~\ref{tab:sigma_effect}, increasing $\sigma$ from 4 to 20 increases the reported transmitted packet count from 85 to 164. This trend is consistent with the role of $\sigma$ in \eqref{eq:adaptive_law}: the equilibrium threshold $1/\sigma$ decreases from 0.25 to 0.05. For fixed sampled state, error, and weighting matrix, a smaller $\delta(t)$ makes the transmission condition in \eqref{eq:Event_TR_1} easier to satisfy. The actual transmission count also depends on the closed-loop trajectory and the evolution of the threshold, so the table reports the observed trend for these simulations.'''
metric=r'''The saving rate is calculated as $(1-N_{\mathrm{ET}}/N_{\mathrm{TT}})\times100\%$, where $N_{\mathrm{ET}}$ and $N_{\mathrm{TT}}$ are the reported AETM and time-triggered transmission counts over the same simulation interval. For example, the first row gives $(1-85/400)\times100\%=78.75\%$. The four settings in Table~\ref{tab:sigma_effect} give saving rates of $78.75\%$, $71.75\%$, $66.00\%$, and $59.00\%$, respectively. These percentages quantify the fraction of transmissions avoided relative to sending every candidate sample.'''
replace('These results confirm that the proposed AETM significantly reduces the number of data transmissions.',
        trend+'\n'+metric,['R3.2','R3.3'],'Example 1, discussion immediately before Table 1')
replace(r'only 65 transmissions are triggered out of 400 candidate sampling instants, yielding a communication saving rate of $83.79\%$.',
        r'65 transmissions are triggered out of the reported 400 candidate sampling instants. Using the same definition as in Example~\ref{exm1}, the saving rate is $(1-65/400)\times100\%=83.75\%$.',
        ['R3.3'],'Example 2, communication saving rate')

fig12text=r'''In Fig.~\ref{fig12}, the blue curve represents the control input $u(t)$ and the black curve represents the membership-function derivative $\dot{h}_1(t)$. The control-input curve shows the actuation generated by the feedback law, whereas the sign of $\dot{h}_1(t)$ supplies the regional switching information described in Remark~\ref{rem:Vl_definition}. Both curves approach zero as the states settle. They are displayed together to relate the control action to the membership dynamics, rather than to compare their magnitudes as a common performance measure. Fig.~\ref{fig13} shows the associated actuator-failure mode.'''
old=r'''Figs.~\ref{fig12} and \ref{fig13} further show the control input, the derivative $\dot{h}_1(t)$, and the stochastic switching of the actuator-failure mode. The control signal remains bounded, and $\dot{h}_1(t)$ approaches zero as the state trajectories converge, which is consistent with the stabilization objective.'''
replace(old,fig12text,['R3.4'],'Example 2, interpretation of Fig. 12')
replace(r'\caption{Evolution of $\dot{h}_1(t)$ and control input $u(t)$.}',
        r'\caption{Control input $u(t)$ (blue) and membership-function derivative $\dot{h}_1(t)$ (black).}',
        ['R3.4'],'Fig. 12 caption')

old=r'''An engineering-motivated PMSM example and a numerical IT-2 fuzzy example have demonstrated the effectiveness and applicability of the developed method. Further research will extend the current IT-2 fuzzy control methodology to observer-based output feedback control, since not all system states are measurable in practical industrial applications. Secure control under more sophisticated cyberattack scenarios, such as DoS attacks, and practical network constraints, such as partially unknown Markov transition probabilities, also deserve further investigation.'''
scope=r'''The PMSM example and the numerical IT-2 fuzzy example illustrate the closed-loop responses and transmission savings. The present formulation uses state feedback, a specified bound on the deception signal, and known Markov transition rates. Its conclusions apply to this modeled setting. Future work will consider observer-based output feedback when full state measurements are unavailable, as well as DoS attacks and partially unknown Markov transition rates.'''
replace(old,scope,['R3.5'],'Conclusion, final paragraph')

# A visible gap between the paired minipages avoids captions running together.
anchor='\\end{minipage}\n\t\\begin{minipage}{0.45\\linewidth}'
n=text.count(anchor)
replace(anchor,'\\end{minipage}\\hfill\n\t\\begin{minipage}{0.45\\linewidth}',
        ['Layout'],'Paired figure spacing',n)

bib_original=(SOURCE/'ref2.bib').read_text(encoding='utf-8')
bib=(ROOT/'paper2_审稿意见'/'paper2_修改副本'/'ref2.bib').read_text(encoding='utf-8')
assert bib.startswith(bib_original)
(REV/'ref2.bib').write_text(bib,encoding='utf-8')
(REV/'paper2.tex').write_text(text,encoding='utf-8')

# Replace only the sixteen text-showing operands of the incorrect axis label.
# Existing paths, coordinates, drawing operations and other labels remain intact.
pdfmetrics.registerFont(TTFont('ReviewArial',r'C:\Windows\Fonts\arial.ttf'))
figure_edits=[]
for name in ['actuator_fault.pdf','2_actuator_fault.pdf']:
    reader=PdfReader(SOURCE/'figs'/name); page=reader.pages[0]
    cs=ContentStream(page.get_contents(),reader)
    original_ops=repr(cs.operations)
    old_ops=[(list(a),op) for a,op in cs.operations]
    start=next(i for i,(a,op) in enumerate(cs.operations) if op==b'Tj' and str(a[0])=='\x0f')
    indices=[i for i,(a,op) in enumerate(cs.operations) if i>=start and op==b'Tj'][:16]
    expected='\x0f\x10\x04\x11\x12\x13\x02\x14\x15\x05\x03\x14\x16\x04\x17\x07'
    assert ''.join(str(cs.operations[i][0][0]) for i in indices)==expected
    for i in indices: cs.operations[i]=([ByteStringObject(b'')],b'Tj')
    assert all(cs.operations[i]==old_ops[i] for i in range(len(old_ops)) if i not in indices)
    page.replace_contents(cs)
    buf=io.BytesIO(); cv=canvas.Canvas(buf,pagesize=(702,458),pageCompression=1)
    cv.setFont('ReviewArial',12); cv.translate(10.5,241.8); cv.rotate(90)
    cv.drawCentredString(0,0,'Operating modes'); cv.save(); buf.seek(0)
    page.merge_page(PdfReader(buf).pages[0])
    writer=PdfWriter();writer.add_page(page)
    with (REV/'figs'/name).open('wb') as f:writer.write(f)
    extracted=PdfReader(REV/'figs'/name).pages[0].extract_text()
    assert 'Operation' not in extracted and 'Operating modes' in extracted
    figure_edits.append(dict(file=name,ids=['R1.5'],old='Operation models',new='Operating modes',original_nonlabel_operations_unchanged=True))

for c in changes:
    c['revised_lines']=[text[:m.start()].count('\n')+1 for m in re.finditer(re.escape(c['new']),text)]
    assert c['revised_lines'],c['location']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(SOURCE/k)==v for k,v in prior['source_hashes'].items())
manifest=dict(source_hashes=prior['source_hashes'],changes=changes,figure_edits=figure_edits,new_references=prior['new_references'])
(WORK/'revision_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'paper2_修改对照.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='original/paper2.tex',tofile='paper2_修改副本/paper2.tex')),encoding='utf-8')
print(json.dumps(dict(revision=str(REV),changes=len(changes),figure_edits=2),ensure_ascii=False))
