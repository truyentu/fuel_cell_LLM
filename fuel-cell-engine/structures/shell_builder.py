"""
Graphene shell builder with vacancies and N-doping.
Builds graphene layers commensurate with Ni(111) slab for Ni@C model.
"""

import logging
from typing import Optional

import numpy as np
from ase import Atoms

logger = logging.getLogger("engine.structures.shell")


def _make_graphene_positions(nx: int, ny: int, a: float = 2.46) -> np.ndarray:
    """
    Generate graphene atom positions in hexagonal lattice.

    Parameters:
        nx, ny: Supercell repeats
        a: Graphene lattice constant (Å)

    Returns:
        (N, 3) array of positions
    """
    # Basis: 2 atoms per unit cell
    basis = np.array([
        [0.0, 0.0, 0.0],
        [a / 2, a * np.sqrt(3) / 6, 0.0],
    ])
    # Lattice vectors
    a1 = np.array([a, 0.0, 0.0])
    a2 = np.array([a / 2, a * np.sqrt(3) / 2, 0.0])

    positions = []
    for i in range(nx):
        for j in range(ny):
            for b in basis:
                pos = b + i * a1 + j * a2
                positions.append(pos)

    return np.array(positions)


def build_graphene_layers(
    n_layers: int,
    vacancy_percent: float,
    n_doping_percent: float,
    cell_xy: tuple[float, float],
    z_start: float,
    seed: int = 42,
    interlayer_spacing: float = 3.4,
    stacking: str = "AB",
) -> Atoms:
    """
    Build graphene layer(s) commensurate with Ni slab cell.

    Parameters:
        n_layers: 1, 2, or 3 graphene layers
        vacancy_percent: 0-20, percentage of C atoms removed
        n_doping_percent: 0-10, percentage of C atoms replaced by N
        cell_xy: (a, b) cell dimensions from Ni slab (Å)
        z_start: z-coordinate for first graphene layer (Å)
        seed: Random seed for reproducibility
        interlayer_spacing: Distance between graphene layers (Å)
        stacking: "AB" or "AA" stacking

    Returns:
        ASE Atoms object with graphene layers (tagged as adsorbate=2)
    """
    rng = np.random.default_rng(seed=seed)

    # Determine graphene supercell to match Ni slab cell
    a_graphene = 2.46  # Å
    # For Ni(111) 4×4: cell ~9.96 Å. Graphene 4×4: ~9.84 Å. Stretch ~1.2%
    nx = max(1, int(round(cell_xy[0] / a_graphene)))
    ny = max(1, int(round(cell_xy[1] / (a_graphene * np.sqrt(3) / 2))))

    # Adjust a_graphene to exactly match Ni cell (small strain)
    a_stretched_x = cell_xy[0] / nx
    # Use average of x and y strain
    a_effective = a_stretched_x  # simplified: use x-direction match

    all_positions = []
    all_symbols = []

    for layer_i in range(n_layers):
        # Z position
        z = z_start + layer_i * interlayer_spacing

        # Generate base positions
        positions = _make_graphene_positions(nx, ny, a=a_effective)

        # AB stacking offset for odd layers
        if stacking == "AB" and layer_i % 2 == 1:
            offset = np.array([a_effective / 2, a_effective * np.sqrt(3) / 6, 0.0])
            positions += offset

        # Set z coordinate
        positions[:, 2] = z

        n_atoms_total = len(positions)
        symbols = ["C"] * n_atoms_total

        # Apply vacancies (random removal)
        n_vacancies = int(n_atoms_total * vacancy_percent / 100)
        if n_vacancies > 0:
            # Don't remove ALL atoms
            n_vacancies = min(n_vacancies, n_atoms_total - 2)
            vac_indices = set(rng.choice(n_atoms_total, n_vacancies, replace=False))

            # Filter out vacancy atoms
            positions = np.array([
                p for i, p in enumerate(positions) if i not in vac_indices
            ])
            symbols = [
                s for i, s in enumerate(symbols) if i not in vac_indices
            ]

        n_remaining = len(symbols)

        # Apply N-doping (substitute C → N)
        n_ndope = int(n_remaining * n_doping_percent / 100)
        if n_ndope > 0:
            dope_indices = rng.choice(n_remaining, n_ndope, replace=False)
            for idx in dope_indices:
                symbols[idx] = "N"

        all_positions.extend(positions.tolist())
        all_symbols.extend(symbols)

    # Create Atoms object (no cell — will be set by parent)
    graphene = Atoms(
        symbols=all_symbols,
        positions=all_positions,
    )

    # Tag all as adsorbate (2) for OC20 compatibility
    graphene.set_tags([2] * len(graphene))

    logger.debug(
        f"Built graphene: {n_layers} layers, {len(graphene)} atoms "
        f"({vacancy_percent}% vac, {n_doping_percent}% N), "
        f"nx={nx}, ny={ny}"
    )

    return graphene


def get_graphene_stats(graphene: Atoms) -> dict:
    """Get statistics about generated graphene structure."""
    symbols = graphene.get_chemical_symbols()
    n_c = symbols.count("C")
    n_n = symbols.count("N")
    n_total = len(symbols)

    return {
        "n_atoms": n_total,
        "n_carbon": n_c,
        "n_nitrogen": n_n,
        "n_doping_actual_percent": 100 * n_n / n_total if n_total > 0 else 0,
    }
