# Structure Generator Spec — Slab Model for Ni@C AEMFC

Date: 2026-06-03
Purpose: Define cách tạo atomic structures từ config params cho Level 2 engine
Model: Slab (periodic 2D) — Ni alloy surface + graphene shell layers

---

## Tổng Quan

```
Config params:                    Generated structure:
  dopant_type: "Mo"
  dopant_percent: 20%               ═══ Graphene layer 2 (with vacancies + N) ═══
  n_layers: 2                       ─── gap (3.4 Å) ───
  vacancy_percent: 9%               ═══ Graphene layer 1 (with vacancies + N) ═══
  n_doping_percent: 4%              ─── gap (2.1 Å, Ni-C distance) ───
                                    ███ Ni₈₀Mo₂₀ surface layer ███
                                    ███ Ni₈₀Mo₂₀ layer 2 ███
                                    ███ Ni₈₀Mo₂₀ layer 3 ███
                                    ███ Ni₈₀Mo₂₀ layer 4 (fixed) ███

                                    ↕ vacuum (15+ Å)

                                  Periodic in X, Y. Non-periodic (vacuum) in Z.
```

---

## Model Components

### 1. Ni Alloy Slab (Bottom)

```
Surface: FCC(111) — most stable, most studied
Size: (3×3) hoặc (4×4) supercell
Layers: 4 layers (bottom 2 fixed, top 2 relaxed)
Lattice constant: a_Ni = 3.52 Å (pure Ni), adjust for alloy

Atoms count:
  (3×3) × 4 layers = 36 atoms
  (4×4) × 4 layers = 64 atoms → RECOMMEND (đủ lớn cho alloy substitution)
```

### 2. Graphene Shell (Top)

```
Commensurate with Ni(111):
  Ni(111) surface lattice = 2.49 Å
  Graphene lattice = 2.46 Å
  Mismatch: ~1.2% → gần perfect match!
  → Dùng graphene AS-IS trên Ni(111), minimal strain

Layer spacing:
  Ni-to-graphene gap: 2.1 Å (chemisorbed, first layer)
  Graphene-to-graphene: 3.4 Å (van der Waals, multilayer)

Atoms per graphene layer (matching Ni 4×4 supercell):
  Ni (4×4) surface = 16 Ni atoms, cell ~ 9.96 × 9.96 Å
  Graphene in same cell: ~32 C atoms per layer
  2 layers: 64 C atoms
  3 layers: 96 C atoms
```

### 3. Combined Structure

```
(4×4) Ni₈₀Mo₂₀(111), 4 layers:     64 atoms (Ni + Mo)
2× graphene layers:                   64 atoms (C + N, minus vacancies)
Vacuum:                               15 Å above top graphene
─────────────────────────────────────────────────
Total: ~120-128 atoms
Cell: ~9.96 × 9.96 × 30.0 Å
PBC: [True, True, False] (periodic X,Y; vacuum Z)
```

---

## Generation Algorithm

### Step 1: Build Ni Alloy Slab

