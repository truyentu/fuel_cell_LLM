"""
Phase 1a: Coarse Filter — 2-step stability screening.

Step 1: CHGNet predict formation energy → stable/unstable (PRIMARY)
Step 2: GNoME lookup → bonus confidence if found (BONUS, not filter)

NOTE: MACE is NOT used here. MACE is reserved for Phase 1b (NEB + MD).
      CHGNet is specialized for stability prediction.
      GNoME = novel materials only (absence ≠ unstable).
"""

import logging
from typing import Optional

import numpy as np
from ase import Atoms

from runners.chgnet_runner import CHGNetRunner
from data.gnome_lookup import GNoMELookup
from structures.ni_at_c_generator import generate_structure_from_params, validate_structure

logger = logging.getLogger("engine.phases.coarse_filter")


def coarse_filter(
    config: dict,
    chgnet_runner: CHGNetRunner,
    gnome_lookup: Optional[GNoMELookup] = None,
    n_random: int = 100,
    keep_percentile: int = 30,
    seed: int = 42,
) -> list[dict]:
    """
    2-step coarse filter: CHGNet stability + GNoME bonus.

    Logic:
      Step 1: CHGNet predict stability for alloy bulk structure
              → stable (energy reasonable) → PASS
              → unstable → REJECT

      Step 2: GNoME lookup (bonus, optional)
              → found + stable → extra confidence tag
              → not found → NO ACTION (absence ≠ unstable)

    Parameters:
        config: Pipeline config (search_space + structure_generator)
        chgnet_runner: CHGNet runner (stability prediction)
        gnome_lookup: GNoME dataset lookup (optional, bonus info)
        n_random: Number of random structures to generate
        keep_percentile: Keep top X% (lowest energy/atom from CHGNet)
        seed: Random seed

    Returns:
        List of param dicts that passed filter, enriched with stability info
    """
    logger.info("=" * 50)
    logger.info(f"Phase 1a: COARSE FILTER ({n_random} random → top {keep_percentile}%)")
    logger.info("  Step 1: CHGNet stability (primary filter)")
    logger.info(f"  Step 2: GNoME lookup (bonus confidence)")
    logger.info("=" * 50)

    rng = np.random.default_rng(seed=seed)
    variables = config["search_space"]["variables"]
    struct_config = config["structure_generator"]

    # Generate random params
    random_params_list = []
    for i in range(n_random):
        params = _sample_random_params(variables, rng)
        random_params_list.append(params)

    # Evaluate each
    results = []
    n_failed = 0
    n_gnome_confirmed = 0

    for i, params in enumerate(random_params_list):
        # Generate structure (full Ni@C for validation, bulk alloy for CHGNet)
        structure = generate_structure_from_params(params, struct_config, seed=seed + i)

        if structure is None:
            n_failed += 1
            continue

        validation = validate_structure(structure)
        if not validation["valid"]:
            n_failed += 1
            continue

        # --- Step 1: CHGNet stability prediction ---
        # Use bulk alloy slab (not full Ni@C) for stability check
        from structures.slab_builder import build_ni_alloy_slab
        bulk_slab = build_ni_alloy_slab(
            dopant_type=params.get("dopant_type", "none"),
            dopant_percent=params.get("dopant_percent", 0),
            size=(2, 2, 2),  # small bulk for quick CHGNet eval
            vacuum=0,
            seed=seed + i,
        )

        chgnet_result = chgnet_runner.predict_stability(bulk_slab)

        if chgnet_result is None:
            n_failed += 1
            continue

        # --- Step 2: GNoME bonus lookup ---
        gnome_info = None
        if gnome_lookup and gnome_lookup.is_available:
            formula = _params_to_formula(params)
            gnome_result = gnome_lookup.lookup(formula)

            if gnome_result and gnome_result["stable"]:
                gnome_info = gnome_result
                n_gnome_confirmed += 1

            # Also check containing elements (broader search)
            if gnome_info is None:
                elements = _params_to_elements(params)
                containing = gnome_lookup.search_containing_elements(
                    elements, max_results=1, only_stable=True
                )
                if containing:
                    gnome_info = {"related_stable": containing[0]["formula"]}

        results.append({
            "params": params,
            "energy_per_atom": chgnet_result["energy_per_atom_eV"],
            "chgnet_stable": chgnet_result["stable"],
            "gnome_confirmed": gnome_info is not None,
            "gnome_info": gnome_info,
            "n_atoms": len(structure),
        })

    if not results:
        logger.error("Coarse filter: ALL structures failed! Check structure generator.")
        return random_params_list[:8]  # fallback

    # --- Filtering logic ---
    # Primary: sort by CHGNet energy (lower = more stable)
    results.sort(key=lambda x: x["energy_per_atom"])

    # Keep top percentile
    n_keep = max(1, int(len(results) * keep_percentile / 100))
    survivors = results[:n_keep]

    # Bonus: if GNoME-confirmed candidate didn't make percentile cut, add it anyway
    gnome_bonus = [
        r for r in results[n_keep:]
        if r["gnome_confirmed"] and r["chgnet_stable"]
    ]
    if gnome_bonus:
        survivors.extend(gnome_bonus[:5])  # max 5 bonus additions
        logger.info(f"  GNoME bonus: {len(gnome_bonus[:5])} candidates added (confirmed novel stable)")

    logger.info(f"  Generated: {n_random}, Valid: {len(results)}, Failed: {n_failed}")
    logger.info(f"  CHGNet filtered: {len(results)} → {len(survivors)} (top {keep_percentile}% + bonus)")
    logger.info(f"  GNoME confirmed: {n_gnome_confirmed}/{len(results)}")
    if results:
        logger.info(
            f"  Energy range: {results[0]['energy_per_atom']:.3f} to "
            f"{results[-1]['energy_per_atom']:.3f} eV/atom"
        )
        logger.info(f"  Cutoff: {survivors[n_keep-1]['energy_per_atom']:.3f} eV/atom")

    return [s["params"] for s in survivors]


