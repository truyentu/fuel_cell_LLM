# Upgrade Specs + Implementation Plan

Date: 2026-06-04
Purpose: Chi tiết HOW cho mỗi component trong upgrade-tasklist.md
Prerequisites: Đã đọc upgrade-tasklist.md (WHAT) + audit notes

---

## SPEC 1: GNoME Data Lookup (`data/gnome_lookup.py`)

### Bước 0: Verify Format (PHẢI LÀM TRƯỚC KHI CODE)

```
Download repo: git clone https://github.com/google-deepmind/materials_discovery
Inspect: ls, file formats, README

Possible formats:
  A) Single large JSON/CSV with all 520K entries → easy, parse trực tiếp
  B) Individual .cif files → cần build composition index
  C) Database dump (sqlite, HDF5) → cần adapter

ACTION: download + inspect → ghi lại format thật → adapt spec
```

### Interface (Dù Format Nào)

```python
class GNoMELookup:
    """Lookup alloy stability from GNoME 520K dataset."""

    def __init__(self, data_dir: str = "data/gnome/"):
        """Load index. Build from raw data if index doesn't exist."""
        self.index = self._load_or_build_index(data_dir)

    def lookup(self, formula: str) -> dict | None:
        """
        Check if composition exists in GNoME stable crystals.

        Args:
            formula: Chemical formula (e.g., "Ni3Mo", "NiFe2")

        Returns:
            {"stable": True, "formation_energy_eV": -0.12, "structure_id": "mp-123"}
            or None if not found
        """

    def search_by_elements(self, elements: list[str], max_results: int = 100) -> list[dict]:
        """
        Find all stable structures containing specified elements.

        Args:
            elements: e.g., ["Ni", "Mo"]

        Returns:
            List of matching entries sorted by formation_energy
        """

    def _load_or_build_index(self, data_dir: str) -> dict:
        """
        If index.json exists → load it.
        If not → parse raw data → build composition→entry mapping → save index.json
        """
```

### Output Format

```json
{
  "formula": "Ni3Mo",
  "stable": true,
  "formation_energy_eV_per_atom": -0.05,
  "energy_above_hull_eV": 0.0,
  "structure_id": "gnome-123456",
  "space_group": "Pm-3m",
  "source": "GNoME predicted stable"
}
```

### Edge Cases

```
- Formula không standard ("NiMo" vs "Ni1Mo1" vs "MoNi") → normalize trước
- Composition match nhưng stoichiometry khác → return closest matches
- Element không trong dataset → return None gracefully
- Data file corrupt/missing → raise clear error, suggest re-download
```

### Test Cases

```python
def test_known_stable():
    # Ni FCC is definitely in dataset
    result = lookup.lookup("Ni")
    assert result is not None
    assert result["stable"] == True

def test_known_binary():
    # NiO should be in dataset
    result = lookup.lookup("NiO")
    assert result is not None

def test_search_ni_alloys():
    results = lookup.search_by_elements(["Ni", "Mo"])
    assert len(results) > 0
    assert all("Ni" in r["formula"] and "Mo" in r["formula"] for r in results)

def test_nonexistent():
    result = lookup.lookup("XxYy99")
    assert result is None
```

---

## SPEC 2: SynTERRA Query (`data/synterra_query.py`)

### Data Format (Known từ GitHub README)

```json
// SynTERRA entries format (from CederGroupHub):
{
  "doi": "10.1016/...",
  "target": {"material_formula": "LiCoO2", "phase": "..."},
  "precursors": [
    {"material_formula": "Li2CO3", "amount": "..."},
    {"material_formula": "Co3O4", "amount": "..."}
  ],
  "operations": [
    {"type": "Heating", "temperature": 900, "duration": 12, "atmosphere": "air"}
  ]
}
```

### Interface

