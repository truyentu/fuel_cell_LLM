# Upgrade Tasklist — Post-Research Improvements (Audited)

Date: 2026-06-04
Status: Planning (Audited — 4 critical fixes applied)
Purpose: Tất cả actions cần làm để upgrade pipeline dựa trên deep research mới

---

## ⚠️ AUDIT NOTES (Read Before Implement)

```
CRITICAL FIXES APPLIED:
  #1: GNoME data → VERIFY FORMAT trước khi viết script
  #2: SynTERRA → chủ yếu cho BULK synthesis, KHÔNG cho MOF/nanoparticle
  #3: Phase 1a → 2-step (GNoME + CHGNet), KHÔNG 3-step (bỏ MACE)
  #4: Duplicate tracking removed

KNOWN LIMITATIONS:
  - SynTERRA recipes = BULK powder, cần adapt cho nanoparticle
  - Ensemble uncertainty = LOWER BOUND (shared training bias)
  - Sanity ranking test = validates VACUUM model, NOT alkaline reality
  - Oxidation resistance (Hướng B) = chỉ JDFTx tính chính xác
  - Fine-tune MACE cần >50 structures (100-200 recommended)

ROLLBACK PLAN:
  Nếu Calibration FAIL →
    A) Thử CHGNet thay MACE cho NEB (khác architecture)
    B) Fallback: MACE cho cả HOR predict (bỏ OC20)
    C) Last resort: chỉ dùng JDFTx (chậm 100x, đắt 10x, nhưng chính xác)
```

---

## Priority 1: Trước Khi Deploy Engine (BLOCKING)

### 1.1 Download + VERIFY Databases (Verify Format Trước Khi Code)

- [ ] **SynTERRA DB** — 33K synthesis recipes
  - Source: https://github.com/CederGroupHub/text-mined-synthesis_public
  - Download: clone repo → extract JSON
  - Lưu tại: `fuel-cell-engine/data/synterra/`
  - **VERIFY TRƯỚC**: format JSON ra sao? fields nào?
  - **VERIFY**: search "Ni" → có bao nhiêu entries?
  - **VERIFY**: search "NiMo" → có entries không?
  - **CAVEAT**: SynTERRA = SOLID-STATE synthesis (grind + heat)
    Ni@C trong paper = MOF PYROLYSIS (khác quy trình!)
    → SynTERRA hữu ích cho Hướng B (bulk NiMo alloy)
    → KHÔNG trực tiếp applicable cho Ni@C nanoparticle
    → Khi attach recipe vào output: caveat "BULK recipe, adapt needed"

- [ ] **GNoME 520K structures**
  - Source: https://github.com/google-deepmind/materials_discovery
  - Download: clone → inspect format TRƯỚC
  - **VERIFY TRƯỚC KHI CODE**:
    - File format: .cif? JSON? CSV? sqlite?
    - Có searchable index by composition?
    - Hay 520K file .cif riêng lẻ (cần build index)?
  - Lưu tại: `fuel-cell-engine/data/gnome/`
  - NẾU format = individual .cif: cần build composition index script TRƯỚC
  - NẾU format = structured DB: viết lookup ngay

### 1.2 Viết Query Scripts

- [ ] **`data/synterra_query.py`** — Tìm recipe cho Ni-alloys
  - Input: alloy formula (e.g., "NiMo", "Ni3Mo")
  - Output: list recipes {precursors, temp, time, gas, source_paper}
  - Logic: fuzzy match target material trong 33K entries

- [ ] **`data/gnome_lookup.py`** — Check alloy stability
  - Input: alloy formula
  - Output: {stable: bool, formation_energy: float, structure_id: str}
  - Logic: search 520K entries by composition

### 1.3 Thêm CHGNet Runner

