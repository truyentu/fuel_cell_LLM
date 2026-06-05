# Verification Report

Trust Score: **B** (5.0/7.0)

| # | Check | Status | Detail |
|---|-------|--------|--------|
| 1 | Sanity | ✅ | All values in physical range |
| 2 | Convergence | ✅ | BoTorch reported convergence |
| 3 | Cross-tool | ✅ | 0/10 inconsistent (0%) |
| 4 | Ensemble | ❌ | 3/5 top candidates have high uncertainty |
| 5 | Perturbation | ✅ | Top-half CV=0.051 (robust) |
| 6 | Literature | ✅ | NiMo HOR=-0.405 vs Ni=-0.430 (NiMo better: True) |
| 7 | Consistency | ❌ | 3/10 have H₂_barrier > O₂_barrier (unexpected) |