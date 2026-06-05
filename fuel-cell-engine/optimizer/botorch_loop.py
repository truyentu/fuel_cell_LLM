"""
BoTorch optimization loop — multi-objective Bayesian optimization.
Suggests next candidates based on Pareto front optimization.
"""

import logging
from typing import Literal, Optional

import numpy as np
import torch

logger = logging.getLogger("engine.optimizer.botorch_loop")

# Default dtype for BoTorch (float32 → GP instability, always use float64)
DTYPE = torch.double


class BayesianOptimizer:
    """Multi-objective Bayesian optimization using BoTorch."""

    def __init__(
        self,
        bounds: torch.Tensor,
        objectives: list[str],
        constraints: list[dict] = None,
        acquisition: str = "qLogExpectedHypervolumeImprovement",
        seed: int = 42,
        device: str = "cpu",
    ):
        """
        Parameters:
            bounds: (2, d) tensor — [lower; upper] for each dimension
            objectives: list of objective names to MAXIMIZE
            constraints: [{"metric": str, "operator": "</>", "value": float}]
            acquisition: Acquisition function name
            seed: Random seed
            device: torch device
        """
        self.bounds = bounds.to(dtype=DTYPE, device=device)
        self.d = bounds.shape[1]
        self.objectives = objectives
        self.constraints = constraints or []
        self.acquisition_name = acquisition
        self.seed = seed
        self.device = device

        self.train_X = torch.empty(0, self.d, dtype=DTYPE, device=device)
        self.train_Y = torch.empty(0, len(objectives), dtype=DTYPE, device=device)
        self.constraint_values = []  # list of dicts per observation

        torch.manual_seed(seed)
        logger.info(
            f"BoTorch optimizer: {self.d}D, {len(objectives)} objectives, "
            f"{len(self.constraints)} constraints, acq={acquisition}"
        )

    def suggest_initial(self, n: int) -> torch.Tensor:
        """Generate n random initial candidates within bounds."""
        rand = torch.rand(n, self.d, dtype=DTYPE, device=self.device)
        candidates = self.bounds[0] + (self.bounds[1] - self.bounds[0]) * rand
        logger.debug(f"Generated {n} initial random candidates")
        return candidates

    def tell(self, X: torch.Tensor, Y: torch.Tensor, constraint_vals: list[dict] = None):
        """Add new observations."""
        self.train_X = torch.cat([self.train_X, X.to(dtype=DTYPE, device=self.device)])
        self.train_Y = torch.cat([self.train_Y, Y.to(dtype=DTYPE, device=self.device)])
        if constraint_vals:
            self.constraint_values.extend(constraint_vals)

    def suggest_next(self, q: int = 1) -> Optional[torch.Tensor]:
        """
        Suggest next q candidate(s) using Bayesian optimization.

        Returns:
            (q, d) tensor of suggested parameters, or None on failure.
        """
        if len(self.train_X) < 2:
            logger.warning("Not enough data for GP. Returning random.")
            return self.suggest_initial(q)

        try:
            return self._botorch_suggest(q)
        except ImportError:
            logger.warning("BoTorch not installed. Using random fallback.")
            return self.suggest_initial(q)
        except Exception as e:
            logger.error(f"BoTorch suggest failed: {e}. Using random fallback.")
            return self.suggest_initial(q)

    def _botorch_suggest(self, q: int) -> torch.Tensor:
        """Internal: use BoTorch GP + acquisition function."""
        from botorch.models import SingleTaskGP
        from botorch.models.transforms import Normalize, Standardize
        from botorch.fit import fit_gpytorch_mll
        from botorch.acquisition import LogExpectedImprovement
        from botorch.acquisition.multi_objective import (
            qExpectedHypervolumeImprovement,
            qLogExpectedHypervolumeImprovement,
        )
        from botorch.optim import optimize_acqf
        from botorch.utils.multi_objective.pareto import is_non_dominated
        from gpytorch.mlls import ExactMarginalLogLikelihood

        n_obj = self.train_Y.shape[1]

        if n_obj == 1:
            # Single objective
            gp = SingleTaskGP(
                self.train_X, self.train_Y,
                input_transform=Normalize(d=self.d),
                outcome_transform=Standardize(m=1),
            )
            mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
            fit_gpytorch_mll(mll)

            acq = LogExpectedImprovement(model=gp, best_f=self.train_Y.max())
            candidate, _ = optimize_acqf(
                acq, bounds=self.bounds, q=q,
                num_restarts=10, raw_samples=64,
            )
        else:
            # Multi-objective
            from botorch.models import ModelListGP

            models = []
            for i in range(n_obj):
                gp_i = SingleTaskGP(
                    self.train_X, self.train_Y[:, i:i+1],
                    input_transform=Normalize(d=self.d),
                    outcome_transform=Standardize(m=1),
                )
                mll_i = ExactMarginalLogLikelihood(gp_i.likelihood, gp_i)
                fit_gpytorch_mll(mll_i)
                models.append(gp_i)

            model_list = ModelListGP(*models)

            # Reference point (worst acceptable values)
            ref_point = self.train_Y.min(dim=0).values - 0.1

            # Use qLogEHVI for numerical stability
            from botorch.utils.multi_objective.box_decompositions import (
                NondominatedPartitioning,
            )
            partitioning = NondominatedPartitioning(
                ref_point=ref_point, Y=self.train_Y
            )

            acq = qLogExpectedHypervolumeImprovement(
                model=model_list,
                ref_point=ref_point,
                partitioning=partitioning,
            )

            candidate, _ = optimize_acqf(
                acq, bounds=self.bounds, q=q,
                num_restarts=10, raw_samples=64,
            )

        logger.debug(f"BoTorch suggested: {candidate.squeeze().tolist()}")
        return candidate

    def get_best(self) -> dict:
        """Get current best observation."""
        if len(self.train_Y) == 0:
            return {"params": None, "score": None}

        # For multi-objective: return best hypervolume contributor
        # Simplified: return highest sum of normalized objectives
        Y_norm = (self.train_Y - self.train_Y.min(0).values) / (
            self.train_Y.max(0).values - self.train_Y.min(0).values + 1e-8
        )
        scores = Y_norm.sum(dim=1)
        best_idx = scores.argmax().item()

        return {
            "params": self.train_X[best_idx].tolist(),
            "objectives": self.train_Y[best_idx].tolist(),
            "score": scores[best_idx].item(),
            "index": best_idx,
        }

    def check_convergence(self, n_last: int = 5, threshold: float = 0.01) -> bool:
        """Check if optimization has converged (no improvement in last n iterations)."""
        if len(self.train_Y) < n_last + 1:
            return False

        Y_norm = (self.train_Y - self.train_Y.min(0).values) / (
            self.train_Y.max(0).values - self.train_Y.min(0).values + 1e-8
        )
        scores = Y_norm.sum(dim=1)

        recent_best = scores[-n_last:].max().item()
        overall_best = scores.max().item()

        improvement = overall_best - scores[:-n_last].max().item()
        return improvement < threshold

    def update_bounds(self, new_bounds: torch.Tensor):
        """Update search space bounds (e.g., after LLM advice)."""
        self.bounds = new_bounds.to(dtype=DTYPE, device=self.device)
        logger.info(f"Bounds updated: {self.bounds.tolist()}")
