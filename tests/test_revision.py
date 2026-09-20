from pathlib import Path
import sys, numpy as np, pandas as pd, pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from certified_energy import energy_audit, exact_reference_dominance

@pytest.mark.parametrize('m,n,p',[(12,4,1),(12,4,3),(4,12,2)])
@pytest.mark.parametrize('gamma',[1e-6,1e-3,1.])
@pytest.mark.parametrize('rank_deficient',[False,True])
def test_energy_identity(m,n,p,gamma,rank_deficient):
    r=np.random.default_rng(851+m+n+p)
    j=r.normal(size=(m,n)); y=r.normal(size=(m,p))
    if rank_deficient:j[:,-1]=j[:,0]
    M=j.T@j+gamma*np.eye(n)
    zstar=np.linalg.solve(M,j.T@y)
    z=zstar+0.03*r.normal(size=(n,p))
    a=energy_audit(lambda x:j@x,lambda q:j.T@q,y,z,gamma)
    e=y-j@zstar;ref=e.T@e+gamma*zstar.T@zstar
    expected=a.normal_residual.T@np.linalg.solve(M,a.normal_residual)
    np.testing.assert_allclose(a.curvature-ref,expected,rtol=2e-7,atol=2e-9)
    assert np.linalg.eigvalsh(a.curvature-ref).min()>-2e-9
    assert np.linalg.eigvalsh(a.loewner_upper_error-(a.curvature-ref)).min()>-1e-6

@pytest.mark.parametrize('gamma',[1e-5,.1,10])
def test_spectrum_and_unit_eigenvalue(gamma):
    j=np.array([[1.],[0.]])
    A=np.eye(2)-j@np.linalg.solve(j.T@j+gamma*np.eye(1),j.T)
    np.testing.assert_allclose(np.linalg.eigvalsh(A),[gamma/(1+gamma),1])

@pytest.mark.parametrize('seed',range(20))
def test_gain_condition(seed):
    r=np.random.default_rng(seed)
    c=r.normal(size=(3,3));c=c.T@c+np.eye(3)
    q=np.eye(3);h=q+c;d=.002*r.normal(size=(3,3));d=(d+d.T)/2
    e=.001*r.normal(size=(3,3));e=(e+e.T)/2
    f=h+d;g=f-c-e
    a=exact_reference_dominance(f,h,g,q)
    assert a['sufficient_condition']
    assert a['saeps_absolute_error']<a['raw_absolute_error']

@pytest.mark.parametrize('gamma',[0,-1,float('inf'),float('nan')])
def test_gamma_validation(gamma):
    with pytest.raises(ValueError):energy_audit(lambda z:z,lambda q:q,np.ones((2,1)),np.zeros((2,1)),gamma)

def test_e3_source_metrics_and_units():
    d=pd.read_csv(ROOT/'data/e3_heldout_corrected.csv')
    assert len(d)==24 and len(d.data_seed.unique())==6
    assert (d.E_SAEPS<d.E_raw).all()
    assert np.isclose(d.E_SAEPS.median(),.0012466421922557517)
    a=d.groupby('data_seed')[['E_raw','E_SAEPS']].median()
    assert np.isclose(a.E_SAEPS.median(),.0010602976245172922)
    assert 2**-len(a)==.015625

def test_e6_metrics():
    d=pd.read_csv(ROOT/'data/e6_metrics_recomputed.csv')
    assert len(d)==18 and len(d[d.n_theta!=65])==12
    assert (d.E_SAEPS<d.E_raw).all()
    assert np.isclose(d[d.n_theta==337].E_SAEPS.median(),.00043223501955742485)
    # Subtracting raw from Fse is not the fixed-state GN truncation.
    np.testing.assert_allclose(d.E_GN_fix,abs(d.F_raw-d.H_fix_exact)/(abs(d.H_red_exact)+1e-8))

def test_historical_values():
    d=pd.read_csv(ROOT/'data/historical_scalar.csv')
    assert len(d[d.cohort=='Burgers'])==12 and len(d[d.cohort=='Allen-Cahn'])==9
    for cohort,value in [('Burgers',.07503228596679316),('Allen-Cahn',.2785667026005181)]:
        assert np.isclose(d[d.cohort==cohort].E_SAEPS.median(),value)

def test_profile_counts():
    d=pd.read_csv(ROOT/'data/e7_profile_extract.csv')
    assert len(d)==21 and (d.relative_difference<.1).sum()==20
    np.testing.assert_allclose(d.relative_difference,abs(d.symmetric_curvature-d.exact_schur)/abs(d.exact_schur),rtol=1e-10,atol=1e-11)

def test_cost_population():
    d=pd.read_csv(ROOT/'data/e8_timing_extract.csv')
    assert len(d)==72 and len(d.seed.unique())==2 and len(d.method.unique())==3
    assert not d.duplicated(['seed','alpha','method','repeat']).any()
    assert (d.reported_total_seconds>=d.solve_seconds).all()
    x=d[(d.seed==215)&(d.method=='CG')&(d.alpha==1e-8)].solve_seconds.median()
    assert np.isclose(x,10.630182099999729)


def test_ratios_keep_their_statistical_unit():
    d=pd.read_csv(ROOT/'data/e3_heldout_corrected.csv')
    s=d.groupby('data_seed')[['E_raw','E_SAEPS']].median()
    fit_ratio=float((d.E_raw/d.E_SAEPS).median())
    seed_ratio=float((s.E_raw/s.E_SAEPS).median())
    assert np.isclose(fit_ratio,13257.167846502536)
    assert np.isclose(seed_ratio,16883.087154009856)
    assert not np.isclose(fit_ratio,seed_ratio)
