# Experiment Plan — Optimize Ni@C Carbon Shell for AEMFC

| Field | Value |
|-------|-------|
| Date | 2026-06-03 |
| Phase | Validation |
| Goal | Tìm optimal carbon shell configuration (layers, vacancy%, N-doping%) cho Ni-alloy@C AEMFC anode |
| Config file | [carbon-shell-config.json](carbon-shell-config.json) |
| Estimated compute | 4-12 giờ × 1 GPU (L4/A100) |
| Estimated cost | $5-15 (Phase 1) + $200-500 (Phase 2 JDFTx) |

---

## Tại Sao Chạy Plan Này

Ni@C AEMFC đạt 1.0 W/cm² nhưng chỉ bền 145 giờ. Nguyên nhân chính: carbon shell chưa tối ưu — hoặc quá kín (H₂ không qua) hoặc quá hở (O₂ vào oxidize Ni). Cần tìm sweet spot: shell cho H₂ qua nhưng chặn O₂, ổn định ở 70°C trong KOH.

Paper gợi ý "optimize thickness, defect size, defect density" nhưng CHƯA có ai scan systematic. Đây là gap mà AI compute lấp.

---

## Targets

| Target | Metric | Giá trị tốt | Direction | Source |
|--------|--------|-------------|-----------|--------|
| HOR activity | ΔG_H* (eV) | ≈ 0 eV (thermoneutral) | minimize abs value | [UNVERIFIED] Nørskov Sabatier principle, cần paper confirm |
| H₂ permeation | NEB barrier (eV) | < 0.3 eV | minimize | [REASONING] H₂ kinetic diameter 0.29nm, low barrier = fast permeation |
| O₂ blocking | NEB barrier (eV) | > 0.8 eV | maximize | [REASONING] O₂ diameter 0.35nm > H₂, must be blocked to prevent Ni oxidation |
| Shell stability | MD intact ratio | > 0.95 | maximize | [REASONING] Shell must survive at 343K (70°C) without collapse |

---

## Search Space

| Variable | Type | Range | Tại sao | Source |
|----------|------|-------|---------|--------|
| dopant_type | categorical | Mo, Fe, Co, none | [REASONING] Common HOR-active Ni alloys in alkaline |
| dopant_percent | float | 0–30%, step 5 | [REASONING] >30% destabilizes FCC structure |
| n_layers | int | 1–3 | [FACT] Paper tested "few layers graphitic carbon" — Source: Unveiling...Ni oxidation |
| vacancy_percent | float | 0–20%, step 2 | [FACT] Authors suggest optimize "defect size and density" — Source: same |
| n_doping_percent | float | 0–10%, step 2 | [REASONING] N-doping may stabilize shell + modify permeation selectivity |

### Fixed Conditions

| Condition | Value | Source |
|-----------|-------|--------|
| Temperature | 343 K (70°C) | [FACT] Stability test at 70°C — Source: Unveiling...Ni oxidation |
| Ni-C distance | 2.15 Å | [FACT] "2.15 Å separation from Ni surface" — Source: same |
| Potential threshold | 0.3 V vs RHE | [FACT] "metallic Ni stable up to 0.3V" — Source: same |
| Electrolyte (JDFTx) | KOH 0.1M → 7M | [FACT] "0.1M KOH" measured — Source: same |

---

## Pipeline

```
BoTorch suggest params → Generate Ni-alloy(111) slab + graphene shell
    ↓
OC20: bare Ni-alloy(111) + H → ΔG_H* (HOR activity proxy)
MACE (ensemble 3 sizes): NEB H₂ + NEB O₂ + MD stability
    ↓
Combined score → BoTorch update → next iteration
    ↓ (25 iterations)
Top 5 → JDFTx validate in KOH + 0.3V
```

---

## Risks & Assumptions

- [REASONING] Slab model ≈ nanoparticle surface (valid cho particle >2nm, curvature negligible)
- [REASONING] OC20 chưa train trên Ni-alloy surfaces → calibration Phase 0 sẽ detect nếu unreliable
- [REASONING] MACE trong vacuum ≠ trong KOH → JDFTx Phase 2 bridges gap
- [GAP] H adsorption optimal value: cần paper confirm Sabatier ΔG_H* ≈ 0 eV
- [GAP] N-doped graphene H₂/O₂ permeation data: chưa có trong notebook
- [REASONING] vacancy% > 20 sẽ destabilize graphene — capped at 20%

---

## Confidence: MEDIUM

| Aspect | Confidence | Lý do |
|--------|-----------|-------|
| Fixed conditions | HIGH | Trực tiếp từ paper |
| Search space ranges | MEDIUM-HIGH | Phần lớn từ paper + physical reasoning |
| Target thresholds | MEDIUM | H₂ barrier <0.3 là reasoning, chưa có exact validation |
| HOR reference value | LOW | [UNVERIFIED] — cần paper confirm ΔG_H* ≈ 0 |
| Overall | MEDIUM | 1 UNVERIFIED target, nhưng không block screening (chỉ ảnh hưởng ranking interpretation) |

---

## ⚠️ BLOCKING GAPS (Cần Resolve Trước Khi Chạy Engine)

1. **HOR target reference value:** ΔG_H* optimal = 0 eV? hoặc E_ads = -0.27 eV?
   - Cần paper: "hydrogen adsorption energy Pt DFT benchmark Norskov"
   - NẾU không resolve: vẫn chạy được, dùng "minimize |ΔG_H*|" (thermoneutral) thay vì absolute reference

---

## Checklist

- [✓] Mọi variable range có source tag
- [✓] Mọi target threshold có source tag
- [⚠️] 1 target reference [UNVERIFIED] — non-blocking (minimize abs value works)
- [✓] Fixed conditions đủ (temperature, Ni-C distance, potential)
- [✓] structure_generator.type defined
- [✓] output.dir unique
- [✓] meta.source_confidence = MEDIUM (reflects 1 unverified gap)