```python
from ase.build import fcc111
from ase import Atoms
import numpy as np

def build_ni_alloy_slab(dopant_type, dopant_percent, size=(4,4,4), vacuum=15.0):
    """
    Build Ni-alloy FCC(111) slab.

    Parameters:
        dopant_type: "Mo", "Fe", "Co", or "none"
        dopant_percent: 0-30 (atomic %)
        size: (nx, ny, n_layers) supercell
        vacuum: Å of vacuum above slab

    Returns:
        ASE Atoms object with slab
    """
    # 1. Build pure Ni slab
    slab = fcc111('Ni', size=size, vacuum=vacuum, periodic=True)

    # 2. Substitute dopant atoms (random positions in TOP 2 layers)
    if dopant_type != "none" and dopant_percent > 0:
        # Get indices of top 2 layers (surface + subsurface)
        z_positions = slab.positions[:, 2]
        z_sorted = np.sort(np.unique(np.round(z_positions, 1)))
        top_2_z = z_sorted[-2:]  # top 2 layer z-values

        surface_indices = [i for i, z in enumerate(z_positions)
                          if np.round(z, 1) in top_2_z]

        # Calculate number to substitute
        n_substitute = int(len(surface_indices) * dopant_percent / 100)

        # Random substitution (reproducible with seed)
        rng = np.random.default_rng(seed=42)
        sub_indices = rng.choice(surface_indices, n_substitute, replace=False)

        # Substitute
        symbols = list(slab.get_chemical_symbols())
        for idx in sub_indices:
            symbols[idx] = dopant_type
        slab.set_chemical_symbols(symbols)

    # 3. Set constraints: fix bottom 2 layers
    from ase.constraints import FixAtoms
    z_positions = slab.positions[:, 2]
    z_sorted = np.sort(np.unique(np.round(z_positions, 1)))
    bottom_2_z = z_sorted[:2]
    fix_indices = [i for i, z in enumerate(z_positions)
                   if np.round(z, 1) in bottom_2_z]
    slab.set_constraint(FixAtoms(indices=fix_indices))

    # 4. Set tags for OC20 compatibility
    # 0 = bulk (fixed), 1 = surface (relaxed)
    tags = np.zeros(len(slab), dtype=int)
    for i, z in enumerate(z_positions):
        if np.round(z, 1) in top_2_z:
            tags[i] = 1
    slab.set_tags(tags)

    return slab
```

### Step 2: Build Graphene Layers (With Defects)

```python
from ase.build import graphene
from ase import Atoms
import numpy as np

def build_graphene_layers(n_layers, vacancy_percent, n_doping_percent,
                          cell_xy, z_start, seed=42):
    """
    Build graphene layer(s) commensurate with Ni slab.

    Parameters:
        n_layers: 1, 2, or 3
        vacancy_percent: 0-20 (% of C atoms removed)
        n_doping_percent: 0-10 (% of C atoms → N)
        cell_xy: (a, b) cell dimensions from Ni slab (Å)
        z_start: z-coordinate for first graphene layer (Å)
        seed: random seed for reproducibility

    Returns:
        ASE Atoms object with graphene layers
    """
    rng = np.random.default_rng(seed=seed)

    # 1. Build single graphene layer matching Ni(111) cell
    # Ni(111) 4×4: cell ≈ 9.96 × 9.96 Å (with 60° angle)
    # Graphene unit cell: a=2.46 Å, 2 atoms
    # → 4×4 graphene supercell ≈ 9.84 × 9.84 Å (stretch 1.2% to match Ni)

    a_graphene = 2.46  # Å
    nx = int(round(cell_xy[0] / a_graphene))
    ny = int(round(cell_xy[1] / (a_graphene * np.sqrt(3)/2)))

    # Build using ASE graphene nanoribbon (then make periodic)
    from ase.build import graphene_nanoribbon
    # Alternative: build manually

    def make_graphene_sheet(nx, ny, a=2.46):
        """Generate graphene positions in hexagonal lattice."""
        positions = []
        # Basis atoms in unit cell
        basis = np.array([[0, 0, 0],
                         [a/2, a*np.sqrt(3)/6, 0]])
        # Lattice vectors
        a1 = np.array([a, 0, 0])
        a2 = np.array([a/2, a*np.sqrt(3)/2, 0])

        for i in range(nx):
            for j in range(ny):
                for b in basis:
                    pos = b + i * a1 + j * a2
                    positions.append(pos)
        return np.array(positions)

    all_positions = []
    all_symbols = []

    for layer_i in range(n_layers):
        # Z position for this layer
        if layer_i == 0:
            z = z_start  # First layer: Ni-C distance
        else:
            z = z_start + layer_i * 3.4  # Subsequent: interlayer spacing

        # AB stacking: offset every other layer
        positions = make_graphene_sheet(nx, ny)
        if layer_i % 2 == 1:  # B layer offset
            positions += np.array([a_graphene/2, a_graphene*np.sqrt(3)/6, 0])

        positions[:, 2] = z  # Set z

        n_atoms = len(positions)
        symbols = ['C'] * n_atoms

        # 2. Create vacancies (random removal)
        n_vacancies = int(n_atoms * vacancy_percent / 100)
        if n_vacancies > 0:
            vac_indices = rng.choice(n_atoms, n_vacancies, replace=False)
            # Remove by marking (will filter later)
            for idx in sorted(vac_indices, reverse=True):
                positions = np.delete(positions, idx, axis=0)
                symbols.pop(idx)

        n_remaining = len(symbols)

        # 3. N-doping (substitute C → N at random positions)
        n_ndope = int(n_remaining * n_doping_percent / 100)
        if n_ndope > 0:
            dope_indices = rng.choice(n_remaining, n_ndope, replace=False)
            for idx in dope_indices:
                symbols[idx] = 'N'

        all_positions.extend(positions.tolist())
        all_symbols.extend(symbols)

    # 4. Create Atoms object
    graphene_atoms = Atoms(
        symbols=all_symbols,
        positions=all_positions,
    )

    # Tag as adsorbate (2) for OC20 compatibility
    graphene_atoms.set_tags([2] * len(graphene_atoms))

    return graphene_atoms
```

