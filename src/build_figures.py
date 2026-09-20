"""Publication figures from archived numerical values only.
Every chart has one axes; no smoothing, fitted trend, or invented error bars.
Default matplotlib colours are used. PDF/SVG are vector outputs.
"""
from pathlib import Path
import json, re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'; OUT=ROOT/'figures'
OUT.mkdir(exist_ok=True)
S=json.loads((ROOT/'review/recomputed_summary.json').read_text())
h=pd.read_csv(D/'historical_scalar.csv');e3=pd.read_csv(D/'e3_heldout_corrected.csv')
seed=pd.read_csv(D/'e3_pooled_seed_summary.csv');e6=pd.read_csv(D/'e6_metrics_recomputed.csv')
cost=pd.read_csv(D/'e8_timing_summary.csv');profile=pd.read_csv(D/'e7_profile_extract.csv')

def start(w=6.7,h=3.8):
 f=plt.figure(figsize=(w,h));a=f.add_subplot(111)
 a.spines['top'].set_visible(False);a.spines['right'].set_visible(False)
 a.tick_params(labelsize=10);a.grid(True,axis='y',which='major',alpha=.16)
 return f,a

def save(f,name):
 f.tight_layout(pad=.9)
 for ext in ['pdf','svg']:f.savefig(OUT/f'{name}.{ext}',bbox_inches='tight')
 f.savefig(OUT/f'{name}.png',dpi=180,bbox_inches='tight')
 plt.close(f)

# Paired endpoints. The saturation points are data-seed medians, not 24 independent fits.
f,a=start(6.8,4.2)
groups=[h[h.cohort=='Burgers'],h[h.cohort=='Allen-Cahn'],seed]
xr=[];xs=[];yr=[];ys=[];cx=[];cy=[]
for i,v in enumerate(groups):
 offsets=np.linspace(-.14,.14,len(v))
 for off,(_,r) in zip(offsets,v.iterrows()):
  x1=i-.23+off*.25;x2=i+.23+off*.25
  xr.append(x1);xs.append(x2);yr.append(r.E_raw);ys.append(r.E_SAEPS)
  cx += [x1,x2,np.nan];cy += [r.E_raw,r.E_SAEPS,np.nan]
a.plot(cx,cy,alpha=.23,linewidth=.8)
a.scatter(xr,yr,marker='s',s=28,label='Frozen state',zorder=3)
a.scatter(xs,ys,marker='o',s=30,label='SAEPS',zorder=3)
a.set_yscale('log');a.set_ylim(2e-4,1e2)
a.set_xlim(-.65,2.65)
a.set_xticks(range(3),['Burgers\n12 / 15 valid','Allen–Cahn\n9 / 10 valid','Saturation\n6 data seeds; 24 / 24 fits'])
a.set_ylabel('Relative error against the matched Schur reference',fontsize=10)
a.legend(frameon=False,loc='upper center',ncol=2)
save(f,'fig02_paired_accuracy')

# All three error quantities share the same reduced-curvature denominator.
f,a=start(6.8,3.65)
mech=np.array([[27.75,.1563,.07503228596679316],[19.9472,.2903,.2785667026005181],
 [e3.E_fix.median(),e3.E_GN_fix.median(),e3.E_SAEPS.median()]])
for j,(lab,mark) in enumerate([('Exact state-freezing error','s'),('Fixed-state GN truncation','^'),('SAEPS error','o')]):
 a.plot(np.arange(3)+(j-1)*.16,mech[:,j],linestyle='none',marker=mark,markersize=7,label=lab)
a.set_yscale('log');a.set_ylim(3e-4,80);a.set_xlim(-.5,2.5)
a.set_xticks(range(3),['Burgers\n12 centers','Allen–Cahn\n9 centers','Saturation\n24 fits'])
a.set_ylabel('Median relative error (common denominator)',fontsize=10)
a.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,1.2),ncol=1,fontsize=9)
save(f,'fig03_error_mechanisms')

# Actual paired fits rather than a median-only architecture claim.
f,a=start(6.8,3.8)
for (ds,ins),v in e6.groupby(['data_seed','initialization_seed']):
 v=v.sort_values('n_theta');a.plot(range(3),v.E_SAEPS,marker='o',markersize=4,linewidth=.9,alpha=.5)
med=e6.groupby('n_theta').E_SAEPS.median().reindex([65,129,337])
a.plot(range(3),med,marker='D',linewidth=2.4,markersize=7,label='Fit median')
a.set_yscale('log');a.set_ylim(3e-5,8e-3);a.set_xlim(-.18,2.18)
a.set_xticks(range(3),['65','129','337']); a.set_xlabel(r'State parameters $n_\theta$',fontsize=11)
a.set_ylabel('SAEPS relative error',fontsize=11)
a.legend(frameon=False,loc='upper right')
a.text(.02,.04,'Each thin line tracks one data / initialization pair.',transform=a.transAxes,fontsize=9)
save(f,'fig04_architecture_pairs')

# E8: include the dense baseline, and keep the two centers distinct.
f,a=start(6.8,3.75)
for method,mark in [('Dense','s'),('CG','o'),('Scaled LSQR','^')]:
 xx=[];yy=[]
 for sd in [215,224]:
  z=cost[(cost.seed==sd)&(cost.method==method)].sort_values('alpha')
  xx+=list(z.alpha)+[np.nan];yy+=list(z.solve_seconds)+[np.nan]
 a.plot(xx,yy,marker=mark,markersize=5,linewidth=1.25,label=method)
