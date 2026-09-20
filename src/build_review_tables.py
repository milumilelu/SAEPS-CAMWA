"""Final editorial tables; read-only aggregation of packaged historical records.

Run after build_tables.py and build_supplement_tables.py. This script changes no
input record and adds empirical quartiles, not a new experiment or calibrated CI.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D, T, V = ROOT/'data', ROOT/'tables', ROOT/'review'

def num(value, digits=4):
    return format(float(value), f'.{digits}g')

def tab(name, caption, label, cols, headers, rows, note=''):
    text = ('\\begin{table}[!htbp]\n\\centering\n\\caption{'+caption+'}\n'
            '\\label{'+label+'}\n\\small\n\\setlength{\\tabcolsep}{4pt}\n'
            '\\begin{tabular}{'+cols+'}\n\\toprule\n')
    text += ' & '.join('{'+h+'}' for h in headers)+r' \\'+'\n\\midrule\n'
    text += '\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    text += '\n\\bottomrule\n\\end{tabular}\n'
    if note:
        text += '\\par\\vspace{3pt}\\begin{minipage}{.98\\linewidth}\\footnotesize '+note+'\\end{minipage}\n'
    (T/(name+'.tex')).write_text(text+'\\end{table}\n', encoding='utf-8')

h = pd.read_csv(D/'historical_scalar.csv')
s = pd.read_csv(D/'e3_pooled_seed_summary.csv')
e = pd.read_csv(D/'e3_heldout_corrected.csv')
a = pd.read_csv(D/'e6_metrics_recomputed.csv')
summary=json.loads((V/'recomputed_summary.json').read_text())
rows=[]
for name, plan in [('Burgers',15),('Allen-Cahn',10)]:
    x=h.loc[h.cohort.eq(name)]
    rows.append([name.replace('-','--'),f'{len(x)}/{plan}',str(len(x)),num(x.E_raw.median(),6),f"{x.E_SAEPS.median():.4f}",f"{2**(-len(x)):.2e}"])
rows.append(['Saturation','24/24 fits','6 seeds',num(s.E_raw.median(),6),f'{s.E_SAEPS.median():.6f}',f'{2**-6:.4e}'])
tab('main_results','State-relaxed curvature improves the matched exact-Hessian Schur comparison.',
    'tab:main_results',r'lcc S[table-format=2.4] S[table-format=1.6] S[table-format=1.4e-1,scientific-notation=true]',
    ['Problem','Valid/planned','Units',r'Median $E_{\rm raw}$',r'Median $E_{\rm SAEPS}$',r'$p$'],rows,
    r'Errors are dimensionless. Historical units are accepted checkpoints. Saturation units are six data-seed medians, each pooling four dependent fits. All 24 saturation fits improve individually. Values of $p$ are exact, one-sided sign tests under $H_0:\Pr(D>0\mid D\ne0)=1/2$; no ties occur. They are unadjusted for multiplicity. Saturation cross-noise pooling and its seed-level test are post hoc. Failed cases remain in planned-cohort counts, not in numerical-error summaries.')
rows=[['Burgers',27.75,.1563,.07503228596679316,.00308],['Allen--Cahn',19.9472,.2903,.2785667026005181,.00234],['Saturation',e.E_fix.median(),e.E_GN_fix.median(),e.E_SAEPS.median(),e.E_relax.median()]]
tab('mechanism','The state-freezing term dominates the observed error budgets.','tab:mechanism',
    r'l S[table-format=2.4] S[table-format=1.6] S[table-format=1.6] S[table-format=1.3e-1,scientific-notation=true]',
    ['Problem',r'$E_{\rm fix}$',r'$E_{\rm GN,fix}$',r'$E_{\rm SAEPS}$',r'$E_{\rm relax}$'],
    [[r[0]]+[num(x,4) for x in r[1:]] for r in rows],
    r'Entries are medians over 12, 9, and 24 accepted fits, respectively. The first three errors share the reduced-curvature denominator. The correction error $E_{\rm relax}$ uses $|C_{\rm relax}^{\rm exact}|+10^{-8}$. Historical decomposition values retain their archived precision; the two normalizations are not interchangeable.')
rows=[]
for arch,nth in [('2_16_1',65),('2_32_1',129),('2_16_16_1',337)]:
    x=a.loc[a.architecture.eq(arch)]
    rows.append([arch.replace('_','--'),nth,'6/6',num(x.E_raw.median(),5),num(x.E_SAEPS.median(),4),num(x.kappa_relative_error.median(),4)])
tab('architecture','The advantage persists across paired, trained architectures.','tab:architecture',
    r'l S[table-format=3.0] c S[table-format=2.4] S[table-format=1.3e-1,scientific-notation=true] S[table-format=1.6]',
    ['Architecture',r'$n_\theta$','Valid',r'Median $E_{\rm raw}$',r'Median $E_{\rm SAEPS}$',r'Coefficient error'],rows,
    r'Each architecture uses three data seeds and two initializations at noise 0.02. Six base fits are reused from E3; twelve fits are additional. The last column is the median saturation coefficient error $|\widehat\kappa-\kappa^\star|/\kappa^\star$ of the underlying PINN fits, not an error of SAEPS. Post-training diagnosis does not update $\widehat\kappa$.')

failures=[
    dict(cohort='Burgers',planned=15,accepted=12,state_center=3,solve=0,nonfinite=0,other=0,seeds='57;61;63'),
    dict(cohort='Allen-Cahn',planned=10,accepted=9,state_center=1,solve=0,nonfinite=0,other=0,seeds='81'),
    dict(cohort='Coupled',planned=10,accepted=8,state_center=2,solve=0,nonfinite=0,other=0,seeds='219;221')]
pd.DataFrame(failures).to_csv(D/'historical_failure_categories.csv',index=False)
tab('failure_counts','Terminal failure categories for the historical accuracy cohorts.','tab:failure_counts',
    r'l *{6}{S[table-format=2.0]}',
    ['Cohort','Planned','Accepted',r'\shortstack{State\\center}',r'Solve',r'Non-finite','Other'],
    [[x['cohort'].replace('-','--')]+[x[k] for k in ['planned','accepted','state_center','solve','nonfinite','other']] for x in failures],
    r'Burgers failures are seeds 57, 61, and 63; Allen--Cahn fails at seed 81; coupled failures are 219 and 221. All are recorded as state-center acceptance failures. Counts classify the primary accuracy endpoint, not the separate profile experiments or nonbinding score diagnostics. The source aggregates are listed in the revision provenance. This classification does not assume ignorable missingness or alter historical acceptance gates.')

stats=[]
for name,x in [('Burgers',h[h.cohort.eq('Burgers')]),('Allen-Cahn',h[h.cohort.eq('Allen-Cahn')]),('Saturation',s)]:
    diff=(x.E_raw-x.E_SAEPS).to_numpy(); ratio=(x.E_raw/x.E_SAEPS).to_numpy()
    dq=np.quantile(diff,[.25,.5,.75],method='linear'); rq=np.quantile(ratio,[.25,.5,.75],method='linear')
    stats.append(dict(cohort=name,n=len(x),D_q25=float(dq[0]),D_median=float(dq[1]),D_q75=float(dq[2]),ratio_q25=float(rq[0]),ratio_median=float(rq[1]),ratio_q75=float(rq[2])))
(V/'effect_size_summary.json').write_text(json.dumps({'classification':'POSTHOC_DESCRIPTIVE_REAGGREGATION','quantile_method':'numpy linear','new_training':False,'confidence_interval_claimed':False,'statistics':stats},indent=2)+'\n')
tab('effect_sizes','Paired effect sizes and empirical quartiles at the declared statistical unit.','tab:effect_sizes',
    r'l S[table-format=2.0] *{3}{S[table-format=2.3]} *{3}{S[table-format=5.1]}',
    ['Cohort',r'$n$',r'$D_{25}$',r'$D_{50}$',r'$D_{75}$',r'$R_{25}$',r'$R_{50}$',r'$R_{75}$'],
    [[x['cohort'].replace('-','--'),x['n']]+[f'{x[k]:.3f}' for k in ['D_q25','D_median','D_q75']]+[f'{x[k]:.1f}' for k in ['ratio_q25','ratio_median','ratio_q75']] for x in stats],
    r'$D=E_{\rm raw}-E_{\rm SAEPS}$ and $R=E_{\rm raw}/E_{\rm SAEPS}$ use the same unit-level pair. Subscripts denote empirical percentiles, using linear interpolation. Historical units are accepted checkpoints; saturation units are six four-fit medians. The saturation difference is formed after that pooling. These quartiles summarize dispersion, not a bootstrap or calibrated 95\% confidence interval. No cohorts are pooled for inference.')

# Re-runnable numeric macro block.
npath=ROOT/'numbers.tex'; base=npath.read_text().split('% Editorial effect-size macros')[0].rstrip()
x=stats[-1]
extras='\n% Editorial effect-size macros: generated from six paired data-seed summaries\n'
for macro,key in [('SaturationDMedian','D_median'),('SaturationDLower','D_q25'),('SaturationDUpper','D_q75')]:
    extras+='\\newcommand{\\'+macro+'}{\\num{'+f'{x[key]:.3f}'+'}}\n'
npath.write_text(base+'\n'+extras)
# Consistent profile symbol in generated supplementary table.
p=T/'profile_all.tex';p.write_text(p.read_text().replace('$C(h)$',r'$D_\gamma(h;1)$'))
print('Editorial tables and effect-size macros regenerated.')

# Supplementary quantitative tables: native siunitx numeric cells, not image tables.
# Automatic widths retain the archived rounding without an arbitrary precision cap.
import re
formats={
 'aggregation_levels':('lSSSS',[1,2,3,4]),
 'e3_seeds':('SSSS',[0,1,2,3]),
 'e3_all':('SScSSS',[0,1,3,4,5]),
 'historical_all':('lScSS',[1,3,4]),
 'cost_all':('SSlSSS',[0,1,3,4,5]),
 'architecture_resources':('SSSSSS',[0,1,2,3,4,5]),
 'profile_all':('SSSSS',[0,1,2,3,4]),
 'stress_anchors':('SSSS',[0,1,2,3]),
}
number=re.compile(r'^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$')
for name,(fmt,numeric) in formats.items():
    path=T/f'{name}.tex'; text=path.read_text()
    text=re.sub(r'\\begin\{(tabular|longtable)\}\{[^\n]+?\}',lambda m:'\\begin{'+m.group(1)+'}{'+fmt+'}',text,count=1)
    lines=[]
    for line in text.splitlines():
        if '&' in line and line.rstrip().endswith(r'\\'):
            vals=line.rstrip()[:-2].split('&')
            if len(vals)==len(fmt):
                for i in numeric:
                    v=vals[i].strip()
                    v=re.sub(r'^\\num\{([^}]+)\}$',r'\1',v)
                    if not number.match(v) and not (v.startswith('{') and v.endswith('}')):v='{'+v+'}'
                    vals[i]=v
                line=' & '.join(v.strip() for v in vals)+r' \\'
        lines.append(line)
    path.write_text('\n'.join(lines)+'\n')
p=T/'cost_all.tex'
text=p.read_text()
if not text.startswith('\\begingroup'):
    p.write_text('\\begingroup\n\\small\\setlength{\\tabcolsep}{4pt}\n'+text+'\\endgroup\n')