### Step 3: Combine Slab + Graphene

```python
def build_ni_at_c_structure(dopant_type, dopant_percent, n_layers,
                             vacancy_percent, n_doping_percent,
                             slab_size=(4,4,4), vacuum=15.0, seed=42):
    """
    Build complete Ni@C slab model.

    Parameters:
        dopant_type: "Mo", "Fe", "Co", "none"
        dopant_percent: 0-30
        n_layers: 1-3 graphene layers
        vacancy_percent: 0-20
        n_doping_percent: 0-10
        slab_size: (nx, ny, n_layers) for Ni slab
        vacuum: Å vacuum above graphene
        seed: reproducibility

    Returns:
        ASE Atoms object — complete structure ready for MACE/OC20
    """
    # 1. Build Ni alloy slab
    slab = build_ni_alloy_slab(dopant_type, dopant_percent, slab_size, vacuum=0)

    # 2. Get slab top z-position + cell XY
    z_top = slab.positions[:, 2].max()
    cell_xy = (slab.cell[0, 0], slab.cell[1, 1])

    # 3. Build graphene at z_top + 2.1 Å (Ni-C bond distance)
    z_start = z_top + 2.1
    graphene = build_graphene_layers(
        n_layers, vacancy_percent, n_doping_percent,
        cell_xy, z_start, seed
    )

    # 4. Combine
    combined = slab + graphene

    # 5. Set cell with vacuum above
    z_max_graphene = graphene.positions[:, 2].max()
    cell_z = z_max_graphene + vacuum
    combined.cell[2, 2] = cell_z
    combined.pbc = [True, True, True]  # periodic for MACE
    # Note: for isolated slab, large vacuum = effectively non-periodic in Z

    # 6. Center in cell
    combined.center(vacuum=vacuum/2, axis=2)

    return combined


def build_neb_structures(structure, molecule='H2',
                         initial_side='outside', final_side='inside'):
    """
    Build initial + final structures for NEB (diffusion through shell).

    Parameters:
        structure: combined Ni@C Atoms object
        molecule: 'H2' or 'O2'
        initial_side: 'outside' (above graphene)
        final_side: 'inside' (between graphene and Ni)

    Returns:
        (initial, final) ASE Atoms objects
    """
    from ase import Atoms
    from ase.build import molecule as mol_builder

    # Get graphene layer positions
    c_indices = [i for i, s in enumerate(structure.get_chemical_symbols())
                 if s in ['C', 'N']]
    graphene_z = structure.positions[c_indices, 2]
    z_top_graphene = graphene_z.max()
    z_bottom_graphene = graphene_z.min()

    # Ni surface z
    ni_indices = [i for i, s in enumerate(structure.get_chemical_symbols())
                  if s in ['Ni', 'Mo', 'Fe', 'Co']]
    z_ni_surface = structure.positions[ni_indices, 2].max()

    # Find a vacancy site (hole in graphene) for diffusion path
    # Use center of cell XY as path
    cx = structure.cell[0, 0] / 2
    cy = structure.cell[1, 1] / 2

    # Build molecule
    mol = mol_builder(molecule)

    # Initial: molecule ABOVE graphene (outside shell)
    initial = structure.copy()
    mol_initial = mol.copy()
    mol_initial.positions += np.array([cx, cy, z_top_graphene + 2.5])
    initial += mol_initial

    # Final: molecule BETWEEN graphene and Ni (inside shell)
    final = structure.copy()
    mol_final = mol.copy()
    z_inside = (z_bottom_graphene + z_ni_surface) / 2  # midpoint
    mol_final.positions += np.array([cx, cy, z_inside])
    final += mol_final

    # Tag molecule atoms as adsorbate (2)
    tags_initial = list(initial.get_tags())
    tags_final = list(final.get_tags())
    for i in range(len(mol)):
        tags_initial[-len(mol) + i] = 2
        tags_final[-len(mol) + i] = 2
    initial.set_tags(tags_initial)
    final.set_tags(tags_final)

    return initial, final
```

