"""
Phase 1b: Screening — Main BO loop with OC20 + MACE + ensemble + failure learning.
This is the CORE of the engine. 25 iterations of Bayesian optimization.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import torch

from config_schema import PipelineConfig
from llm_advisor import LLMAdvisor
from optimizer.botorch_loop import BayesianOptimizer, DTYPE
from runners.mace_runner import MACERunner
from runners.mace_ensemble import EnsembleRunner
from runners.oc20_runner import OC20Runner
from structures.slab_builder import build_bare_slab_with_h
from structures.ni_at_c_generator import (
    build_ni_at_c_structure,
    build_neb_structures,
    generate_structure_from_params,
    validate_structure,
)
from utils.checkpoint import save_checkpoint, load_checkpoint

logger = logging.getLogger("engine.phases.screening")


@dataclass
class CandidateResult:
    """Result of evaluating one candidate."""
    iteration: int
    params: dict
    status: str  # "success", "failed_generation", "failed_oc20", "failed_neb", "failed_md"
    scores: dict = field(default_factory=dict)
    uncertainty: dict = field(default_factory=dict)
    failure_reason: str = ""
    elapsed_s: float = 0.0


@dataclass
class ScreeningResults:
    """All results from screening phase."""
    candidates: list[CandidateResult] = field(default_factory=list)
    n_success: int = 0
    n_failed: int = 0
    best_score: float = 0.0
    best_params: dict = field(default_factory=dict)
    converged: bool = False
    n_iterations: int = 0


def run_screening(
    config: PipelineConfig,
    mace_runner: MACERunner,
    ensemble_runner: EnsembleRunner,
    oc20_runner: OC20Runner,
    llm_advisor: LLMAdvisor,
    initial_params: list[dict] = None,
    resume_checkpoint: str = None,
) -> ScreeningResults:
    """
    Main screening loop: BoTorch + OC20 + MACE ensemble.

    Parameters:
        config: Validated pipeline config
        mace_runner: MACE runner (primary model)
        ensemble_runner: MACE ensemble (3 sizes for uncertainty)
        oc20_runner: OC20 runner (HOR activity)
        llm_advisor: Claude API advisor (triggered on issues)
        initial_params: Pre-filtered params from coarse_filter (optional)
        resume_checkpoint: Path to checkpoint.pt for resume

    Returns:
        ScreeningResults with all candidates evaluated
    """
    logger.info("=" * 50)
    logger.info("Phase 1b: BAYESIAN OPTIMIZATION SCREENING")
    logger.info("=" * 50)

    opt_config = config.optimizer
    n_init = opt_config.n_init
    n_iter = opt_config.n_iterations
    total_evals = n_init + n_iter

    # Setup bounds from config
    bounds = _build_bounds(config.search_space)
    var_names = list(config.search_space.variables.keys())

    # Initialize optimizer
    optimizer = BayesianOptimizer(
        bounds=bounds,
        objectives=opt_config.objectives,
        constraints=[c.model_dump() for c in opt_config.constraints],
        acquisition=opt_config.acquisition,
        seed=opt_config.seed,
        llm_advisor=llm_advisor,
    )

    # Resume from checkpoint if available
    start_iter = 0
    results = ScreeningResults()

    if resume_checkpoint:
        ckpt = load_checkpoint(resume_checkpoint)
        if ckpt:
            start_iter = ckpt["iteration"] + 1
            optimizer.train_X = ckpt["train_X"]
            optimizer.train_Y = ckpt["train_Y"]
            results.best_score = ckpt["best_score"]
            results.best_params = ckpt["best_params"]
            logger.info(f"Resumed from iteration {start_iter}")

    # --- Initial random evaluation ---
    if start_iter == 0:
        logger.info(f"── Init Round ({n_init} candidates) ──")

        if initial_params and len(initial_params) >= n_init:
            # Use pre-filtered params from coarse_filter
            init_candidates = initial_params[:n_init]
        else:
            # Random initialization
            init_X = optimizer.suggest_initial(n_init)
            init_candidates = [_tensor_to_params(init_X[i], var_names, config.search_space)
                              for i in range(n_init)]

        for i, params in enumerate(init_candidates):
            result = _evaluate_candidate(
                params, i, config, mace_runner, ensemble_runner, oc20_runner
            )
            results.candidates.append(result)

            if result.status == "success":
                Y = _scores_to_tensor(result.scores, opt_config.objectives)
                X = _params_to_tensor(result.params, var_names, config.search_space)
                optimizer.tell(X.unsqueeze(0), Y.unsqueeze(0))
                results.n_success += 1
            else:
                results.n_failed += 1

            _log_candidate(result, i, n_init, "init")

        start_iter = n_init

    # --- BO iterations ---
    n_no_improve = 0

    for iter_i in range(start_iter, total_evals):
        iter_label = iter_i - n_init + 1
        logger.info(f"── BO Iteration {iter_label}/{n_iter} ──")

        # BoTorch suggest next candidate
        candidate_X = optimizer.suggest_next(q=opt_config.batch_size)
        if candidate_X is None:
            logger.warning("BoTorch suggest returned None, using random")
            candidate_X = optimizer.suggest_initial(1)

        params = _tensor_to_params(candidate_X.squeeze(), var_names, config.search_space)

        # Evaluate
        result = _evaluate_candidate(
            params, iter_i, config, mace_runner, ensemble_runner, oc20_runner
        )
        results.candidates.append(result)

        if result.status == "success":
            Y = _scores_to_tensor(result.scores, opt_config.objectives)
            X = _params_to_tensor(result.params, var_names, config.search_space)
            optimizer.tell(X.unsqueeze(0), Y.unsqueeze(0))
            results.n_success += 1

            # Track best
            score = Y.sum().item()
            if score > results.best_score:
                results.best_score = score
                results.best_params = params
                n_no_improve = 0
            else:
                n_no_improve += 1
        else:
            results.n_failed += 1
            n_no_improve += 1

        _log_candidate(result, iter_i, total_evals, "BO")

        # --- LLM triggers ---
        failure_rate = results.n_failed / (results.n_success + results.n_failed)
        triggers = config.llm_in_loop.triggers

        # Trigger: high failure rate
        if llm_advisor.should_trigger(
            "high_failure_rate", triggers, failure_rate=failure_rate
        ):
            _handle_high_failure(llm_advisor, results, optimizer, config)

        # Trigger: convergence stalled
        if llm_advisor.should_trigger(
            "convergence_stalled", triggers, n_no_improve=n_no_improve
        ):
            _handle_stalled(llm_advisor, results, optimizer, config)
            n_no_improve = 0  # reset counter after intervention

        # Checkpoint
        save_checkpoint(
            path=config.output.dir + "/checkpoint.pt",
            iteration=iter_i,
            train_X=optimizer.train_X,
            train_Y=optimizer.train_Y,
            best_score=results.best_score,
            best_params=results.best_params,
            config_path="",
        )

        # Check convergence
        if optimizer.check_convergence(n_last=5, threshold=0.01):
            logger.info(f"✅ CONVERGED at iteration {iter_label}")
            results.converged = True
            break

    results.n_iterations = iter_i + 1
    logger.info(
        f"Screening complete: {results.n_success} success, "
        f"{results.n_failed} failed, best={results.best_score:.3f}"
    )

    return results


def _evaluate_candidate(
    params: dict,
    iteration: int,
    config: PipelineConfig,
    mace_runner: MACERunner,
    ensemble_runner: EnsembleRunner,
    oc20_runner: OC20Runner,
) -> CandidateResult:
    """Evaluate a single candidate: OC20 + MACE NEB + MACE MD."""
    t0 = time.time()
    struct_config = config.structure_generator.model_dump()

    # 1. Generate structure
    structure = generate_structure_from_params(params, struct_config)
    if structure is None:
        return CandidateResult(
            iteration=iteration, params=params,
            status="failed_generation", failure_reason="Structure generation failed",
            elapsed_s=time.time() - t0,
        )

    # 2. OC20: HOR activity (bare slab + H)
    bare_slab = build_bare_slab_with_h(
        dopant_type=params.get("dopant_type", "none"),
        dopant_percent=params.get("dopant_percent", 0),
        seed=hash(str(params)) % (2**31),
    )
    oc20_result = oc20_runner.predict_h_adsorption(bare_slab)
    if oc20_result is None:
        return CandidateResult(
            iteration=iteration, params=params,
            status="failed_oc20", failure_reason="OC20 H adsorption failed",
            elapsed_s=time.time() - t0,
        )

    # 3. MACE: NEB H₂ barrier (with ensemble)
    initial_h2, final_h2 = build_neb_structures(structure, "H2")
    h2_result = ensemble_runner.predict_neb_with_uncertainty(initial_h2, final_h2)
    if h2_result["mean_barrier"] is None:
        return CandidateResult(
            iteration=iteration, params=params,
            status="failed_neb", failure_reason="H2 NEB failed (all models)",
            elapsed_s=time.time() - t0,
        )

    # 4. MACE: NEB O₂ barrier
    initial_o2, final_o2 = build_neb_structures(structure, "O2")
    o2_result = ensemble_runner.predict_neb_with_uncertainty(initial_o2, final_o2)
    if o2_result["mean_barrier"] is None:
        return CandidateResult(
            iteration=iteration, params=params,
            status="failed_neb", failure_reason="O2 NEB failed (all models)",
            elapsed_s=time.time() - t0,
        )

    # 5. MACE: MD stability
    md_result = ensemble_runner.predict_md_with_uncertainty(
        structure,
        temperature_K=config.search_space.fixed_conditions.get(
            "temperature_K", type("", (), {"value": 343})()
        ).value,
    )
    if md_result.get("intact_ratio") is None:
        return CandidateResult(
            iteration=iteration, params=params,
            status="failed_md", failure_reason="MD stability failed",
            elapsed_s=time.time() - t0,
        )

    # 6. Compile scores
    delta_G_H = oc20_result["delta_G_H"]
    scores = {
        "hor_activity": -abs(delta_G_H),  # Maximize → closer to 0 = better
        "h2_barrier": h2_result["mean_barrier"],
        "o2_barrier": o2_result["mean_barrier"],
        "shell_stability": md_result["intact_ratio"],
    }

    uncertainty = {
        "h2_barrier_std": h2_result["std_barrier"],
        "o2_barrier_std": o2_result.get("std_barrier", 0),
        "h2_confident": h2_result["confident"],
        "energy_std": md_result.get("energy_std", 0),
    }

    # 7. Check constraints
    constraints_pass = _check_constraints(scores, config.optimizer.constraints)

    return CandidateResult(
        iteration=iteration,
        params=params,
        status="success",
        scores=scores,
        uncertainty=uncertainty,
        failure_reason="" if constraints_pass else "constraint_violation",
        elapsed_s=time.time() - t0,
    )


def _check_constraints(scores: dict, constraints: list) -> bool:
    """Check if candidate passes all constraints."""
    for c in constraints:
        metric = c.metric if hasattr(c, 'metric') else c["metric"]
        operator = c.operator if hasattr(c, 'operator') else c["operator"]
        value = c.value if hasattr(c, 'value') else c["value"]

        score_val = scores.get(metric)
        if score_val is None:
            return False

        if operator == "<" and score_val >= value:
            return False
        elif operator == ">" and score_val <= value:
            return False
        elif operator == "<=" and score_val > value:
            return False
        elif operator == ">=" and score_val < value:
            return False

    return True


def _build_bounds(search_space) -> torch.Tensor:
    """Build BoTorch bounds tensor from config search_space."""
    lowers = []
    uppers = []

    for name, var in search_space.variables.items():
        if var.type == "categorical":
            # Encode categorical as integer index
            lowers.append(0)
            uppers.append(len(var.values) - 1)
        else:
            lowers.append(var.range[0])
            uppers.append(var.range[1])

    return torch.tensor([lowers, uppers], dtype=DTYPE)


def _params_to_tensor(params: dict, var_names: list, search_space) -> torch.Tensor:
    """Convert params dict to tensor for BoTorch."""
    values = []
    for name in var_names:
        var = search_space.variables[name]
        if var.type == "categorical":
            idx = var.values.index(params[name]) if params[name] in var.values else 0
            values.append(float(idx))
        else:
            values.append(float(params[name]))
    return torch.tensor(values, dtype=DTYPE)


def _tensor_to_params(tensor: torch.Tensor, var_names: list, search_space) -> dict:
    """Convert BoTorch tensor back to params dict."""
    params = {}
    for i, name in enumerate(var_names):
        var = search_space.variables[name]
        val = tensor[i].item()

        if var.type == "categorical":
            idx = int(round(val))
            idx = max(0, min(idx, len(var.values) - 1))
            params[name] = var.values[idx]
        elif var.type == "int":
            params[name] = int(round(val))
        else:
            params[name] = float(val)

    return params


def _scores_to_tensor(scores: dict, objectives: list) -> torch.Tensor:
    """Extract objective values from scores dict."""
    values = [scores.get(obj, 0.0) for obj in objectives]
    return torch.tensor(values, dtype=DTYPE)


def _log_candidate(result: CandidateResult, i: int, total: int, phase: str):
    """Log candidate evaluation result."""
    if result.status == "success":
        scores_str = ", ".join(f"{k}={v:.3f}" for k, v in result.scores.items())
        logger.info(
            f"  [{phase} {i+1}/{total}] {_params_short(result.params)} → "
            f"{scores_str} ({result.elapsed_s:.1f}s)"
        )
    else:
        logger.warning(
            f"  [{phase} {i+1}/{total}] {_params_short(result.params)} → "
            f"FAILED: {result.failure_reason} ({result.elapsed_s:.1f}s)"
        )


def _params_short(params: dict) -> str:
    """Short string representation of params."""
    parts = []
    if params.get("dopant_type", "none") != "none":
        parts.append(f"{params['dopant_type']}{int(params.get('dopant_percent', 0))}")
    else:
        parts.append("Ni")
    parts.append(f"{int(params.get('n_layers', 2))}L")
    parts.append(f"{int(params.get('vacancy_percent', 0))}%v")
    if params.get("n_doping_percent", 0) > 0:
        parts.append(f"{int(params['n_doping_percent'])}%N")
    return " ".join(parts)


def _handle_high_failure(llm_advisor, results, optimizer, config):
    """LLM trigger: too many failures."""
    failures = [c for c in results.candidates if c.status != "success"]
    failure_modes = {}
    for f in failures:
        mode = f.failure_reason
        failure_modes[mode] = failure_modes.get(mode, 0) + 1

    context = (
        f"Pipeline: {config.meta.pipeline}\n"
        f"Failures: {len(failures)}/{len(results.candidates)} "
        f"({100*len(failures)/len(results.candidates):.0f}%)\n"
        f"Failure modes: {failure_modes}\n"
        f"Current bounds: {optimizer.bounds.tolist()}"
    )
    question = "High failure rate. Should I adjust search space bounds? Give specific new ranges."

    advice = llm_advisor.ask(context, question)
    if advice:
        logger.info(f"LLM advice (high failure): {advice[:200]}...")
        # Note: In production, parse advice to extract new bounds
        # For now, log only — manual bound update would need parsing logic


def _handle_stalled(llm_advisor, results, optimizer, config):
    """LLM trigger: score not improving."""
    best = optimizer.get_best()
    context = (
        f"Pipeline: {config.meta.pipeline}\n"
        f"Best score: {results.best_score:.3f}\n"
        f"Best params: {results.best_params}\n"
        f"Iterations without improvement: 5+\n"
        f"Current bounds: {optimizer.bounds.tolist()}"
    )
    question = "Score stalled for 5 iterations. Suggest a different region to explore or new variable to add."

    advice = llm_advisor.ask(context, question)
    if advice:
        logger.info(f"LLM advice (stalled): {advice[:200]}...")
