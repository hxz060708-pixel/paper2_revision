from pathlib import Path
import re,json,hashlib,shutil,difflib

ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).resolve().parent
OUT=ROOT/'filally_22'
SOURCE=ROOT/'paper2'
REV=OUT/'paper2'
original=(SOURCE/'paper2.tex').read_text(encoding='utf-8')
patches=[]
LANG=['R1.1','R2.6','R3.4']

def add(old,new,ids,location,reason,kind='replace',anchor=None):
    if kind=='insert':
        assert original.count(anchor)==1,(location,anchor)
        start=original.index(anchor)
        end=start
    else:
        assert original.count(old)>=1,(location,old)
        for m in re.finditer(re.escape(old),original):
            patches.append(dict(start=m.start(),end=m.end(),old=old,new=new,ids=ids,location=location,reason=reason,kind=kind))
        return
    patches.append(dict(start=start,end=end,old='',new=new,ids=ids,location=location,reason=reason,kind=kind,anchor=anchor))

prior=json.loads((ROOT/'_review_work/finally_work/manifest.json').read_text(encoding='utf-8'))
for c in prior['changes']:
    if c.get('language_id') and c['language_id'] not in ['L07','L15','L16','L17']:
        add(c['old'],c['new'],LANG,c['location'],'语言润色：保留技术含义，改进语法、术语或句子结构。')

add('MFs are denoted','membership functions are denoted',LANG+['R2.4'],'Section 2.1, after Eq. (3)','避免在未单独定义时引入 MFs 缩写，与 FMFs 的表达保持清楚。')
add('In this example, the resulting IT-2 T-S fuzzy representation','In this example, the resulting IT-2 T--S fuzzy representation',LANG,'Example 1 opening','统一 Takagi--Sugeno 缩写中的连接号。')
add('Based on the IT-2 T-S fuzzy modeling approach','Based on the IT-2 T--S fuzzy modeling approach',LANG,'Example 1, model description','统一 T--S 缩写。')
add('The same actuator-failure transition rate matrix, and deception attack signal','The same actuator-failure transition rate matrix and deception attack signal',LANG,'Example 2, disturbance paragraph','删除并列主语之间多余的逗号。')
add('For the same initial state $x(0) =','For the initial state $x(0) =',LANG,'Example 2, state-response discussion','避免 same 被误解为与算例一使用相同初始状态。')
add('the resultant IT-2 fuzzy CPSs \\eqref{eq:closed_loop} is','the resultant IT-2 fuzzy system \\eqref{eq:closed_loop} is',LANG,'Definition 2.1, requirement 1','修正单复数搭配。')

add('',r'''The considered impairments affect different but interconnected parts of the closed loop. Deception attacks may corrupt the sampled information used by the controller, whereas actuator failures change the effectiveness of the control input applied to the plant. Event-triggered transmission reduces communication by retaining the last transmitted sample between releases, so the controller must also accommodate the resulting sampling error. Their simultaneous presence therefore motivates a joint analysis of closed-loop stability and disturbance attenuation under the specified attack, failure, and transmission models.

''',['R1.2'],'Introduction, after the actuator-failure paragraph','分别解释三类机制，并说明它们通过同一闭环共同影响稳定性和抗扰性能。','insert','Lyapunov--Krasovskii functional (LKF) techniques')

add('',r'''Recent studies provide closely related developments under different modeling and control settings. Liu et al.\ \cite{liuTorusEventBased2025} investigated discrete-time IT-2 fuzzy systems under deception attacks using a two-threshold torus-event-triggering protocol and sliding-mode control. Chandrasekar et al.\ \cite{chandrasekarAdaptiveEvent2026} considered adaptive event-triggered asynchronous control of uncertain IT-2 fuzzy Markov jump systems under deception attacks, with a hidden Markov model describing the plant--controller mode mismatch. The attack/failure combination has also been studied: Chen et al.\ \cite{chenProbabilisticEventTriggeredPolicy2023} addressed extended dissipative finite-time control of Markov jump systems under cyberattacks and actuator failures using a probabilistic event-triggered policy. These studies connect communication scheduling, information security, and actuator reliability. The present formulation instead concerns continuous-time IT-2 fuzzy CPSs with Bernoulli deception attacks and Markov-type actuator effectiveness, and uses membership-function derivative signs to organize regional controller gains and triggering weight matrices within a two-sided FMF-dependent looped-functional synthesis. This comparison identifies the particular formulation and design structure studied here; it does not imply that joint attack/failure modeling or adaptive event triggering is itself new.

''',['R1.3','R2.1','R3.7'],'Introduction, immediately before the contribution paragraph','补充两篇已核实的近期文献，并与原有联合攻击/故障文献比较；不作未经文献支持的排他性创新声明。','insert','Building on the above discussion, this study addresses adaptive event-triggered')

