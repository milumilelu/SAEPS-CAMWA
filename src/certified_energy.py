"""Equivalent SAEPS energy evaluation and an exact-arithmetic error bound.

This revision-time numerical utility DOES NOT change historical benchmark outputs.
The bound controls error from the linear solve, not GN truncation or state stationarity.
A small bound is sufficient, not necessary. Floating-point roundoff is not enclosed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import numpy as np
from numpy.typing import NDArray
Array=NDArray[np.float64]
@dataclass(frozen=True)
class EnergyAudit:
    curvature: Array
    normal_residual: Array
    loewner_upper_error: Array
    spectral_error_upper_bound: float

def energy_audit(jvp: Callable[[Array],Array], vjp: Callable[[Array],Array],
                 parameter_response: Array, state_fit: Array, gamma: float) -> EnergyAudit:
    """Evaluate Fhat = (Y-JZ)'(Y-JZ) + gamma Z'Z and R'R/gamma.

    jvp and vjp must act on matrices columnwise. Y has shape (m,p);
    Z has shape (n,p). The caller supplies the approximate state solve.
    In exact arithmetic 0 <= Fhat-F_SAEPS <= R'R/gamma.
    """
    if not np.isfinite(gamma) or gamma <= 0:
        raise ValueError('gamma must be positive and finite')
    y=np.asarray(parameter_response,dtype=np.float64)
    z=np.asarray(state_fit,dtype=np.float64)
    if y.ndim!=2 or z.ndim!=2 or y.shape[1]!=z.shape[1]:
        raise ValueError('Y and Z must be 2D with the same number of columns')
    if not np.isfinite(y).all() or not np.isfinite(z).all():
        raise ValueError('inputs must be finite')
    jz=np.asarray(jvp(z),dtype=np.float64)
    if jz.shape!=y.shape: raise ValueError('jvp returned an incompatible shape')
    retained=y-jz
    residual=np.asarray(vjp(-retained),dtype=np.float64)+gamma*z
    if residual.shape!=z.shape: raise ValueError('vjp returned an incompatible shape')
    f=retained.T@retained+gamma*(z.T@z)
    upper=(residual.T@residual)/gamma
    return EnergyAudit((f+f.T)/2,residual,(upper+upper.T)/2,
                       float(np.linalg.norm(residual,2)**2/gamma))

def exact_reference_dominance(raw: Array, exact_fixed: Array,
                              reduced_gn: Array, exact_reduced: Array) -> dict:
    """Retrospective sufficient condition; requires exact reference blocks.

    ||C_exact|| > 2||raw-exact_fixed|| + ||C_GN-C_exact|| guarantees
    ||reduced_gn-exact_reduced|| < ||raw-exact_reduced|| in the Frobenius norm.
    """
    f,h,g,q=[np.atleast_2d(np.asarray(a,dtype=np.float64)) for a in
             (raw,exact_fixed,reduced_gn,exact_reduced)]
    if not (f.shape==h.shape==g.shape==q.shape):raise ValueError('shapes must match')
    c=h-q;delta=f-h;error=(f-g)-c
    cn=float(np.linalg.norm(c,'fro')); need=2*np.linalg.norm(delta,'fro')+np.linalg.norm(error,'fro')
    return {'ratio':float(need/cn) if cn>0 else None,'sufficient_condition':bool(cn>need),
            'raw_absolute_error':float(np.linalg.norm(f-q,'fro')),
            'saeps_absolute_error':float(np.linalg.norm(g-q,'fro'))}
