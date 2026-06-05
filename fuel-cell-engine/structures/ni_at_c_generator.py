"""
Complete Ni@C structure generator — combines slab + graphene shell.
Also builds NEB initial/final structures for H₂/O₂ diffusion.
"""

import logging
from typing import Literal, Optional

import numpy as np
from ase import Atoms
from ase.build import molecule

from structures.slab_builder import build_ni_alloy_slab
from structures.shell_builder import build_graphene_layers

logger = logging.getLogger("engine.structures.generator")


def build_ni_at_c_structure(
    dopant_type: str = "none",
    dopant_percent: float = 0,
    n_layers: int = 2,
    vacancy_percent: float = 9,
    n_doping_percent: float = 0,
    slab_size: tuple[int, int, int] = (4, 4, 4),
    vacuum: float = 15.0,
    ni_c_gap: float = 2.15,
    seed: int = 42,
) -> Atoms:
    """
    Build complete Ni@C slab model: Ni-alloy(111) + graphene shell.

    Parameters:
        dopant_type: "Mo", "Fe", "Co", or "none"
        dopant_percent: 0-30 at%
        n_layers: 1-3 graphene layers
        vacancy_percent: 0-20%
        n_doping_percent: 0-10%
        slab_size: (nx, ny, n_layers) for Ni slab
        vacuum: Å vacuum above top graphene
        ni_c_gap: Ni surface to first graphene distance (Å)
        seed: Random seed

    Returns:
        ASE Atoms object — complete Ni@C structure, periodic, ready for MACE.
    """
    # 1. Build Ni alloy slab (no vacuum — we'll add later)
    slab = build_ni_alloy_slab(
        dopant_type=dopant_type,
        dopant_percent=dopant_percent,
        size=slab_size,
        vacuum=0,  # no vacuum yet
        seed=seed,
    )

    # 2. Get slab dimensions
    z_top_ni = slab.positions[:, 2].max()
    cell_xy = (slab.cell[0, 0], slab.cell[1, 1])

    # 3. Build graphene shell at z_top + ni_c_gap
    z_start = z_top_ni + ni_c_gap
    graphene = build_graphene_layers(
        n_layers=n_layers,
        vacancy_percent=vacancy_percent,
        n_doping_percent=n_doping_percent,
        cell_xy=cell_xy,
        z_start=z_start,
        seed=seed + 1000,  # different seed from slab for independence
    )

    # 4. Combine slab + graphene
    combined = slab + graphene

    # 5. Set cell with vacuum
    z_max = combined.positions[:, 2].max()
    z_min = combined.positions[:, 2].min()
    cell_z = (z_max - z_min) + vacuum
    new_cell = slab.cell.copy()
    new_cell[2, 2] = cell_z
    combined.set_cell(new_cell)
    combined.pbc = [True, True, True]

    # 6. Center in cell (shift so structure is centered in Z)
    combined.center(vacuum=vacuum / 2, axis=2)

    logger.info(
        f"Built Ni@C: {dopant_type}{int(dopant_percent) if dopant_percent else ''}, "
        f"{n_layers}L, {vacancy_percent}%vac, {n_doping_percent}%N → "
        f"{len(combined)} atoms, cell={combined.cell[2,2]:.1f} Å Z"
    )

    return combined


def _find_best_xy_for_molecule(
    structure: Atoms,
    graphene_mask: np.ndarray,
    n_grid: int = 24,
) -> tuple[float, float]:
    """
    Find XY position that maximizes minimum distance to graphene atoms.
    Returns center of largest hole/vacancy — avoids atom overlap in NEB path.
    """
    positions = structure.positions
    cell = structure.cell
    graphene_xy = positions[graphene_mask, :2]

    cell_a = float(cell[0, 0])
    cell_b = float(cell[1, 1])

    best_xy = (cell_a / 2, cell_b / 2)
    best_min_dist = 0.0

    xs = np.linspace(0.2, cell_a - 0.2, n_grid)
    ys = np.linspace(0.2, cell_b - 0.2, n_grid)

    for x in xs:
        for y in ys:
            dx = graphene_xy[:, 0] - x
            dy = graphene_xy[:, 1] - y
            # Apply PBC in XY
            dx -= cell_a * np.round(dx / cell_a)
            dy -= cell_b * np.round(dy / cell_b)
            min_dist = np.sqrt(dx**2 + dy**2).min()
            if min_dist > best_min_dist:
                best_min_dist = min_dist
                best_xy = (x, y)

    logger.debug(f"Best XY for molecule: {best_xy}, min_dist_to_graphene={best_min_dist:.2f} Å")
    return best_xy