old='Building on the above discussion, this study addresses adaptive event-triggered\n$\\mathrm{H}_\\infty$ control for IT-2 fuzzy CPSs affected by stochastic deception\nattacks and Markov-type actuator failures. The principal contributions are fourfold:'
new=r'''The above discussion motivates an integrated design: the attack and actuator-failure models specify the closed-loop setting, the adaptive triggering mechanism determines when measurements are transmitted, and the membership-function derivative signs select regional constraints for the LMI-based synthesis. The main contributions are organized around these connected roles as follows:'''
add(old,new,['R3.1']+LANG,'Introduction, contribution-list transition','明确模型、触发机制、分区与 LMI 综合之间的衔接。')
items=[
('A unified adaptive event‑triggered closed‑loop model is established for IT‑2 fuzzy CPSs under concurrent cyber attacks and actuator failures.',r'A unified closed-loop model combines an IT-2 fuzzy plant, an adaptive event-triggering mechanism, Bernoulli deception attacks, and Markov-type actuator failures. It specifies how transmission decisions, corrupted feedback, and actuator effectiveness enter the dynamics.'),
('An adaptive triggering scheme is proposed, with its threshold updated according to the state error. By adjusting the threshold online according to real-time state-error information, the proposed mechanism reduces redundant transmissions while maintaining the desired control performance.',r'An adaptive event-triggering mechanism updates its threshold using the sampling error. This component regulates transmission decisions and is included in the stability and performance analysis, thereby linking communication use to the control design.'),
('A region-dependent fuzzy control scheme is developed by exploiting the sign information of the membership-function derivatives. The resulting region partition enables the control and triggering parameters to be jointly designed for each operational region.',r'A region-dependent fuzzy control scheme uses membership-function derivative signs to partition the operational regions. The associated matrix inequalities incorporate this sign information into the joint design of controller gains and event-triggering weight matrices.'),
('A two-sided FMF-dependent looped functional is formulated to incorporate state information from both subintervals of each sampling period. This construction reduces conservatism and yields tractable LMI-based $\\mathrm{H}_\\infty$ stability and synthesis conditions.',r'A two-sided FMF-dependent looped functional incorporates membership information and state information from both parts of a sampling interval. It provides the basis for sufficient stability and prescribed $\mathrm{H}_\infty$ performance conditions and the subsequent LMI-based synthesis.')]
for i,(old,new) in enumerate(items,1):add(old,new,['R3.1']+LANG,f'Introduction, contribution {i}','各条贡献分别说明一个方法组成及其作用，避免内容重复和未经比较验证的优势表述。')

add('Here, $\\sigma>0$ governs the convergence speed of $\\delta(t)$.','Here, $\\sigma>0$ sets the equilibrium threshold $1/\\sigma$ and influences the adaptive response.',['R1.4'],'Section 2.2, after Eq. (6)','参数不仅影响动态变化，还决定平衡阈值。')
add('When the triggering error is small, the update of $\\delta(t)$ is weakened, thereby avoiding unnecessary fluctuations of the threshold and reducing redundant data transmissions.',r'''When the triggering error is small, the update of $\delta(t)$ is weakened. For $\delta(t)>0$ and nonzero triggering error, \eqref{eq:adaptive_law} gives an increasing threshold when $\delta(t)<1/\sigma$ and a decreasing threshold when $\delta(t)>1/\sigma$; its derivative is zero when the error is zero or the threshold equals $1/\sigma$. Thus, the equilibrium provides a reference value, rather than implying the same direction of evolution for every initial threshold. For fixed sampled state, error, and weighting matrix, a larger threshold makes the inequality in \eqref{eq:Event_TR_1} harder to satisfy. Actual release instants depend on the joint evolution of the sampled state, sampling error, and threshold, and cannot be inferred from the equilibrium value alone.''',['R1.4'],'Remark 2.2, final sentence','分别说明阈值位于平衡值两侧、误差为零时的变化，以及触发不等式的作用。')

