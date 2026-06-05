"""
MACE Ensemble runner — runs 3 model sizes for uncertainty estimation.
Inspired by GNoME (10 GNNs ensemble for confidence).
"""

import logging
from typing import Optional

import numpy as np
from ase import Atoms

from runners.mace_runner import MACERunner

logger = logging.getLogger("engine.runners.ensemble")


class EnsembleRunner:
    """Run multiple MACE model sizes → mean ± std for uncertainty."""

    def __init__(
        self,
        models: list[str] = None,
        device: str = "cuda",
        confidence_threshold: float = 0.10,
    ):
        if models is None:
            models = ["small", "medium", "large"]

        self.model_names = models
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.runners: dict[str, MACERunner] = {}

        for name in models:
            self.runners[name] = MACERunner(model=name, device=device)

        n_available = sum(1 for r in self.runners.values() if r.is_available)
        logger.info(
            f"Ensemble initialized: {n_available}/{len(models)} models available"
        )

    @property
    def is_available(self) -> bool:
        return any(r.is_available for r in self.runners.values())

    def predict_energy_with_uncertainty(self, atoms: Atoms) -> dict:
        """
        Single-point energy from all models → mean ± std.

        Returns:
            {
                "mean": float,
                "std": float,
                "confident": bool,
                "predictions": {model_name: energy},
            }
        """
        predictions = {}
        for name, runner in self.runners.items():
            result = runner.single_point(atoms)
            if result is not None:
                predictions[name] = result["energy_per_atom"]

        if not predictions:
            return {"mean": None, "std": None, "confident": False, "predictions": {}}

        values = list(predictions.values())
        mean = float(np.mean(values))
        std = float(np.std(values))
        confident = std < self.confidence_threshold

        if not confident:
            logger.warning(
                f"Ensemble HIGH uncertainty: std={std:.4f} eV/atom "
                f"(threshold={self.confidence_threshold}). "
                f"Predictions: {predictions}"
            )

        return {
            "mean": mean,
            "std": std,
            "confident": confident,
            "predictions": predictions,
        }

    def predict_neb_with_uncertainty(
        self,
        initial: Atoms,
        final: Atoms,
        n_images: int = 5,
        fmax: float = 0.05,
        max_steps: int = 200,
    ) -> dict:
        """
        NEB barrier from all models → mean ± std.

        Returns:
            {
                "mean_barrier": float,
                "std_barrier": float,
                "confident": bool,
                "predictions": {model_name: barrier},
                "all_converged": bool,
            }
        """
        predictions = {}
        converged_all = True

        for name, runner in self.runners.items():
            result = runner.run_neb(initial, final, n_images, fmax, max_steps)
            if result is not None:
                predictions[name] = result["barrier"]
                if not result.get("converged", False):
                    converged_all = False
            else:
                converged_all = False

        if not predictions:
            return {
                "mean_barrier": None,
                "std_barrier": None,
                "confident": False,
                "predictions": {},
                "all_converged": False,
            }

        values = list(predictions.values())
        mean = float(np.mean(values))
        std = float(np.std(values))
        confident = std < self.confidence_threshold

        return {
            "mean_barrier": mean,
            "std_barrier": std,
            "confident": confident,
            "predictions": predictions,
            "all_converged": converged_all,
        }

    def predict_md_with_uncertainty(
        self,
        atoms: Atoms,
        temperature_K: float = 343,
        steps: int = 10000,
        timestep_fs: float = 1.0,
    ) -> dict:
        """
        MD stability from primary model only (too expensive for ensemble).
        Use energy ensemble for confidence instead.

        Returns MD from medium model + energy uncertainty from ensemble.
        """
        # MD only from primary (medium) — too expensive to run 3×
        primary = self.runners.get("medium") or list(self.runners.values())[0]
        md_result = primary.run_md(atoms, temperature_K, steps, timestep_fs)

        # Energy uncertainty from ensemble (cheap single-point)
        energy_uncertainty = self.predict_energy_with_uncertainty(atoms)

        if md_result is None:
            return {
                "intact_ratio": None,
                "energy_std": energy_uncertainty.get("std"),
                "confident": False,
            }

        return {
            **md_result,
            "energy_std": energy_uncertainty.get("std"),
            "energy_confident": energy_uncertainty.get("confident", False),
        }

    def assess_ood_risk(self, atoms: Atoms) -> dict:
        """
        Assess out-of-distribution risk for a candidate structure.

        Heuristics:
        1. Ensemble disagreement (std) — high std = likely OOD
        2. Composition check — elements in OC20/MACE training data?
        3. Energy reasonableness — very positive energy = unphysical

        Returns:
            {
                "ood_risk": "low" | "medium" | "high",
                "reasons": [str],
                "ensemble_std": float,
                "recommendation": str
            }
        """
        reasons = []
        risk_score = 0  # 0-3: low, medium, high

        # 1. Ensemble energy std
        energy_result = self.predict_energy_with_uncertainty(atoms)
        std = energy_result.get("std", 0) or 0

        if std > 0.20:
            reasons.append(f"Ensemble std={std:.3f} eV >> 0.10 threshold (models strongly disagree)")
            risk_score += 2
        elif std > 0.10:
            reasons.append(f"Ensemble std={std:.3f} eV > 0.10 threshold (moderate disagreement)")
            risk_score += 1

        # 2. Composition check vs known training data
        symbols = set(atoms.get_chemical_symbols())
        # OC20 trained on ~55 elements, covers most transition metals
        # MACE (Materials Project) covers ~90 elements
        # Rare/exotic elements likely OOD
        exotic_elements = {"Tc", "Pm", "At", "Fr", "Ra", "Ac", "Pa", "Np", "Pu", "Am"}
        found_exotic = symbols.intersection(exotic_elements)
        if found_exotic:
            reasons.append(f"Contains exotic elements {found_exotic} likely NOT in training data")
            risk_score += 2

        # Ni-alloy specific: check if combination is represented
        # OC20 has good coverage of Ni, Mo, Fe, Co, Cu, W surfaces
        well_represented = {"Ni", "Mo", "Fe", "Co", "Cu", "W", "Mn", "Cr", "Pt", "Pd"}
        not_represented = symbols - well_represented - {"C", "N", "O", "H"}
        if not_represented:
            reasons.append(f"Elements {not_represented} less represented in training data")
            risk_score += 1

        # 3. Energy reasonableness
        mean_energy = energy_result.get("mean")
        if mean_energy is not None:
            if mean_energy > 0:
                reasons.append(f"Positive energy/atom ({mean_energy:.3f} eV) = unphysical/unstable")
                risk_score += 2
            elif mean_energy > -1.0:
                reasons.append(f"Very low cohesive energy ({mean_energy:.3f} eV/atom) = weakly bound")
                risk_score += 1

        # Classify risk
        if risk_score >= 3:
            ood_risk = "high"
            recommendation = "DO NOT trust predictions. Need DFT verification or skip candidate."
        elif risk_score >= 1:
            ood_risk = "medium"
            recommendation = "Predictions may be less accurate. Include in screening but flag in output."
        else:
            ood_risk = "low"
            recommendation = "Predictions likely reliable for this composition."

        if not reasons:
            reasons.append("All checks passed — composition well within training distribution")

        return {
            "ood_risk": ood_risk,
            "risk_score": risk_score,
            "reasons": reasons,
            "ensemble_std": std,
            "recommendation": recommendation,
        }
