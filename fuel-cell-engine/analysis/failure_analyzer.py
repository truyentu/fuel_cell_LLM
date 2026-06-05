"""
Failure Analyzer — classify failure modes and suggest BoTorch constraints.
Inspired by A-Lab (ARROWS3): learn from failures, don't just skip them.
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("engine.analysis.failure")


@dataclass
class FailureAnalysis:
    """Analysis of why a candidate failed."""
    failure_type: str
    description: str
    constraint_suggestion: Optional[dict] = None
    region_to_avoid: Optional[str] = None


# Failure mode definitions
FAILURE_MODES = {
    "shell_collapse": {
        "description": "Shell structurally collapsed during MD — vacancy too high or layers too few",
        "indicators": ["intact_ratio < 0.5", "max_displacement > 3.0 Å"],
    },
    "h2_blocked": {
        "description": "H₂ barrier too high — shell too thick or too few defects",
        "indicators": ["h2_barrier > 0.5 eV", "NEB converged but barrier excessive"],
    },
    "o2_leaks": {
        "description": "O₂ barrier too low — shell too porous, won't protect Ni",
        "indicators": ["o2_barrier < 0.3 eV"],
    },
    "neb_no_converge": {
        "description": "NEB optimization did not converge — structure may be unstable",
        "indicators": ["NEB fmax > threshold after max steps"],
    },
    "alloy_unstable": {
        "description": "Alloy formation energy positive — phase separation likely",
        "indicators": ["energy_per_atom much higher than pure Ni"],
    },
    "generation_failed": {
        "description": "Structure generation produced invalid geometry",
        "indicators": ["atom overlap", "validation failed"],
    },
}


def analyze_failure(params: dict, failure_reason: str, scores: dict = None) -> FailureAnalysis:
    """
    Classify failure and suggest what to avoid.

    Parameters:
        params: Candidate parameters that failed
        failure_reason: Raw failure reason string
        scores: Partial scores if available

    Returns:
        FailureAnalysis with classification and suggestions
    """
    scores = scores or {}

    # Classify based on failure reason
    if "generation" in failure_reason.lower():
        return _analyze_generation_failure(params)

    if "neb" in failure_reason.lower() and "h2" in failure_reason.lower():
        return _analyze_h2_blocked(params, scores)

    if "neb" in failure_reason.lower() and "o2" in failure_reason.lower():
        return _analyze_o2_failure(params, scores)

    if "md" in failure_reason.lower() or "stability" in failure_reason.lower():
        return _analyze_shell_collapse(params, scores)

    if "oc20" in failure_reason.lower():
        return _analyze_oc20_failure(params, scores)

    # Generic
    return FailureAnalysis(
        failure_type="unknown",
        description=f"Unclassified failure: {failure_reason}",
    )


def _analyze_generation_failure(params: dict) -> FailureAnalysis:
    """Structure couldn't be generated."""
    vacancy = params.get("vacancy_percent", 0)
    layers = params.get("n_layers", 2)

    suggestion = None
    if vacancy > 15 and layers <= 1:
        suggestion = {
            "type": "avoid_region",
            "condition": "vacancy_percent > 15 AND n_layers <= 1",
            "reason": "High vacancy + thin shell = structural instability",
        }

    return FailureAnalysis(
        failure_type="generation_failed",
        description=f"Failed to generate valid structure (vac={vacancy}%, layers={layers})",
        constraint_suggestion=suggestion,
        region_to_avoid=f"vacancy>{vacancy}% with layers<={layers}" if suggestion else None,
    )


def _analyze_h2_blocked(params: dict, scores: dict) -> FailureAnalysis:
    """H₂ can't permeate shell."""
    layers = params.get("n_layers", 2)
    vacancy = params.get("vacancy_percent", 0)

    suggestion = None
    if vacancy < 5:
        suggestion = {
            "type": "soft_constraint",
            "condition": f"vacancy_percent >= 5",
            "reason": "Need minimum defects for H₂ permeation",
        }
    elif layers >= 3:
        suggestion = {
            "type": "avoid_region",
            "condition": "n_layers >= 3 AND vacancy_percent < 10",
            "reason": "3 layers requires high vacancy for H₂ access",
        }

    return FailureAnalysis(
        failure_type="h2_blocked",
        description=f"H₂ barrier too high (layers={layers}, vac={vacancy}%)",
        constraint_suggestion=suggestion,
        region_to_avoid=f"layers={layers} with vacancy<{vacancy+3}%",
    )


def _analyze_o2_failure(params: dict, scores: dict) -> FailureAnalysis:
    """O₂ can pass through shell (bad — Ni will oxidize)."""
    vacancy = params.get("vacancy_percent", 0)
    layers = params.get("n_layers", 2)

    suggestion = None
    if vacancy > 12 and layers <= 1:
        suggestion = {
            "type": "avoid_region",
            "condition": f"vacancy_percent > 12 AND n_layers <= 1",
            "reason": "Too porous for O₂ blocking with single layer",
        }

    return FailureAnalysis(
        failure_type="o2_leaks",
        description=f"O₂ barrier too low (vac={vacancy}%, layers={layers})",
        constraint_suggestion=suggestion,
        region_to_avoid=f"vacancy>{vacancy}% with layers<={layers}",
    )


def _analyze_shell_collapse(params: dict, scores: dict) -> FailureAnalysis:
    """Shell collapsed during MD."""
    vacancy = params.get("vacancy_percent", 0)
    layers = params.get("n_layers", 2)
    n_doping = params.get("n_doping_percent", 0)

    suggestion = {
        "type": "avoid_region",
        "condition": f"vacancy_percent > {vacancy - 2} AND n_layers <= {layers}",
        "reason": "Shell collapse observed — reduce vacancy or increase layers",
    }

    return FailureAnalysis(
        failure_type="shell_collapse",
        description=(
            f"Shell collapsed in MD (vac={vacancy}%, layers={layers}, N={n_doping}%)"
        ),
        constraint_suggestion=suggestion,
        region_to_avoid=f"vacancy>={vacancy}% with layers<={layers}",
    )


def _analyze_oc20_failure(params: dict, scores: dict) -> FailureAnalysis:
    """OC20 calculation failed."""
    dopant = params.get("dopant_type", "none")
    dopant_pct = params.get("dopant_percent", 0)

    return FailureAnalysis(
        failure_type="alloy_unstable",
        description=f"OC20 failed for {dopant}{int(dopant_pct)}% — alloy may be unstable",
        constraint_suggestion=None,
        region_to_avoid=f"{dopant}>{dopant_pct}%" if dopant_pct > 25 else None,
    )


def summarize_failures(candidates: list) -> dict:
    """
    Summarize all failures from screening results.

    Parameters:
        candidates: list of CandidateResult objects

    Returns:
        {"total_failed": int, "by_type": {type: count}, "analyses": [FailureAnalysis]}
    """
    failed = [c for c in candidates if c.status != "success"]

    if not failed:
        return {"total_failed": 0, "by_type": {}, "analyses": []}

    analyses = []
    by_type = {}

    for c in failed:
        analysis = analyze_failure(c.params, c.failure_reason, c.scores)
        analyses.append(analysis)
        by_type[analysis.failure_type] = by_type.get(analysis.failure_type, 0) + 1

    logger.info(f"Failure summary: {len(failed)} total, by type: {by_type}")

    return {
        "total_failed": len(failed),
        "by_type": by_type,
        "analyses": analyses,
        "suggested_constraints": [a.constraint_suggestion for a in analyses if a.constraint_suggestion],
        "regions_to_avoid": [a.region_to_avoid for a in analyses if a.region_to_avoid],
    }
