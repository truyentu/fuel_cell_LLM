# Level 2 Engine Design — Compute Pipeline

Date: 2026-06-03
Status: Design phase
Purpose: Python engine đọc config.json (Level 1) → chạy trên GPU → output ranked candidates

---

## Architecture Overview

```
config.json (Level 1)
    │
    ▼
┌──────────────────────────────────────────────────────┐
│  ENGINE (run.py)                                      │
│                                                       │
│  Phase 0: Calibration                                 │
│  Phase 1a: Coarse Filter (MatterGen inspired)         │
│  Phase 1b: Screening + Ensemble + Failure Learning    │
│  Phase 2: DFT Feedback Loop (Pt Intermetallic)        │
│  Verification: 7-step trust assessment                │
│                                                       │
│  Output: results.csv + ranked.md + trust score        │
└──────────────────────────────────────────────────────┘
```

---

## Trust Model

```
KHÔNG TIN: absolute numbers từ ML (±0.2-0.3 eV sai số)
CÓ THỂ TIN: ranking + trends (nếu qua calibration)
TIN ĐƯỢC: JDFTx validated results
GROUND TRUTH: chỉ có experiment (Level 3)

Engine value = "narrow 1000 candidates → 5" NHANH + RẺ
```

---

## Phase 0: Calibration (BẮT BUỘC)

Verify model TRƯỚC KHI tin predictions. PASS → tiếp. FAIL → STOP.

### Benchmarks

| System | Tool | Expected | Tolerance | Source |
|--------|------|----------|-----------|--------|
| Pt(111)+H | OC20 | -0.27 eV | ±0.15 | Nørskov benchmark |
| Ni(111)+H | OC20 | -0.45 eV | ±0.15 | DFT literature |
| Ni₃Mo(111)+H | OC20 | -0.33 eV | ±0.15 | DFT literature |
| Pristine graphene MD | MACE | intact=1.0 | ±0.01 | Physical certainty |
| 50% vacancy graphene MD | MACE | intact<0.5 | — | Physical certainty |
| Ni bulk lattice | MACE | 3.52 Å | ±0.05 | Experimental |

### Output
- `calibration_report.md`: PASS/FAIL + MAE per tool

---

## Phase 1a: Coarse Filter (MatterGen Inspired)

```
100 random structures → MACE small single-point → loại 70% unstable → ~30 survivors
```

- Timing: ~1 second (100 × 10ms)
- Cost: ~$0
- Impact: +5-10% accuracy (BoTorch starts with better initial set)

---

## Phase 1b: Screening (Core Loop)

### Execution Flow

```
For each candidate (from BoTorch):
  1. Generate structure (ASE/Pymatgen)
  2. OC20: H adsorption energy (HOR activity)     ← parallel
  3. MACE ensemble (3 sizes): NEB H₂ barrier      ← parallel
  4. MACE ensemble: NEB O₂ barrier                 ← parallel
  5. MACE: MD stability (10ps, 343K)              ← sequential after NEB
  6. Failure analysis (nếu fail)
  7. Combine scores + uncertainty
  8. BoTorch update → suggest next

Iterations: 8 init + 17 BO = 25 total
```

### Ensemble (GNoME Inspired)

Run MACE small + medium + large → mean ± std:
- std < 0.10 eV → CONFIDENT
- std > 0.10 eV → FLAG, deprioritize

Impact: +10-15%, giảm ~30% false positives

### Failure Learning (A-Lab Inspired)

Candidate fail → classify mode:
- `shell_collapse`: vacancy quá nhiều / layers quá ít
- `h2_blocked`: shell quá dày / quá ít defects
- `o2_leaks`: shell quá mỏng / quá nhiều defects
- `neb_no_converge`: structure bất ổn
- `alloy_unstable`: formation energy > 0

→ Feed constraints vào BoTorch → avoid dead-end regions

### Timing