add('',r'''The deception process and actuator failures enter the feedback path at different points. At a release instant, \eqref{eq:deception_attacks} selects the transmitted state or its falsified replacement as the controller input. The fuzzy gains act on this received signal, and the mode-dependent matrix $F_i$ describes the effectiveness of the actuator applying the resulting control action. Substitution therefore produces the term $B_mF_iK_n[(1-\theta(t_kh))x(t_kh)+\theta(t_kh)f(x(t_kh))]$ in \eqref{eq:closed_loop}. The event-triggering mechanism determines the release times and hence which sampled information is used between releases.

''',['R2.2'],'Section 2.4, immediately before the paragraph leading to Eq. (15)','按采样信息、攻击替换、控制增益、执行器有效性的顺序解释模型代入。','insert','By substituting the controller \\eqref{eq:local_controller}')

add('',r'''Here, $H_m$ denotes an interval, its endpoints $\underline h_m$ and $\overline h_m$ are the lower and upper firing strengths, and $h_m$ is the scalar normalized weight used in the blended model. The functions $\underline l_m$ and $\overline l_m$ are the weighting coefficients in the stated construction of $h_m$; they are distinct from the lower and upper membership functions $\underline\mu_{G_v^m}$ and $\overline\mu_{G_v^m}$.

''',['R2.4'],'Section 2.1, after the normalized-weight definitions','解释区间、端点、归一化权重、混合系数之间的区别，不改变定义或约束。','insert','\\begin{rem}\n\tFig.~\\ref{fig1}')
add('For notational convenience, let $i = r(t)$.',r'For notational convenience, let $i=r(t)$ denote the current actuator-failure mode. The process $r(t)$ is distinct from the fixed number $r$ of fuzzy rules.',['R2.4']+LANG,'Section 2.4, after Eq. (12)','区分故障模式过程 r(t) 与模糊规则数 r。')
add('',r'''In this decomposition, $F_{i0}$ is the diagonal midpoint matrix of the actuator effectiveness intervals, $F_{i1}$ contains their half-widths, and $V_i$ contains the bounded normalized deviations. The subscript $i$ identifies the actuator mode and does not index a fuzzy rule or a derivative-sign region.

''',['R2.4'],'Section 2.4, after the definition of F_i0 F_i1 V_i','澄清矩阵各部分与模式下标的含义。','insert','The stochastic parameter $r(t)$ evolves')
add('',r'''Here, $K_n^l$ is the gain for fuzzy rule $n$ in derivative-sign region $\mathcal V_l$, whereas $F_i$ depends on the actuator-failure mode $i$. Thus, the region index $l$, the fuzzy-rule index $n$, and the actuator-mode index $i$ have different roles. In the numerical examples, $K_{ln}$ denotes the same regional gain as $K_n^l$, and $S_l$ denotes $S^l$.

''',['R2.4'],'Section 2.4, immediately after Eq. (17)','明确区域、规则和故障模式下标，并解释算例中 K_ln 与 K_n^l 的对应。','insert','Corresponding to the switching fuzzy controller,')

add('',r'''For controller synthesis, the sign pattern defining $\mathcal V_l$ determines which inequalities are collected in $\mathcal C_l$ and imposed together with the LMIs. For example, when $\dot h_v\leq0$, the condition $P_{iv}-P_{ir}\geq0$ makes $\dot h_v(P_{iv}-P_{ir})$ negative semidefinite; when $\dot h_v>0$, the reversed matrix inequality has the same effect. The constraint on $R_{2v}-R_{2r}$ has the opposite orientation because \eqref{dot_small_0} requires $\dot R_{2h}\geq0$. Applying these sign choices for every $v$ implements the derivative constraints in the analysis and in the transformed synthesis conditions. The resulting regional gains and triggering matrices are then selected according to the active sign pattern.

''',['R1.5'],'Remark 2.4, after the regional-controller and triggering definitions','用 P 的乘积符号与 R2 的相反符号说明区域约束如何进入综合，不更改定理条件。','insert','\\begin{Lem}\\label{lem2}')