- [ ] **`runners/chgnet_runner.py`**
  - Install: `pip install chgnet`
  - Class CHGNetRunner:
    - predict_stability(atoms) → {energy_per_atom, formation_energy, stable}
    - relax_structure(atoms) → relaxed_atoms
  - Mock mode khi chgnet not installed
  - Test: predict Ni bulk (should match known value)

- [ ] **Update `requirements.txt`**: thêm `chgnet`

### 1.4 Upgrade Coarse Filter (Phase 1a)

- [ ] **Update `phases/coarse_filter.py`**
  - Trước: MACE single-point only
  - Sau: 2-step filter (KHÔNG 3-step — MACE dành riêng cho Phase 1b NEB/MD):
    ```
    Step 1: GNoME lookup (instant) — alloy composition trong 520K?
            YES → likely stable → pass
            NO → proceed to CHGNet (unknown, need prediction)
    Step 2: CHGNet predict formation energy
            < 0.1 eV above hull → pass (stable enough)
            > 0.1 eV → LOẠI (unstable)
    ```
  - NOTE: MACE KHÔNG dùng ở Phase 1a (redundant với CHGNet cho stability)
  - MACE chỉ dùng Phase 1b (NEB barrier + MD — task CHGNet KHÔNG làm được)

- [ ] **Update `config_schema.py`**: thêm CHGNet settings trong tools section

### 1.5 Upgrade Reporter (Output Kèm Recipe)

- [ ] **Update `utils/reporter.py`**
  - Khi generate ranked_candidates.md:
    - Cho mỗi top candidate → auto-query SynTERRA
    - Nếu có recipe → attach vào output KÈM CAVEAT:
      "⚠️ SynTERRA recipe = BULK POWDER synthesis.
       For nanoparticle/thin-film: adapt approach needed
       (e.g., co-reduction, sputtering, MOF pyrolysis)"
    - Format: "SynTERRA recipe: [precursors] → [temp] [time] [gas]"
  - Thêm column "recipe_available" trong results.csv
  - Thêm column "synthesis_note" (bulk/nanoparticle/custom)

### 1.6 Unit Tests Cho New Components (BLOCKING)

- [ ] **Test `data/synterra_query.py`**
  - Verify: query "Ni" returns >0 results
  - Verify: output format correct (precursors, temp, time)
  - Verify: query "XYZNONEXIST" returns empty gracefully

- [ ] **Test `data/gnome_lookup.py`**
  - Verify: format parsing correct (after inspecting real data)
  - Verify: query "Ni" returns known Ni entry
  - Verify: lookup non-existent composition returns None

- [ ] **Test `runners/chgnet_runner.py`**
  - Mock test: fake output format correct
  - Real test (if GPU): Ni bulk formation energy ≈ 0 (known stable)
  - Real test: NiO formation energy < 0 (known stable oxide)

- [ ] **Integration test: Phase 1a (GNoME + CHGNet) end-to-end**
  - Input: 10 random Ni-alloy compositions
  - Expected: some pass, some fail (not all same)
  - Verify: output format matches screening.py expectations

---

## Priority 2: Upgrade Skills (Sau Deploy)

### 2.1 Update `/scientist plan` Skill

- [ ] **Update SKILL.md section `/scientist plan`**
  - Thêm bước: query SynTERRA trước khi tạo config
  - Thêm bước: query GNoME check alloy existence
  - Nếu SynTERRA có recipe → ghi vào plan.md
  - Nếu GNoME nói unstable → loại khỏi search space + warning

- [ ] **Thêm vào config.json schema**
  ```json
  "knowledge_sources": {
    "synterra_matches": [...],
    "gnome_stable": {...},
    "notebooklm_facts": [...]
  }
  ```

### 2.2 Update `/scientist start` + `/scientist digest`

- [ ] **Khi scan landscape**, thêm:
  - Count: bao nhiêu alloys trong GNoME data match search space?
  - Count: bao nhiêu recipes trong SynTERRA cho Ni-X?
  - Báo user: "Có sẵn X recipes, Y stable alloys trong database"

