"""
Ni-alloy FCC(111) slab builder.
Builds Ni or Ni-X alloy surface slabs for OC20 and MACE calculations.
"""

import logging
from typing import Literal

import numpy as np
from ase import Atoms
from ase.build import fcc111
from ase.constraints import FixAtoms

logger = logging.getLogger("engine.structures.slab")


def build_ni_alloy_slab(
    dopant_type: Literal["Mo", "Fe", "Co", "none"] = "none",
    dopant_percent: float = 0,
    size: tuple[int, int, int] = (4, 4, 4),
    vacuum: float = 15.0,
    seed: int = 42,
) -> Atoms:
    """
    Build Ni-alloy FCC(111) slab.

    Parameters:
        dopant_type: Element to alloy with Ni ("Mo", "Fe", "Co", or "none")
        dopant_percent: Atomic % of dopant in surface layers (0-30)
        size: (nx, ny, n_layers) supercell dimensions
        vacuum: Å of vacuum above slab
        seed: Random seed for reproducible substitution

    Returns:
        ASE Atoms object with slab, constraints set, tags assigned.
    """
    # 1. Build pure Ni(111) slab
    slab = fcc111("Ni", size=size, vacuum=vacuum, periodic=True)
    logger.debug(f"Built Ni(111) slab: {len(slab)} atoms, cell={slab.cell.tolist()}")

    # 2. Identify layer z-positions
    z_positions = slab.positions[:, 2]
    z_unique = np.sort(np.unique(np.round(z_positions, decimals=1)))
    n_layers = len(z_unique)

    # 3. Substitute dopant atoms in TOP 2 layers
    if dopant_type != "none" and dopant_percent > 0:
        top_2_z = z_unique[-2:]  # top 2 layer z-values
        surface_indices = [
            i for i, z in enumerate(z_positions)
            if np.round(z, 1) in top_2_z
        ]

        n_substitute = max(1, int(len(surface_indices) * dopant_percent / 100))
        n_substitute = min(n_substitute, len(surface_indices))

        rng = np.random.default_rng(seed=seed)
        sub_indices = rng.choice(surface_indices, n_substitute, replace=False)

        symbols = list(slab.get_chemical_symbols())
        for idx in sub_indices:
            symbols[idx] = dopant_type
        slab.set_chemical_symbols(symbols)

        logger.debug(
            f"Substituted {n_substitute} {dopant_type} atoms "
            f"({dopant_percent}% of {len(surface_indices)} surface atoms)"
        )

    # 4. Fix bottom 2 layers
    bottom_2_z = z_unique[:2]
    fix_indices = [
        i for i, z in enumerate(z_positions)
        if np.round(z, 1) in bottom_2_z
    ]
    slab.set_constraint(FixAtoms(indices=fix_indices))

    # 5. Set tags for OC20 compatibility
    # 0 = subsurface/bulk (fixed), 1 = surface (relaxed)
    tags = np.zeros(len(slab), dtype=int)
    top_2_z = z_unique[-2:]
    for i, z in enumerate(z_positions):
        if np.round(z, 1) in top_2_z:
            tags[i] = 1
    slab.set_tags(tags)

    logger.debug(f"Tags: {sum(tags==0)} bulk, {sum(tags==1)} surface")
    return slab


def build_bare_slab_with_h(
    dopant_type: str = "none",
    dopant_percent: float = 0,
    size: tuple[int, int, int] = (4, 4, 4),
    vacuum: float = 15.0,
    seed: int = 42,
    h_site: str = "fcc",
    h_height: float = 1.0,
) -> Atoms:
    """
    Build bare Ni-alloy slab + H adsorbate for OC20 HOR activity prediction.

    Parameters:
        dopant_type, dopant_percent, size, vacuum, seed: same as build_ni_alloy_slab
        h_site: Adsorption site ("fcc", "hcp", "ontop", "bridge")
        h_height: Height of H above surface (Å)

    Returns:
        ASE Atoms with slab + H, tagged for OC20 (H tag=2)
    """
    from ase.build import add_adsorbate

    slab = build_ni_alloy_slab(dopant_type, dopant_percent, size, vacuum, seed)

    # Add H adsorbate
    add_adsorbate(slab, "H", height=h_height, position=h_site)

    # Tag H as adsorbate (2)
    tags = list(slab.get_tags())
    tags[-1] = 2  # last atom is the added H
    slab.set_tags(tags)

    logger.debug(f"Added H at {h_site} site, height={h_height} Å")
    return slab
