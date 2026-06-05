"""
Config schema validation for Level 2 Engine.
Reads config.json from /scientist plan → validates → returns typed config.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


# --- Sub-models ---

class Meta(BaseModel):
    pipeline: str
    created_by: str = "scientist_level1"
    date: str
    goal: str
    plan_file: str = ""
    source_confidence: Literal["HIGH", "MEDIUM", "LOW"]


class Benchmark(BaseModel):
    name: str
    structure_type: str = ""
    element: str = ""
    elements: dict = Field(default_factory=dict)
    expected: float | None = None
    expected_intact: float | None = None
    expected_intact_max: float | None = None
    expected_intact_range: list[float] | None = None
    expected_lattice_A: float | None = None
    tolerance: float | None = None
    tolerance_A: float | None = None
    units: str = ""
    source: str = ""
    md_temperature_K: float | None = None
    md_steps: int | None = None
    vacancy_percent: float | None = None


class CalibrationConfig(BaseModel):
    enabled: bool = True
    stop_on_fail: bool = True
    oc20_benchmarks: list[Benchmark] = Field(default_factory=list)
    mace_benchmarks: list[Benchmark] = Field(default_factory=list)
    pass_criteria: dict = Field(default_factory=dict)


class Variable(BaseModel):
    type: Literal["int", "float", "categorical"]
    range: list[float] | None = None
    step: float | None = None
    values: list[str] | None = None
    units: str = ""
    source: str = ""

    @field_validator("source")
    @classmethod
    def source_not_empty(cls, v):
        if not v:
            logger.warning("Variable missing source tag")
        return v


class FixedCondition(BaseModel):
    value: float | list | str
    units: str = ""
    source: str = ""


class SearchSpace(BaseModel):
    description: str = ""
    variables: dict[str, Variable]
    fixed_conditions: dict[str, FixedCondition] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_ranges(self):
        for name, var in self.variables.items():
            if var.type in ("int", "float") and var.range:
                if var.range[0] >= var.range[1]:
                    raise ValueError(f"Variable '{name}': range[0] >= range[1]")
                if "percent" in name and var.range[1] > 100:
                    raise ValueError(f"Variable '{name}': percent > 100")
        return self


class Target(BaseModel):
    metric: str
    direction: Literal["minimize", "maximize", "minimize_abs", "minimize_distance_to"]
    reference: float | None = None
    threshold: float
    units: str = ""
    source: str = ""
    priority: int = 1
    note: str = ""

    @field_validator("source")
    @classmethod
    def check_unverified(cls, v):
        if "[UNVERIFIED]" in v.upper():
            logger.warning(f"Target source contains [UNVERIFIED]: {v}")
        return v


class ScreeningTool(BaseModel):
    tool: str
    model: str = ""
    task_name: str = ""
    evaluates: list[str] = Field(default_factory=list)
    settings: dict = Field(default_factory=dict)
    note: str = ""


class EnsembleConfig(BaseModel):
    enabled: bool = True
    models: list[str] = Field(default_factory=lambda: ["small", "medium", "large"])
    confidence_threshold_eV: float = 0.10
    action_on_high_uncertainty: str = "flag_and_deprioritize"


class ValidationTool(BaseModel):
    tool: str = "jdftx"
    when: Literal["top_n", "all", "skip"] = "top_n"
    n: int = 5
    evaluates: list[str] = Field(default_factory=list)
    settings: dict = Field(default_factory=dict)


class Tools(BaseModel):
    screening: ScreeningTool
    simulation: ScreeningTool
    ensemble: EnsembleConfig = Field(default_factory=EnsembleConfig)
    validation: ValidationTool = Field(default_factory=ValidationTool)


class Constraint(BaseModel):
    metric: str
    operator: Literal["<", ">", "<=", ">=", "=="]
    value: float


class Optimizer(BaseModel):
    tool: str = "botorch"
    type: Literal["single_objective", "multi_objective"] = "multi_objective"
    objectives: list[str]
    constraints: list[Constraint] = Field(default_factory=list)
    n_init: int = 8
    n_iterations: int = 25
    batch_size: int = 1
    acquisition: str = "qLogExpectedHypervolumeImprovement"
    seed: int = 42

    @field_validator("n_iterations")
    @classmethod
    def warn_high_iterations(cls, v):
        if v > 50:
            logger.warning(f"n_iterations={v} > 50: diminishing returns likely")
        return v


class LLMTrigger(BaseModel):
    threshold: float | None = None
    n_iter_no_improve: int | None = None


class LLMInLoop(BaseModel):
    enabled: bool = True
    api: str = "anthropic"
    model: str = "claude-sonnet-4-20250514"
    triggers: dict[str, LLMTrigger | bool] = Field(default_factory=dict)
    max_llm_calls: int = 5
    fallback_if_no_api: str = "continue_with_defaults"


class StructureGenerator(BaseModel):
    type: str
    slab_surface: str = "fcc111"
    slab_layers: int = 4
    fix_bottom_layers: int = 2
    graphene_interlayer_A: float = 3.4
    ni_c_gap_A: float = 2.15
    graphene_stacking: str = "AB"
    vacancy_method: str = "random_removal"
    doping_method: str = "random_substitution_C_to_N"
    alloy_method: str = "random_substitution_surface_layers"
    description: str = ""


class Output(BaseModel):
    dir: str
    results_csv: str = "results.csv"
    ranked_md: str = "ranked_candidates.md"
    pareto_plot: str = "pareto.png"
    best_structure: str = "best_candidate.xyz"
    calibration_report: str = "calibration_report.md"
    verification_report: str = "verification_report.md"
    failure_analysis: str = "failure_analysis.md"


# --- Main Config Model ---

class PipelineConfig(BaseModel):
    meta: Meta
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)
    search_space: SearchSpace
    targets: dict[str, Target]
    tools: Tools
    optimizer: Optimizer
    llm_in_loop: LLMInLoop = Field(default_factory=LLMInLoop)
    structure_generator: StructureGenerator
    output: Output

    @model_validator(mode="after")
    def validate_cross_references(self):
        """Ensure optimizer references valid targets."""
        target_names = set(self.targets.keys())

        for obj in self.optimizer.objectives:
            if obj not in target_names:
                raise ValueError(
                    f"Optimizer objective '{obj}' not found in targets: {target_names}"
                )

        for constraint in self.optimizer.constraints:
            if constraint.metric not in target_names:
                raise ValueError(
                    f"Optimizer constraint metric '{constraint.metric}' "
                    f"not found in targets: {target_names}"
                )

        return self

    @model_validator(mode="after")
    def warn_unverified_targets(self):
        """Warn (not reject) if targets have UNVERIFIED sources."""
        for name, target in self.targets.items():
            if "[UNVERIFIED]" in target.source.upper():
                logger.warning(
                    f"Target '{name}' has [UNVERIFIED] source. "
                    f"Results should be interpreted with caution. "
                    f"Engine will proceed but flag in verification report."
                )
        return self

    @model_validator(mode="after")
    def warn_skip_validation(self):
        """Warn if JDFTx validation is skipped."""
        if self.tools.validation.when == "skip":
            logger.warning(
                "JDFTx validation is SKIPPED. "
                "Results will NOT be validated in electrolyte."
            )
        return self


# --- Load function ---

def load_config(config_path: str | Path) -> PipelineConfig:
    """Load and validate config.json."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    config = PipelineConfig(**raw)
    logger.info(f"Config loaded: {config.meta.pipeline} ({config.meta.source_confidence})")
    logger.info(f"  Search space: {len(config.search_space.variables)} variables")
    logger.info(f"  Targets: {len(config.targets)} metrics")
    logger.info(f"  Optimizer: {config.optimizer.n_init} init + {config.optimizer.n_iterations} iterations")

    return config