```
Per candidate: ~10-15 min (NEB × 2 + MD + OC20)
Phase 1 total: ~4h (A100) | ~8h (L4) | ~12h (T4)
```

---

## Phase 2: DFT Feedback Loop (Pt Intermetallic Inspired)

```
Round 1: Top 5 → JDFTx (KOH, 0.3V) → results
Round 2: Feed DFT back (weight 5×) → BoTorch re-optimize → 5 new → JDFTx
Round 3: Iterate if still improving
Max 3 rounds.
```

### Validation Report

Compare OC20 ranking vs JDFTx ranking → Spearman ρ:
- ρ > 0.8 → OC20 ranking reliable
- ρ 0.5-0.8 → trust JDFTx ranking only
- ρ < 0.5 → OC20 unreliable for this system

### Timing & Cost

- Per candidate JDFTx: 2-8 giờ (16 cores)
- 3 rounds × 5 candidates: ~60-120 giờ (~$200-500)
- Impact: +15-20% accuracy

---

## Verification Pipeline (Auto, Sau Phase 1b)

| # | Method | Reliability | Cost | Checks |
|---|--------|-------------|------|--------|
| 1 | Sanity checks | 100% | $0 | Energy range, forces converged, no overlap |
| 2 | Convergence | 100% | $0 | Score flat last 5 iter? |
| 3 | Cross-tool | 90% | $0 | |OC20-MACE| < 0.15 eV? |
| 4 | Ensemble agreement | 85% | included | std < 0.10 for top 5? |
| 5 | Perturbation test | 80% | ~$50 | ±10% params → <20% score change? |
| 6 | Literature comparison | 70% | $0 | Match known trends from papers? |
| 7 | Internal consistency | 80% | $0 | Numbers don't contradict? |

### Trust Score

```
A: All pass + DFT confirms + literature agrees
B: Auto checks pass + literature agrees (no DFT yet)
C: Most pass, 1-2 warnings
D: Multiple warnings, inconsistencies
F: Sanity/calibration fail → DO NOT USE
```

---

## Accuracy Estimates

```
⚠️ ESTIMATES from papers. True accuracy only after lab validation.

Metric: P("Top 3 chứa best candidate")

| Pipeline Stage                     | Accuracy | Extra Cost |
|------------------------------------|----------|------------|
| Random guess (1000 candidates)     | 0.3%     | $0         |
| Basic (OC20+MACE+BoTorch)         | 65-75%   | ~$50-200   |
| + Coarse filter                    | 70-80%   | +$0        |
| + Ensemble uncertainty             | 75-85%   | +$50       |
| + Failure learning                 | 80-88%   | +$0        |
| + DFT feedback loop                | 90-95%   | +$200-500  |
| + Lab feedback (future)            | 98%+     | +$5000+    |
```

---

## Known Limitations

1. **Out-of-Distribution:** OC20 chưa thấy Ni@C → possible systematic bias
2. **Solvent Effect:** OC20+MACE = vacuum; thực tế = KOH 7M
3. **Kinetics:** Không predict degradation rate (145h→2000h)
4. **Manufacturing:** AI output "9% vacancy" nhưng lab có thể không control chính xác

---

## LLM-in-Loop: Claude API + GPU Hybrid

### Nguyên Tắc

```
Claude API giỏi: REASONING, interpret, adapt, read papers, plan
GPU engine giỏi: TÍNH TOÁN, simulate atoms, optimize toán học, batch

Rule: KHÔNG ép Claude tính physics. KHÔNG ép GPU reasoning.
      GPU chạy auto 90% thời gian. Claude can thiệp 10% khi CẦN.
```

### Phân Chia Trách Nhiệm