```python
class SynTERRAQuery:
    """Query synthesis recipes from text-mined solid-state synthesis database."""

    def __init__(self, data_path: str = "data/synterra/reactions.json"):
        """Load 33K recipes into memory."""
        self.recipes = self._load(data_path)

    def search(self, formula: str, fuzzy: bool = True) -> list[dict]:
        """
        Find recipes where target material matches formula.

        Args:
            formula: Target material (e.g., "NiMo", "Ni3Mo", "NiO")
            fuzzy: If True, match partial (e.g., "Ni" matches "Ni3Mo")

        Returns:
            List of matching recipes, sorted by relevance
        """

    def search_by_elements(self, elements: list[str]) -> list[dict]:
        """
        Find recipes where target contains ALL specified elements.

        Args:
            elements: e.g., ["Ni", "Mo"]
        """

    def get_recipe_summary(self, recipe: dict) -> str:
        """
        Format recipe as human-readable string.

        Returns:
            "Precursors: Li2CO3 + Co3O4 → Heat 900°C, 12h, air"
        """
```

### Output Format

```json
{
  "target_formula": "Ni3Mo",
  "precursors": ["Ni(NO3)2·6H2O", "MoO3"],
  "temperature_C": 800,
  "duration_h": 6,
  "atmosphere": "H2/Ar",
  "source_doi": "10.1016/...",
  "recipe_summary": "Precursors: Ni(NO3)2 + MoO3 → Heat 800°C, 6h, H2/Ar",
  "caveat": "⚠️ BULK solid-state recipe. Adapt for nanoparticle synthesis."
}
```

### Matching Algorithm

```
1. Normalize formula: "NiMo" → {"Ni": 1, "Mo": 1}
2. For each recipe in 33K:
   - Parse target.material_formula → composition dict
   - Compare:
     - Exact match: compositions identical → score 1.0
     - Element match: same elements, different ratio → score 0.7
     - Subset match: target contains query elements + others → score 0.3
3. Sort by score, return top N
```

### CAVEAT (CRITICAL)

```
SynTERRA = SOLID-STATE synthesis (powder mixing + high-temp sintering)
Ni@C = MOF PYROLYSIS (solution → MOF → decompose)

SynTERRA recipes for "NiMo" = "grind NiO + MoO3, heat 900°C, 12h"
This produces BULK NiMo powder, NOT nanoparticles wrapped in carbon.

For Ni@C: recipe từ SynTERRA chỉ là REFERENCE POINT:
  - Biết precursors nào phổ biến
  - Biết temperature range hợp lý
  - KHÔNG copy trực tiếp → cần adapt cho nanoparticle method

Reporter PHẢI ghi caveat khi attach recipe.
```

### Test Cases

```python
def test_search_ni():
    results = query.search("Ni")
    assert len(results) > 0

def test_search_elements():
    results = query.search_by_elements(["Ni", "Mo"])
    # Có thể 0 results nếu NiMo không có trong solid-state DB
    # → acceptable, document

def test_summary_format():
    results = query.search("LiCoO2")  # known to be in DB
    assert len(results) > 0
    summary = query.get_recipe_summary(results[0])
    assert "°C" in summary or "C" in summary

def test_empty_result():
    results = query.search("NonExistentMaterial123")
    assert results == []
```

---

## SPEC 3: CHGNet Runner (`runners/chgnet_runner.py`)

### API Reference (từ chgnet docs)

```python
from chgnet.model import CHGNet
from chgnet.model.dynamics import MolecularDynamics
from pymatgen.core import Structure

model = CHGNet.load()
prediction = model.predict_structure(structure)
# Returns: {"energy": float, "forces": array, "stress": array, "magmom": array}
```

### Interface

