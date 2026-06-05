# R&D Landscape — PGM-Free AEMFC (Ni@C + Co₃O₄)

| Field | Value |
|-------|-------|
| Date | 2026-06-02 |
| Phase | Discovery |
| Notebooks queried | hydrogen (42 sources), AI scientist (10 sources) |
| Confidence | HIGH (data grounded from papers) |
| Related files | [gaps.md](gaps.md), [decisions.md](decisions.md) |

---

## Mục Tiêu

Phát triển fuel cell hoàn toàn PGM-free (không Pt, không Ir) dựa trên:
- Anode: Ni@C (nickel bọc carbon shell)
- Cathode: Co₃O₄/C (cobalt oxide trên carbon)
- Membrane: Anion Exchange Membrane (AEM)

---

## Current State-of-the-Art

### [FACT + source]

| Metric | Giá trị | Điều kiện | Source |
|--------|---------|-----------|--------|
| Peak power (H₂/O₂) | 1.0 W/cm² | 70°C, Ni@C 16 mg/cm² | Unveiling the sensitivity...Ni oxidation state |
| Peak power (H₂/air) | 510 mW/cm² | CO₂-free air | same |
| Max current density | 2.5 A/cm² | H₂/O₂ | same |
| Durability | 145 giờ | 0.15 A/cm², 70°C | same |
| Voltage decay | 0.75V → 0.6V | Trong 145h | same |
| Anode loading | 16 mg/cm² | Ni@C | same |
| Cathode loading | 0.8 mg/cm² | Co₃O₄/C | same |
| DOE 2030 target | ≥600 mW/cm² | H₂/air PGM-free | DOE (referenced in same paper) |
| DOE PGM target | 0.1 g_PGM/kW | — | DOE (referenced in same paper) |

### Đạt vs Chưa Đạt

| DOE Target | Status |
|-----------|--------|
| PGM loading (0.1 g/kW) | ✅ VƯỢT (0 g/kW) |
| H₂/air power (≥600 mW/cm²) | ⚠️ GẦN ĐẠT (510 vs 600) |
| Durability (≥2,000h) | ❌ RẤT XA (145h vs 2,000h) |

---

## 5 Vấn Đề Chính (Ranked)

### 1. Ni Oxidation → Catalyst Deactivation (Critical)
- [FACT] Ni metallic bị oxy hóa thành α-Ni(OH)₂ ở >0.3V vs RHE [Source: Unveiling the sensitivity...Ni oxidation state]
- [FACT] Carbon shell có lỗ hổng → NiO islands hình thành tại defect sites [Source: same]
- [FACT] Operating window cực hẹp: 0–0.3V vs RHE [Source: same]

### 2. Durability (Critical)
- [FACT] Chỉ 145 giờ @ 0.15 A/cm², 70°C (DOE cần ≥2,000h) [Source: Unveiling...Ni oxidation state]
- [FACT] Sau 70h bắt đầu voltage fluctuation lớn — nguyên nhân: poor water management + ionomer QAPPT degradation [Source: same]
- [FACT] QAPPT membrane/ionomer có stability constraints acknowledged bởi authors [Source: same]

### 3. Catalyst Loading Quá Cao (Major)
- [FACT] Cần 16 mg/cm² anode loading để đạt 1.0 W/cm² (vs Pt chỉ 0.1–0.4 mg/cm²) [Source: Unveiling...Ni oxidation state]
- [FACT] Tăng loading >16 mg/cm² → crack catalyst layer + pinhole membrane [Source: same]
- [REASONING] Đã chạm giới hạn vật lý của phương pháp fabrication hiện tại

### 4. CO₂ Sensitivity (Moderate)
- [FACT] Test đạt 510 mW/cm² chỉ với CO₂-free air [Source: Unveiling...Ni oxidation state]
- [REASONING] Air thường chứa ~420 ppm CO₂ → CO₂ + OH⁻ → carbonate → block membrane conductivity
- [REASONING] Phải dùng CO₂-free air hoặc CO₂ scrubber — không thực tế cho thương mại

### 5. Manufacturing Complexity (Moderate)
- [FACT] Ni@C cần forming gas (5% H₂/Ar) khi fabricate MEA để tránh oxy hóa [Source: Unveiling...Ni oxidation state]
- [FACT] Hot plate temperature giới hạn 55°C [Source: same]
- [FACT] Activation phải giữ cell voltage >0.45V liên tục [Source: same]
- [REASONING] Quy trình phức tạp hơn Pt-based MEA fabrication đáng kể