def build_neb_structures(
    structure: Atoms,
    mol_formula: Literal["H2", "O2"] = "H2",
    seed: int = 42,
) -> tuple[Atoms, Atoms]:
    """
    Build initial + final structures for NEB diffusion calculation.
    Initial: molecule OUTSIDE shell (above graphene)
    Final: molecule INSIDE shell (between graphene and Ni)

    Parameters:
        structure: Combined Ni@C Atoms object
        mol_formula: "H2" or "O2"
        seed: For positioning

    Returns:
        (initial, final) Atoms objects for NEB
    """
    symbols = structure.get_chemical_symbols()
    positions = structure.positions

    # Identify graphene atoms (C or N with tag=2)
    tags = structure.get_tags()
    graphene_mask = tags == 2
    ni_mask = np.array([s in ("Ni", "Mo", "Fe", "Co") for s in symbols])

    graphene_z = positions[graphene_mask, 2]
    ni_z = positions[ni_mask, 2]

    z_top_graphene = graphene_z.max()
    z_bottom_graphene = graphene_z.min()
    z_top_ni = ni_z.max()

    # Find XY position at center of graphene hole (not cell center which may overlap atoms)
    cx, cy = _find_best_xy_for_molecule(structure, graphene_mask)

    # Build molecule with correct bond length per species
    mol = molecule(mol_formula)
    # Orient vertically (along z), preserve correct bond length from ASE
    if len(mol) == 2:
        mol.positions -= mol.positions.mean(axis=0)
        bond_len = np.linalg.norm(mol.positions[0] - mol.positions[1])
        half = bond_len / 2
        mol.positions = np.array([[0, 0, -half], [0, 0, half]])

    # Initial: molecule ABOVE graphene (outside)
    initial = structure.copy()
    mol_outside = mol.copy()
    mol_outside.translate([cx, cy, z_top_graphene + 2.5])
    initial += mol_outside

    # Final: molecule BETWEEN graphene and Ni (inside)
    # Lay flat (horizontal along x) to fit in narrow Ni-graphene gap (~2.15 Å)
    # Vertical orientation causes atom overlap with Ni surface → repulsion energy millions eV
    final = structure.copy()
    mol_inside = mol.copy()
    if len(mol_inside) == 2:
        bond_len_inside = np.linalg.norm(mol_inside.positions[0] - mol_inside.positions[1])
        half_inside = bond_len_inside / 2
        mol_inside.positions = np.array([[-half_inside, 0, 0], [half_inside, 0, 0]])
    # Safe Z: at least mol_half + 2.0 Å above Ni surface
    mol_half = half_inside if len(mol_inside) == 2 else 0.5
    z_safe = z_top_ni + mol_half + 2.0
    z_midpoint = (z_bottom_graphene + z_top_ni) / 2
    z_inside = max(z_midpoint, z_safe)
    mol_inside.translate([cx, cy, z_inside])
    final += mol_inside

    # Tag molecule atoms as adsorbate (tag=3 to not conflict with graphene tag=2)
    n_mol = len(mol)
    for struct in (initial, final):
        t = list(struct.get_tags())
        for i in range(n_mol):
            t[-(n_mol - i)] = 3
        struct.set_tags(t)

    logger.debug(
        f"NEB structures: {mol_formula}, "
        f"xy=({cx:.2f},{cy:.2f}), "
        f"outside z={z_top_graphene + 2.5:.1f}, "
        f"inside z={z_inside:.1f}"
    )

    return initial, final