add('',r'''The two objectives in Theorem~\ref{thm1} correspond to the two requirements of Definition~\ref{Def1}. Stability concerns the unforced closed loop with $w(t)=0$. The prescribed $\mathrm H_\infty$ level concerns the expected output-energy bound relative to the disturbance energy for nonzero square-integrable disturbances under the zero-initial-condition convention of that definition. The terms involving $C$ and $\gamma$ in the matrix inequalities encode this output--disturbance performance requirement within the same sufficient-condition framework. These conditions provide a certificate under the stated assumptions; LMI infeasibility alone does not establish instability.

''',['R1.7'],'Section 3, immediately after Theorem 3.1 and its proof','对照 Definition 2.1 区分无扰稳定性与零初值能量增益要求；只解释原文保证，不增加推导。','insert','\\begin{rem}\nThe construction of the two-sided')

old='Furthermore, this methodological framework is not restricted to the current system and can be extended to other networked or sampled-data systems.'
new=r'''The factors $d_1(t)$ and $d_2(t)$ measure the elapsed and remaining parts of the candidate sampling interval $[t_k^j,t_k^{j+1})$. In $V_3$, the two integrals use the state derivative over the portions before and after the current time; $V_2$ and $V_4$ combine endpoint states, the current state, and interval integrals through the augmented vectors. The endpoint property $V_p(t_k^j)=V_p(t_k^{j+1})=0$ for $p=2,3,4$ permits these auxiliary terms to describe intersample evolution while preserving the endpoint matching used in the analysis. The FMF-weighted matrices retain the dependence on the active fuzzy memberships, and the regional constraints control the signs of their derivatives. Finally, $V_5$ incorporates the adaptive threshold. The future-endpoint quantities are used in the analysis and are not additional measurements required by the implemented controller. These choices make sampling and membership information available to the sufficient-condition derivation without asserting a quantified advantage over every alternative functional.'''
add(old,new,['R2.3'],'Remark 3.1, final sentence','逐项对应 d1/d2、V2/V3/V4、FMF 权重与 V5，区分分析中的未来端点和实际实现。')

add('This section considers an engineering-motivated example and a numerical simulation study to assess the effectiveness and applicability of the developed control scheme.',r'''The following examples illustrate the controllers obtained from Theorem~\ref{thm3} under the specified parameter settings. Example~\ref{exm1} uses a normalized PMSM benchmark to provide an engineering context and compares transmission counts for several values of $\sigma$. Example~\ref{exm2} uses different system matrices and membership functions with a fixed parameter setting. In each case, the state plots describe the observed closed-loop response, the control and derivative plots illustrate the regional control action, and the threshold and release plots describe communication activity. These complementary illustrations connect the synthesis conditions to simulated behavior; they do not independently establish the theorem's guarantees for all admissible disturbances or switching realizations.''',['R2.5','R3.2','R3.6'],'Section 4, opening paragraph','说明理论到算例的衔接、两例分工与每类图的证据范围。')
add('It can be observed that the open-loop system exhibits evident oscillatory behavior, whereas the proposed controller drives all system states to equilibrium despite deception attacks and stochastic actuator failures.',r'''The uncontrolled trajectories exhibit pronounced oscillations, whereas the controlled trajectories settle near the origin after the initial transient. Small residual oscillations are visible under the imposed sinusoidal disturbance $w(t)=0.5\sin(t)$. This plot illustrates disturbance-affected regulation over the simulated interval, rather than exact asymptotic convergence under a persistent input.''',['R2.5','R3.6'],'Example 1, state-response discussion','图中存在残余振荡，按已展示轨迹描述；不把持续正弦扰动下的曲线当作零扰动渐近稳定证明。')
add('Its bounded transient behavior and convergence to zero indicate that the membership-function derivative information can be effectively exploited in the region-dependent piecewise control design.',r'Its sign supplies the regional selection information, while its transient evolution describes the changing membership weights. The plot illustrates this signal along the simulated trajectory; the validity of the regional design follows from the analytical conditions.',['R2.5','R3.5','R3.6'],'Example 1, membership-derivative figure discussion','说明导数图用于区域选择而非单幅图证明控制设计。')