---

## Giải Pháp Đã Đề Xuất (Trong Papers)

| Vấn đề | Giải pháp đề xuất | Status | Tag |
|---------|-------------------|--------|-----|
| Ni oxidation | Carbon shell engineering (thickness, defect control) | Concept only | [FACT] Source: Unveiling...Ni oxidation state |
| Ni oxidation | Forming gas protocols khi fabrication | Tested, works | [FACT] Source: same |
| Low activity | Tăng loading lên 16 mg/cm² | Đã max | [FACT] Source: same |
| Flooding | Chạy ở current density cao hơn | Tested | [FACT] Source: same |
| Ionomer degrade | Cần membrane material mới | Open problem | [FACT] Source: same |

---

## AI Methods Có Thể Áp Dụng

[REASONING — logical mapping từ AI scientist notebook, chưa có paper áp dụng trực tiếp cho Ni@C AEMFC]

| Vấn đề | AI Method | Paper reference |
|---------|-----------|----------------|
| Shell optimization | MLIP simulate defect/thickness variants | MatterSim concept |
| Shell design | CVAE generate optimal shell structure | CVAE ORR paper |
| Ni alloy screening | GNN predict HOR activity | Open Catalyst |
| GDL/CL structure | Bayesian optimization | Bayesian GDL paper |
| New membrane | MatterGen generate candidates | MatterGen paper |

---

## Research Questions (Mapped từ mục tiêu)

[REASONING — suy luận từ gaps + problems identified, cần validate khi có thêm papers]

Mục tiêu: PGM-free AEMFC thương mại → 5 câu hỏi R&D cần giải quyết:

1. **Làm sao tăng durability từ 145h → ≥2,000h?**
   - Sub: ionomer nào thay QAPPT? Shell design nào ngăn oxidation?

2. **Carbon shell tối ưu: bao nhiêu layers, defect density bao nhiêu?**
   - Sub: H₂ permeation đủ nhanh mà O₂ bị block?

3. **Có thể giảm loading từ 16 mg/cm² mà giữ performance không?**
   - Sub: tăng intrinsic activity Ni thay vì tăng lượng?

4. **Giải quyết CO₂ poisoning bằng cách nào khi dùng air thật?**
   - Sub: CO₂ scrubber? CO₂-tolerant membrane? Self-purging design?

5. **Có thể dùng AI/ML để tối ưu shell design nhanh hơn trial-and-error?**
   - Sub: MLIP screen defect configs? Bayesian optimize loading?

---

## Knowledge Gaps (Chi tiết: [gaps.md](gaps.md))

- [ ] CVD conditions cụ thể cho carbon shell trên Ni nanoparticles
- [ ] N-doped graphene shell properties (H₂ vs O₂ permeability)
- [ ] AEM membrane alternatives (beyond QAPPT) — durability >1000h
- [ ] NiMo, NiFe alloy trong AEMFC anode (chưa có data)
- [ ] MLIP/MD simulation cho graphene defect + gas permeation
- [ ] CO₂-tolerant AEM membrane research

---

## Next Steps

- [ ] **[Level 1]** Tìm papers về CVD carbon shell synthesis → upload notebook hydrogen
- [ ] **[Level 1]** Tìm papers về graphene defect + H₂/O₂ permeation simulation
- [ ] **[Level 1]** Tìm papers về AEM membrane alternatives (durability >1000h)
- [ ] **[Level 2]** MLIP simulate Ni@C shell: thickness × defect density matrix (cần H100)
- [ ] **[Level 2]** GNN screen NiMo/NiFe alloy variants cho HOR alkaline
- [ ] **[Level 3]** Synthesize top candidates + single cell test (cần lab)

---

## Confidence Assessment

| Section | Confidence | Lý do |
|---------|-----------|-------|
| Performance numbers | HIGH | Trực tiếp từ paper, NotebookLM confirm |
| DOE targets | HIGH | Published standards |
| Problems ranked | HIGH | Authors tự identify trong papers |
| AI methods applicable | MEDIUM | Logical mapping, chưa có paper áp dụng trực tiếp cho Ni@C |
| Research questions | MEDIUM | Suy luận từ gaps, cần validate khi có thêm papers |
