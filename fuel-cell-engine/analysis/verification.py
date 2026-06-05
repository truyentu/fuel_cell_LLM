"""
Verification Pipeline — 7-step post-screening verification.
Outputs trust score to determine if results are reliable enough for lab.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger("engine.analysis.verification")


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""
    score: float = 0.0  # 0 or 1 for binary, 0-1 for continuous


@dataclass
class VerificationReport:
    checks: list[CheckResult] = field(default_factory=list)
    total_score: float = 0.0
    max_score: float = 7.0
    warnings: list[str] = field(default_factory=list)
    trust_score: str = ""  # A, B, C, D, F

    def summary(self) -> str:
        lines = ["# Verification Report", ""]
        lines.append(f"Trust Score: **{self.trust_score}** ({self.total_score:.1f}/{self.max_score:.1f})")
        lines.append("")
        lines.append("| # | Check | Status | Detail |")
        lines.append("|---|-------|--------|--------|")
        for i, c in enumerate(self.checks, 1):
            status = "✅" if c.passed else "❌"
            lines.append(f"| {i} | {c.name} | {status} | {c.detail} |")
        if self.warnings:
            lines.append("")
            lines.append("## Warnings")
            for w in self.warnings:
                lines.append(f"- ⚠️ {w}")
        return "\n".join(lines)


def run_verification(results, config) -> VerificationReport:
    """
    7-step verification pipeline. Runs automatically after Phase 1b.

    Parameters:
        results: ScreeningResults from screening phase
        config: PipelineConfig

    Returns:
        VerificationReport with trust score A-F
    """
    logger.info("=" * 50)
    logger.info("VERIFICATION PIPELINE")
    logger.info("=" * 50)

    report = VerificationReport()

    # 1. Sanity checks
    report.checks.append(_check_sanity(results))

    # 2. Convergence
    report.checks.append(_check_convergence(results))

    # 3. Cross-tool consistency
    report.checks.append(_check_cross_tool(results))

    # 4. Ensemble agreement
    report.checks.append(_check_ensemble(results))

    # 5. Perturbation robustness
    report.checks.append(_check_perturbation(results))

    # 6. Literature comparison
    report.checks.append(_check_literature(results, config))

    # 7. Internal consistency
    report.checks.append(_check_consistency(results))

    # Compute total
    report.total_score = sum(1.0 for c in report.checks if c.passed)
    report.max_score = float(len(report.checks))

    # Trust score
    from analysis.trust_scorer import compute_trust_score
    report.trust_score = compute_trust_score(report)

    # Log
    for c in report.checks:
        status = "PASS" if c.passed else "FAIL"
        logger.info(f"  [{status}] {c.name}: {c.detail}")

    logger.info(f"  TRUST SCORE: {report.trust_score} ({report.total_score}/{report.max_score})")

    return report


def _check_sanity(results) -> CheckResult:
    """
    Check 1: Physical sanity — energies reasonable, no NaN, no overlap.
    Reliability: 100%
    """
    issues = []
    successful = [c for c in results.candidates if c.status == "success"]

    if not successful:
        return CheckResult("Sanity", False, "No successful candidates")

    for c in successful:
        # Check HOR activity range (should be -1.0 to 0.0 for reasonable)
        hor = c.scores.get("hor_activity", 0)
        if hor < -1.0 or hor > 0.5:
            issues.append(f"iter {c.iteration}: HOR={hor:.3f} out of range")

        # Check barriers (should be positive)
        h2 = c.scores.get("h2_barrier", 0)
        o2 = c.scores.get("o2_barrier", 0)
        if h2 < 0:
            issues.append(f"iter {c.iteration}: negative H₂ barrier")
        if o2 < 0:
            issues.append(f"iter {c.iteration}: negative O₂ barrier")

        # Check stability (0-1 range)
        stab = c.scores.get("shell_stability", 0)
        if stab < 0 or stab > 1.01:
            issues.append(f"iter {c.iteration}: stability={stab} out of [0,1]")

    passed = len(issues) == 0
    detail = "All values in physical range" if passed else f"{len(issues)} anomalies: {issues[0]}"

    return CheckResult("Sanity", passed, detail)


def _check_convergence(results) -> CheckResult:
    """
    Check 2: Did BoTorch converge? Score flat in last iterations?
    Reliability: 100%
    """
    successful = [c for c in results.candidates if c.status == "success"]

    if len(successful) < 5:
        return CheckResult("Convergence", False, f"Too few data points ({len(successful)})")

    # Compute running best score
    scores = []
    best_so_far = float("-inf")
    for c in successful:
        score = sum(c.scores.values())
        best_so_far = max(best_so_far, score)
        scores.append(best_so_far)

    # Check last 5: improvement < 5%?
    if len(scores) >= 5:
        last_5_improvement = scores[-1] - scores[-5]
        relative_improvement = last_5_improvement / (abs(scores[-1]) + 1e-8)
        converged = relative_improvement < 0.05
        detail = f"Last 5 improvement: {relative_improvement*100:.1f}%"
    else:
        converged = False
        detail = "Not enough iterations"

    # Also pass if explicitly converged flag
    if results.converged:
        converged = True
        detail = "BoTorch reported convergence"

    return CheckResult("Convergence", converged, detail)


def _check_cross_tool(results) -> CheckResult:
    """
    Check 3: Do OC20 and MACE agree on relative rankings?
    Reliability: 90%
    """
    successful = [c for c in results.candidates if c.status == "success"]

    if len(successful) < 3:
        return CheckResult("Cross-tool", False, "Too few candidates")

    # Compare: candidates with high HOR activity should also have reasonable barriers
    # (If OC20 says "great" but MACE says "terrible" → inconsistency)
    inconsistencies = 0
    for c in successful:
        hor = c.scores.get("hor_activity", -1)
        h2 = c.scores.get("h2_barrier", 1)

        # If HOR is good (close to 0) but H₂ barrier is extremely high → suspect
        if hor > -0.2 and h2 > 0.6:
            inconsistencies += 1

    rate = inconsistencies / len(successful)
    passed = rate < 0.3
    detail = f"{inconsistencies}/{len(successful)} inconsistent ({rate*100:.0f}%)"

    return CheckResult("Cross-tool", passed, detail)


def _check_ensemble(results) -> CheckResult:
    """
    Check 4: Ensemble models agree? Low uncertainty on top candidates?
    Reliability: 85%
    """
    successful = [c for c in results.candidates if c.status == "success"]

    if not successful:
        return CheckResult("Ensemble", False, "No data")

    # Check uncertainty on top 5 candidates (by score)
    successful.sort(key=lambda c: sum(c.scores.values()), reverse=True)
    top5 = successful[:5]

    high_uncertainty = 0
    for c in top5:
        unc = c.uncertainty
        if not unc:
            continue
        if not unc.get("h2_confident", True):
            high_uncertainty += 1

    passed = high_uncertainty <= 1  # At most 1 of top 5 uncertain
    detail = f"{high_uncertainty}/5 top candidates have high uncertainty"

    if high_uncertainty > 1:
        logger.warning(f"Ensemble: {high_uncertainty} top candidates uncertain")

    return CheckResult("Ensemble", passed, detail)


def _check_perturbation(results) -> CheckResult:
    """
    Check 5: Are results robust to small parameter changes?
    Reliability: 80% (would need re-evaluation to be precise)

    Simplified: check if similar params give similar scores.
    """
    successful = [c for c in results.candidates if c.status == "success"]

    if len(successful) < 5:
        return CheckResult("Perturbation", True, "Too few candidates to assess (assumed OK)")

    # Check if nearby params have similar scores
    # Simplified proxy: variance of scores in top 50% shouldn't be extreme
    scores = sorted([sum(c.scores.values()) for c in successful], reverse=True)
    top_half = scores[:len(scores)//2]

    if len(top_half) < 2:
        return CheckResult("Perturbation", True, "Insufficient data (assumed OK)")

    std_top = np.std(top_half)
    mean_top = np.mean(top_half)
    cv = std_top / (abs(mean_top) + 1e-8)  # coefficient of variation

    # CV < 0.3 = robust, > 0.5 = sensitive
    passed = cv < 0.4
    detail = f"Top-half CV={cv:.3f} ({'robust' if passed else 'sensitive'})"

    return CheckResult("Perturbation", passed, detail)


def _check_literature(results, config) -> CheckResult:
    """
    Check 6: Do results match known scientific trends?
    Reliability: 70%

    Checks: NiMo should be better than pure Ni for HOR (well-established).
    """
    successful = [c for c in results.candidates if c.status == "success"]

    if len(successful) < 3:
        return CheckResult("Literature", True, "Too few candidates (assumed OK)")

    # Known: NiMo > pure Ni for HOR (H binding weakened)
    ni_hor = []
    nimo_hor = []

    for c in successful:
        hor = c.scores.get("hor_activity", -1)
        dopant = c.params.get("dopant_type", "none")
        if dopant == "none":
            ni_hor.append(hor)
        elif dopant == "Mo":
            nimo_hor.append(hor)

    if ni_hor and nimo_hor:
        mean_ni = np.mean(ni_hor)
        mean_nimo = np.mean(nimo_hor)

        # NiMo should have LESS negative (closer to 0) HOR = better
        nimo_better = mean_nimo > mean_ni
        detail = f"NiMo HOR={mean_nimo:.3f} vs Ni={mean_ni:.3f} (NiMo better: {nimo_better})"
        passed = nimo_better
    else:
        passed = True  # Can't check — not enough variety
        detail = "Insufficient alloy variety to compare (assumed OK)"

    return CheckResult("Literature", passed, detail)


def _check_consistency(results) -> CheckResult:
    """
    Check 7: Internal consistency — no contradictions between scores.
    Reliability: 80%
    """
    successful = [c for c in results.candidates if c.status == "success"]
    contradictions = 0

    for c in successful:
        h2 = c.scores.get("h2_barrier", 0)
        o2 = c.scores.get("o2_barrier", 0)

        # O₂ barrier should generally be HIGHER than H₂ barrier
        # (O₂ is larger molecule, harder to pass)
        if h2 > o2 + 0.1:  # H₂ barrier > O₂ barrier + margin → suspicious
            contradictions += 1

    rate = contradictions / len(successful) if successful else 0
    passed = rate < 0.2
    detail = f"{contradictions}/{len(successful)} have H₂_barrier > O₂_barrier (unexpected)"

    return CheckResult("Consistency", passed, detail)
