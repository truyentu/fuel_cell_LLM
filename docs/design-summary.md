# AI Scientist Pipeline — Design Summary

> Hệ thống AI-driven R&D tìm kiếm chất xúc tác PGM-free cho AEMFC
> Version: 1.0 | Date: 2026-06-04

---

## 1. Mục Tiêu

```
Tìm chất xúc tác KHÔNG DÙNG Pt cho pin nhiên liệu anion exchange membrane (AEMFC):

Target DOE 2030:
  - Peak power ≥600 mW/cm² (H₂/air)
  - Durability ≥2,000 giờ
  - PGM loading = 0 g/kW

Hai hướng:
  A) Tối ưu Ni@C hiện tại (shell engineering)
  B) Tìm Ni@X alloy mới (tự kháng oxy hóa, có thể bỏ shell)
```

---

## 2. Kiến Trúc Hệ Thống

```
USER (Project Director)
  │ upload papers, chọn hướng, approve decisions
  │
LEVEL 0: KNOWLEDGE EXTRACTION
  │ NotebookLM (52 papers) + SynTERRA DB (33K recipes) + MatSciBERT (NER)
  │ Output: structured knowledge (facts, parameters, recipes)
  │
LEVEL 1: AI SCIENTIST (Claude as brain)
  │ Skills: /scientist start|digest|search|plan|review
  │ Reviewer: subagent adversarial audit (4-step, score A-F)
  │ Output: config.json + plan.md → rnd/ folder
  │
LEVEL 2: COMPUTE ENGINE (Cloud GPU)
  │ Phase 0: Calibration (verify models trước khi tin)
  │ Phase 1a: CHGNet filter (loại unstable alloys)
  │ Phase 1b: OC20 + MACE + BoTorch loop (screen + optimize)
  │ Phase 2: JDFTx validate (trong electrolyte thật)
  │ LLM-in-loop: Claude API gọi khi stuck
  │ Output: ranked_candidates.md + results.csv
  │
LEVEL 3: LAB VALIDATION
  │ Synthesize → Characterize (XRD, XPS, Raman) → Test cell
  │ Feed back → Level 2 re-optimize → converge
  │
RESULT: Optimal catalyst + synthesis recipe + publication/patent
```

---

## 3. Tools — Mỗi Tool Giải Bài Toán Gì

### 3.1 Brain + Orchestration

| Tool | Vai trò | Tại sao |
|------|---------|---------|
| **Claude API** | Brain chính — reasoning, planning, orchestration | Multi-step reasoning tốt nhất, anti-hallucination |
| **NotebookLM** | Paper knowledge store (≈ ChemCrow LitSearch) | Pre-loaded PDFs + vector search, grounded answers |

### 3.2 Knowledge Extraction

| Tool | Vai trò | Tại sao |
|------|---------|---------|
| **MatSciBERT** | NER: extract structured data từ papers | "calcined 350°C 2h Ar" → JSON {temp:350, time:2, gas:Ar} |
| **SynTERRA DB** | Lookup synthesis recipes (33K entries) | Tìm recipe Ni-Mo, Ni-Fe đã publish |
| **Materials Project API** | Query 150K+ materials properties | Check alloy existence, lattice params |

### 3.3 Compute — 3 Tools Cho 3 Câu Hỏi Khác Nhau

```
Câu hỏi 1: "Alloy này tồn tại được không?"
  → CHGNet (hoặc GNoME 520K data lookup)
  → Predict: formation energy → stable/unstable

Câu hỏi 2: "Bề mặt alloy này xúc tác HOR tốt không?"
  → OC20/fairchem
  → Predict: H adsorption energy → close to Pt?

Câu hỏi 3: "Carbon shell bảo vệ được không? H₂ qua? O₂ chặn?"
  → MACE (NEB barrier + MD stability)
  → Predict: diffusion barriers, shell integrity at 70°C
```

| Tool | Bài toán | Input | Output |
|------|----------|-------|--------|
| **CHGNet** | Alloy stable? | Crystal structure | Formation energy (eV/atom) |
| **OC20** | HOR activity? | Slab + H adsorbate | ΔG_H* (eV) |
| **MACE** | Shell protection? | Ni@C full structure | NEB barrier (eV), MD intact ratio |
| **JDFTx** | Validate in KOH? | Slab + solvation model | Energy in electrolyte (eV) |

### 3.4 Optimization

| Tool | Vai trò |
|------|---------|
| **BoTorch** | Bayesian multi-objective optimization (suggest next candidate) |
| **Claude API** (in-loop) | Adjust strategy khi failure rate cao hoặc stalled |

### 3.5 Optional / Future