---

## Config → Structure Mapping

```json
{
  "search_space": {
    "variables": {
      "dopant_type": {"values": ["Mo", "Fe", "Co", "none"]}
      → build_ni_alloy_slab(dopant_type=...)

      "dopant_percent": {"range": [0, 30]}
      → build_ni_alloy_slab(dopant_percent=...)

      "n_layers": {"range": [1, 3]}
      → build_graphene_layers(n_layers=...)

      "vacancy_percent": {"range": [0, 20]}
      → build_graphene_layers(vacancy_percent=...)

      "n_doping_percent": {"range": [0, 10]}
      → build_graphene_layers(n_doping_percent=...)
    }
  }
}
```

| Config param | Function param | Physical meaning |
|-------------|---------------|-----------------|
| `dopant_type` | `build_ni_alloy_slab(dopant_type=)` | Alloy element mixed with Ni |
| `dopant_percent` | `build_ni_alloy_slab(dopant_percent=)` | % atoms in surface layers replaced |
| `n_layers` | `build_graphene_layers(n_layers=)` | Graphene shell thickness |
| `vacancy_percent` | `build_graphene_layers(vacancy_percent=)` | % C atoms removed (holes for gas) |
| `n_doping_percent` | `build_graphene_layers(n_doping_percent=)` | % C → N substitution |

---

## Physical Constraints (Validation)

```python
CONSTRAINTS = {
    "dopant_percent": {
        "max": 30,
        "reason": "FCC Ni destabilizes above ~30% dopant"
    },
    "n_layers": {
        "min": 1, "max": 3,
        "reason": "0 = no protection, >3 = H₂ cannot permeate"
    },
    "vacancy_percent": {
        "max": 20,
        "reason": ">20% = graphene sheet structurally unstable"
    },
    "n_doping_percent": {
        "max": 10,
        "reason": ">10% N distorts graphene lattice significantly"
    },
    "min_c_c_distance": {
        "value": 1.2,  # Å
        "reason": "C-C bond ~1.42 Å, anything shorter = unphysical"
    },
    "min_ni_c_distance": {
        "value": 1.8,  # Å
        "reason": "Ni-C bond ~2.1 Å, <1.8 = overlap"
    }
}
```

---

## Structure Validation (Sau Khi Generate)

```python
def validate_structure(atoms):
    """Sanity check generated structure before submitting to MACE/OC20."""
    issues = []

    # 1. No atom overlap (min distance > 0.8 Å)
    from ase.geometry import get_distances
    d = atoms.get_all_distances(mic=True)
    np.fill_diagonal(d, 999)
    min_dist = d.min()
    if min_dist < 0.8:
        issues.append(f"Atom overlap: min distance = {min_dist:.2f} Å")

    # 2. Ni-C distance reasonable (1.8 - 3.0 Å for first layer)
    # ... check interface

    # 3. Graphene C-C bonds reasonable (1.2 - 1.8 Å)
    # ... check within graphene

    # 4. Cell large enough (no self-interaction through PBC)
    # min(cell_xy) > 2 * cutoff_radius (~6 Å for MACE)
    if atoms.cell[0, 0] < 8.0:
        issues.append(f"Cell too small: {atoms.cell[0,0]:.1f} Å (need >8)")

    # 5. Vacuum sufficient
    z_range = atoms.positions[:, 2].max() - atoms.positions[:, 2].min()
    vacuum = atoms.cell[2, 2] - z_range
    if vacuum < 10:
        issues.append(f"Insufficient vacuum: {vacuum:.1f} Å (need >10)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "n_atoms": len(atoms),
        "min_distance": min_dist,
        "cell": atoms.cell.tolist()
    }
```

