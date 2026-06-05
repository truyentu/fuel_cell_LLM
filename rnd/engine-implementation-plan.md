# Implementation Plan — Level 2 Engine Code

Date: 2026-06-03
Status: Ready to implement
Config input: `rnd/experiments/carbon-shell-config.json`
Target: Python project chạy trên Google Cloud GPU

---

## Overview

```
19 files cần viết, chia thành 5 phases:

Phase A: Foundation (5 files) — config, utils, không cần GPU test
Phase B: Structure Generator (3 files) — tạo atoms, test local
Phase C: Runners (4 files) — MACE, OC20, JDFTx, ensemble
Phase D: Pipeline (4 files) — calibration, filter, screening, DFT feedback
Phase E: Analysis + Reports (3 files) — verify, trust, output
```

---

## Dependencies Graph

```
config_schema.py ← (mọi thứ depend vào config)
    ↓
utils/logger.py + utils/checkpoint.py (independent)
    ↓
structures/slab_builder.py → structures/shell_builder.py → structures/ni_at_c_generator.py
    ↓
runners/mace_runner.py + runners/oc20_runner.py (parallel, independent)
runners/mace_ensemble.py (depends on mace_runner)
runners/jdftx_runner.py (independent)
    ↓
optimizer/botorch_loop.py (depends on runners output format)
    ↓
phases/calibration.py (depends on runners + structures)
phases/coarse_filter.py (depends on mace_runner + structures)
phases/screening.py (depends on ALL runners + optimizer + structures)
phases/dft_feedback.py (depends on jdftx_runner + optimizer)
    ↓
analysis/failure_analyzer.py (depends on screening output)
analysis/verification.py (depends on results format)
analysis/trust_scorer.py (depends on verification)
utils/reporter.py (depends on results format)
    ↓
llm_advisor.py (independent, only needs anthropic SDK)
    ↓
run.py (orchestrates everything)
```

---

## Phase A: Foundation (No GPU needed, test local)

### A1: `config_schema.py`

```
Input: rnd/experiments/carbon-shell-config.json
Output: Validated config dict (or raise ValidationError)

Implement:
- Pydantic BaseModel for each config section
- Validation rules (reject UNVERIFIED targets, range checks)
- Load + validate function
- Warning vs Error distinction

Test: load real config.json → validate → pass/fail
Dependencies: pydantic
LOC estimate: ~150 lines
```

### A2: `utils/logger.py`

```
Standard Python logging setup:
- Console handler (tqdm-friendly)
- File handler (run.log)
- Structured format: [timestamp] [phase] [level] message

LOC estimate: ~40 lines
```

### A3: `utils/checkpoint.py`

```
Save/load BoTorch state:
- torch.save/load wrapper
- Fields: iteration, train_X, train_Y, best, config_hash, timestamp
- Resume detection (compare config_hash)

LOC estimate: ~60 lines
```

### A4: `llm_advisor.py`

```
Claude API integration:
- anthropic.Anthropic() client
- ask(context, question) → str | None
- Call count tracking + max_calls limit
- Fallback when disabled/maxed

Test: mock API call
LOC estimate: ~50 lines
```

### A5: `requirements.txt`

```
torch>=2.2.0
mace-torch>=0.3.0
fairchem-core>=1.0.0
botorch>=0.9.0
gpytorch>=1.11
ase>=3.22.0
pymatgen>=2024.1.0
numpy>=1.24
pandas>=2.0
matplotlib>=3.7
pydantic>=2.0
tqdm>=4.65
anthropic>=0.25.0
```

---

## Phase B: Structure Generator (Test local, no GPU needed for generation)

### B1: `structures/slab_builder.py`

```
Functions:
- build_ni_alloy_slab(dopant_type, dopant_percent, size, vacuum) → Atoms
- Set constraints (fix bottom 2 layers)
- Set tags (0=bulk, 1=surface for OC20 compat)
- Random substitution with seed

Test: build pure Ni, build NiMo20 → check atom counts, symbols, constraints
Source: structure-generator-spec.md (full code provided)
LOC estimate: ~80 lines
```

### B2: `structures/shell_builder.py`

```
Functions:
- build_graphene_layers(n_layers, vacancy%, n_doping%, cell_xy, z_start, seed) → Atoms
- Hexagonal lattice generation (commensurate with Ni 4×4)
- AB stacking for multilayer
- Random vacancy removal
- Random N substitution
- Tag=2 for OC20 compat

Test: pristine sheet (32 atoms), 10% vacancy (~29 atoms), 5% N (~1-2 N)
Source: structure-generator-spec.md (full code provided)
LOC estimate: ~100 lines
```