### 2.3 Thêm `/scientist recipe` Mode (Mới)

- [ ] **New mode**: query SynTERRA cho 1 material cụ thể
  - Trigger: `/scientist recipe NiMo`
  - Output: all matching recipes + conditions
  - Useful cho Level 3 (lab prep)

---

## Priority 3: Hướng B Config (Alloy Without Shell)

### 3.1 Define Search Space Hướng B

- [ ] **Xác định nguyên tố X candidates**
  - Từ papers: Mo, Cu, Co, W, Mn, Cr
  - Từ GNoME: filter Ni-X alloys stable
  - Từ SynTERRA: filter Ni-X có recipe
  - Combine → realistic search space

- [ ] **Xác định targets Hướng B**
  - HOR activity: ΔG_H* close to 0 (same as A)
  - Oxidation resistance: potential > +0.3V vs RHE (MỚI — critical)
  - Bulk stability: formation energy < 0.05 eV above hull
  - KHÔNG CẦN: shell targets (barrier, stability)

- [ ] **Viết config cho Hướng B**: `rnd/experiments/alloy-screening-config.json`

### 3.2 Thêm Oxidation Resistance Target

- [ ] **Research**: cách tính oxidation potential bằng DFT/MLIP
  - JDFTx: grand-canonical DFT ở fixed potential (CHÍNH XÁC nhưng CHẬM)
  - Proxy metric: Ni → NiOH₂ formation energy difference (bằng MACE, NHANH)
  - **⚠️ DECISION NEEDED trước khi code:**
    ```
    Option A: Dùng PROXY (MACE surface oxide energy)
      Pro: Screen 1000 candidates nhanh
      Con: Proxy ≠ real oxidation potential (approximate)

    Option B: Two-phase (MACE screen 1000→50, JDFTx screen 50→5)
      Pro: Accurate oxidation potential từ JDFTx
      Con: JDFTx Phase 1 = $200-500 (đắt hơn 10x) + 1-2 tuần

    Option C: Skip oxidation target, dùng CHGNet stability + OC20 HOR only
      Pro: Simple, fast
      Con: Có thể miss oxidation-resistant alloys
    ```
  - Recommend: Option B (accuracy quan trọng cho Hướng B)
  - Cần thêm papers vào notebook? CÓ — cần DFT oxidation potential data cho NiMo/NiFe

- [ ] **Implement**: thêm metric vào engine (SAU KHI decide option)
  - Option A: thêm `mace_runner.surface_oxidation_energy()`
  - Option B: thêm JDFTx vào Phase 1 (restructure pipeline)
  - Option C: no implementation needed

---

## Priority 4: Level 3 Synthesis Optimization (Sau Lab Data)

### 4.1 Chiều Ngược — BoTorch Cho Synthesis Params

- [ ] **Design `config_synthesis.json`**
  - Variables: temp, time, gas_ratio, precursor_percent, heating_rate
  - Objective: maximize HOR activity (measured từ CV)
  - Same BoTorch framework, khác variables

- [ ] **Viết `phases/synthesis_optimization.py`**
  - Input: synthesis params → lab nấu → user input kết quả
  - BoTorch suggest next recipe
  - Loop: suggest → lab → measure → feedback → suggest

### 4.2 Fine-Tune MACE Trên Actual Data

- [ ] **Collect DFT data** (từ Phase 2 JDFTx): 50+ structures
  - ⚠️ NOTE: 50 = MINIMUM. 100-200 recommended cho reliable fine-tune
  - Consider: augment data (add noise, strain structures) nếu <100 raw points
- [ ] **Fine-tune MACE** trên Ni@C specific data
  - Script: `scripts/finetune_mace.py`
  - Expect: accuracy tăng từ 80-90% → 92-95%
  - Fallback nếu not enough data: transfer learning (freeze early layers)
- [ ] **Re-run screening** với fine-tuned model → better ranking

---

