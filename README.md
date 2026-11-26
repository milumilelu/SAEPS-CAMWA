# SAEPS-CAMWA reproducibility materials

Companion code and data for *Correcting frozen-state curvature in inverse
physics-informed neural networks via regularized state elimination*.

The archived benchmark inputs and summary tables are in `data/`. Python
generators and the energy-form Schur-complement evaluation are in `src/`.
The manuscript and supplement are provided as LaTeX source with their final
table fragments and figures. The numerical tests cover the energy identity,
solve-error bound, dominance condition, cohort counts, and aggregation rules.

## Build the manuscript and supplement

Use a TeX distribution with pdfLaTeX, Latin Modern, TikZ, siunitx, and the
packages listed in the preambles. Run from the repository root.

```sh
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
```

## Recompute results from the archived extracts

Python 3.12 was used for the commands below. Run in a separate checkout if
you wish to keep the supplied LaTeX formatting and publication figures.
The generators reproduce the numerical rows and plots, with their own
table formatting. Timing scripts read archived measurements for analysis.
Rerunning these commands does not require PINN training.

```sh
python -m pip install -r requirements.txt
python -m pytest -q
python src/prepare_data.py
python src/build_tables.py
python src/build_supplement_tables.py
python src/build_review_tables.py
python src/build_figures.py
```

The conceptual diagram can be rebuilt with `pdflatex fig01_geometry.tex`
from the `figures/` directory.

## Evidence and implementation

The [SAEPS repository](https://github.com/milumilelu/SAEPS) contains the
[core implementation](https://github.com/milumilelu/SAEPS/blob/main/src/saeps/core.py),
experimental scripts, configurations, and archived logs. The added
experiments are traceable to [the integrated snapshot](https://github.com/milumilelu/SAEPS/tree/1c4a37310bb8ee2ecd9f4703d9214e289ad7ce99).

| Released data | Source and interpretation |
| --- | --- |
| `historical_scalar.csv`, `historical_failure_categories.csv` | Accepted scalar errors and planned counts from the [historical audit](https://github.com/milumilelu/SAEPS/blob/main/docs/evidence/v5_final_audit.json). Cohort failures are reported separately. The earlier scalar state tensors are unavailable for independent tensor-level replay. |
| `e3_heldout_corrected.csv` and the noise/pooled summaries | [Corrected saturation records](https://github.com/milumilelu/SAEPS/blob/1c4a37310bb8ee2ecd9f4703d9214e289ad7ce99/experiments/paper_revision_20260916/outputs/posthoc/report_correction_20260918/e3_metrics_corrected.csv). The 24 held-out fits correspond to six data seeds. Cross-noise pooling is post hoc. |
| `e6_curvature_extract.csv`, `e6_metrics_recomputed.csv` | [Architecture accuracy records](https://github.com/milumilelu/SAEPS/blob/1c4a37310bb8ee2ecd9f4703d9214e289ad7ce99/experiments/paper_revision_20260916/outputs/development/e6/e6_architecture_accuracy.csv). The 18 rows include six reused from E3. Fixed-state GN truncation is recomputed from the archived curvature blocks. |
| `e7_profile_extract.csv` | [Profile and branch diagnostics](https://github.com/milumilelu/SAEPS/blob/1c4a37310bb8ee2ecd9f4703d9214e289ad7ce99/experiments/paper_revision_20260916/outputs/heldout/e7/e7_branch_diagnostics.csv). The extract contains 21 symmetric differences. The upstream records preserve the state-gradient acceptance outcomes. |
| `e8_timing_extract.csv`, `e8_timing_summary.csv` | [Matched-damping timing records](https://github.com/milumilelu/SAEPS/blob/1c4a37310bb8ee2ecd9f4703d9214e289ad7ce99/experiments/paper_revision_20260916/outputs/posthoc/e8/e8_matched_gamma_cost.csv). The extract includes both centers, three solvers, four damping levels, and three repetitions. |
| Section 4.2 and supplementary damping analyses | [Undamped block and TSVD records](https://github.com/milumilelu/SAEPS/blob/main/docs/evidence/posthoc_variable_projection_v1.json) and [finite-damping audit](https://github.com/milumilelu/SAEPS/blob/main/docs/evidence/v5/V5_FINITE_GAMMA_AUDIT.json). The condition numbers are for the retained eigenspace of the Gauss–Newton state block. Acceptance is determined by the numerical positivity gate. |

The CSV inputs are selected-field extracts from the cited sources. The
[BSD 3-Clause license](LICENSE) applies to the released code.