| Task | Ai chạy | Lý do |
|------|---------|-------|
| BoTorch suggest next point | GPU | Toán thuần, BoTorch > LLM |
| MACE NEB/MD | GPU | Physics calc, batch |
| OC20 adsorption | GPU | GNN inference |
| JDFTx solvation | GPU (CPU) | Heavy linear algebra |
| Diagnose failures | Claude API | Pattern recognition, creative |
| Adjust strategy khi stuck | Claude API | Domain reasoning |
| Interpret results | Claude API | Connect numbers → meaning |
| Compare vs literature | Claude API | Cross-reference papers |
| Plan lab experiments | Claude API | Integrate multiple knowledge |

### Triggers — Khi Nào Engine Gọi Claude

```
Engine chạy TỰ ĐỘNG (không gọi Claude):
  - BoTorch loop bình thường
  - Candidates pass/fail (failure rate < 30%)
  - Score đang improve
  - Sanity checks pass

Engine PAUSE + gọi Claude API:
  1. failure_rate > 30%
     → "30% fail. Modes: shell_collapse(6), h2_blocked(4). Adjust bounds?"

  2. score stalled 5+ iterations
     → "Stuck at 0.72. Best: NiMo15. Suggest new region?"

  3. phase_complete
     → "Phase 1 done. Results: [summary]. Interpret + plan next?"

  4. anomaly detected
     → "Candidate X: energy = -50 eV (abnormal). What happened?"

  5. ensemble high disagreement on top candidate
     → "Top 1 NiMo20: MACE small=-0.28, large=-0.55. Trust?"
```

### Config

```json
{
  "llm_in_loop": {
    "enabled": true,
    "api": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "triggers": {
      "high_failure_rate": {"threshold": 0.3},
      "convergence_stalled": {"n_iter_no_improve": 5},
      "phase_complete": true,
      "anomaly_detected": true,
      "ensemble_disagreement": {"std_threshold": 0.15}
    },
    "max_llm_calls": 5,
    "fallback_if_no_api": "continue_with_defaults",
    "context_includes": ["failure_log", "score_history", "current_bounds", "top_candidates"]
  }
}
```

### Implementation

```python
import anthropic

class LLMAdvisor:
    def __init__(self, config):
        self.client = anthropic.Anthropic()
        self.model = config["llm_in_loop"]["model"]
        self.enabled = config["llm_in_loop"]["enabled"]
        self.call_count = 0
        self.max_calls = config["llm_in_loop"]["max_llm_calls"]

    def ask(self, context: str, question: str) -> str | None:
        if not self.enabled or self.call_count >= self.max_calls:
            logger.warning("LLM advisor disabled or max calls reached")
            return None

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system="You are a materials science expert advising an automated catalyst screening pipeline for PGM-free AEMFC. Be concise. Output actionable parameters.",
            messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}]
        )
        self.call_count += 1
        logger.info(f"LLM call #{self.call_count}: {question[:50]}...")
        return response.content[0].text

# Trong screening loop:
if failure_rate > triggers["high_failure_rate"]["threshold"]:
    advice = advisor.ask(
        context=format_failure_log(failures, bounds, scores),
        question="High failure rate. Should I adjust search space bounds? Give new ranges."
    )
    if advice:
        new_bounds = parse_bounds(advice)  # extract numbers from LLM response
        optimizer.update_bounds(new_bounds)
        logger.info(f"Bounds updated per LLM advice: {new_bounds}")
```

### Cost Estimate (Ni@C Full Pipeline)

```
Claude API:
  Plan (1 call):                    ~$0.10
  Failure triggers (2-3 calls):     ~$0.15
  Phase complete (1 call):          ~$0.10
  Final interpretation (1 call):    ~$0.10
  ─────────────────────────────────────────
  Total Claude:                     ~$0.45

GPU (Google Cloud L4):
  Phase 0 calibration:  0.5h × $0.70 = $0.35
  Phase 1a filter:      ~0                = $0
  Phase 1b screening:   8h × $0.70   = $5.60
  Phase 2 JDFTx (CPU): 40h × $0.30  = $12.00
  ─────────────────────────────────────────
  Total GPU:                        ~$18.00

  GRAND TOTAL: ~$18.50 full pipeline
```

