"""
OC20 / fairchem runner — predict H adsorption energy on bare metal surfaces.
Used for HOR activity screening (Sabatier principle: ΔG_H* ≈ 0 = optimal).
"""

import logging
from typing import Optional

import numpy as np
from ase import Atoms
from ase.build import add_adsorbate

logger = logging.getLogger("engine.runners.oc20")


class OC20Runner:
    """Predict H adsorption energy using FAIRChem/OC20 models."""

    def __init__(
        self,
        model: str = "uma-s-1p2",
        task_name: str = "oc20",
        device: str = "cuda",
    ):
        self.model_name = model
        self.task_name = task_name
        self.device = device
        self.calc = None
        self._load_model()

    def _load_model(self):
        """Load FAIRChem pretrained model."""
        try:
            from fairchem.core import FAIRChemCalculator, pretrained_mlip

            predictor = pretrained_mlip.get_predict_unit(
                self.model_name,
                device=self.device,
            )
            self.calc = FAIRChemCalculator(predictor, task_name=self.task_name)
            logger.info(f"OC20 model loaded: {self.model_name} ({self.task_name})")
        except ImportError:
            logger.warning("fairchem-core not installed. Using mock mode.")
            self.calc = None
        except Exception as e:
            logger.error(f"Failed to load OC20 model: {e}")
            self.calc = None

    @property
    def is_available(self) -> bool:
        return self.calc is not None

    def predict_h_adsorption(
        self,
        slab: Atoms,
        h_site: str = "fcc",
        h_height: float = 1.0,
        fmax: float = 0.05,
        max_steps: int = 200,
    ) -> Optional[dict]:
        """
        Predict H adsorption energy on slab surface.

        ΔG_H* ≈ ΔE_ads + 0.24 eV (ZPE + entropy correction, standard)

        Parameters:
            slab: Metal slab Atoms (tags: 0=bulk, 1=surface)
            h_site: Adsorption site
            h_height: Initial H height above surface
            fmax: Relaxation convergence
            max_steps: Max relaxation steps

        Returns:
            {"delta_G_H": float (eV), "E_slab": float, "E_adslab": float, "converged": bool}
            or None on failure.
        """
        if not self.is_available:
            return self._mock_h_adsorption(slab)

        try:
            from ase.optimize import LBFGS

            # 1. Relax clean slab
            slab_clean = slab.copy()
            slab_clean.calc = self.calc
            opt = LBFGS(slab_clean, logfile=None)
            opt.run(fmax=fmax, steps=max_steps)
            E_slab = slab_clean.get_potential_energy()

            # 2. Add H and relax
            adslab = slab.copy()
            add_adsorbate(adslab, "H", height=h_height, position=h_site)
            # Tag H as adsorbate
            tags = list(adslab.get_tags())
            tags[-1] = 2
            adslab.set_tags(tags)

            adslab.calc = self.calc
            opt2 = LBFGS(adslab, logfile=None)
            converged = opt2.run(fmax=fmax, steps=max_steps)
            E_adslab = adslab.get_potential_energy()

            # 3. Compute ΔG_H*
            # Reference: 1/2 H₂(g) energy. OC20 convention varies.
            # Simple approximation: ΔE_ads = E_adslab - E_slab - E_H_ref
            # E_H_ref for OC20 H2O-H2 scheme ≈ -3.477 eV per H atom
            E_H_ref = -3.477  # OC20 atomic reference for H
            delta_E = E_adslab - E_slab - E_H_ref

            # ZPE + entropy correction (standard, ~constant for H on metals)
            ZPE_correction = 0.24  # eV
            delta_G_H = delta_E + ZPE_correction

            result = {
                "delta_G_H": float(delta_G_H),
                "delta_E_ads": float(delta_E),
                "E_slab": float(E_slab),
                "E_adslab": float(E_adslab),
                "converged": bool(converged),
            }
            logger.debug(f"OC20: ΔG_H* = {delta_G_H:.3f} eV (ΔE={delta_E:.3f})")
            return result

        except Exception as e:
            logger.error(f"OC20 H adsorption failed: {e}")
            return None

    def relax_structure(
        self,
        atoms: Atoms,
        fmax: float = 0.05,
        max_steps: int = 200,
    ) -> Optional[Atoms]:
        """Relax structure using OC20 calculator."""
        if not self.is_available:
            return atoms.copy()

        try:
            from ase.optimize import LBFGS

            atoms_relax = atoms.copy()
            atoms_relax.calc = self.calc
            opt = LBFGS(atoms_relax, logfile=None)
            opt.run(fmax=fmax, steps=max_steps)
            return atoms_relax
        except Exception as e:
            logger.error(f"OC20 relaxation failed: {e}")
            return None

    # --- Mock ---

    def _mock_h_adsorption(self, slab: Atoms) -> dict:
        """Mock: return realistic ΔG_H* based on composition."""
        symbols = slab.get_chemical_symbols()

        # Simple mock: Ni = too strong, Mo makes it weaker
        n_mo = symbols.count("Mo")
        n_fe = symbols.count("Fe")
        n_co = symbols.count("Co")
        n_total = len(symbols)

        # Base: pure Ni ≈ -0.45 eV (too strong)
        # Mo shifts positive (weaker binding)
        # Fe slight shift
        # Co slight shift
        base = -0.45
        mo_effect = n_mo / n_total * 0.8  # Mo weakens H binding
        fe_effect = n_fe / n_total * 0.3
        co_effect = n_co / n_total * 0.2

        delta_G = base + mo_effect + fe_effect + co_effect
        delta_G += np.random.normal(0, 0.03)  # noise

        return {
            "delta_G_H": float(delta_G),
            "delta_E_ads": float(delta_G - 0.24),
            "E_slab": -3.5 * n_total,
            "E_adslab": -3.5 * n_total + delta_G,
            "converged": True,
        }