```python
class CHGNetRunner:
    """Predict crystal stability using CHGNet universal potential."""

    def __init__(self, device: str = "cpu"):
        """Load CHGNet pre-trained model."""
        self.model = None
        self.device = device
        self._load_model()

    @property
    def is_available(self) -> bool:
        return self.model is not None

    def predict_stability(self, atoms) -> dict | None:
        """
        Predict formation energy and stability.

        Args:
            atoms: ASE Atoms object

        Returns:
            {
                "energy_per_atom_eV": float,
                "energy_total_eV": float,
                "forces_max_eV_A": float,
                "stable": bool (energy_above_hull < 0.1 eV/atom heuristic)
            }
        """

    def relax_structure(self, atoms, fmax: float = 0.05, steps: int = 300) -> dict:
        """
        Relax atomic positions + cell using CHGNet.

        Returns:
            {"relaxed_atoms": Atoms, "final_energy": float, "converged": bool}
        """

    # Mock methods
    def _mock_predict_stability(self, atoms) -> dict:
        """Realistic mock for testing without CHGNet installed."""
```

### Khác Biệt vs MACE

```
CHGNet:
  - Dùng cho: STABILITY prediction (formation energy, relaxation)
  - Input: pymatgen Structure hoặc ASE Atoms
  - Strength: trained specifically on Materials Project (stability data)
  - Weakness: không design cho NEB/MD (dùng MACE cho đó)

MACE:
  - Dùng cho: DYNAMICS (NEB barriers, MD simulations)
  - Input: ASE Atoms
  - Strength: general force field, accurate forces
  - Weakness: stability prediction not as focused as CHGNet

→ CHGNet cho Phase 1a (stability filter)
→ MACE cho Phase 1b (NEB + MD)
→ KHÔNG overlap, KHÔNG redundant
```

### Test Cases

```python
def test_ni_bulk_stable():
    from ase.build import bulk
    ni = bulk("Ni", "fcc", a=3.52)
    result = runner.predict_stability(ni)
    assert result["stable"] == True  # Ni is known stable

def test_mock_mode():
    runner = CHGNetRunner(device="cpu")  # will use mock if not installed
    ni = bulk("Ni", "fcc", a=3.52)
    result = runner.predict_stability(ni)
    assert "energy_per_atom_eV" in result
    assert "stable" in result

def test_relax():
    # Slightly distorted Ni should relax back
    ni = bulk("Ni", "fcc", a=3.60)  # wrong lattice constant
    result = runner.relax_structure(ni)
    assert result["converged"]
```

---

## SPEC 4: Phase 1a Revised (`phases/coarse_filter.py` Upgrade)

### Flow Logic

```
Input: config (search_space) + gnome_lookup + chgnet_runner
Output: list of params that PASSED stability filter

def coarse_filter_v2(config, gnome_lookup, chgnet_runner, n_random=100, seed=42):
    """
    2-step stability filter:
      Step 1: GNoME lookup (instant, free)
      Step 2: CHGNet predict (fast, ~100ms/structure)

    Returns filtered params list (typically 30-50% survive)
    """

    candidates = generate_random_params(config, n_random, seed)
    passed = []

    for params in candidates:
        # Step 1: GNoME lookup
        formula = params_to_formula(params)  # e.g., "Ni3Mo"
        gnome_result = gnome_lookup.lookup(formula)

        if gnome_result and gnome_result["stable"]:
            # Known stable in GNoME → fast pass, skip CHGNet
            passed.append(params)
            continue

        if gnome_result and not gnome_result["stable"]:
            # Known UNSTABLE → reject immediately
            continue

        # Not in GNoME (unknown) → need CHGNet prediction
        # Step 2: CHGNet
        atoms = build_alloy_bulk(params)  # simple bulk, not full Ni@C
        chgnet_result = chgnet_runner.predict_stability(atoms)

        if chgnet_result and chgnet_result["stable"]:
            passed.append(params)
        # else: reject (unstable prediction)

    return passed
```

### Decision Logic Table

```
GNoME says    | CHGNet says  | Decision
──────────────┼──────────────┼──────────
STABLE        | (skip)       | ✅ PASS (fast path)
UNSTABLE      | (skip)       | ❌ REJECT (fast path)
NOT FOUND     | STABLE       | ✅ PASS
NOT FOUND     | UNSTABLE     | ❌ REJECT
NOT FOUND     | ERROR        | ⚠️ PASS with warning (give benefit of doubt)
```