def validate_structure(atoms: Atoms) -> dict:
    """
    Sanity check generated structure before submitting to calculators.

    Returns:
        {"valid": bool, "issues": list[str], "n_atoms": int, "min_distance": float}
    """
    issues = []

    # 1. Minimum interatomic distance (no overlap)
    from ase.geometry import get_distances

    positions = atoms.positions
    cell = atoms.cell
    n = len(atoms)

    if n < 2:
        issues.append(f"Too few atoms: {n}")
        return {"valid": False, "issues": issues, "n_atoms": n, "min_distance": 0}

    # Compute pairwise distances (with PBC)
    _, distances = get_distances(positions, cell=cell, pbc=atoms.pbc)
    np.fill_diagonal(distances, 999.0)
    min_dist = distances.min()

    if min_dist < 0.8:
        issues.append(f"Atom overlap: min distance = {min_dist:.3f} Å (< 0.8)")

    # 2. Check for reasonable bond lengths
    symbols = atoms.get_chemical_symbols()

    # Ni-Ni should be ~2.49 Å (FCC nearest neighbor)
    ni_indices = [i for i, s in enumerate(symbols) if s in ("Ni", "Mo", "Fe", "Co")]
    if len(ni_indices) > 1:
        ni_dists = distances[np.ix_(ni_indices, ni_indices)]
        np.fill_diagonal(ni_dists, 999.0)
        min_ni = ni_dists.min()
        if min_ni < 2.0:
            issues.append(f"Ni-Ni too close: {min_ni:.3f} Å (expected ~2.49)")

    # 3. Cell size (must be > 2× MACE cutoff ~5-6 Å in XY)
    if atoms.cell[0, 0] < 8.0:
        issues.append(f"Cell X too small: {atoms.cell[0,0]:.1f} Å (need >8)")
    if atoms.cell[1, 1] < 8.0:
        issues.append(f"Cell Y too small: {atoms.cell[1,1]:.1f} Å (need >8)")

    # 4. Vacuum in Z (need >10 Å to avoid self-interaction)
    z_range = positions[:, 2].max() - positions[:, 2].min()
    vacuum_actual = atoms.cell[2, 2] - z_range
    if vacuum_actual < 10.0:
        issues.append(f"Insufficient vacuum: {vacuum_actual:.1f} Å (need >10)")

    # 5. No NaN or Inf
    if np.any(np.isnan(positions)) or np.any(np.isinf(positions)):
        issues.append("NaN or Inf in positions")

    result = {
        "valid": len(issues) == 0,
        "issues": issues,
        "n_atoms": n,
        "min_distance": float(min_dist),
        "cell_z": float(atoms.cell[2, 2]),
        "vacuum": float(vacuum_actual),
    }

    if issues:
        logger.warning(f"Structure validation FAILED: {issues}")
    else:
        logger.debug(f"Structure valid: {n} atoms, min_dist={min_dist:.2f} Å")

    return result


def generate_structure_from_params(
    params: dict,
    config: dict,
    seed: int = 42,
) -> Optional[Atoms]:
    """
    Generate structure from BoTorch-suggested parameters.
    Deterministic: same params + seed → same structure.

    Parameters:
        params: {"dopant_type": "Mo", "dopant_percent": 20, "n_layers": 2, ...}
        config: structure_generator config section
        seed: Base seed (combined with params for uniqueness)

    Returns:
        Valid Atoms object, or None if generation fails after retries.
    """
    # Deterministic seed from params
    param_str = str(sorted(params.items()))
    param_hash = hash(param_str) % (2**31)
    local_seed = (seed + param_hash) % (2**32)

    slab_size = tuple(config.get("slab_size", [4, 4, 4]))
    ni_c_gap = config.get("ni_c_gap_A", 2.15)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            atoms = build_ni_at_c_structure(
                dopant_type=params.get("dopant_type", "none"),
                dopant_percent=params.get("dopant_percent", 0),
                n_layers=int(params.get("n_layers", 2)),
                vacancy_percent=params.get("vacancy_percent", 0),
                n_doping_percent=params.get("n_doping_percent", 0),
                slab_size=slab_size,
                ni_c_gap=ni_c_gap,
                seed=local_seed + attempt,
            )

            validation = validate_structure(atoms)
            if validation["valid"]:
                return atoms
            else:
                logger.warning(
                    f"Attempt {attempt+1}: validation failed: {validation['issues']}"
                )
        except Exception as e:
            logger.error(f"Attempt {attempt+1}: generation error: {e}")

    logger.error(f"Failed to generate valid structure after {max_retries} attempts: {params}")
    return None
