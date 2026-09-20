from pathlib import Path
import json, numpy as np, pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data';T=R/'tables';T.mkdir(exist_ok=True)
S=json.loads((R/'review/recomputed_summary.json').read_text())
h=pd.read_csv(D/'historical_scalar.csv');e3=pd.read_csv(D/'e3_heldout_corrected.csv');seed=pd.read_csv(D/'e3_pooled_seed_summary.csv');e6=pd.read_csv(D/'e6_metrics_recomputed.csv')
def n(x,d=4):return r'\num{'+format(float(x),f'.{d}g')+'}'
def table(name,caption,label,cols,header,rows,foot=''):
 s='\\begin{table}[!htbp]\n\\centering\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\small\n\\setlength{\\tabcolsep}{5pt}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+r' \\'+'\n\\midrule\n'+'\n'.join(' & '.join(row)+r' \\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n'
 if foot:s+='\\par\\vspace{3pt}\\begin{minipage}{.98\\linewidth}\\footnotesize '+foot+'\\end{minipage}\n'
 s+='\\end{table}\n';(T/(name+'.tex')).write_text(s)
rows=[]
for name in ['Burgers','Allen-Cahn']:
 v=S[name];rows.append([name.replace('-','--'),f"{v['n_valid']}/{v['n_planned']}",str(v['n_valid']),n(v['median_E_raw'],5),n(v['median_E_SAEPS'],4),f"$2^{{-{v['n_valid']}}}$"])
ss=S['saturation'];rows.append(['Saturation','$24/24$ fits','$6$ data seeds',n(ss['pooled_seed_medians']['E_raw'],5),n(ss['pooled_seed_medians']['E_SAEPS'],4),'$2^{-6}$'])
table('main_results','State-relaxed curvature is closer to the matched objective-Hessian Schur reference.','tab:main_results','lccccc',r'Problem & Valid/planned & Summary units & Median $E_{\rm raw}$ & Median $E_{\rm SAEPS}$ & $p$',rows,r'Burgers and Allen--Cahn summarize valid checkpoints. Saturation summarizes six data-seed medians, each pooling four fits. The cross-noise pooling and its sign test are post hoc. All $24$ saturation fits improve individually. No cohorts are pooled for inference.')
rows=[['Burgers',n(27.75),n(.1563),n(.07503228596679316),n(.00308)],['Allen--Cahn',n(19.9472),n(.2903),n(.2785667026005181),n(.00234)],['Saturation',n(e3.E_fix.median()),n(e3.E_GN_fix.median()),n(e3.E_SAEPS.median()),n(e3.E_relax.median())]]
table('mechanism','The state-freezing term dominates the tested error budgets.','tab:mechanism','lrrrr',r'Problem & $E_{\rm fix}$ & $E_{\rm GN,fix}$ & $E_{\rm SAEPS}$ & $E_{\rm relax}$',rows,r'All entries are medians over valid fits: $12$, $9$, and $24$, respectively. The first three metrics share the reduced-curvature denominator. $E_{\rm relax}$ is normalized by the exact relaxation correction, not by the final curvature. Historical decomposition values are retained at their archived precision.')
rows=[]
for a,ni in [('2_16_1',65),('2_32_1',129),('2_16_16_1',337)]:
 v=e6[e6.architecture==a];rows.append([a.replace('_','--'),str(ni),'6/6',n(v.E_raw.median(),5),n(v.E_SAEPS.median()),n(v.kappa_relative_error.median())])