### Helper: params_to_formula

```python
def params_to_formula(params: dict) -> str:
    """Convert search params to approximate chemical formula for lookup."""
    dopant = params.get("dopant_type", "none")
    dopant_pct = params.get("dopant_percent", 0)

    if dopant == "none" or dopant_pct == 0:
        return "Ni"

    # Approximate: 20% Mo → Ni4Mo or Ni3Mo (closest integer ratio)
    ni_parts = round(100 / dopant_pct) - 1
    return f"Ni{ni_parts}{dopant}"

    # Examples:
    # 20% Mo → Ni4Mo
    # 25% Mo → Ni3Mo
    # 33% Mo → Ni2Mo
    # 50% Mo → NiMo
```

---

## SPEC 5: Reporter Upgrade (`utils/reporter.py` Additions)

### Thêm Recipe Attachment

```python
def attach_recipes(ranked_candidates: list, synterra_query) -> list:
    """
    For each top candidate, query SynTERRA and attach recipe if found.

    Adds to each candidate dict:
      "recipe_available": True/False
      "recipe_summary": str or None
      "recipe_caveat": str
      "synthesis_feasibility": "HIGH" | "MEDIUM" | "LOW"
    """
    for candidate in ranked_candidates:
        formula = params_to_formula(candidate["params"])
        recipes = synterra_query.search(formula, fuzzy=True)

        if recipes:
            candidate["recipe_available"] = True
            candidate["recipe_summary"] = synterra_query.get_recipe_summary(recipes[0])
            candidate["recipe_caveat"] = (
                "⚠️ BULK solid-state recipe. For nanoparticle/thin-film: "
                "adapt approach (co-reduction, sputtering, MOF pyrolysis)."
            )
            candidate["synthesis_feasibility"] = "MEDIUM"  # recipe exists but needs adapt
        else:
            candidate["recipe_available"] = False
            candidate["recipe_summary"] = None
            candidate["recipe_caveat"] = "No known recipe. Custom synthesis required."
            candidate["synthesis_feasibility"] = "LOW"

    return ranked_candidates
```

### Updated ranked_candidates.md Format

```markdown
## Top 5 Candidates

| Rank | Config | Score | Feasibility | Recipe? |
|------|--------|-------|-------------|---------|
| 1 | NiMo20, 2L, 9%vac | 0.92 | MEDIUM | ✅ |
| 2 | NiMo25, 2L, 8%vac | 0.89 | MEDIUM | ✅ |
| 3 | NiFe15, 2L, 10%vac | 0.82 | LOW | ❌ |

### Candidate 1: NiMo20

⚠️ RANKING ONLY — absolute numbers ±0.15 eV uncertainty

| Metric | Value | Confidence |
|--------|-------|-----------|
| HOR activity | -0.28 eV | ensemble std: 0.03 (confident) |
| H₂ barrier | 0.21 eV | ensemble std: 0.05 (confident) |
| O₂ barrier | 0.93 eV | ensemble std: 0.08 (moderate) |
| Shell stability | 98% intact | — |

**SynTERRA Recipe (Reference):**
Precursors: NiO + MoO₃ → Heat 900°C, 8h, H₂/Ar
⚠️ BULK solid-state recipe. For nanoparticle: adapt approach needed.

**⚠️ LIMITATIONS:**
- This pipeline predicts ACTIVITY and STABILITY (thermodynamic)
- It CANNOT predict DURABILITY (kinetic degradation over time)
- Durability MUST be tested in lab
```

---

## IMPLEMENTATION PLAN (Upgrade)

### Order + Dependencies