a.set_xscale('log');a.set_yscale('log');a.set_ylim(3e-5,3e2)
a.set_xlabel(r'Damping scale $\alpha$',fontsize=11);a.set_ylabel('Median solve / factorization time (s)',fontsize=10)
# Label the two CG centers at the right end of their curves.
for sd,dy in [(215,6),(224,-8)]:
 z=cost[(cost.seed==sd)&(cost.method=='CG')].sort_values('alpha')
 a.annotate(str(sd), xy=(z.alpha.iloc[-1], z.solve_seconds.iloc[-1]),
            xytext=(6,dy), textcoords='offset points', fontsize=8, va='center')
a.legend(frameon=False,loc='center left',bbox_to_anchor=(1.0,.5),fontsize=9)
# Repetition and center counts are stated in the caption.
save(f,'fig05a_matched_cost')
f,a=start(6.8,3.75)
for method,mark in [('CG','o'),('Scaled LSQR','^')]:
 xx=[];yy=[]
 for sd in [215,224]:
  z=cost[(cost.seed==sd)&(cost.method==method)].sort_values('alpha')
  xx+=list(z.alpha)+[np.nan];yy+=list(z.accuracy_vs_dense)+[np.nan]
 a.plot(xx,yy,marker=mark,markersize=5,linewidth=1.25,label=method)
a.axhline(1e-6,linestyle=':',linewidth=1,label=r'$10^{-6}$ algebraic tolerance')
a.set_xscale('log');a.set_yscale('log');a.set_ylim(1e-16,1e-5)
a.set_xlabel(r'Damping scale $\alpha$',fontsize=11);a.set_ylabel('Relative difference from dense GN reduction',fontsize=10)
a.legend(frameon=False,loc='center left',bbox_to_anchor=(1.,.5),fontsize=9)
save(f,'fig05b_solver_agreement')

f,a=start(6.8,3.65)
for (sd,v),mark in zip(profile.groupby('data_seed'),['o','s','^']):
 v=v.sort_values('step');a.plot(v.step,v.relative_difference,marker=mark,markersize=5,label=f'Data seed {sd}')
a.axhline(.1,linestyle=':',linewidth=1,label='10% agreement criterion')
a.set_xscale('log');a.set_yscale('log');a.set_ylim(8e-6,.3)
a.set_xlabel(r'Parameter displacement $|h|$',fontsize=11);a.set_ylabel('Finite-difference / Schur discrepancy',fontsize=10)
a.legend(frameon=False,fontsize=8,loc='center left',bbox_to_anchor=(1.0,.45))
a.text(.02,.96,'20 / 21 agreement; 0 / 21 tight stationarity',transform=a.transAxes,va='top',fontsize=9)
# Annotate the single point outside the 10% band (seed 916102, smallest h).
out=profile[(profile.data_seed==916102)&(profile.step==profile.step.min())].iloc[0]
a.annotate('1/21 outside', xy=(out.step, out.relative_difference),
            xytext=(10,-12), textcoords='offset points', fontsize=8, color='#cc6600')
save(f,'fig06_profile_resolution')

# Supplement: retain all seven damping scales and the unresolved low-damping count.
alpha=[1e-10,1e-8,1e-6,1e-4,1e-2,1,100]
for name,vals,yl in [('s01_retained_fraction',[.045627,.0482649,.065335,.130094,.57982,.968803,.999637],r'Median retained fraction $\eta$'),('s02_effective_rank',[41.1599,35.7827,27.0456,16.3312,6.575,.949496,.0151977],r'Median effective state rank')]:
 f,a=start(5.8,3.1);a.plot(alpha,vals,marker='o');a.set_xscale('log');a.set_xlabel(r'Damping scale $\alpha$');a.set_ylabel(yl)
 a.axvline(1e-8,linestyle=':',linewidth=1)
 # Availability is stated in each caption to avoid obscuring the curves.
 save(f,name)

f,a=start(5.8,3.3)
for n,t,m in [(1001,[.353524,.431057,.650188],'o'),(10001,[.436132,.926875,3.9367],'s'),(100001,[1.88744,8.31442,40.9669],'^')]:
 a.plot([213,853,3413],t,marker=m,label=fr'$n_\theta={n}$')
a.set_xscale('log');a.set_yscale('log');a.set_xticks([213,853,3413],['213','853','3413'])
a.set_xlabel('Residual count');a.set_ylabel('Median iterative time (s)')
a.legend(frameon=False,fontsize=9);save(f,'s03_operator_scaling')

# Supplementary noise-stratified E3 data-seed medians.
n=pd.read_csv(D/'e3_noise_seed_summary.csv')
f,a=start(6.8,3.5)
for noise,mark in [(0.,'o'),(.02,'s')]:
 z=n[n.noise_level==noise];a.plot(np.arange(1,7),z.E_SAEPS,marker=mark,label=f'Noise {noise:g}',linewidth=1)
a.set_yscale('log');a.set_xticks(range(1,7),[str(s)[-3:] for s in sorted(n.data_seed.unique())])
a.set_xlabel('Data-seed suffix (916xxx)');a.set_ylabel('Median SAEPS error within noise layer')
a.legend(frameon=False);save(f,'s04_noise_stratified')
print('Built 10 data figures: PDF, SVG and PNG.')
