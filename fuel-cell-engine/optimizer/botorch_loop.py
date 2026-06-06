"""
BoTorch optimization loop — multi-objective Bayesian optimization.
Suggests next candidates based on Pareto front optimization.

When data is insufficient for GP, can use LLM-guided suggestions
based on literature knowledge (Norskov volcano plot, known alloy systems)
instead of pure random sampling.
"""

import logging
from typing import Literal, Optional

import numpy as np
import torch

logger = logging.getLogger("engine.optimizer.botorch_loop")

# Default dtype for BoTorch (float32 → GP instability, always use float64)
DTYPE = torch.double

# Search variable names and known-good ranges from literature
# Used by LLM-guided suggestions
SEARCH_VARS = [
    {"name": "dopant_type", "options": ["Fe", "Co", "Cu", "Mo", "W", "none"], "idx_map": True},
    {"name": "dopant_percent", "range": [5, 45]},
    {"name": "n_layers", "range": [1, 4]},
    {"name": "vacancy_percent", "range": [0, 20]},
    {"name": "n_doping_percent", "range": [0, 16]},
]


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
        llm_advisor=None,
    ):
        """
        Parameters:
            bounds: (2, d) tensor — [lower; upper] for each dimension
            objectives: list of objective names to MAXIMIZE
            constraints: [{"metric": str, "operator": "</>", "value": float}]
            acquisition: Acquisition function name
            seed: Random seed
            device: torch device
            llm_advisor: Optional LLMAdvisor instance for guided suggestions
        """
        self.bounds = bounds.to(dtype=DTYPE, device=device)
        self.d = bounds.shape[1]
        self.objectives = objectives
        self.constraints = constraints or []
        self.acquisition_name = acquisition
        self.seed = seed
        self.device = device
        self.llm_advisor = llm_advisor

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
        When insufficient data for GP, uses LLM-guided suggestions if available.

        Returns:
            (q, d) tensor of suggested parameters, or None on failure.
        """
        if len(self.train_X) < 2:
            # Try LLM-guided suggestion first
            if self.llm_advisor and self.llm_advisor.enabled:
                guided = self._llm_guided_suggest(q)
                if guided is not None:
                    return guided
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

    def _llm_guided_suggest(self, q: int) -> Optional[torch.Tensor]:
        """
        Use LLM to suggest promising compositions based on literature knowledge.
        Returns normalized tensor in bounds, or None if LLM unavailable/fails.
        """
        # Build context from existing observations (if any)
        context_parts = [
            "System: Ni@C catalyst for AEMFC anode (HOR).",
            f"Search variables (normalized 0-1 within bounds):",
            f"  dim0: dopant_type (0=Fe, 0.2=Co, 0.4=Cu, 0.6=Mo, 0.8=W, 1.0=none)",
            f"  dim1: dopant_percent ({self.bounds[0][1]:.0f}-{self.bounds[1][1]:.0f}%)",
            f"  dim2: n_layers ({self.bounds[0][2]:.0f}-{self.bounds[1][2]:.0f})",
            f"  dim3: vacancy_percent ({self.bounds[0][3]:.0f}-{self.bounds[1][3]:.0f}%)",
            f"  dim4: n_doping_percent ({self.bounds[0][4]:.0f}-{self.bounds[1][4]:.0f}%)",
            f"Objectives: minimize |ΔG_H|, minimize h2_barrier, maximize o2_barrier, maximize shell_stability.",
        ]

        if len(self.train_X) > 0:
            context_parts.append(f"\nPrevious results ({len(self.train_X)} candidates):")
            for i in range(len(self.train_X)):
                x = self.train_X[i].tolist()
                y = self.train_Y[i].tolist()
                context_parts.append(f"  X={[f'{v:.2f}' for v in x]} → Y={[f'{v:.3f}' for v in y]}")

        context = "\n".join(context_parts)

        question = (
            f"Suggest {q} promising candidate composition(s) as raw parameter values.\n"
            f"Based on literature: Ni3Fe@C (Yan 2020) and N-doped graphene (Deng 2015) "
            f"showed best HOR in alkaline. Consider:\n"
            f"- Fe 25-40% for optimal HOR (near volcano peak)\n"
            f"- 1-2 layers graphene for H2 permeability\n"
            f"- 10-16% vacancy for low H2 barrier\n"
            f"- 4-8% N-doping for electronic modification\n\n"
            f"Output ONLY {q} line(s), each with 5 numbers separated by commas:\n"
            f"dopant_type_idx(0-5), dopant_percent, n_layers, vacancy_percent, n_doping_percent\n"
            f"Example: 0, 35, 2, 12, 6"
        )

        try:
            response = self.llm_advisor.ask(context, question)
            if response is None:
                return None

            candidates = []
            for line in response.strip().split("\n"):
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("//"):
                    continue
                # Parse numbers from line
                parts = [p.strip() for p in line.replace(";", ",").split(",")]
                try:
                    values = [float(p) for p in parts[:5]]
                    if len(values) == 5:
                        candidates.append(values)
                except ValueError:
                    continue
                if len(candidates) >= q:
                    break

            if not candidates:
                logger.warning("LLM response could not be parsed. Falling back to random.")
                return None

            # Convert to tensor and clip to bounds
            tensor = torch.tensor(candidates[:q], dtype=DTYPE, device=self.device)

            # Map dopant_type_idx (0-5) to normalized bound range
            # dim0: dopant index needs mapping to actual bounds
            n_dopants = 6  # Fe, Co, Cu, Mo, W, none
            tensor[:, 0] = tensor[:, 0] / (n_dopants - 1) * (
                self.bounds[1][0] - self.bounds[0][0]
            ) + self.bounds[0][0]

            # Clip all dimensions to bounds
            for d in range(self.d):
                tensor[:, d] = tensor[:, d].clamp(
                    self.bounds[0][d].item(), self.bounds[1][d].item()
                )

            logger.info(
                f"LLM-guided suggestion: {tensor.squeeze().tolist()} "
                f"(literature-informed, not random)"
            )
            return tensor

        except Exception as e:
            logger.warning(f"LLM-guided suggest failed: {e}. Falling back to random.")
            return None

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