## Priority 5: Optional / Future Enhancements

### 5.1 MatSciBERT Auto-Extract (Khi Scale Up)

- [ ] **Setup MatSciBERT NER pipeline**
  - Download: `huggingface.co/m3rg-iitd/matscibert`
  - Input: raw paper text (abstract/fulltext)
  - Output: JSON {material, temp, time, precursor, activity}
  - Use case: batch process 100+ papers → structured DB

### 5.2 ChemLLM Integration (Optional)

- [ ] **Add ChemLLM as tool** (not brain)
  - Use case: predict reaction products, explain mechanisms
  - Download: `huggingface.co/AI4Chem/ChemLLM-7B-Chat`
  - Cần: GPU local hoặc Ollama setup
  - Integrate vào LLM advisor? Hoặc standalone tool?

### 5.3 Local FAISS Vector DB (Thay NotebookLM Long-Term)

- [ ] **Build local paper search** (giống ChemCrow LitSearch)
  - Embed papers → FAISS index
  - Query local (không cần NotebookLM auth)
  - Advantage: unlimited papers, no expire, faster
  - Library: `paper-qa` (same as ChemCrow)

### 5.4 Materials Project API Integration

- [ ] **Viết `data/mp_query.py`**
  - Query: lattice constants, known phases, band gaps
  - API key: free registration
  - Use: validate CHGNet predictions against known data

---

## Priority 6: Risk Mitigation (Xuyên Suốt Các Level)

### 6.1 Strategy "Fail Fast, Fail Cheap" — Gate Checks

- [ ] **Thêm gate check giữa mỗi level**
  - Level 1 → Level 2: Reviewer audit ≥10/12? Nếu không → DỪNG, fix
  - Level 2 Phase 1a → 1b: Có ≥30 candidates pass filter? Nếu không → expand search space
  - Level 2 → Level 3: Trust Score ≥B? Nếu không → debug, KHÔNG vào lab
  - Level 3 mini → Level 3 full: XRD match structure? Nếu không → adjust synthesis
  - Implement: thêm `if not gate_pass: sys.exit("Gate failed")` trong run.py

- [ ] **Thêm cost tracking realtime trong engine**
  - Log: "Iteration 15/25, estimated cost so far: $4.20"
  - Alert: nếu cost > budget threshold → pause, hỏi user continue?

### 6.2 Strategy "Known Test Cases First" — Expanded Calibration

- [ ] **Mở rộng Phase 0 calibration benchmarks**
  - Thêm: NiMo alloy (nếu có DFT data trong literature)
  - Thêm: Graphene on Ni(111) binding energy (có papers)
  - Thêm: Known HOR activity ranking: Pt > NiMo > Ni (từ papers)
  - Nếu model predict ranking SAI → STOP pipeline

- [ ] **Thêm "sanity ranking test" trước BO loop**
  - Input: 3 known materials (Pt, NiMo, pure Ni)
  - Expected ranking: Pt > NiMo > Ni
  - Nếu OC20 + MACE cho ranking KHÁC → model unreliable cho hệ này

### 6.3 Strategy "Verify Before Scale" — Trust Gates

- [ ] **Thêm WARNING rõ hơn trong output files**
  - ranked_candidates.md: banner "⚠️ RANKING ONLY — absolute numbers ±0.15 eV"
  - results.csv: column "confidence_level" per candidate (from ensemble std)
  - verification_report.md: section "WHAT THIS DOES NOT PREDICT: durability, kinetics"

- [ ] **Thêm "synthesis feasibility score" từ SynTERRA**
  - Mỗi candidate: check SynTERRA → recipe exists? → "feasibility: HIGH"
  - No recipe found? → "feasibility: LOW — custom synthesis needed, higher risk"
  - Output trong ranked_candidates.md

### 6.4 Out-of-Distribution Detection

