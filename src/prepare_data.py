"""Recompute derived plot and table inputs from the released numerical extracts.
See the README for the upstream paths and cohort definitions.
"""
from pathlib import Path
import json, numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'
h=pd.read_csv(D/'historical_scalar.csv')
e3=pd.read_csv(D/'e3_heldout_corrected.csv')
assert len(e3)==24 and not e3.duplicated(['data_seed','initialization_seed','noise_level']).any()
metrics=['E_raw','E_SAEPS','E_fix','E_GN_fix','E_relax']
# Noise-stratified summaries follow the within-layer initialization rule.
# Cross-noise pooling is reported separately and labeled post hoc.
noise=e3.groupby(['data_seed','noise_level'])[metrics].median().reset_index()
noise.to_csv(D/'e3_noise_seed_summary.csv',index=False,float_format='%.17g')
# For two initialisations and two noise layers, nested medians need not equal
# a pooled median. Preserve the original reported POOLING rule as the main summary.
pooled=e3.groupby('data_seed')[metrics].median().reset_index()
pooled.to_csv(D/'e3_pooled_seed_summary.csv',index=False,float_format='%.17g')
# Repository data_seed_level_summary actually pools all four fits by median.
assert np.isclose(pooled.E_SAEPS.median(),.0010602976245172922,rtol=1e-12)
e6=pd.read_csv(D/'e6_curvature_extract.csv')
assert len(e6)==18 and not e6.duplicated(['architecture','data_seed','initialization_seed']).any()
den=e6.H_red_exact.abs()+1e-8
for col,num in [('E_raw',e6.F_raw-e6.H_red_exact),('E_SAEPS',e6.F_se_GN-e6.H_red_exact),('E_fix',e6.H_fix_exact-e6.H_red_exact),('E_GN_fix',e6.F_raw-e6.H_fix_exact)]:e6[col]=num.abs()/den
cg=e6.F_raw-e6.F_se_GN; ce=e6.H_fix_exact-e6.H_red_exact
err=cg-ce
e6['E_relax']=err.abs()/(ce.abs()+1e-8)
e6['n_theta']=e6.architecture.map({'2_16_1':65,'2_32_1':129,'2_16_16_1':337})
# Optional retrospective sufficient condition. Requires the exact reference;
# it is not an oracle-free deployment certificate.
e6['gain_ratio']=(2*(e6.F_raw-e6.H_fix_exact).abs()+err.abs())/ce.abs()
e6.to_csv(D/'e6_metrics_recomputed.csv',index=False,float_format='%.17g')
summary={}
for name,df in h.groupby('cohort'):
 summary[name]={'n_valid':len(df),'n_planned':15 if name=='Burgers' else 10,'median_E_raw':df.E_raw.median(),'median_E_SAEPS':df.E_SAEPS.median(),'ratio_of_medians':df.E_raw.median()/df.E_SAEPS.median(),'median_paired_ratio':(df.E_raw/df.E_SAEPS).median()}
summary['saturation']={'n_fits':len(e3),'n_data_seeds':len(pooled),'fit_medians':e3[metrics].median().to_dict(),'pooled_seed_medians':pooled[metrics].median().to_dict(),'ratio_of_seed_medians':pooled.E_raw.median()/pooled.E_SAEPS.median(),'median_ratio_of_seed_medians':(pooled.E_raw/pooled.E_SAEPS).median(),'median_fit_paired_ratio':(e3.E_raw/e3.E_SAEPS).median(),'ratio_of_fit_medians':e3.E_raw.median()/e3.E_SAEPS.median(),'seed_sign_p':2**-6,'pooling':'post hoc median over four fits within each data seed','noise_stratified':noise.groupby('noise_level')[metrics].median().to_dict()}
summary['architectures']={str(n):{'n':len(v),'raw_median':v.E_raw.median(),'saeps_median':v.E_SAEPS.median(),'saeps_min':v.E_SAEPS.min(),'saeps_max':v.E_SAEPS.max(),'median_parameter_error':v.kappa_relative_error.median(),'median_seconds':v.train_seconds.median(),'median_polish_iterations':v.polish_iterations.median(),'gain_ratio_max':v.gain_ratio.max()} for n,v in e6.groupby('n_theta')}
summary['E6_unique_new_fits']=12
summary['E6_base_reused']=6
summary['E6_improves_over_raw']=int((e6.E_SAEPS<e6.E_raw).sum())
summary['derived_gain_condition']={'classification':'NEW_POSTHOC_DERIVED_20260920','records':18,'unique_added_beyond_E3':12,'condition_holds':int((e6.gain_ratio<1).sum()),'max_ratio':float(e6.gain_ratio.max()),'note':'Requires exact blocks; only an explanatory sufficient condition.'}
review=ROOT/'review'
review.mkdir(exist_ok=True)
(review/'recomputed_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
print(json.dumps(summary,indent=2))
