# Fuel Cell LLM — AI-Driven Catalyst Discovery for AEMFC

## Overview

Computational engine for discovering PGM-free anode catalysts for Alkaline Exchange Membrane Fuel Cells (AEMFC). Uses ML foundation models + Bayesian optimization to screen Ni@C (Nickel-alloy core + graphene shell) catalyst compositions.

## Architecture

```
Phase 1a: Coarse Filter (CHGNet + GNoME)
    → 100 random compositions → 30 stable candidates

Phase 1b: Bayesian Optimization Screening (MACE + OC20 + BoTorch)
    → NEB barriers (H2/O2 diffusion)
    → MD stability (shell integrity at 343K)
    → HOR activity (delta_G_H)

Phase 2: DFT Validation (JDFTx)
    → Top-3 candidates verified with high-fidelity DFT
```

## Models Used

| Model | Purpose | Level |
|-------|---------|-------|
| CHGNet | Coarse stability filter | L1 |
| GNoME | Cross-reference with known stable materials | L1 |
| MACE-MP-medium | NEB barriers + MD stability | L2 |
| OC20 (fairchem) | HOR activity prediction | L2 |
| BoTorch | Multi-objective Bayesian optimization | L2 |
| JDFTx | DFT validation (optional) | L3 |

## Search Space (Direction A: Carbon Shell Optimization)

- **Dopant type:** Fe, Co, Cu, Mo, W, none
- **Dopant %:** 5–45%
- **Graphene layers:** 1–4
- **Vacancy %:** 0–20%
- **N-doping %:** 0–16%

## Optimization Targets

1. `hor_activity` → minimize |ΔG_H| (closer to 0 = better HOR)
2. `h2_barrier` → minimize (H2 must penetrate shell easily)
3. `o2_barrier` → maximize (O2 must NOT penetrate — protect Ni core)
4. `shell_stability` → maximize (shell intact at 70°C operating temp)

## Project Structure

```
fuel-cell-engine/          # Main compute engine
├── run.py                 # Entry point
├── config_schema.py       # Config validation
├── structures/            # Crystal structure generators
│   ├── ni_at_c_generator.py   # Ni@C slab + shell builder
│   ├── slab_builder.py
│   └── shell_builder.py
├── runners/               # ML model wrappers
│   ├── mace_runner.py     # MACE NEB + MD
│   ├── oc20_runner.py     # OC20/fairchem HOR
│   ├── chgnet_runner.py   # CHGNet stability
│   └── jdftx_runner.py   # DFT runner
├── optimizer/             # BO loop
│   └── botorch_loop.py
├── phases/                # Pipeline phases
│   ├── coarse_filter.py
│   ├── screening.py
│   ├── calibration.py
│   └── dft_feedback.py
├── analysis/              # Post-processing
│   ├── verification.py
│   ├── trust_scorer.py
│   └── failure_analyzer.py
├── utils/
├── data/                  # Reference databases
│   ├── gnome_repo/        # GNoME model code
│   ├── gnome_data/        # GNoME stable materials DB
│   └── synterra_repo/     # SynTERRA text mining
└── colab_fuel_cell_engine.ipynb  # Colab notebook (T4 GPU)

rnd/                       # Research & experiment configs
├── experiments/
│   └── carbon-shell-config.json
├── landscape.md
├── gaps.md
└── decisions.md

research/                  # Literature research notes
docs/                      # Design docs & specs
```

## Quick Start (Google Colab T4)

1. Upload `fuel-cell-engine/` to Google Drive
2. Open `colab_fuel_cell_engine.ipynb` in Colab
3. Select T4 GPU runtime
4. Run cells sequentially:
   - Mount Drive + install dependencies
   - Verify GPU + models (MACE, CHGNet, fairchem)
   - Configure experiment
   - Run quick test (2 candidates, ~1h)
   - Run full pipeline (33 candidates, ~15-30h)

## Requirements

- Python 3.10+
- CUDA GPU (T4 or better)
- See `fuel-cell-engine/requirements.txt`

Key dependencies:
- `mace-torch` (MACE foundation model)
- `chgnet` (CHGNet)
- `fairchem-core` (OC20)
- `botorch` (Bayesian optimization)
- `ase` (Atomic Simulation Environment)
- `torch`, `torch_geometric`

## Status

- [x] Engine architecture complete
- [x] CHGNet coarse filter working
- [x] MACE NEB barriers (H2 fix applied)
- [x] BoTorch multi-objective optimization
- [x] Verification pipeline + Trust Score
- [ ] OC20 real model (currently mock on some setups)
- [ ] JDFTx integration (requires compiled binary)
- [ ] O2 barrier geometry fix (flat orientation in narrow gap)

## License

Research use only.