### B3: `structures/ni_at_c_generator.py`

```
Functions:
- build_ni_at_c_structure(**params) → Atoms (combined slab + shell)
- build_neb_structures(structure, molecule) → (initial, final)
- validate_structure(atoms) → {valid, issues, n_atoms, min_distance}
- generate_structure_deterministic(params, seed) → Atoms

Test: full structure → validate → pass; NEB structures → H₂ outside/inside
Source: structure-generator-spec.md (full code provided)
LOC estimate: ~120 lines
```

---

## Phase C: Runners (NEED GPU to test, but can write + mock test local)

### C1: `runners/mace_runner.py`

```
Class MACERunner:
- __init__(model="medium", device="cuda")
- run_neb(initial, final, n_images=5, fmax=0.05) → barrier_eV
- run_md(atoms, T_K, steps, timestep_fs) → intact_ratio
- single_point(atoms) → energy_eV

Error handling: NEB not converge → return None + error msg
Source: tool-apis-reference.md (full NEB + MD code)
LOC estimate: ~120 lines
```

### C2: `runners/mace_ensemble.py`

```
Class EnsembleRunner:
- __init__(device="cuda")
- predict_with_uncertainty(atoms, property) → {mean, std, confident, predictions}
- Load 3 MACE models (small, medium, large)
- Confidence threshold from config

Source: level2-engine-design.md (code snippet provided)
LOC estimate: ~70 lines
```

### C3: `runners/oc20_runner.py`

```
Class OC20Runner:
- __init__(model="uma-s-1p2", device="cuda")
- predict_h_adsorption(slab, adsorbate="H") → delta_G_H_eV
- relax_slab(slab, fmax) → relaxed_slab
- Build slab + add H adsorbate + relax + compute ΔG_H*

Source: tool-apis-reference.md (full adsorption code)
LOC estimate: ~100 lines
```

### C4: `runners/jdftx_runner.py`

```
Class JDFTxRunner:
- __init__(config)
- generate_input(atoms, solvation, potential) → input_file_str
- run(input_path) → subprocess call
- parse_output(output_path) → energy_eV
- she_to_mu(V_she) → Hartrees

Source: tool-apis-reference.md (input format + helper)
LOC estimate: ~100 lines
```

---

## Phase D: Pipeline Phases (NEED GPU, core logic)

### D1: `phases/calibration.py`

```
Function: run_calibration(config, runners) → CalibrationReport
- Run OC20 benchmarks (Pt+H, Ni+H)
- Run MACE benchmarks (graphene MD, Ni lattice)
- Compare vs expected → compute MAE
- PASS/FAIL decision

Source: level2-engine-design.md (Phase 0 section, benchmarks defined in config)
LOC estimate: ~100 lines
```

### D2: `phases/coarse_filter.py`

```
Function: coarse_filter(config, mace_runner) → list[params]
- Generate 100 random structures
- MACE single-point energy each
- Filter top 30% (lowest energy/atom)
- Return filtered params list

Source: level2-engine-design.md (code snippet provided)
LOC estimate: ~50 lines
```

### D3: `phases/screening.py` (LARGEST file)

```
Function: run_screening(config, runners, state) → Results
- Main BO loop (8 init + 17 iterations)
- For each candidate: generate → OC20 → MACE NEB × 2 → MACE MD → score
- Ensemble uncertainty check
- Failure detection + logging
- LLM trigger checks (failure rate, stalled)
- Checkpoint save every iteration
- Return all results

Source: level2-engine-design.md + botorch_loop code
LOC estimate: ~250 lines
```

### D4: `phases/dft_feedback.py`

```
Function: dft_feedback_loop(config, results, jdftx_runner) → UpdatedResults
- Select top N
- Run JDFTx for each
- Feed results back (weight 5×)
- BoTorch re-optimize
- Iterate max 3 rounds

Source: level2-engine-design.md (DFT feedback section)
LOC estimate: ~120 lines
```

---

## Phase E: Analysis + Reports

### E1: `analysis/failure_analyzer.py`