table('architecture','The reduction improves all paired fits across three trained architectures.','tab:architecture','lccrrr',r'Architecture & $n_\theta$ & Valid & Median $E_{\rm raw}$ & Median $E_{\rm SAEPS}$ & $\kappa$ error',rows,r'Each architecture uses three data seeds and two initializations at noise level $0.02$. The six base fits are reused from the saturation cohort; only twelve fits are additional. Coefficient errors describe the fitted networks and are not caused by post-training SAEPS evaluation.')
# Supplementary seed and complete-fit tables.
table('e3_seeds','Saturation results by data seed under the reported four-fit pooling rule.','tab:e3_seeds','lrrr',r'Data seed & $E_{\rm raw}$ & $E_{\rm SAEPS}$ & $E_{\rm GN,fix}$',[[str(int(v.data_seed)),n(v.E_raw,6),n(v.E_SAEPS,5),n(v.E_GN_fix,5)] for _,v in seed.iterrows()],r'The median over four fits is an explicitly post-hoc cross-noise summary. It is not the same as taking a median after a within-noise averaging step.')
# Long tables for audit records.
def longtable(name,caption,label,cols,header,rows):
 s='\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+r'}\\'+'\n\\toprule\n'+header+r'\\'+'\n\\midrule\\endfirsthead\n\\toprule\n'+header+r'\\'+'\n\\midrule\\endhead\n'+'\n'.join(' & '.join(row)+r'\\' for row in rows)+'\n\\bottomrule\n\\end{longtable}\n';(T/(name+'.tex')).write_text(s)
longtable('e3_all','All saturation held-out fits. Init. A/B denote 926001/926002.','tab:e3_all','rrcrrr',r'Data seed & Noise & Init. & $E_{\rm raw}$ & $E_{\rm SAEPS}$ & $E_{\rm GN,fix}$',[[str(int(v.data_seed)),f'{v.noise_level:g}','A' if v.initialization_seed==926001 else 'B',n(v.E_raw,5),n(v.E_SAEPS,5),n(v.E_GN_fix,5)] for _,v in e3.iterrows()])
rows=[]
for name,start,end in [('Burgers',55,69),('Allen--Cahn',75,84)]:
 co=name.replace('--','-');q=h[h.cohort==co].set_index('seed')
 for si in range(start,end+1):
  if si in q.index:r=q.loc[si];row=[name,str(si),'valid',n(r.E_raw,6),n(r.E_SAEPS,6)]
  else:row=[name,str(si),'invalid','--','--']
  rows.append(row)
longtable('historical_all','Complete historical scalar cohorts. Invalid centers remain in the planned denominator.','tab:historical_all','llcrr',r'Problem & Seed & Status & $E_{\rm raw}$ & $E_{\rm SAEPS}$',rows)
c=pd.read_csv(D/'e8_timing_summary.csv');rows=[]
for sd in [215,224]:
 for alpha in [1e-8,1e-6,1e-4,1e-2]:
  for method in ['Dense','CG','Scaled LSQR']:
   v=c[(c.seed==sd)&np.isclose(c.alpha,alpha,rtol=1e-10,atol=0)&(c.method==method)].iloc[0]
   rows.append([str(sd),n(alpha,1),method,n(v.solve_seconds,5),n(v.reported_total_seconds,5),'reference' if method=='Dense' else n(v.accuracy_vs_dense,4)])
longtable('cost_all','Matched-damping costs for both archived centers. Medians of three repeats.','tab:cost_all','rllrrl',r'Seed & $\alpha$ & Method & Solve (s) & Reported total (s) & Dense difference',rows)
# Numeric macros are regenerated, not hand-edited in prose.
vals={'BurgersError':S['Burgers']['median_E_SAEPS'],'AllenError':S['Allen-Cahn']['median_E_SAEPS'],'SaturationError':ss['pooled_seed_medians']['E_SAEPS'],'SaturationPercent':100*ss['pooled_seed_medians']['E_SAEPS'],'SaturationRaw':ss['pooled_seed_medians']['E_raw'],'SaturationFitError':e3.E_SAEPS.median(),'SaturationGNError':e3.E_GN_fix.median(),'SaturationRelaxError':e3.E_relax.median(),'GainRatioMaximum':e6.gain_ratio.max(),'DeepError':e6[e6.n_theta==337].E_SAEPS.median(),'WideError':e6[e6.n_theta==129].E_SAEPS.median(),'BaseError':e6[e6.n_theta==65].E_SAEPS.median()}
(R/'numbers.tex').write_text('% Generated by src/build_tables.py\n'+'\n'.join('\\newcommand{\\'+k+'}{'+n(v,4)+'}' for k,v in vals.items())+'\n')
print('Generated main and supplementary tables.')
