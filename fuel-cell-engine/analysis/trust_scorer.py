"""
Trust Scorer — compute A-F trust score from verification results.
"""

import logging

logger = logging.getLogger("engine.analysis.trust")


def compute_trust_score(report) -> str:
    """
    Compute trust score based on verification checks.

    A: All pass + high confidence
    B: Most pass, minor warnings
    C: Some pass, notable warnings
    D: Multiple failures
    F: Critical failure (sanity or no data)

    Parameters:
        report: VerificationReport

    Returns:
        Letter grade "A", "B", "C", "D", or "F"
    """
    checks = report.checks
    if not checks:
        return "F"

    n_passed = sum(1 for c in checks if c.passed)
    n_total = len(checks)

    # Critical checks (if these fail → immediate downgrade)
    sanity_check = next((c for c in checks if c.name == "Sanity"), None)
    convergence_check = next((c for c in checks if c.name == "Convergence"), None)

    # F: Sanity failed → results untrustworthy
    if sanity_check and not sanity_check.passed:
        logger.warning("Trust F: Sanity check failed")
        return "F"

    # D: Convergence failed → BO didn't find optimum
    if convergence_check and not convergence_check.passed:
        if n_passed >= 5:
            return "C"  # Other things OK, just not converged
        return "D"

    # Scoring
    if n_passed >= 7:
        return "A"
    elif n_passed >= 6:
        return "B"
    elif n_passed >= 5:
        return "B"  # 5/7 still reasonable
    elif n_passed >= 4:
        return "C"
    elif n_passed >= 3:
        return "D"
    else:
        return "F"