```
Class FailureAnalyzer:
- analyze(params, failure_type, details) → constraint dict
- Failure modes: shell_collapse, h2_blocked, o2_leaks, neb_no_converge, alloy_unstable
- Return BoTorch-compatible constraint

Source: level2-engine-design.md (failure modes + logic)
LOC estimate: ~80 lines
```

### E2: `analysis/verification.py`

```
Function: run_verification(results, config) → VerificationReport
- 7 checks: sanity, convergence, cross-tool, ensemble, perturbation, literature, consistency
- Each check → pass/fail + detail

Source: level2-engine-design.md (7-step pipeline)
LOC estimate: ~150 lines
```

### E3: `analysis/trust_scorer.py`

```
Function: compute_trust_score(verification_report) → "A"|"B"|"C"|"D"|"F"
- Scoring logic from design doc

LOC estimate: ~40 lines
```

### E4: `utils/reporter.py`

```
Functions:
- generate_results_csv(results) → save CSV
- generate_ranked_md(results) → save markdown
- generate_pareto_plot(results) → save PNG
- generate_calibration_report(cal_result) → save MD
- generate_verification_report(ver_result) → save MD

Source: output formats defined in design doc
LOC estimate: ~150 lines
```

---

## Phase F: Entry Point

### F1: `run.py`

```
main(config_path, resume_from, skip_calibration):
  1. Load config (Phase A)
  2. Init runners (Phase C)
  3. Calibration (Phase D1)
  4. Coarse filter (Phase D2)
  5. Screening (Phase D3)
  6. Verification (Phase E)
  7. DFT feedback (Phase D4, optional)
  8. Reports (Phase E4)

CLI args: --config, --resume, --skip-calibration, --phase-only
LOC estimate: ~80 lines
```

---

## Implementation Order (Critical Path)

```
Week 1: Phase A (foundation) + Phase B (structures)
  Day 1: config_schema.py + requirements.txt
  Day 2: utils/logger.py + utils/checkpoint.py + llm_advisor.py
  Day 3: slab_builder.py + shell_builder.py
  Day 4: ni_at_c_generator.py + all structure tests
  Day 5: Integration test: config → generate structure → validate

Week 2: Phase C (runners) + Phase D (pipeline)
  Day 1: mace_runner.py + mace_ensemble.py
  Day 2: oc20_runner.py
  Day 3: calibration.py + coarse_filter.py (test with GPU)
  Day 4: optimizer/botorch_loop.py
  Day 5: screening.py (main loop, largest file)

Week 3: Phase D continued + Phase E + F
  Day 1: jdftx_runner.py
  Day 2: dft_feedback.py
  Day 3: failure_analyzer.py + verification.py + trust_scorer.py
  Day 4: reporter.py
  Day 5: run.py + end-to-end test
```

---

## Testing Strategy

```
Phase A+B: Test LOCAL (no GPU)
  - pytest: config validation, structure generation, atom counts
  - Run: pytest tests/ (any machine)

Phase C: Test with GPU (mock + real)
  - Mock test: fake calculator → verify flow logic
  - Real test: 1 structure × MACE → verify output format
  - Run: pytest tests/ --gpu (on cloud VM)

Phase D+E: Integration test (GPU required)
  - Mini config: 2 init + 3 iterations (instead of 8+17)
  - Verify: calibration passes, screening produces results, reports generate
  - Run: python run.py --config test_config.json

Full test: Real config (4-12 hours)
  - Run actual pipeline with carbon-shell-config.json
  - Verify end-to-end
```

---

## File Size Summary

```
Total estimated: ~1,740 LOC

Phase A (foundation):    ~300 LOC
Phase B (structures):    ~300 LOC
Phase C (runners):       ~390 LOC
Phase D (pipeline):      ~520 LOC
Phase E (analysis):      ~420 LOC
Phase F (entry):         ~80 LOC
Tests:                   ~300 LOC (separate)
─────────────────────────────────
Grand total:             ~2,040 LOC (including tests)
```

---

## Risks

| Risk | Mitigation |
|------|-----------|
| OC20 model API change (v1 vs v2) | Pin fairchem-core version in requirements |
| MACE NEB diverge often | Max steps + fallback (return None, log failure) |
| BoTorch GP numerical instability | Always float64, Normalize + Standardize transforms |
| JDFTx not installed on cloud | Phase 2 optional (config: when="skip") |
| Graphene lattice mismatch with Ni | 1.2% strain acceptable, document in code |
| Memory OOM on T4 (16GB) | Recommend L4/A100; add memory check at start |
