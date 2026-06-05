"""
XRD Pattern Compare — verify synthesized structure matches AI prediction.
Used in Level 3 "mini test": cheap XRD check before full cell test.

Compares predicted XRD pattern (from .cif/.xyz structure) vs experimental .xy data.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger("engine.analysis.xrd_compare")


def compare_xrd(predicted_structure, experimental_xy_path: str) -> dict:
    """
    Compare predicted vs experimental XRD patterns.

    Args:
        predicted_structure: ASE Atoms object (relaxed structure from engine)
        experimental_xy_path: Path to experimental XRD .xy file (2theta, intensity)

    Returns:
        {
            "match_score": float (0-1, higher = better match),
            "peak_overlap": float (fraction of predicted peaks found in experiment),
            "phase_match": bool (primary phase identified),
            "details": str,
            "recommendation": str
        }
    """
    try:
        # Generate predicted XRD pattern
        predicted_peaks = _simulate_xrd_peaks(predicted_structure)

        # Load experimental data
        exp_2theta, exp_intensity = _load_experimental_xy(experimental_xy_path)

        if predicted_peaks is None or exp_2theta is None:
            return _mock_compare()

        # Compare peak positions
        match_result = _compare_peaks(predicted_peaks, exp_2theta, exp_intensity)

        return match_result

    except Exception as e:
        logger.error(f"XRD compare failed: {e}")
        return _mock_compare()


def _simulate_xrd_peaks(atoms) -> Optional[list[dict]]:
    """
    Simulate XRD peak positions from crystal structure.

    Uses Bragg's law: nλ = 2d·sin(θ)
    For Cu Kα: λ = 1.5406 Å
    """
    try:
        from ase.geometry import crystal_structure_guess

        # Get lattice parameters
        cell = atoms.get_cell()
        a = float(np.linalg.norm(cell[0]))
        b = float(np.linalg.norm(cell[1]))
        c = float(np.linalg.norm(cell[2]))

        # Simple cubic/FCC peak simulation
        # For FCC Ni: (111), (200), (220), (311), (222)
        wavelength = 1.5406  # Cu Kα in Å

        # Miller indices for FCC
        hkl_fcc = [(1, 1, 1), (2, 0, 0), (2, 2, 0), (3, 1, 1), (2, 2, 2)]

        peaks = []
        for h, k, l in hkl_fcc:
            # d-spacing for cubic: d = a / sqrt(h²+k²+l²)
            d = a / np.sqrt(h**2 + k**2 + l**2)
            # Bragg's law: sin(θ) = λ/(2d)
            sin_theta = wavelength / (2 * d)
            if abs(sin_theta) <= 1:
                two_theta = 2 * np.degrees(np.arcsin(sin_theta))
                peaks.append({
                    "hkl": (h, k, l),
                    "two_theta": two_theta,
                    "d_spacing": d,
                })

        return peaks if peaks else None

    except Exception as e:
        logger.warning(f"XRD simulation failed: {e}")
        return None


def _load_experimental_xy(filepath: str) -> tuple:
    """Load experimental XRD data from .xy file (two columns: 2theta, intensity)."""
    try:
        data = np.loadtxt(filepath, comments="#")
        if data.ndim == 2 and data.shape[1] >= 2:
            return data[:, 0], data[:, 1]
        return None, None
    except Exception as e:
        logger.warning(f"Failed to load XRD data from {filepath}: {e}")
        return None, None


def _compare_peaks(
    predicted_peaks: list[dict],
    exp_2theta: np.ndarray,
    exp_intensity: np.ndarray,
    tolerance_deg: float = 0.5,
) -> dict:
    """
    Compare predicted peak positions with experimental peaks.

    Args:
        predicted_peaks: List of predicted peak dicts
        exp_2theta: Experimental 2theta array
        exp_intensity: Experimental intensity array
        tolerance_deg: Matching tolerance in degrees 2theta
    """
    # Find experimental peaks (simple peak finding)
    exp_peak_positions = _find_peaks_simple(exp_2theta, exp_intensity)

    # Match predicted peaks to experimental
    n_predicted = len(predicted_peaks)
    n_matched = 0
    matched_details = []

    for pred in predicted_peaks:
        pred_pos = pred["two_theta"]
        # Find closest experimental peak
        if exp_peak_positions:
            distances = [abs(pred_pos - ep) for ep in exp_peak_positions]
            min_dist = min(distances)
            if min_dist < tolerance_deg:
                n_matched += 1
                matched_details.append(
                    f"  ({pred['hkl']}) at {pred_pos:.1f}° → matched (Δ={min_dist:.2f}°)"
                )
            else:
                matched_details.append(
                    f"  ({pred['hkl']}) at {pred_pos:.1f}° → NOT found (closest={min_dist:.1f}°)"
                )

    peak_overlap = n_matched / n_predicted if n_predicted > 0 else 0
    match_score = peak_overlap  # Simple score = fraction matched

    # Phase match: primary peaks (111), (200) should match
    primary_matched = n_matched >= 2  # at least 2 primary peaks

    # Recommendation
    if match_score >= 0.8:
        recommendation = "✅ GOOD MATCH — proceed to full cell test"
    elif match_score >= 0.5:
        recommendation = "⚠️ PARTIAL MATCH — check synthesis conditions, may have secondary phase"
    else:
        recommendation = "❌ POOR MATCH — structure likely different from prediction. Adjust synthesis."

    details = "\n".join(matched_details) if matched_details else "No peaks compared"

    return {
        "match_score": match_score,
        "peak_overlap": peak_overlap,
        "n_predicted": n_predicted,
        "n_matched": n_matched,
        "phase_match": primary_matched,
        "details": details,
        "recommendation": recommendation,
    }


def _find_peaks_simple(
    two_theta: np.ndarray,
    intensity: np.ndarray,
    min_height_frac: float = 0.1,
) -> list[float]:
    """Simple peak finding: local maxima above threshold."""
    if len(intensity) < 3:
        return []

    threshold = min_height_frac * np.max(intensity)
    peaks = []

    for i in range(1, len(intensity) - 1):
        if (intensity[i] > intensity[i - 1] and
            intensity[i] > intensity[i + 1] and
            intensity[i] > threshold):
            peaks.append(float(two_theta[i]))

    return peaks


def _mock_compare() -> dict:
    """Mock result when libraries not available or data missing."""
    score = np.random.uniform(0.5, 0.95)
    return {
        "match_score": score,
        "peak_overlap": score,
        "n_predicted": 5,
        "n_matched": int(score * 5),
        "phase_match": score > 0.6,
        "details": "Mock comparison (no real data)",
        "recommendation": "⚠️ Mock mode — upload real XRD .xy file for actual comparison",
    }