add('These results confirm that the proposed AETM significantly reduces the number of data transmissions.',r'The reported counts quantify the reduction in transmitted packets for these simulation settings.',['R1.6'],'Example 1, paragraph before Table 1','限定数值结果适用范围。')
add('Therefore, the results of Example~\\ref{exm1} confirm that the co-design method achieves closed-loop stability while effectively reducing the communication burden.',r'''Table~\ref{tab:sigma_effect} reports 400 candidate samples for the time-triggered baseline, in which every candidate is transmitted. The saving rate is $(1-N_{\mathrm{ET}}/N_{\mathrm{TT}})\times100\%$, where $N_{\mathrm{ET}}$ and $N_{\mathrm{TT}}$ count transmissions over the same simulation interval. As $\sigma$ increases from 4 to 20, the AETM count rises from 85 to 164 and the saving rate falls from $78.75\%$ to $59.00\%$. Over the same parameter range, the equilibrium threshold $1/\sigma$ decreases from 0.25 to 0.05. With sampled state, error, and weighting matrix fixed, a smaller threshold makes \eqref{eq:Event_TR_1} easier to satisfy. This explains the direction of the observed trend, while the actual counts also depend on the state trajectory, the adaptive-threshold evolution, and the resulting design matrices. The table therefore illustrates a communication trade-off under the tested settings, not a universal monotonicity guarantee. Together with the state-response plots, it illustrates regulated behavior with fewer transmissions in this example.''',['R1.6','R2.5','R3.6'],'Example 1, after Table 1','给出基线、节省率公式和参数趋势解释，不添加实验或普遍保证。')

old='For the same initial state $x(0) = \\begin{bmatrix} -3, 0.5, -2 \\end{bmatrix}^{\\mathrm{T}}$, Figs.~\\ref{fig10} and \\ref{fig11} compare the responses under open-loop and closed-loop conditions. The open-loop system exhibits a clear divergent behavior, whereas the proposed controller maintains system stability despite deception attacks and Markov-type actuator failures.'
# The first phrase is separately corrected above; replace only the second sentence here.
add('The open-loop system exhibits a clear divergent behavior, whereas the proposed controller maintains system stability despite deception attacks and Markov-type actuator failures.',r'The uncontrolled trajectories depart from the origin over the plotted interval, whereas the controlled trajectories approach it. This comparison illustrates the response of the second model under the stated attack and failure setting.',['R2.5','R3.6']+LANG,'Example 2, state-response discussion','描述曲线实际显示的变化，并把结论限制为选定仿真。')
add('Figs.~\\ref{fig12} and \\ref{fig13} further show the control input, the derivative $\\dot{h}_1(t)$, and the stochastic switching of the actuator-failure mode. The control signal remains bounded, and $\\dot{h}_1(t)$ approaches zero as the state trajectories converge, which is consistent with the stabilization objective.',r'''In Fig.~\ref{fig12}, the blue curve is the control input $u(t)$ and the black curve is the membership-function derivative $\dot h_1(t)$. With two fuzzy rules, $\dot h_2(t)=-\dot h_1(t)$, so the sign of the plotted derivative identifies the corresponding regional constraint set: $\mathcal C_1$ for $\dot h_1(t)\leq0$ and $\mathcal C_2$ for $\dot h_1(t)>0$. The control-input trajectory shows the transient actuation and its subsequent decay as the states in Fig.~\ref{fig11} approach the origin. The two curves are displayed together to relate the control action to the membership dynamics, not to compare their magnitudes as a common physical quantity. The plot does not attribute every input variation solely to a regional switch, since the control law also depends on the received sample, memberships, and actuator mode. Fig.~\ref{fig13} shows the actuator-failure switching associated with this simulation.''',['R3.3','R2.5','R3.5'],'Example 2, Figure 12 discussion','逐条解释蓝色控制输入、黑色导数、两区域符号规则及与状态响应的关系。')
add('only 65 transmissions are triggered out of 400 candidate sampling instants, yielding a communication saving rate of $83.79\\%$. These results demonstrate that the proposed co-design remains effective for a different IT-2 fuzzy model and offers the same communication-efficiency advantage.',r'''65 transmissions are triggered out of 400 candidate sampling instants, giving $(1-65/400)\times100\%=83.75\%$ using the same time-triggered baseline. The state trajectories illustrate the achieved response, the input curve illustrates the control action, and the threshold and release plots characterize the transmission process. These are numerical observations for the selected configuration. The theoretical stability and $\mathrm H_\infty$ statements are those of the theorems under their assumptions; the finite plotted trajectories and packet counts do not by themselves verify the energy inequality for every admissible disturbance.''',['R2.5','R3.6']+LANG,'Example 2, final discussion','按已有计数纠正百分比，明确不同图的作用与理论保证的区别。')

