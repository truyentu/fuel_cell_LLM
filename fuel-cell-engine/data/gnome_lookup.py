"""
GNoME 520K+ Stable Materials Lookup.
Query alloy stability from Google DeepMind's GNoME dataset (554K entries).
"""

import csv
import logging
import os
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger("engine.data.gnome")

# Default path relative to engine root
DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "gnome_data", "stable_materials_summary.csv"
)


class GNoMELookup:
    """Lookup alloy stability from GNoME 554K stable crystals dataset."""

    def __init__(self, data_path: str = DEFAULT_DATA_PATH):
        """
        Load GNoME CSV into searchable index.

        Args:
            data_path: Path to stable_materials_summary.csv
        """
        self.data_path = data_path
        self.entries = []
        self._index_by_formula = {}
        self._index_by_elements = {}
        self._loaded = False
        self._load()

    @property
    def is_available(self) -> bool:
        return self._loaded and len(self.entries) > 0

    def _load(self):
        """Load CSV and build indexes."""
        path = Path(self.data_path)
        if not path.exists():
            logger.warning(f"GNoME data not found at {path}. Lookup disabled.")
            return

        logger.info(f"Loading GNoME data from {path}...")
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entry = {
                        "formula": row.get("Reduced Formula", ""),
                        "composition": row.get("Composition", ""),
                        "elements": row.get("Elements", ""),
                        "material_id": row.get("MaterialId", ""),
                        "formation_energy_per_atom": _safe_float(row.get("Formation Energy Per Atom")),
                        "decomposition_energy_per_atom": _safe_float(row.get("Decomposition Energy Per Atom")),
                        "space_group": row.get("Space Group", ""),
                        "crystal_system": row.get("Crystal System", ""),
                        "nsites": _safe_int(row.get("NSites")),
                        "bandgap": _safe_float(row.get("Bandgap")),
                    }
                    self.entries.append(entry)

                    # Index by reduced formula
                    formula = entry["formula"].strip()
                    if formula:
                        self._index_by_formula.setdefault(formula, []).append(entry)

                    # Index by element set (sorted, frozen)
                    elements_str = entry["elements"].strip()
                    if elements_str:
                        elem_key = _normalize_elements_key(elements_str)
                        self._index_by_elements.setdefault(elem_key, []).append(entry)

            self._loaded = True
            logger.info(
                f"GNoME loaded: {len(self.entries)} entries, "
                f"{len(self._index_by_formula)} unique formulas, "
                f"{len(self._index_by_elements)} unique element combinations"
            )
        except Exception as e:
            logger.error(f"Failed to load GNoME data: {e}")

    def lookup(self, formula: str) -> Optional[dict]:
        """
        Check if composition exists in GNoME stable crystals.

        Args:
            formula: Chemical formula (e.g., "Ni3Mo", "NiFe2", "NiO")

        Returns:
            Best match entry or None if not found.
            {
                "formula": str,
                "stable": bool (decomposition_energy ≈ 0),
                "formation_energy_per_atom": float,
                "decomposition_energy_per_atom": float,
                "material_id": str,
                "space_group": str,
                "source": "GNoME stable materials dataset"
            }
        """
        if not self._loaded:
            return None

        # Try exact formula match first
        normalized = _normalize_formula(formula)
        matches = self._index_by_formula.get(normalized, [])

        if not matches:
            # Try common variants (e.g., "NiMo" → "MoNi", "Ni3Mo" → "MoNi3")
            variants = _formula_variants(formula)
            for variant in variants:
                matches = self._index_by_formula.get(variant, [])
                if matches:
                    break

        if not matches:
            return None

        # Return most stable (lowest decomposition energy)
        best = min(matches, key=lambda e: e["decomposition_energy_per_atom"] or 999)
        decomp_e = best["decomposition_energy_per_atom"]

        return {
            "formula": best["formula"],
            "stable": decomp_e is not None and decomp_e <= 0.05,  # ≤50 meV above hull
            "formation_energy_per_atom": best["formation_energy_per_atom"],
            "decomposition_energy_per_atom": decomp_e,
            "material_id": best["material_id"],
            "space_group": best["space_group"],
            "crystal_system": best["crystal_system"],
            "source": "GNoME stable materials dataset (554K entries)",
        }

    def search_by_elements(
        self, elements: list[str], max_results: int = 50, only_stable: bool = True
    ) -> list[dict]:
        """
        Find all stable structures containing EXACTLY the specified elements.

        Args:
            elements: e.g., ["Ni", "Mo"]
            max_results: Maximum entries to return
            only_stable: If True, only return entries with decomp_energy ≤ 0.05 eV

        Returns:
            List of matching entries sorted by formation_energy
        """
        if not self._loaded:
            return []

        elem_key = tuple(sorted(elements))
        matches = self._index_by_elements.get(elem_key, [])

        if only_stable:
            matches = [
                m for m in matches
                if m["decomposition_energy_per_atom"] is not None
                and m["decomposition_energy_per_atom"] <= 0.05
            ]

        # Sort by formation energy (most stable first)
        matches.sort(key=lambda e: e["formation_energy_per_atom"] or 999)

        return matches[:max_results]

    def search_containing_elements(
        self, elements: list[str], max_results: int = 100, only_stable: bool = True
    ) -> list[dict]:
        """
        Find structures containing AT LEAST the specified elements (may have more).

        Args:
            elements: e.g., ["Ni", "Mo"] → finds Ni-Mo, Ni-Mo-O, Ni-Mo-Fe-O, etc.
            max_results: Maximum entries to return
            only_stable: If True, only return entries with decomp_energy ≤ 0.05 eV

        Returns:
            List of matching entries sorted by formation_energy
        """
        if not self._loaded:
            return []

        required = set(elements)
        matches = []

        for elem_key, entries in self._index_by_elements.items():
            if required.issubset(set(elem_key)):
                for entry in entries:
                    if only_stable:
                        decomp = entry["decomposition_energy_per_atom"]
                        if decomp is None or decomp > 0.05:
                            continue
                    matches.append(entry)

        matches.sort(key=lambda e: e["formation_energy_per_atom"] or 999)
        return matches[:max_results]

    def count_by_elements(self, elements: list[str]) -> dict:
        """Quick count of entries containing specified elements."""
        if not self._loaded:
            return {"total": 0, "stable": 0}

        required = set(elements)
        total = 0
        stable = 0

        for elem_key, entries in self._index_by_elements.items():
            if required.issubset(set(elem_key)):
                total += len(entries)
                stable += sum(
                    1 for e in entries
                    if e["decomposition_energy_per_atom"] is not None
                    and e["decomposition_energy_per_atom"] <= 0.05
                )

        return {"total": total, "stable": stable}


