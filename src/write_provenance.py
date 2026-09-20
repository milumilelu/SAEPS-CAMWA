"""Record explicit source identities and local extract hashes, without equating them."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[1]
sha='1c4a37310bb8ee2ecd9f4703d9214e289ad7ce99'
ns='experiments/paper_revision_20260916/'
def h(path):return hashlib.sha256(path.read_bytes()).hexdigest()
sources=[
 {'local_file':'review/input_integrated.tex','input_name':'SAEPS_manuscript_integrated.tex','chat_file_id':'file_00000000f30881f5b414f18b02131d9e','role':'uploaded manuscript; embedded full-precision historical curves; displayed historical appendix summaries'},
 {'local_file':'data/e3_heldout_corrected.csv','repository_path':ns+'outputs/posthoc/report_correction_20260918/e3_metrics_corrected.csv','git_blob_sha1':'77b6d800431d331922c7a34e0435656a5b3dcf3d','selection':'24 rows with cohort e3_heldout_1e5; selected seed, initialization, noise and corrected-error columns','representation':'visible-value selected-field extract, not byte-identical raw CSV'},
 {'local_file':'data/e6_curvature_extract.csv','repository_path':ns+'outputs/development/e6/e6_architecture_accuracy.csv','git_blob_sha1':'328b8c3d2c6b9486918a9c9bcaa86ea874c7ac9a','selection':'all18 rows; selected exact and GN curvatures, state size, gradients, realized iterations, fit time, coefficient error, HVP discrepancy','representation':'visible-value selected-field extract; E_GN_fix recomputed rather than retaining erroneous historical field'},
 {'local_file':'data/e7_profile_extract.csv','repository_path':ns+'outputs/heldout/e7/e7_branch_diagnostics.csv','git_blob_sha1':'a1c92f48ed98d50768ada55c47e4f70fef91dce0','selection':'all21 rows; data seed, step, symmetric curvature, Schur reference, relative discrepancy','representation':'visible-value selected-field extract'},
 {'local_file':'data/e8_timing_extract.csv','repository_path':ns+'outputs/posthoc/e8/e8_matched_gamma_cost.csv','git_blob_sha1':'c626314e4b055c26d1e4411579f8fcf6c9ddabcc','selection':'all72 rows; seed, alpha, method, repeat, solve time, total time, agreement, shared Jacobian time','representation':'selected-field extract generated from recorded numeric triples; method labels explicit->Dense and scaled_LSQR->Scaled LSQR'},
]
for row in sources:
 row['local_sha256']=h(R/row['local_file'])
 if 'repository_path' in row:
  row['commit']=sha
  row['source_url']=f'https://github.com/milumilelu/SAEPS/blob/{sha}/'+row['repository_path']
report={'date':'2026-09-20','repository':'https://github.com/milumilelu/SAEPS','integrated_commit':sha,
'historical_tag':'jcp-submission-v1','historical_commit':'d5a231d857e410b96ae66174fb98fec9c8b9b34a',
'sources':sources,'additional_context':{'chat_file_id':'file_0000000024c081f5a4b5b776e8c21a04','name':'WRITING_MATERIALS_LIMITED_CLAIMS.md','use':'separate historical/Q2S2 scope and limitation context; not a replacement source for E3-E8 outcomes'},
'limitations':['No new PINN training was run.','No complete historical repository test suite was run.','Selected-field extracts are not original-file byte copies. Git SHA1 identifies the remote source; local SHA256 identifies the extract.','Q2S2 counts are attributed to the supplied writing materials and not pooled with E7.'],
'new_derived_results':['E6 retrospective sufficient-gain condition on18existing records with6reusedbasefits.','Energy-form exact-arithmetic identity tested on synthetic matrices.','Consistent fit/seed ratio aggregation and all-record plot regeneration.']}
(R/'review/SOURCES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('Wrote explicit source and extract identities.')