### Tại Sao Hybrid > Pure LLM hoặc Pure Engine

```
Pure LLM (Coscientist style):
  ❌ BoTorch toán học > LLM gut feeling cho optimization
  ❌ Chậm (+10% overhead mỗi iteration cho zero value)
  ❌ Không reproducible (stochastic)
  ❌ Đắt hơn ($1.25-2.50 extra, value ~$0)

Pure Engine (no LLM):
  ❌ Không adapt khi unexpected (coded failures only)
  ❌ Không interpret results (output numbers, not insights)
  ❌ Không compare vs literature
  ❌ Không plan next phase

Hybrid:
  ✅ BoTorch tính toán (optimal)
  ✅ Claude reasoning khi cần (adaptive)
  ✅ Reproducible (engine deterministic, LLM chỉ advise bounds)
  ✅ Rẻ ($0.45 Claude + $18 GPU)
  ✅ Best of both worlds
```

---

## Engine Code Structure

```
fuel-cell-engine/
├── run.py                          # Entry point
├── config_schema.py                # Pydantic validate
├── phases/
│   ├── calibration.py              # Phase 0
│   ├── coarse_filter.py            # Phase 1a
│   ├── screening.py                # Phase 1b
│   └── dft_feedback.py             # Phase 2
├── runners/
│   ├── oc20_runner.py
│   ├── mace_runner.py
│   ├── mace_ensemble.py            # 3 model sizes
│   └── jdftx_runner.py
├── analysis/
│   ├── failure_analyzer.py
│   ├── verification.py             # 7-step verify
│   └── trust_scorer.py             # A-F score
├── structures/
│   ├── slab_builder.py
│   ├── shell_builder.py
│   └── ni_at_c_generator.py
├── optimizer/
│   └── botorch_loop.py             # Multi-obj + weighted DFT
├── utils/
│   ├── checkpoint.py               # Save/resume
│   ├── logger.py
│   └── reporter.py                 # Generate reports + plots
├── requirements.txt
└── README.md
```

---

## run.py Flow

```python
def main(config_path, resume_from=None, skip_calibration=False):
    config = load_and_validate(config_path)

    # Phase 0
    if not skip_calibration:
        cal = run_calibration(config)
        if not cal.passed: sys.exit(1)

    # Phase 1a
    filtered = coarse_filter(config)

    # Phase 1b
    results = run_screening(config, filtered, resume_from)

    # Verification
    trust = run_verification(results, config)

    # Phase 2 (optional)
    if config["tools"]["validation"]["when"] != "skip":
        results = dft_feedback_loop(config, results)

    # Reports
    generate_reports(results, trust, config)
```

---

## Checkpoint & Resume

```
Mỗi iteration save: checkpoint.pt
  - iteration number
  - train_X, train_Y
  - best score + params
  - GP state

Resume: python run.py --config config.json --resume checkpoint.pt
```

---

## Hardware Requirements

| Phase | GPU | RAM | Time |
|-------|-----|-----|------|
| 0 (calibration) | 1× L4/T4 | 16 GB | 30-60 min |
| 1a (filter) | 1× any | 8 GB | ~1 second |
| 1b (screening) | 1× A100/L4 | 32 GB | 4-12 hours |
| 2 (JDFTx) | CPU 16-32 cores | 64 GB | 1-3 days |

---

## Deliverables

```
rnd/compute/<pipeline_name>/
├── calibration_report.md
├── coarse_filter_log.csv
├── results.csv
├── failure_analysis.md
├── ranked_candidates.md
├── dft_feedback_log.md
├── validation_report.md
├── verification_report.md    ← Trust Score A-F
├── pareto.png
├── best_candidate.xyz
├── checkpoint.pt
└── run.log
```

---

## Dependencies

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
```