| Tool | Vai trò | Khi nào dùng |
|------|---------|-------------|
| **ChemLLM** (7B) | Predict reactions, SMILES conversion | Nếu cần chemistry-specific tasks |
| **ChemCrow** framework | Agent + 18 tools reference | Architecture inspiration |
| **GNoME data** (520K) | Lookup stable crystals | Phase 1a filter |

---

## 4. Pipeline Chi Tiết — Hướng A (Ni@C Shell Optimization)

```
1000 random configs (dopant × layers × vacancy × N-doping)
    │
    ▼ [Phase 1a: CHGNet] loại alloy unstable
300 candidates
    │
    ▼ [Phase 1b: OC20] rank HOR activity (bare surface + H)
    ▼ [Phase 1b: MACE] NEB H₂/O₂ barrier + MD stability (full Ni@C)
    ▼ [Phase 1b: BoTorch] optimize multi-objective (25 iterations)
    ▼ [Phase 1b: Ensemble] 3 MACE sizes → uncertainty estimate
Top 5 (ranked, with confidence)
    │
    ▼ [Phase 2: JDFTx] validate in KOH 7M, 0.3V vs SHE
Top 3 (DFT-confirmed)
    │
    ▼ [Level 3: Lab] synthesize + test
Result
```

### Search Space (Hướng A)

| Variable | Range | Source |
|----------|-------|--------|
| Dopant type | Mo, Fe, Co, none | [REASONING] NiMo > NiFe > NiCo for HOR |
| Dopant % | 0-30% | [REASONING] >30% destabilizes FCC |
| Shell layers | 1-3 | [FACT] Paper tested 1-3 |
| Vacancy % | 0-20% | [REASONING] >20% unstable |
| N-doping % | 0-10% | [REASONING] >10% distorts lattice |

### Targets

| Metric | Direction | Threshold | Source |
|--------|-----------|-----------|--------|
| H adsorption | Minimize |ΔG_H*| | ~0 eV (thermoneutral) | Sabatier principle |
| H₂ barrier | Minimize | < 0.3 eV | H₂ kinetic diameter 0.29 nm |
| O₂ barrier | Maximize | > 0.8 eV | O₂ kinetic diameter 0.35 nm |
| Shell stability | Maximize | > 95% intact | 70°C operational temp |

---

## 5. Pipeline Chi Tiết — Hướng B (Tìm Ni@X Mới)

```
Khác Hướng A: Tìm alloy TỰ KHÁNG OXY HÓA (không cần shell)

Search space:
  - Alloy: Ni-Mo, Ni-Cu, Ni-Co, Ni-W, Ni-Mn, Ni-Mo-Cu (ternary)
  - Stoichiometry: Ni₃X, Ni₂X, NiX, Ni₃XY...
  - Surface facets: (111), (100), (110)

Targets:
  - HOR activity: ΔG_H* close to 0
  - Oxidation resistance: potential > +0.3V vs RHE (CRITICAL — từ Cornell paper)
  - Bulk stability: formation energy below convex hull

Tools thay đổi:
  - CHGNet: check alloy bulk stability
  - OC20: screen HOR activity
  - JDFTx: check oxidation potential IN KOH (không chỉ vacuum)
  - MACE NEB/MD: KHÔNG CẦN (không có shell)
  - SynTERRA: lookup recipe cho alloy composition

Status: Research phase — cần define config.json
```

---

## 6. Verification & Trust

### Trust Hierarchy

```
WEAKEST ─────────────────────────────────── STRONGEST
LLM reasoning → ML predict → DFT (JDFTx) → Experiment
```

### Engine Verification (7-Step)

