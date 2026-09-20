"""Editorial regression checks: source consistency, arithmetic, and source scopes."""
from pathlib import Path
import re,json,hashlib
import numpy as np
import pandas as pd
import pytest
ROOT=Path(__file__).resolve().parents[1]
M=(ROOT/'manuscript.tex').read_text()
S=(ROOT/'supplement.tex').read_text()

def test_five_introduction_paragraphs():
    intro=M.split(r'\section{Introduction}')[1].split(r'\section{Regularized')[0]
    blocks=[re.sub(r'\\label\{[^}]+\}','',b).strip() for b in re.split(r'\n\s*\n',intro)]
    assert len([b for b in blocks if b])==5

def test_all_bibliography_items_cited():
    bibs=set(re.findall(r'\\bibitem\{([^}]+)\}',M))
    cites=set(k.strip() for v in re.findall(r'\\cite\w*\{([^}]+)\}',M) for k in v.split(','))
    assert bibs==cites and len(bibs)==28

@pytest.mark.parametrize('name',['manuscript.tex','supplement.tex','figures/fig01_geometry.tikz'])
def test_no_control_characters(name):
    text=(ROOT/name).read_text()
    assert not any(ord(c)<32 and c not in '\n\r' for c in text)

def test_reference_updates():
    assert r'10.1063/5.0349054' in M
    assert r'arXiv:2608.15373v1' in M
    assert r'\cite{raue2009structural}' in M

def test_profile_direction_notation_and_scope():
    assert r'D_\gamma(h;v)' in M
    assert 'It checks displacement magnitudes' in M
    assert 'shared local basin' in S
    assert '$C(h)$' not in (ROOT/'tables/profile_all.tex').read_text()

def test_stationarity_is_state_only():
    assert r'does not require $\nabla_\lambda\ell=0$' in M
    assert 'exact state-stationarity condition' in M
    assert 'a posteriori' in M and 'a priori bound' not in M

def test_eigenvalue_metric_and_scale_statements():
    assert 'nonzero singular values' in M
    assert 'summed-loss scale' in M
    assert 'divide both curvature blocks and damping by $m$' in M

@pytest.mark.parametrize('cohort',['Burgers','Allen-Cahn','Saturation'])
def test_empirical_effect_quartiles(cohort):
    stats=json.loads((ROOT/'review/effect_size_summary.json').read_text())
    row=next(x for x in stats['statistics'] if x['cohort']==cohort)
    if cohort=='Saturation':
        x=pd.read_csv(ROOT/'data/e3_pooled_seed_summary.csv')
    else:
        x=pd.read_csv(ROOT/'data/historical_scalar.csv');x=x[x.cohort==cohort]
    d=x.E_raw-x.E_SAEPS;r=x.E_raw/x.E_SAEPS
    assert np.allclose([row[k] for k in ['D_q25','D_median','D_q75']],np.quantile(d,[.25,.5,.75],method='linear'))
    assert np.allclose([row[k] for k in ['ratio_q25','ratio_median','ratio_q75']],np.quantile(r,[.25,.5,.75],method='linear'))
    assert stats['confidence_interval_claimed'] is False

def test_failure_counts_and_primary_endpoint():
    x=pd.read_csv(ROOT/'data/historical_failure_categories.csv')
    assert np.all(x.accepted+x.state_center+x.solve+x.nonfinite+x.other==x.planned)
    assert x.state_center.tolist()==[3,1,2]
    assert x.accepted.tolist()==[12,9,8]

def test_cost_workload_limits_disclosed():
    assert 'must not be interpreted as pure LSQR iteration time or a clean preconditioner-cost decomposition' in S
    assert 'BLAS' in S and 'not recorded' in S
    assert '500 iterations per right-hand side' in S

def test_diagram_is_vector_pdf():
    import fitz
    doc=fitz.open(ROOT/'figures/fig01_geometry.pdf')
    assert len(doc)==1 and not doc[0].get_images()
    text=doc[0].get_text()
    assert 'Frozen-state baseline' in text
    assert 'fitted parameters remain unchanged' in text

def test_main_table_decimal_alignment_and_note():
    for name in ['main_results','mechanism','architecture']:
        text=(ROOT/f'tables/{name}.tex').read_text()
        assert 'S[table-format=' in text
        assert r'\toprule' in text and r'\bottomrule' in text
    assert 'underlying PINN' in (ROOT/'tables/architecture.tex').read_text()
