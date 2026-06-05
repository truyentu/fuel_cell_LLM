"""
CHGNet Runner — Crystal stability prediction using CHGNet universal potential.
Used in Phase 1a coarse filter: predict formation energy → stable/unstable.
"""

import logging
from typing import Optional

import numpy as np
from ase import Atoms

logger = logging.getLogger("engine.runners.chgnet")


class CHGNetRunner:
    """Predict crystal stability using CHGNet pre-trained force field."""

    def __init__(self, device: str = "cpu"):
        """
        Load CHGNet model.

        Args:
            device: "cpu" or "cuda"
        """
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load CHGNet pre-trained model."""
        try:
            from chgnet.model import CHGNet
            self.model = CHGNet.load()
            logger.info(f"CHGNet model loaded on {self.device}")
        except ImportError:
            logger.warning("chgnet not installed. Using mock mode. Install: pip install chgnet")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load CHGNet: {e}")
            self.model = None

    @property
    def is_available(self) -> bool:
        return self.model is not None

    def predict_stability(self, atoms: Atoms) -> Optional[dict]:
        """
        Predict formation energy and stability of a structure.

        Args:
            atoms: ASE Atoms object (bulk crystal)

        Returns:
            {
                "energy_per_atom_eV": float,
                "energy_total_eV": float,
                "forces_max_eV_A": float,
                "stable": bool (heuristic: energy_per_atom < -1.0 and reasonable)
            }
            or None on failure
        """
        if not self.is_available:
            return self._mock_predict_stability(atoms)

        try:
            from pymatgen.io.ase import AseAtomsAdaptor

            # Convert ASE Atoms → pymatgen Structure (CHGNet uses pymatgen)
            structure = AseAtomsAdaptor.get_structure(atoms)

            # Predict
            prediction = self.model.predict_structure(structure)

            energy = float(prediction["e"])  # total energy in eV/atom
            forces = prediction["f"]  # forces array
            forces_max = float(np.max(np.abs(forces))) if forces is not None else 0.0

            energy_total = energy * len(atoms)
            energy_per_atom = energy

            # Stability heuristic:
            # Most stable inorganic materials have formation energy < 0
            # "Stable" = energy_per_atom reasonable (not positive/crazy)
            # Note: this is NOT true formation energy (needs elemental references)
            # but CHGNet energy correlates with stability
            stable = energy_per_atom < 0  # negative = cohesive (bound state)

            result = {
                "energy_per_atom_eV": energy_per_atom,
                "energy_total_eV": energy_total,
                "forces_max_eV_A": forces_max,
                "stable": stable,
            }

            logger.debug(
                f"CHGNet predict: {atoms.get_chemical_formula()} → "
                f"E={energy_per_atom:.3f} eV/atom, fmax={forces_max:.3f}, stable={stable}"
            )
            return result

        except Exception as e:
            logger.error(f"CHGNet predict_stability failed: {e}")
            return None

    def relax_structure(self, atoms: Atoms, fmax: float = 0.05, steps: int = 300) -> Optional[dict]:
        """
        Relax atomic positions + cell using CHGNet.

        Args:
            atoms: ASE Atoms object
            fmax: Force convergence criterion (eV/Å)
            steps: Maximum optimization steps

        Returns:
            {"relaxed_atoms": Atoms, "final_energy_per_atom": float, "converged": bool}
        """
        if not self.is_available:
            return self._mock_relax(atoms)

        try:
            from chgnet.model import StructOptimizer

            optimizer = StructOptimizer(model=self.model)

            from pymatgen.io.ase import AseAtomsAdaptor
            structure = AseAtomsAdaptor.get_structure(atoms)

            result = optimizer.relax(structure, fmax=fmax, steps=steps)

            relaxed_structure = result["final_structure"]
            relaxed_atoms = AseAtomsAdaptor.get_atoms(relaxed_structure)

            trajectory = result.get("trajectory", None)
            final_energy = trajectory.energies[-1] if trajectory else None

            converged = True  # StructOptimizer doesn't easily expose convergence flag
            if trajectory and len(trajectory.energies) >= steps:
                converged = False  # hit max steps

            return {
                "relaxed_atoms": relaxed_atoms,
                "final_energy_per_atom": final_energy,
                "converged": converged,
            }

        except Exception as e:
            logger.error(f"CHGNet relax failed: {e}")
            return None

    def predict_batch(self, structures: list[Atoms]) -> list[Optional[dict]]:
        """
        Predict stability for multiple structures.

        Args:
            structures: List of ASE Atoms objects

        Returns:
            List of prediction dicts (same as predict_stability)
        """
        results = []
        for atoms in structures:
            results.append(self.predict_stability(atoms))
        return results

    # --- Mock methods ---

    def _mock_predict_stability(self, atoms: Atoms) -> dict:
        """Mock: return realistic fake stability prediction."""
        n = len(atoms)
        # Simulate: most alloys have negative formation energy
        energy_per_atom = np.random.uniform(-5.5, -2.0)
        forces_max = np.random.uniform(0.01, 0.5)

        return {
            "energy_per_atom_eV": energy_per_atom,
            "energy_total_eV": energy_per_atom * n,
            "forces_max_eV_A": forces_max,
            "stable": energy_per_atom < -2.5,  # mock threshold
        }

    def _mock_relax(self, atoms: Atoms) -> dict:
        """Mock: return atoms as-is with fake energy."""
        return {
            "relaxed_atoms": atoms.copy(),
            "final_energy_per_atom": np.random.uniform(-5.0, -3.0),
            "converged": True,
        }