add('\\caption{Evolution of $\\dot{h}_1(t)$ and control input $u(t)$.}',r'\caption{\revdel{Evolution of $\dot{h}_1(t)$ and control input $u(t)$.}\revadd{Control input $u(t)$ (blue) and membership-function derivative $\dot h_1(t)$ (black) in Example~\ref{exm2}.}}',['R3.3','R3.5'],'Figure 12 caption','图注与曲线颜色、数量和算例对应。',kind='special')
add('\\caption{Evolution of the actuator fault mode $r(t)$.}',r'\caption{\revdel{Evolution of the actuator fault mode $r(t)$.}\revadd{Actuator-failure mode $r(t)$.}}',['R3.5'],'Figures 7 and 13 captions','统一术语并缩短图注，配合图内坐标文字更正。',kind='special')
add('\\end{minipage}\n\t\\begin{minipage}{0.45\\linewidth}','\\end{minipage}\\hfill\n\t\\begin{minipage}{0.45\\linewidth}',['R3.5'],'Paired-figure spacing','添加水平间隔，防止左右图注贴在一起；排版命令本身不产生文字。',kind='layout')

add('',r'''All horizontal axes in the simulation plots use time in seconds. Example~\ref{exm1} uses the normalized PMSM representation cited above; its plotted state and input values are in model coordinates and are not assigned additional SI units here. The second example uses the numerical model coordinates as specified. The threshold $\delta(t)$ and actuator-mode index $r(t)$ are dimensionless, whereas release intervals are measured in seconds. Legends identify the state components and the two quantities combined in Fig.~\ref{fig12}.

''',['R3.5'],'Section 4, immediately before Example 1','说明时间、阈值、模式、触发间隔和归一化模型量的单位，不擅自给数值模型添加物理量纲。','insert','\\begin{example}\\label{exm1}')

for c in prior['changes']:
    if c.get('language_id')=='L17':add(c['old'],c['new'],LANG,'Conclusion, first paragraph','压缩冗长被动句，保持与方法和定理相符。')
old='An engineering-motivated PMSM example and a numerical IT-2 fuzzy example have demonstrated the effectiveness and applicability of the developed method. Further research will extend the current IT-2 fuzzy control methodology to observer-based output feedback control, since not all system states are measurable in practical industrial applications. Secure control under more sophisticated cyberattack scenarios, such as DoS attacks, and practical network constraints, such as partially unknown Markov transition probabilities, also deserve further investigation.'
new=r'''The PMSM and numerical IT-2 fuzzy examples illustrate closed-loop responses and transmission savings under the selected settings. The present analysis uses state feedback, Bernoulli-modeled deception attacks satisfying the specified signal bound, and Markov-type actuator failures with known transition rates. Its theoretical conclusions apply under these assumptions. Observer-based output feedback is a future direction for applications without full-state measurements. DoS attacks and partially unknown Markov transition rates require additional modeling and analysis and are also left for future work.'''
add(old,new,['R2.7','R3.6']+LANG,'Conclusion, final paragraph','区分当前状态反馈与攻击/故障假设下的结果及尚未完成的扩展。')

patches.sort(key=lambda x:(x['start'],x['end']))
for i,p in enumerate(patches):
    p['id']=f'M{i+1:02d}'
    p['original_line']=original[:p['start']].count('\n')+1
    p['original_end_line']=original[:p['end']].count('\n')+1
    if i:assert patches[i-1]['end']<=p['start'],(patches[i-1]['location'],p['location'])

