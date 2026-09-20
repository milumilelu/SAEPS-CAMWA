"""Generate supplementary summaries from the packaged field extracts."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
R=Path(__file__).resolve().parents[1]
D=R/'data'; T=R/'tables'
S=json.loads((R/'review/recomputed_summary.json').read_text())
def n(v,d=5):
    return r'\num{'+f'{float(v):.{d}g}'+'}'
def table(name,cap,label,cols,header,rows,foot=''):
    text='\\begin{table}[!htbp]\n\\centering\\small\n\\caption{'+cap+'}\n\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+r'\\'+'\n\\midrule\n'
    text+='\n'.join(' & '.join(row)+r'\\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n'
    if foot:text+='\\par\\vspace{3pt}\\begin{minipage}{.96\\linewidth}\\footnotesize '+foot+'\\end{minipage}\n'
    text+='\\end{table}\n'; (T/(name+'.tex')).write_text(text)
ss=S['saturation']; fm=ss['fit_medians'];sm=ss['pooled_seed_medians']
table('aggregation_levels','Aggregation levels are kept consistent for both error ratios.','tab:aggregate','lrrrr',r'Units & Median $E_{\rm raw}$ & Median $E_{\rm SAEPS}$ & $R_1$ & $R_2$',[
 ['24 individual fits',n(fm['E_raw']),n(fm['E_SAEPS']),n(ss['ratio_of_fit_medians'],6),n(ss['median_fit_paired_ratio'],6)],
 ['6 pooled seed medians',n(sm['E_raw']),n(sm['E_SAEPS']),n(ss['ratio_of_seed_medians'],6),n(ss['median_ratio_of_seed_medians'],6)]],
 r'$R_1$ is the ratio of medians at the stated level. $R_2$ is the median of paired error ratios at that same level. The value $13257.2$ describes individual-fit ratios, not ratios of six seed medians. The six-unit pooling is post hoc.')
e6=pd.read_csv(D/'e6_metrics_recomputed.csv')
rows=[]
for nt in [65,129,337]:
 v=e6[e6.n_theta==nt]
 rows.append([str(nt),str(int(v.polish_iterations.min())),str(int(v.polish_iterations.max())),n(v.polish_iterations.median(),7),n(v.train_seconds.median(),6),n(v.normalized_state_gradient.max(),4)])
table('architecture_resources','Realized refinement and archived fit costs. The reported fit-time field is kept at its source scope.','tab:arch_resources','rrrrrr',r'$n_\theta$ & Min. iterations & Max. iterations & Median iterations & Median fit time (s) & Max. $g_\theta^{\rm norm}$',rows)
p=pd.read_csv(D/'e7_profile_extract.csv')
rows=[]
for sd,v in p.groupby('data_seed',sort=True):
 for _,r in v.sort_values('step',ascending=False).iterrows():
  rows.append([str(int(sd)),n(r.step,2),n(r.symmetric_curvature,7),n(r.exact_schur,7),n(r.relative_difference,5)])
text='\\begin{longtable}{rrrrr}\n\\caption{All saturation profile differences, with their local reference and archived relative discrepancy.}\\label{tab:profile_all}'+r'\\'+'\n\\toprule\n'+r'Data seed & $h$ & $D_\gamma(h;1)$ & $H_{\rm red}$ & Relative difference\\'+'\n\\midrule\\endfirsthead\n\\toprule\n'+r'Data seed & $h$ & $D_\gamma(h;1)$ & $H_{\rm red}$ & Relative difference\\'+'\n\\midrule\\endhead\n'
text+='\n'.join(' & '.join(r)+r'\\' for r in rows)+'\n\\bottomrule\n\\end{longtable}\n'
(T/'profile_all.tex').write_text(text)
anchors=[(38.1954,21.6755,.0788),(13.8935,93.6491,.1165),(25.6840,34.6225,.1349),(22.5017,51.0975,.0511),(16.3872,77.6916,.0123),(44.2325,18.9195,.0825),(34.7211,28.3335,.0535),(17.8881,50.7631,.4012),(39.8686,25.9028,.1183),(35.4153,31.4726,.1408),(16.9472,76.7475,.0384),(33.9710,26.1465,.0844),(23.9053,41.6411,.0960),(15.8882,58.0871,.0915)]
table('stress_anchors','All fourteen accepted historical exact-Hessian stress anchors, retained at the original displayed precision.','tab:stress_anchors','rrrr',r'Anchor & $H_{\rm red}$ & $E_{\rm raw}$ & $E_{\rm SAEPS}$',[[str(i+1),f'{h:.4f}',f'{raw:.4f}',f'{sa:.4f}'] for i,(h,raw,sa) in enumerate(anchors)],r'One additional planned anchor fails its center criterion. This table is transcribed from the original manuscript table, not claimed to contain unrounded source precision.')
print('Generated four supplementary tables.')
