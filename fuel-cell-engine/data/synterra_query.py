"""
SynTERRA Query — Search 31K+ solid-state synthesis recipes.
Find recipes for Ni-alloys from text-mined literature database.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger("engine.data.synterra")

DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "synterra_repo", "solid-state_dataset_20200713.json"
)


class SynTERRAQuery:
    """Query synthesis recipes from text-mined solid-state synthesis database (31K+ entries)."""

    def __init__(self, data_path: str = DEFAULT_DATA_PATH):
        """
        Load SynTERRA reactions database.

        Args:
            data_path: Path to solid-state_dataset JSON file
        """
        self.data_path = data_path
        self.recipes = []
        self._loaded = False
        self._load()

    @property
    def is_available(self) -> bool:
        return self._loaded and len(self.recipes) > 0

    def _load(self):
        """Load JSON and index recipes."""
        path = Path(self.data_path)
        if not path.exists():
            logger.warning(f"SynTERRA data not found at {path}. Query disabled.")
            return

        logger.info(f"Loading SynTERRA data from {path}...")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.recipes = data.get("reactions", [])
            self._loaded = True
            logger.info(f"SynTERRA loaded: {len(self.recipes)} recipes")
        except Exception as e:
            logger.error(f"Failed to load SynTERRA data: {e}")

    def search(self, formula: str, fuzzy: bool = True, max_results: int = 20) -> list[dict]:
        """
        Find recipes where target material matches formula.

        Args:
            formula: Target material (e.g., "NiMo", "Ni3Mo", "NiO")
            fuzzy: If True, match partial (element-based)
            max_results: Maximum results to return

        Returns:
            List of formatted recipe dicts, sorted by relevance
        """
        if not self._loaded:
            return []

        target_elements = _parse_elements(formula)
        if not target_elements:
            return []

        matches = []

        for recipe in self.recipes:
            target = recipe.get("target", {})
            compositions = target.get("composition", [])

            for comp in compositions:
                comp_elements = set(comp.get("elements", {}).keys())

                # Exact match: same elements
                if comp_elements == target_elements:
                    matches.append({"recipe": recipe, "score": 1.0, "match_type": "exact"})
                    break
                # Fuzzy: target elements are subset of recipe target
                elif fuzzy and target_elements.issubset(comp_elements):
                    matches.append({"recipe": recipe, "score": 0.5, "match_type": "subset"})
                    break
                # Fuzzy: recipe target is subset of query
                elif fuzzy and comp_elements.issubset(target_elements) and len(comp_elements) > 1:
                    matches.append({"recipe": recipe, "score": 0.3, "match_type": "partial"})
                    break

        # Sort by score descending
        matches.sort(key=lambda m: m["score"], reverse=True)

        # Format results
        results = []
        for m in matches[:max_results]:
            results.append(self._format_recipe(m["recipe"], m["match_type"]))

        return results

    def search_by_elements(self, elements: list[str], max_results: int = 20) -> list[dict]:
        """
        Find recipes where target contains ALL specified elements.

        Args:
            elements: e.g., ["Ni", "Mo"]
        """
        if not self._loaded:
            return []

        required = set(elements)
        matches = []

        for recipe in self.recipes:
            target = recipe.get("target", {})
            compositions = target.get("composition", [])

            for comp in compositions:
                comp_elements = set(comp.get("elements", {}).keys())
                if required.issubset(comp_elements):
                    matches.append(self._format_recipe(recipe, "element_match"))
                    break

        return matches[:max_results]

    def get_recipe_summary(self, recipe: dict) -> str:
        """
        Format recipe as human-readable one-line string.

        Returns:
            "Precursors: NiO + MoO3 → Heat 900°C, 8h, H2/Ar [doi:10.1016/...]"
        """
        precursors = recipe.get("precursors_list", [])
        temp = recipe.get("max_temperature_C")
        time_h = recipe.get("max_duration_h")
        atmosphere = recipe.get("atmosphere")
        doi = recipe.get("doi", "")

        parts = []

        # Precursors
        if precursors:
            parts.append(f"Precursors: {' + '.join(precursors[:5])}")

        # Conditions
        conditions = []
        if temp:
            conditions.append(f"{temp}°C")
        if time_h:
            conditions.append(f"{time_h}h")
        if atmosphere:
            conditions.append(atmosphere)

        if conditions:
            parts.append(f"→ Heat {', '.join(conditions)}")

        # DOI
        if doi:
            parts.append(f"[doi:{doi}]")

        return " ".join(parts) if parts else "No details available"

    def _format_recipe(self, recipe: dict, match_type: str) -> dict:
        """Format raw recipe into clean output dict."""
        target = recipe.get("target", {})
        target_formula = target.get("material_formula", "")
        target_string = recipe.get("targets_string", [""])[0] if recipe.get("targets_string") else ""

        # Extract precursor formulas
        precursors_raw = recipe.get("precursors", [])
        precursors_list = [p.get("material_formula", "") for p in precursors_raw if p.get("material_formula")]

        # Extract operations (temperature, time, atmosphere)
        operations = recipe.get("operations", [])
        max_temp = None
        max_time = None
        atmosphere = None

        for op in operations:
            cond = op.get("conditions", {})
            temp = cond.get("heating_temperature")
            time = cond.get("heating_time")
            atm = cond.get("heating_atmosphere")

            if temp:
                # Parse temperature (could be dict or list)
                t_val = _extract_number(temp)
                if t_val and (max_temp is None or t_val > max_temp):
                    max_temp = t_val

            if time:
                t_val = _extract_number(time)
                if t_val and (max_time is None or t_val > max_time):
                    max_time = t_val

            if atm and not atmosphere:
                atmosphere = _extract_atmosphere(atm)

        result = {
            "target_formula": target_formula or target_string,
            "precursors_list": precursors_list,
            "max_temperature_C": max_temp,
            "max_duration_h": max_time,
            "atmosphere": atmosphere,
            "doi": recipe.get("doi", ""),
            "match_type": match_type,
            "reaction_string": recipe.get("reaction_string", ""),
            "caveat": (
                "⚠️ BULK solid-state recipe. For nanoparticle/thin-film: "
                "adapt approach (co-reduction, sputtering, MOF pyrolysis)."
            ),
        }

        # Add summary
        result["recipe_summary"] = self.get_recipe_summary(result)

        return result


# --- Helpers ---

def _parse_elements(formula: str) -> set:
    """
    Parse chemical formula into set of elements.
    "Ni3Mo" → {"Ni", "Mo"}
    "NiFe2O4" → {"Ni", "Fe", "O"}
    """
    pattern = r"([A-Z][a-z]?)"
    elements = re.findall(pattern, formula)
    return set(elements) if elements else set()


def _extract_number(value) -> Optional[float]:
    """Extract numeric value from various formats."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Try to extract first number from string
        match = re.search(r"(\d+\.?\d*)", value)
        if match:
            return float(match.group(1))
    if isinstance(value, dict):
        # May have "max", "min", "value" keys
        for key in ["max", "value", "min"]:
            if key in value:
                return _extract_number(value[key])
    if isinstance(value, list) and len(value) > 0:
        return _extract_number(value[-1])  # take last (often highest)
    return None


def _extract_atmosphere(value) -> Optional[str]:
    """Extract atmosphere string."""
    if isinstance(value, str):
        return value
    if isinstance(value, list) and len(value) > 0:
        return str(value[0])
    return None