---

## OC20 Compatibility

```
OC20 requires:
  1. tags: 0=subsurface(fixed), 1=surface(relaxed), 2=adsorbate
  2. Slab structure (periodic XY, vacuum Z)
  3. Adsorbate separated from slab

For Ni@C model:
  Ni bottom 2 layers → tag=0 (fixed, bulk)
  Ni top 2 layers → tag=1 (surface, relaxed)
  Graphene layers → tag=2 (adsorbate/shell)
  H₂/O₂ molecule → tag=2

Note: OC20 was NOT trained on graphene-on-metal systems.
      Predictions may be less accurate → ensemble check important.
      Use OC20 for BARE Ni-alloy surface + H (without shell)
      Use MACE for full Ni@C + H₂ diffusion through shell
```

### Task Split

```
OC20 task: Ni-alloy(111) bare surface + H → H adsorption energy (HOR activity)
  → Answers: "Which alloy binds H closest to Pt?"
  → Structure: slab only, NO graphene (OC20 trained on bare surfaces)

MACE task: Full Ni@C (slab + graphene) + H₂/O₂ → NEB barrier, MD stability
  → Answers: "Can H₂ pass through shell? Is shell stable?"
  → Structure: full combined model
```

---

## Slab Sizes & Atom Counts

| Slab size | Ni atoms | Graphene/layer | Total (2L) | MACE time/NEB | GPU RAM |
|-----------|----------|---------------|------------|---------------|---------|
| (3×3×4) | 36 | ~18 | ~72 | ~2 min | 4 GB |
| **(4×4×4)** | **64** | **~32** | **~128** | **~5 min** | **6 GB** |
| (5×5×4) | 100 | ~50 | ~200 | ~12 min | 10 GB |
| (6×6×4) | 144 | ~72 | ~288 | ~25 min | 16 GB |

**Recommend: (4×4×4)** — balance between accuracy và compute cost.

---

## Reproducibility

```python
# CRITICAL: same params → same structure ALWAYS

def generate_structure_deterministic(params, global_seed=42):
    """
    Deterministic generation: same params + seed → same structure.
    BoTorch gives continuous params → discretize reproducibly.
    """
    # Combine params into unique seed per candidate
    param_hash = hash(frozenset(params.items()))
    local_seed = (global_seed + param_hash) % (2**32)

    # Pass local_seed to all random operations
    structure = build_ni_at_c_structure(
        **params, seed=local_seed
    )
    return structure
```

---

## Edge Cases & Error Handling

| Edge case | How to handle |
|-----------|--------------|
| vacancy_percent=0, n_layers=3 | Valid: thick impermeable shell (expect H₂ FAIL) |
| vacancy_percent=20, n_layers=1 | Valid but unstable: flag, let MACE MD determine |
| dopant_percent=0, dopant_type≠"none" | Override: set dopant_type="none" |
| Generated structure has overlap | Reject → reseed → regenerate (max 3 tries) |
| NEB initial/final too close to PBC boundary | Shift molecule position |
| Graphene atoms count = 0 (all vacancies) | Reject: vacancy_percent capped at actual max |
| N-doping > remaining C atoms | Cap: n_doping = min(requested, available_C) |

---

## File Output