| Step | Check | Reliability |
|------|-------|-------------|
| 1 | Physical sanity (energy range, bond lengths) | 100% |
| 2 | BoTorch convergence | 100% |
| 3 | Cross-tool consistency (OC20 vs MACE) | 90% |
| 4 | Ensemble agreement (3 MACE models) | 85% |
| 5 | Perturbation test (±10% params → score stable?) | 80% |
| 6 | Literature comparison (match known trends?) | 70% |
| 7 | Internal consistency (numbers don't contradict) | 80% |

### Trust Score

```
A: All pass + DFT confirms + literature agrees → GO TO LAB
B: Auto checks pass + literature agrees → Consider JDFTx first
C: Most pass, 1-2 warnings → Investigate before lab
D: Multiple warnings → Debug pipeline
F: Sanity/calibration fail → DO NOT USE
```

---

## 7. Anti-Hallucination Framework

### Level 1 (AI Scientist)

```
- Mọi claim phải tag: [FACT + source] / [REASONING] / [UNVERIFIED]
- NotebookLM = grounded (chỉ trả lời từ papers)
- Reviewer audit: structural + source + spot-check + consistency
- [UNVERIFIED] data KHÔNG được feed vào Level 2 compute
```

### Level 2 (Engine)

```
- Phase 0 Calibration: verify model trước khi tin
- Ensemble: 3 models disagree = flag uncertainty
- Results = RANKING (tin được), không phải absolute numbers (sai ±0.15 eV)
- Trust Score gate: <B thì KHÔNG vào lab
```

---

## 8. Inspired By Papers (Validated Approaches)

| Paper | Insight áp dụng | Trong pipeline |
|-------|-----------------|---------------|
| GNoME (DeepMind) | GNN filter + ensemble uncertainty | Phase 1a + ensemble |
| A-Lab (Berkeley) | Learn from failures, active feedback | Failure analyzer + DFT feedback |
| MatterGen (Microsoft) | Coarse pre-filter trước BO | Phase 1a |
| Pt Intermetallic | Active learning DFT → retrain | Phase 2 feedback loop |
| ChemCrow (EPFL) | LLM brain + tools architecture | Claude + runners |
| Coscientist (CMU) | Self-correct + hardware control | LLM-in-loop advisor |
| Bayesian GDL (HKUST) | BO optimize physical structure | BoTorch multi-objective |
| CVAE ORR (Science Tokyo) | Generate + score loop | BoTorch suggest → evaluate → loop |

---

## 9. Hardware & Cost

| Phase | Hardware | Time | Cost |
|-------|----------|------|------|
| Level 1 (AI Scientist) | Local PC (any) | Minutes | ~$0.50 API |
| Level 2 Phase 0 | Cloud L4 GPU | 30 min | ~$0.35 |
| Level 2 Phase 1 | Cloud L4 GPU | 4-12h | ~$3-8 |
| Level 2 Phase 2 | Cloud CPU 16-core | 1-3 days | ~$10-30 |
| **Level 2 Total** | | | **~$15-40** |
| Level 3 (Lab, VN) | Lò nung + CV + XPS | 1-3 months | $3,000-5,000 |

---

## 10. Files & Code Đã Có

### Skills

```
~/.claude/skills/ai-scientist/SKILL.md        ← Level 1 orchestration
~/.claude/skills/scientist-reviewer/SKILL.md   ← Adversarial audit
```

### Engine Code

```
hydrogen_fuel_cell/fuel-cell-engine/           ← Level 2 (19 files, end-to-end tested mock)
```

### Documentation

```
hydrogen_fuel_cell/rnd/
├── landscape.md                    ← Current state-of-art Ni@C
├── gaps.md                         ← Knowledge gaps + keywords
├── decisions.md                    ← Decision log
├── level1-output-format.md         ← Config.json schema
├── level2-engine-design.md         ← Engine architecture
├── structure-generator-spec.md     ← How to build atomic structures
├── tool-apis-reference.md          ← MACE, OC20, BoTorch, JDFTx code
├── engine-implementation-plan.md   ← Phase A-F build plan
└── experiments/
    ├── carbon-shell-plan.md        ← Experiment plan (human readable)
    └── carbon-shell-config.json    ← Config for engine (machine readable)

hydrogen_fuel_cell/docs/
└── research-open-source-tools.md   ← All tools availability + GNN comparison
```

---

## 11. Key Corrections Từ Research

| Claim phổ biến | Thực tế |
|---------------|---------|
| "AI tự crawl papers" | ❌ Cần pre-built DB / pre-loaded PDFs |
| "GNoME thay tất cả" | ❌ GNoME = stability only, cần OC20 + MACE cho catalysis + shell |
| "Galactica thay Claude" | ❌ Hallucinate, dead project |
| "MatBERT = database papers" | ❌ MatBERT = model weights, cần text input riêng |
| "ML cho exact numbers" | ❌ ML cho RANKING (tin được), numbers ±0.15 eV |
| "NotebookLM outdated" | ❌ NotebookLM ≈ ChemCrow LitSearch (same concept) |

---

## 12. Bước Tiếp Theo

```
Immediate:
  □ Deploy engine lên Cloud GPU → chạy Hướng A (shell optimization)
  □ Download SynTERRA + GNoME data → prep Hướng B

1-2 tuần:
  □ Nhận Level 2 results → interpret → chọn lab candidates
  □ Define config.json cho Hướng B (alloy without shell)

1-3 tháng:
  □ Lab synthesis top 3 (VN)
  □ Feed results back → Level 2 round 2
  □ Fine-tune MACE trên actual Ni@C data

6-12 tháng:
  □ Converge → optimal catalyst found
  □ Patent + publish
  □ Scale up
```