# --- Gate Check ---

def check_filter_gate(results: list, min_survivors: int = 10) -> dict:
    """
    Gate check: enough candidates passed filter?

    If too few pass → search space may be too narrow or model broken.

    Returns:
        {"pass": bool, "message": str, "n_survivors": int}
    """
    n = len(results)
    if n >= min_survivors:
        return {"pass": True, "message": f"Gate PASS: {n} candidates survived filter", "n_survivors": n}
    else:
        return {
            "pass": False,
            "message": (
                f"Gate FAIL: only {n} candidates survived (need ≥{min_survivors}). "
                f"Consider: expand search space, lower filter threshold, or check CHGNet predictions."
            ),
            "n_survivors": n,
        }


# --- Helpers ---

def _params_to_formula(params: dict) -> str:
    """Convert params to approximate chemical formula for GNoME lookup."""
    dopant = params.get("dopant_type", "none")
    dopant_pct = params.get("dopant_percent", 0)

    if dopant == "none" or dopant_pct == 0:
        return "Ni"

    # Approximate integer ratio
    if dopant_pct >= 40:
        return f"Ni{dopant}"  # ~50:50
    elif dopant_pct >= 25:
        return f"Ni3{dopant}"  # ~75:25
    elif dopant_pct >= 15:
        return f"Ni4{dopant}"  # ~80:20 → closest
    else:
        return f"Ni8{dopant}"  # ~90:10


def _params_to_elements(params: dict) -> list[str]:
    """Extract elements from params."""
    elements = ["Ni"]
    dopant = params.get("dopant_type", "none")
    if dopant != "none":
        elements.append(dopant)
    return elements


def _sample_random_params(variables: dict, rng: np.random.Generator) -> dict:
    """Sample random parameter combination from search space."""
    params = {}

    for name, var in variables.items():
        var_type = var.get("type") if isinstance(var, dict) else var.type

        if var_type == "categorical":
            values = var.get("values") if isinstance(var, dict) else var.values
            params[name] = rng.choice(values)

        elif var_type in ("int", "float"):
            var_range = var.get("range") if isinstance(var, dict) else var.range
            low, high = var_range[0], var_range[1]
            step = var.get("step") if isinstance(var, dict) else getattr(var, "step", None)

            if var_type == "int":
                params[name] = int(rng.integers(int(low), int(high) + 1))
            elif step:
                possible = np.arange(low, high + step * 0.5, step)
                params[name] = float(rng.choice(possible))
            else:
                params[name] = float(rng.uniform(low, high))

    return params