```python
# Save generated structures for inspection / reproducibility

def save_structure(atoms, path, params):
    """Save structure + metadata."""
    from ase.io import write

    # XYZ with comment line containing params
    comment = f"params: {params}"
    write(path, atoms, comment=comment)

# Output:
# rnd/compute/<pipeline>/structures/
# ├── candidate_001_NiMo20_2L_9v_4N.xyz
# ├── candidate_002_NiFe15_1L_5v_0N.xyz
# ├── candidate_001_neb_initial.xyz
# ├── candidate_001_neb_final.xyz
# └── ...
```

---

## Integration With Engine

```python
# Trong screening.py:

from structures.ni_at_c_generator import (
    build_ni_at_c_structure,
    build_neb_structures,
    validate_structure
)

def evaluate_candidate(params, config):
    """Full evaluation of 1 candidate."""

    # 1. Generate structure
    structure = build_ni_at_c_structure(**params)
    validation = validate_structure(structure)
    if not validation["valid"]:
        return CandidateResult(status="failed_generation",
                               error=validation["issues"])

    # 2. OC20: bare surface + H (strip graphene for this)
    bare_slab = build_ni_alloy_slab(params["dopant_type"], params["dopant_percent"])
    hor_activity = oc20_runner.predict_h_adsorption(bare_slab)

    # 3. MACE: NEB H₂ through shell
    initial_h2, final_h2 = build_neb_structures(structure, molecule='H2')
    h2_barrier = mace_runner.run_neb(initial_h2, final_h2)

    # 4. MACE: NEB O₂ through shell
    initial_o2, final_o2 = build_neb_structures(structure, molecule='O2')
    o2_barrier = mace_runner.run_neb(initial_o2, final_o2)

    # 5. MACE: MD stability
    stability = mace_runner.run_md(structure, T=343, steps=10000)

    return CandidateResult(
        params=params,
        status="success",
        scores={
            "hor_activity": hor_activity,
            "h2_barrier": h2_barrier,
            "o2_barrier": o2_barrier,
            "shell_stability": stability
        }
    )
```

---

## Testing Strategy

```python
# Unit tests cho structure generator:

def test_pure_ni_slab():
    """Pure Ni, no dopant, no graphene."""
    slab = build_ni_alloy_slab("none", 0)
    assert all(s == "Ni" for s in slab.get_chemical_symbols())
    assert len(slab) == 64  # 4×4×4

def test_alloy_substitution():
    """20% Mo substitution."""
    slab = build_ni_alloy_slab("Mo", 20)
    symbols = slab.get_chemical_symbols()
    mo_count = symbols.count("Mo")
    # 20% of surface 2 layers (32 atoms) = ~6-7 Mo
    assert 5 <= mo_count <= 8

def test_graphene_vacancy():
    """10% vacancy removes correct number."""
    g = build_graphene_layers(1, 10, 0, (9.96, 9.96), 5.0)
    n_expected = int(32 * 0.9)  # ~29 atoms
    assert abs(len(g) - n_expected) <= 1

def test_n_doping():
    """5% N-doping."""
    g = build_graphene_layers(1, 0, 5, (9.96, 9.96), 5.0)
    n_nitrogen = g.get_chemical_symbols().count('N')
    assert n_nitrogen == int(32 * 0.05)  # ~1-2

def test_combined_valid():
    """Full structure passes validation."""
    s = build_ni_at_c_structure("Mo", 20, 2, 9, 4)
    v = validate_structure(s)
    assert v["valid"]
    assert v["n_atoms"] > 100

def test_deterministic():
    """Same params → same structure."""
    s1 = build_ni_at_c_structure("Mo", 20, 2, 9, 4, seed=42)
    s2 = build_ni_at_c_structure("Mo", 20, 2, 9, 4, seed=42)
    assert np.allclose(s1.positions, s2.positions)

def test_neb_structures():
    """NEB initial/final have molecule at correct positions."""
    s = build_ni_at_c_structure("Mo", 20, 2, 9, 4)
    initial, final = build_neb_structures(s, 'H2')
    # Final H₂ should be between graphene and Ni (lower z)
    h2_z_initial = initial.positions[-2:, 2].mean()
    h2_z_final = final.positions[-2:, 2].mean()
    assert h2_z_initial > h2_z_final  # outside > inside
```