- [ ] **Thêm OOD detection trong ensemble runner**
  - Nếu ensemble std > 0.15 eV → flag "OUT OF DISTRIBUTION"
  - Thêm: compare candidate structure vs training data distribution
    - Latent space distance (nếu model exposes embeddings)
    - Hoặc: simple heuristic — composition có trong OC20 training set?
  - Output: column "ood_risk" trong results.csv (low/medium/high)

- [ ] **Thêm check: composition có trong OC20/MACE training data?**
  - OC20 trained on: ~55 elements, specific alloy surfaces
  - MACE trained on: Materials Project (150K structures)
  - Nếu candidate composition NGOÀI training → WARNING trong output

### 6.5 Multiple Bets — Parallel Paths

- [ ] **Design cho chạy Hướng A + B parallel**
  - Hướng A config: carbon-shell-config.json (đã có)
  - Hướng B config: alloy-screening-config.json (cần viết)
  - Cả 2 chạy trên cloud cùng lúc (nếu budget cho phép)
  - So sánh results: hướng nào promising hơn → focus budget lab

- [ ] **Thêm "backup candidates" trong output**
  - Top 3 = primary (vào lab)
  - Top 4-10 = backup (nếu top 3 fail trong lab)
  - Tránh phải chạy lại engine từ đầu

### 6.6 Durability Risk (ACCEPT — Không Có Tool Fix)

- [ ] **Document rõ trong output: durability KHÔNG predict được**
  - Thêm section trong ranked_candidates.md:
    "⚠️ LIMITATION: This pipeline predicts ACTIVITY and STABILITY (thermodynamic).
     It CANNOT predict DURABILITY (kinetic degradation over time).
     Durability MUST be tested in lab. Budget accordingly."
  - Suggest: allocate ≥50% lab budget cho durability testing (không chỉ activity)

- [ ] **Thêm durability heuristics (weak signals, better than nothing)**
  - From papers: higher O₂ barrier → likely better durability (shell protects longer)
  - From papers: lower surface energy → less prone to reconstruction
  - Implement: "estimated_durability_proxy" column (LOW confidence, clearly labeled)

### 6.7 Synthesis Gap Mitigation

- [ ] **"Level 3 mini" — cheap XRD verify trước full test**
  - Synthesize 1 candidate → XRD only (không cần full cell test)
  - Check: đúng pha tinh thể? Đúng structure AI predict?
  - Cost: ~$200 (vs $2000 full test)
  - Nếu match → proceed full test
  - Nếu không match → adjust synthesis recipe → retry XRD

- [ ] **Thêm "structure match score" sau synthesis**
  - Compare: predicted XRD pattern (from structure) vs actual XRD
  - Script: `analysis/xrd_compare.py`
  - Input: predicted .cif + experimental .xy XRD data
  - Output: match score (0-1)

---

## Tracking: Progress Summary

```
Priority 1: ___/12 tasks done  (BLOCKING — trước deploy, includes unit tests)
Priority 2: ___/5 tasks done   (sau deploy — skill upgrades)
Priority 3: ___/5 tasks done   (Hướng B — includes decision point)
Priority 4: ___/4 tasks done   (sau lab — synthesis opt + fine-tune)
Priority 5: ___/4 tasks done   (future — optional enhancements)
Priority 6: ___/12 tasks done  (risk mitigation — xuyên suốt)

Total: ___/42 tasks
```

---

## Dependencies

```
Priority 1 → PHẢI XONG trước khi deploy engine lên cloud
Priority 2 → cần Priority 1 xong (data scripts tồn tại)
Priority 3 → cần Priority 1+2 (landscape clear, tools ready)
Priority 4 → cần Lab results (real data)
Priority 5 → independent, làm bất cứ lúc nào
Priority 6 → split:
  6.1, 6.2, 6.3, 6.4 → làm CÙNG Priority 1 (trước deploy)
  6.5 → làm cùng Priority 3 (Hướng B)
  6.6, 6.7 → làm trước Level 3 (trước lab)
```