# --- Helpers ---

def _safe_float(val) -> Optional[float]:
    """Safely convert to float, return None if empty/invalid."""
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_int(val) -> Optional[int]:
    """Safely convert to int."""
    if val is None or val == "":
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _normalize_elements_key(elements_str: str) -> tuple:
    """
    Normalize elements string to sorted tuple.
    GNoME format: "['Ni', 'Y', 'Er', 'Bi']" → ("Bi", "Er", "Ni", "Y")
    Also handles: "Ni-Mo" → ("Mo", "Ni")
    """
    # Handle Python list string format: "['Ni', 'Mo', 'O']"
    if elements_str.startswith("["):
        # Parse as Python list literal
        elements = re.findall(r"'([A-Z][a-z]?)'", elements_str)
        return tuple(sorted(elements))

    # Fallback: split by common separators
    parts = re.split(r"[-\s,]+", elements_str.strip())
    return tuple(sorted(p.strip() for p in parts if p.strip()))


def _normalize_formula(formula: str) -> str:
    """Basic formula normalization."""
    return formula.strip()


def _formula_variants(formula: str) -> list[str]:
    """
    Generate common formula variants for fuzzy matching.
    "NiMo" → ["MoNi", "Ni1Mo1", "NiMo"]
    "Ni3Mo" → ["MoNi3", "Ni3Mo1"]
    """
    variants = [formula]

    # Parse formula into elements + counts
    pattern = r"([A-Z][a-z]?)(\d*)"
    parts = re.findall(pattern, formula)
    elements = [(elem, int(count) if count else 1) for elem, count in parts if elem]

    if not elements:
        return variants

    # Reverse order
    reversed_formula = "".join(f"{e}{c if c > 1 else ''}" for e, c in reversed(elements))
    if reversed_formula != formula:
        variants.append(reversed_formula)

    # Alphabetical order
    sorted_elements = sorted(elements, key=lambda x: x[0])
    alpha_formula = "".join(f"{e}{c if c > 1 else ''}" for e, c in sorted_elements)
    if alpha_formula not in variants:
        variants.append(alpha_formula)

    return variants
