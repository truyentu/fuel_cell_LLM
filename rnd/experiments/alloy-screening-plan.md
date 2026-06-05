# Experiment Plan — Hướng B: Ni-X Alloy Screening (Without Shell)

| Field | Value |
|-------|-------|
| Date | 2026-06-05 |
| Phase | Discovery |
| Goal | Tìm hợp kim Ni-X tự kháng oxy hóa (không cần carbon shell) |
| Config file | rnd/experiments/alloy-screening-config.json |
| Estimated compute | 6-10h (Phase 1) + 40h (Phase 2 JDFTx) |
| Estimated cost | ~$8 (Phase 1) + ~$12-30 (Phase 2) |

---

## Tại Sao Chạy Hướng B

Hướng A (Ni@C shell optimization) giải quyết durability bằng carbon shell bảo vệ.
Hướng B hỏi: "Có alloy Ni-X nào TỰ kháng oxy hóa > +0.3V mà KHÔNG CẦN shell?"

Nếu tìm được → đơn giản hóa sản xuất (bỏ CVD shell step), giảm cost, tăng durability.

---

## Targets

| Target | Metric | Direction | Threshold | Source | Priority |
|--------|--------|-----------|-----------|--------|----------|
| HOR activity | ΔG_H* (H adsorption) | minimize_abs | < 0.15 eV from 0 | [REASONING] Sabatier thermoneutral | 1 |
| Oxidation resistance | ΔE_oxide (surface oxide formation) | maximize | > 0.5 eV/atom (harder to oxidize) | [REASONING] Proxy — higher = more resistant | 2 |
| Bulk stability | Formation energy | minimize | < 0.05 eV above hull | [FACT] Standard convex hull criterion | 3 |

### ⚠️ GAP: Oxidation Resistance

```
Notebook KHÔNG CÓ DFT data cho NiMo/NiW oxidation potential.
Paper Cornell chỉ có: Ni@C threshold = +0.3V, Ni/C = +0.2V

Approach chọn: PROXY METRIC
  ΔE_oxide = E(NiX_surface + O) - E(NiX_surface) - E(O_ref)
  → Số ÂM = dễ oxidize (xấu)
  → Số DƯƠNG hoặc ít âm = khó oxidize (tốt)

Proxy này KHÔNG = electrochemical oxidation potential thật.
JDFTx Phase 2 sẽ validate top 5 TRONG KOH + applied potential.

Confidence: LOW cho proxy, HIGH cho JDFTx validation
```

---

## Search Space

| Variable | Range | Type | Rationale | Source |
|----------|-------|------|-----------|--------|
| dopant_type | Mo, W, Fe, Co, Cu | categorical | Top HOR candidates từ literature + GNoME | [REASONING] |
| dopant_percent | 5–50% | float, step 5 | Wider range — Hướng B cho phép Ni-rich HOẶC X-rich | [REASONING] |
| surface_facet | 111, 100, 110 | categorical | Different facets = different activity + oxidation | [FACT] Standard crystallography |

**KHÔNG CÓ shell variables** (n_layers, vacancy, N-doping) — Hướng B = bare alloy surface.

### GNoME + SynTERRA Findings

```
GNoME novel stable binary Ni-X:
  ✅ Ni8Mo (tetragonal, E_form=-0.047) — Ni-rich Mo alloy
  ✅ Ni8W (E_form=-0.068) — Ni-rich W alloy, MOST STABLE
  ✅ Cu4Ni (E_form=-0.011) — Cu-rich

GNoME containing (broader):
  Ni-Co: 5,142 | Ni-Cu: 2,076 | Ni-Fe: 1,731
  Ni-Mn: 1,285 | Ni-Mo: 1,002 | Ni-W: 642

SynTERRA: Chủ yếu OXIDES — ít applicable cho metallic HOR
  ⚠️ SynTERRA recipes = oxide synthesis, KHÔNG phải metallic alloy
  → Lab sẽ cần: arc melting, sputtering, hoặc co-reduction
```

---

## Pipeline (Khác Hướng A)

```
1000 random Ni-X alloy surfaces (dopant × percent × facet)
    ↓
[Phase 1a: CHGNet] Predict bulk stability → loại unstable
~300 candidates
    ↓
[Phase 1b: OC20] Predict H adsorption → rank HOR activity
[Phase 1b: MACE] Predict O adsorption → rank oxidation resistance (PROXY)
[Phase 1b: BoTorch] Multi-objective optimize (HOR × oxidation resistance)
    ↓
Top 10
    ↓
[Phase 2: JDFTx] Validate TRONG KOH + applied 0.3V
  → Check: alloy vẫn metallic ở +0.3V? +0.4V? +0.5V?
  → Ground truth cho oxidation resistance
    ↓
Top 3 (DFT confirmed)
    ↓
Lab: Arc melt / sputtering → electrochemical test
```

### Khác Biệt Vs Hướng A

| | Hướng A (Ni@C) | Hướng B (Bare Alloy) |
|---|---|---|
| Structure | Slab + graphene shell | Slab only (bare surface) |
| MACE task | NEB barrier (H₂/O₂ through shell) | O adsorption energy (oxidation proxy) |
| Key target | Shell protection | Self oxidation resistance |
| JDFTx role | Validate in KOH (Phase 2) | **CRITICAL**: check oxidation potential |
| Lab synthesis | MOF pyrolysis + CVD | Arc melt / sputtering (simpler!) |

---

## Risks & Assumptions

- [REASONING] "Higher ΔE_oxide = better oxidation resistance" — proxy, NOT proven
- [GAP] No papers confirm NiMo/NiW shift oxidation above +0.3V (chỉ hypothesis)
- [REASONING] OC20 trained on vacuum surfaces — alkaline HOR may differ
- [FACT] JDFTx trong KOH sẽ validate (Phase 2) — nhưng chỉ cho top 5-10
- [REASONING] NiW may be promising (GNoME E_form most negative = most stable)

---

## Confidence: LOW-MEDIUM

```
LOW vì:
  - Oxidation target = PROXY (chưa verify bằng papers)
  - Notebook KHÔNG có data confirm approach
  - Hướng B = more speculative than Hướng A

MEDIUM vì:
  - HOR activity target well-established (Sabatier)
  - Bulk stability from CHGNet/GNoME = reliable
  - JDFTx Phase 2 sẽ provide ground truth
  - Nếu JDFTx confirm proxy works → confidence tăng lên HIGH

Suggest: Chạy Hướng B PARALLEL với Hướng A
  Hướng A = safer (có paper data)
  Hướng B = higher reward nếu thành công (simpler manufacturing)
```