```
Week 1: Data + Verify (NO CODE beyond scripts)
─────────────────────────────────────────────────
Day 1: Download SynTERRA + GNoME repos
       → Inspect formats → document actual structure
       → Decision: adapt specs if format different

Day 2: Viết gnome_lookup.py (based on actual format)
       → Test: lookup "Ni", "NiMo", "NiO"

Day 3: Viết synterra_query.py
       → Test: search "Ni", search_by_elements ["Ni","Mo"]
       → Document: how many Ni-related recipes exist?

Day 4: Viết chgnet_runner.py
       → Test mock mode: predict_stability, relax_structure
       → Test real (if chgnet installed): Ni bulk, NiO

Day 5: Integration: coarse_filter_v2.py
       → Test: 10 random params → GNoME + CHGNet → pass/fail
       → Verify: filter logic correct (2-step)

Week 2: Integration + Reporter + Engine Update
─────────────────────────────────────────────────
Day 1: Update reporter.py (recipe attachment)
       → Test: generate ranked_candidates.md with recipes

Day 2: Update config_schema.py (CHGNet settings + knowledge_sources)
       → Test: load existing config.json → validate still passes

Day 3: Update run.py (swap old coarse_filter → new coarse_filter_v2)
       → Integration test: full pipeline mock with new filter

Day 4: Risk mitigation code:
       → Gate checks in run.py
       → OOD warning in ensemble runner
       → Expanded calibration benchmarks

Day 5: End-to-end test (full mock)
       → python run.py --config config.json --skip-calibration --cpu
       → Verify: GNoME lookup → CHGNet filter → screening → recipes in output
```

### File Changes Summary

```
NEW FILES:
  fuel-cell-engine/data/__init__.py
  fuel-cell-engine/data/gnome_lookup.py        ← SPEC 1
  fuel-cell-engine/data/synterra_query.py      ← SPEC 2
  fuel-cell-engine/runners/chgnet_runner.py    ← SPEC 3

MODIFIED FILES:
  fuel-cell-engine/phases/coarse_filter.py     ← SPEC 4 (rewrite)
  fuel-cell-engine/utils/reporter.py           ← SPEC 5 (add recipe)
  fuel-cell-engine/config_schema.py            ← add CHGNet + knowledge_sources
  fuel-cell-engine/run.py                      ← swap filter, add gates
  fuel-cell-engine/requirements.txt            ← add chgnet
  fuel-cell-engine/runners/mace_ensemble.py    ← add OOD warning
  fuel-cell-engine/phases/calibration.py       ← add ranking test

NOT MODIFIED (keep as-is):
  fuel-cell-engine/runners/mace_runner.py      ← Phase 1b, unchanged
  fuel-cell-engine/runners/oc20_runner.py      ← Phase 1b, unchanged
  fuel-cell-engine/optimizer/botorch_loop.py   ← unchanged
  fuel-cell-engine/structures/*                ← unchanged
```

### Risk Checkpoints

```
AFTER Day 1 (download):
  □ GNoME format documented? → nếu unexpected → adjust Day 2 plan
  □ SynTERRA has Ni entries? → nếu 0 → reconsider reporter attachment

AFTER Day 3:
  □ synterra_query returns results cho "Ni"? → nếu 0 → caveat in reporter
  □ gnome_lookup loads without error? → nếu format issue → fix before Day 5

AFTER Week 1:
  □ All 4 new components unit-tested?
  □ Integration test pass (10 candidates through filter)?
  □ Decision: proceed to Week 2 or fix issues?

AFTER Week 2:
  □ End-to-end mock test pass?
  □ Output files contain recipes + caveats?
  □ Ready to deploy on cloud GPU?
```

---

## POST-UPGRADE: Deployment Checklist

```
Trước khi chạy trên cloud GPU lần đầu:

□ All unit tests pass locally (mock mode)
□ requirements.txt includes: chgnet, mace-torch, fairchem-core, botorch
□ data/ folder contains: synterra JSON + gnome index
□ config.json validated by updated schema
□ --skip-calibration flag works (for initial test)
□ Checkpoint/resume works (kill + restart test)
□ Output files generated correctly (CSV + MD + PNG)
□ Recipes attached with caveats in ranked_candidates.md
□ README.md updated with new data dependencies
```
