"""
Fuel Cell Engine — Level 2 Compute Pipeline
Entry point: python run.py --config config.json [--resume checkpoint.pt] [--skip-calibration]

Finds optimal Ni-alloy + carbon shell configuration for PGM-free AEMFC anode
using Bayesian optimization + MACE + OC20 + JDFTx.
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config_schema import load_config
from utils.logger import setup_logger
from utils.checkpoint import load_checkpoint
from utils.reporter import generate_all_reports
from runners.mace_runner import MACERunner
from runners.mace_ensemble import EnsembleRunner
from runners.oc20_runner import OC20Runner
from runners.jdftx_runner import JDFTxRunner
from runners.chgnet_runner import CHGNetRunner
from data.gnome_lookup import GNoMELookup
from data.synterra_query import SynTERRAQuery
from llm_advisor import LLMAdvisor
from phases.calibration import run_calibration
from phases.coarse_filter import coarse_filter
from phases.screening import run_screening
from phases.dft_feedback import run_dft_feedback
from analysis.verification import run_verification
from analysis.failure_analyzer import summarize_failures


def main():
    args = parse_args()

    # 1. Load + validate config
    config = load_config(args.config)
    output_dir = config.output.dir
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Setup logger
    logger = setup_logger(output_dir)
    logger.info("=" * 60)
    logger.info(f"  FUEL CELL ENGINE — {config.meta.pipeline}")
    logger.info(f"  Goal: {config.meta.goal}")
    logger.info(f"  Confidence: {config.meta.source_confidence}")
    logger.info("=" * 60)

    t_start = time.time()

    # 2. Initialize runners
    device = "cuda" if not args.cpu else "cpu"
    logger.info(f"Device: {device}")

    mace_runner = MACERunner(model="medium", device=device)
    ensemble_runner = EnsembleRunner(device=device)
    oc20_runner = OC20Runner(device=device)
    jdftx_runner = JDFTxRunner()
    chgnet_runner = CHGNetRunner(device=device)
    gnome_lookup = GNoMELookup()
    synterra_query = SynTERRAQuery()
    llm_advisor = LLMAdvisor(config.llm_in_loop.model_dump())

    # Determine OC20 status
    if oc20_runner.calc is not None:
        oc20_status = "OK"
    elif oc20_runner._use_descriptor_fallback:
        oc20_status = "DESCRIPTOR"
    else:
        oc20_status = "MOCK"

    logger.info(
        f"Runners: MACE={'OK' if mace_runner.is_available else 'MOCK'}, "
        f"OC20={oc20_status}, "
        f"CHGNet={'OK' if chgnet_runner.is_available else 'MOCK'}, "
        f"JDFTx={'OK' if jdftx_runner.is_available else 'MOCK'}, "
        f"GNoME={'OK' if gnome_lookup.is_available else 'OFF'}, "
        f"SynTERRA={'OK' if synterra_query.is_available else 'OFF'}, "
        f"LLM={'ON' if llm_advisor.enabled else 'OFF'}"
    )

    # 3. Phase 0: Calibration
    cal_report = None
    if not args.skip_calibration:
        cal_report = run_calibration(
            config.calibration.model_dump(), mace_runner, oc20_runner
        )
        if not cal_report.passed and config.calibration.stop_on_fail:
            logger.error("CALIBRATION FAILED. Pipeline stopped.")
            logger.error(f"Reason: {cal_report.message}")
            logger.error("Fix: check model installation, or use --skip-calibration for mock testing")
            from utils.reporter import generate_calibration_report
            generate_calibration_report(cal_report, f"{output_dir}/{config.output.calibration_report}")
            sys.exit(1)
    else:
        logger.warning("⚠️ Calibration SKIPPED (--skip-calibration flag)")

    # 4. Phase 1a: Coarse Filter
    search_dict = config.search_space.model_dump()
    struct_dict = config.structure_generator.model_dump()
    filtered_params = coarse_filter(
        {"search_space": search_dict, "structure_generator": struct_dict},
        chgnet_runner,
        gnome_lookup=gnome_lookup,
        n_random=100,
        keep_percentile=30,
        seed=config.optimizer.seed,
    )

    # GATE CHECK: Phase 1a → 1b
    from phases.coarse_filter import check_filter_gate
    gate_1a = check_filter_gate(filtered_params, min_survivors=10)
    if not gate_1a["pass"]:
        logger.error(f"GATE FAIL (Phase 1a→1b): {gate_1a['message']}")
        logger.error("Options: expand search space, lower filter threshold, check CHGNet")
        sys.exit(1)
    logger.info(f"GATE PASS (1a→1b): {gate_1a['n_survivors']} candidates → screening")

    # 5. Phase 1b: Screening (main BO loop)
    resume_ckpt = args.resume if args.resume else None
    results = run_screening(
        config=config,
        mace_runner=mace_runner,
        ensemble_runner=ensemble_runner,
        oc20_runner=oc20_runner,
        llm_advisor=llm_advisor,
        initial_params=filtered_params,
        resume_checkpoint=resume_ckpt,
    )

    # 6. Verification
    ver_report = run_verification(results, config)
    logger.info(f"Trust Score: {ver_report.trust_score}")

    # GATE CHECK: Phase 1b → Phase 2
    if ver_report.trust_score in ("D", "F"):
        logger.error(
            f"GATE FAIL (Phase 1→2): Trust Score {ver_report.trust_score}. "
            f"Results NOT reliable. DO NOT proceed to lab."
        )
        logger.error("Options: debug model, check calibration, expand search space, add data")
        # Still generate reports for debugging
        generate_all_reports(results, cal_report, ver_report, config, synterra_query)
        sys.exit(1)
    elif ver_report.trust_score == "C":
        logger.warning(
            f"GATE WARNING: Trust Score C. Proceed with caution. "
            f"Review verification_report.md before lab decisions."
        )

    # 7. Failure Analysis
    failure_summary = summarize_failures(results.candidates)
    if failure_summary["total_failed"] > 0:
        logger.info(
            f"Failures: {failure_summary['total_failed']} total, "
            f"types: {failure_summary['by_type']}"
        )

    # 8. Phase 2: DFT Feedback (optional)
    dft_report = None
    if config.tools.validation.when != "skip":
        if ver_report.trust_score in ("A", "B", "C"):
            dft_report = run_dft_feedback(
                config=config,
                screening_results=results,
                jdftx_runner=jdftx_runner,
            )
        else:
            logger.warning(
                f"Skipping DFT validation: trust score {ver_report.trust_score} too low. "
                f"Fix screening issues first."
            )

    # 9. Generate Reports
    generate_all_reports(results, cal_report, ver_report, config, synterra_query)

    # 10. Summary
    elapsed = time.time() - t_start
    logger.info("")
    logger.info("=" * 60)
    logger.info("  PIPELINE COMPLETE")
    logger.info(f"  Duration: {elapsed/3600:.1f} hours")
    logger.info(f"  Candidates evaluated: {len(results.candidates)}")
    logger.info(f"  Success: {results.n_success}, Failed: {results.n_failed}")
    logger.info(f"  Converged: {results.converged}")
    logger.info(f"  Trust Score: {ver_report.trust_score}")
    logger.info(f"  Best score: {results.best_score:.3f}")
    logger.info(f"  Best params: {results.best_params}")
    if dft_report:
        logger.info(f"  DFT Spearman ρ: {dft_report.spearman_rho:.3f}")
        logger.info(f"  Ranking reliable: {dft_report.ranking_reliable}")
    logger.info(f"  LLM calls used: {llm_advisor.call_count}/{llm_advisor.max_calls}")
    logger.info(f"  Output: {output_dir}")
    logger.info("=" * 60)

    # Exit code based on trust
    if ver_report.trust_score in ("A", "B"):
        logger.info("✅ Results ready for lab validation.")
        return 0
    elif ver_report.trust_score == "C":
        logger.warning("⚠️ Results have warnings. Review before proceeding to lab.")
        return 0
    else:
        logger.error("❌ Results NOT reliable. Do not proceed to lab.")
        return 1


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fuel Cell Engine — Ni@C Catalyst Optimization Pipeline"
    )
    parser.add_argument(
        "--config", required=True,
        help="Path to config.json (from /scientist plan)"
    )
    parser.add_argument(
        "--resume", default=None,
        help="Path to checkpoint.pt for resuming interrupted run"
    )
    parser.add_argument(
        "--skip-calibration", action="store_true",
        help="Skip Phase 0 calibration (for mock testing)"
    )
    parser.add_argument(
        "--cpu", action="store_true",
        help="Force CPU mode (no GPU)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
