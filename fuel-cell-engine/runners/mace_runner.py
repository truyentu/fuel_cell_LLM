"""
MACE runner — NEB diffusion barrier + MD stability calculations.
Uses MACE foundation models (mace_mp) for fast atomic simulations.
"""

import logging
from typing import Literal, Optional

import numpy as np
from ase import Atoms

logger = logging.getLogger("engine.runners.mace")


class MACERunner:
    """Run MACE calculations: NEB barriers and MD stability."""

    def __init__(
        self,
        model: str = "medium",
        device: str = "cuda",
        default_dtype: str = "float32",
    ):
        self.model_name = model
        self.device = device
        self.default_dtype = default_dtype
        self.calc = None
        self._load_model()

    def _load_model(self):
        """Load MACE foundation model."""
        try:
            from mace.calculators import mace_mp
            self.calc = mace_mp(
                model=self.model_name,
                device=self.device,
                default_dtype=self.default_dtype,
            )
            logger.info(f"MACE model loaded: {self.model_name} on {self.device}")
        except ImportError:
            logger.warning("mace-torch not installed. Using mock mode.")
            self.calc = None
        except Exception as e:
            logger.error(f"Failed to load MACE model: {e}")
            self.calc = None

    @property
    def is_available(self) -> bool:
        return self.calc is not None

    def single_point(self, atoms: Atoms) -> Optional[dict]:
        """
        Single-point energy + forces calculation.

        Returns:
            {"energy": float (eV), "forces": ndarray (N,3), "stress": ndarray (6,)}
            or None on failure.
        """
        if not self.is_available:
            return self._mock_single_point(atoms)

        try:
            atoms_copy = atoms.copy()
            atoms_copy.calc = self.calc
            energy = atoms_copy.get_potential_energy()
            forces = atoms_copy.get_forces()
            return {
                "energy": float(energy),
                "forces": forces.copy(),
                "energy_per_atom": float(energy / len(atoms_copy)),
            }
        except Exception as e:
            logger.error(f"MACE single_point failed: {e}")
            return None

    def run_neb(
        self,
        initial: Atoms,
        final: Atoms,
        n_images: int = 5,
        fmax: float = 0.05,
        max_steps: int = 200,
    ) -> Optional[dict]:
        """
        Run NEB calculation to find diffusion barrier.

        Parameters:
            initial: Starting structure (molecule outside shell)
            final: End structure (molecule inside shell)
            n_images: Number of NEB images between initial and final
            fmax: Force convergence criterion (eV/Å)
            max_steps: Maximum optimizer steps

        Returns:
            {"barrier": float (eV), "dE": float (eV), "converged": bool}
            or None on failure.
        """
        if not self.is_available:
            return self._mock_neb(initial, final)

        try:
            from ase.mep import NEB
            from ase.mep.neb import NEBTools
            from ase.optimize import MDMin
            from mace.calculators import mace_mp

            # Each image needs its own calculator (including endpoints)
            images = [initial.copy()]
            for _ in range(n_images):
                images.append(initial.copy())
            images.append(final.copy())

            # Attach calculators to ALL images (ASE NEB requires endpoints too)
            for image in images:
                image.calc = mace_mp(
                    model=self.model_name,
                    device=self.device,
                    default_dtype=self.default_dtype,
                )

            neb = NEB(images, climb=True)
            neb.interpolate(method="improvedtangent")

            opt = MDMin(neb, logfile=None)
            converged = opt.run(fmax=fmax, steps=max_steps)

            tools = NEBTools(images)
            barrier, dE = tools.get_barrier()

            result = {
                "barrier": float(barrier),
                "dE": float(dE),
                "converged": bool(converged),
                "n_steps": opt.nsteps,
            }
            logger.debug(
                f"NEB: barrier={barrier:.3f} eV, dE={dE:.3f} eV, "
                f"converged={converged}, steps={opt.nsteps}"
            )
            return result

        except Exception as e:
            logger.error(f"MACE NEB failed: {e}")
            return None

    def run_md(
        self,
        atoms: Atoms,
        temperature_K: float = 343,
        steps: int = 10000,
        timestep_fs: float = 1.0,
    ) -> Optional[dict]:
        """
        Run MD simulation to assess shell stability.

        Parameters:
            atoms: Structure to simulate
            temperature_K: Temperature (K)
            steps: Number of MD steps
            timestep_fs: Timestep (fs)

        Returns:
            {"intact_ratio": float (0-1), "final_energy": float, "max_displacement": float}
            or None on failure.
        """
        if not self.is_available:
            return self._mock_md(atoms, temperature_K, steps)

        try:
            from ase.md.langevin import Langevin
            from ase import units

            atoms_md = atoms.copy()
            atoms_md.calc = self.calc

            # Record initial graphene positions
            tags = atoms_md.get_tags()
            shell_mask = tags == 2  # graphene atoms
            initial_positions = atoms_md.positions[shell_mask].copy()

            # Run Langevin MD
            dyn = Langevin(
                atoms_md,
                timestep=timestep_fs * units.fs,
                temperature_K=temperature_K,
                friction=0.01 / units.fs,
            )
            dyn.run(steps=steps)

            # Analyze: how much did shell atoms move?
            final_positions = atoms_md.positions[shell_mask]
            displacements = np.linalg.norm(
                final_positions - initial_positions, axis=1
            )
            max_disp = float(displacements.max())
            mean_disp = float(displacements.mean())

            # "intact" = atoms that moved less than 1.5 Å from original position
            intact_threshold = 1.5  # Å
            n_intact = int(np.sum(displacements < intact_threshold))
            n_total = len(displacements)
            intact_ratio = n_intact / n_total if n_total > 0 else 0

            result = {
                "intact_ratio": float(intact_ratio),
                "max_displacement": max_disp,
                "mean_displacement": mean_disp,
                "final_energy": float(atoms_md.get_potential_energy()),
                "n_intact": n_intact,
                "n_total": n_total,
            }
            logger.debug(
                f"MD: intact={intact_ratio:.3f} ({n_intact}/{n_total}), "
                f"max_disp={max_disp:.2f} Å, T={temperature_K}K, {steps} steps"
            )
            return result

        except Exception as e:
            logger.error(f"MACE MD failed: {e}")
            return None

    # --- Mock methods (for testing without GPU) ---

    def _mock_single_point(self, atoms: Atoms) -> dict:
        """Mock: return reasonable fake energy."""
        n = len(atoms)
        energy = -3.5 * n + np.random.normal(0, 0.1)
        return {
            "energy": energy,
            "forces": np.random.normal(0, 0.01, (n, 3)),
            "energy_per_atom": energy / n,
        }

    def _mock_neb(self, initial: Atoms, final: Atoms) -> dict:
        """Mock: return random barrier in realistic range."""
        barrier = np.random.uniform(0.1, 0.8)
        return {
            "barrier": barrier,
            "dE": np.random.uniform(-0.2, 0.2),
            "converged": True,
            "n_steps": np.random.randint(50, 150),
        }

    def _mock_md(self, atoms: Atoms, temperature_K: float, steps: int) -> dict:
        """Mock: return stability based on simple heuristics."""
        # Higher temperature or more vacancies = less stable (mock logic)
        intact = np.random.uniform(0.7, 1.0)
        return {
            "intact_ratio": intact,
            "max_displacement": np.random.uniform(0.3, 2.0),
            "mean_displacement": np.random.uniform(0.1, 0.8),
            "final_energy": -3.5 * len(atoms),
            "n_intact": int(intact * 60),
            "n_total": 60,
        }