assert not OUT.exists(),'New output folder already exists; do not overwrite.'
OUT.mkdir()
for i in range(1,4):(OUT/f'审稿意见{i}').mkdir()
shutil.copytree(SOURCE,REV)
config=r'''
% Revision convention: red = retained deleted text; green = inserted text.
% Define \ReviewClean before inputting this file to accept the changes.
\definecolor{revisionred}{RGB}{190,0,0}
\definecolor{revisiongreen}{RGB}{0,115,35}
\newif\ifreviewmarkup
\ifdefined\ReviewClean\reviewmarkupfalse\else\reviewmarkuptrue\fi
\long\def\revdel#1{\ifreviewmarkup{\color{revisionred}\hypersetup{linkcolor=revisionred,citecolor=revisionred}#1}\fi}
\long\def\revadd#1{{\ifreviewmarkup\color{revisiongreen}\hypersetup{linkcolor=revisiongreen,citecolor=revisiongreen}\fi#1}}
\newcommand{\revfigure}[1]{\ifreviewmarkup\includegraphics[width=0.9\textwidth]{figs/#1}\else\includegraphics[width=0.9\textwidth]{figs_clean/#1}\fi}
\DeclareUnicodeCharacter{2011}{-}
'''

def accept(s):
    # These special snippets contain balanced braces; parse the two wrappers.
    out='';i=0
    while i<len(s):
        m=re.match(r'\\rev(del|add)\{',s[i:])
        if not m:out+=s[i];i+=1;continue
        k=i+m.end();start=k;depth=1
        while depth:
            if s[k]=='{' and (k==0 or s[k-1]!='\\'):depth+=1
            elif s[k]=='}' and (k==0 or s[k-1]!='\\'):depth-=1
            k+=1
        if m.group(1)=='add':out+=s[start:k-1]
        i=k
    return out

tracked='';clean='';cursor=0
for p in patches:
    tracked+=original[cursor:p['start']];clean+=original[cursor:p['start']]
    if p['kind'] in ['special','layout']:
        render=p['new'];replacement=accept(p['new'])
        p['new']=replacement
    elif p['kind']=='insert':render='\\revadd{'+p['new'].rstrip()+'}\n\n';replacement=p['new']
    else:
        render='\\revdel{'+p['old']+'}\\revadd{'+p['new']+'}'
        replacement=p['new']
    p['marked_line']=tracked.count('\n')+1
    p['clean_line']=clean.count('\n')+1
    tracked+=render;clean+=replacement
    cursor=p['end']
tracked+=original[cursor:];clean+=original[cursor:]
# Insert setup after packages and before the document begins.
tracked=tracked.replace('\\begin{document}',config+'\n\\begin{document}',1)
offset=config.count('\n')+1
for p in patches:p['marked_line']+=offset

# Keep the original vector figures, including the deleted label, in the marked edition.
for name in ['actuator_fault.pdf','2_actuator_fault.pdf']:
    old=r'\includegraphics[width=0.9\textwidth]{figs/'+name+'}'
    tracked=tracked.replace(old,r'\revfigure{'+name+'}')

(REV/'paper2.tex').write_text(tracked,encoding='utf-8')
(REV/'paper2_clean.tex').write_text('\\def\\ReviewClean{1}\n\\input{paper2.tex}\n',encoding='utf-8')
(WORK/'accepted_content.tex').write_text(clean,encoding='utf-8')
bib0=(SOURCE/'ref2.bib').read_text(encoding='utf-8')
bib=(ROOT/'finally/paper2_修改副本/ref2.bib').read_text(encoding='utf-8')
assert bib.startswith(bib0)
(REV/'ref2.bib').write_text(bib,encoding='utf-8')
(REV/'figs_clean').mkdir()
for name in ['actuator_fault.pdf','2_actuator_fault.pdf']:
    shutil.copy2(ROOT/'finally/paper2_修改副本/figs'/name,REV/'figs_clean'/name)
sources={str(p.relative_to(SOURCE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.rglob('*') if p.is_file()}
manifest=dict(source_hashes=sources,patches=patches,bib_addition=bib[len(bib0):],new_refs=prior['new_references'],figure_edits=[dict(file=n,old='Operation models',new='Operating modes',ids=['R3.5']) for n in ['actuator_fault.pdf','2_actuator_fault.pdf']],config=config)
(WORK/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'全部修改精确记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'paper2_修改对照.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),clean.splitlines(True),fromfile='original/paper2.tex',tofile='accepted/paper2.tex')),encoding='utf-8')
print(json.dumps({'output':str(OUT),'changes':len(patches),'comments':21},ensure_ascii=False))
