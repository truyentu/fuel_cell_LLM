"""
Checkpoint save/load for BoTorch optimization state.
Saves after EVERY iteration — resume if crash/disconnect.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

import torch

logger = logging.getLogger("engine.checkpoint")


def _config_hash(config_path: str) -> str:
    """Hash config file to detect changes between sessions."""
    with open(config_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def save_checkpoint(
    path: str | Path,
    iteration: int,
    train_X: torch.Tensor,
    train_Y: torch.Tensor,
    best_score: float,
    best_params: dict,
    config_path: str = "",
):
    """Save optimization state to disk."""
    checkpoint = {
        "iteration": iteration,
        "train_X": train_X,
        "train_Y": train_Y,
        "best_score": best_score,
        "best_params": best_params,
        "config_hash": _config_hash(config_path) if config_path else "",
        "timestamp": datetime.now().isoformat(),
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint, path)
    logger.debug(f"Checkpoint saved: iter={iteration}, best={best_score:.4f}")


def load_checkpoint(path: str | Path, config_path: str = "") -> dict | None:
    """Load checkpoint. Returns None if not found or config mismatch."""
    path = Path(path)
    if not path.exists():
        return None

    checkpoint = torch.load(path, weights_only=False)

    # Verify config hasn't changed
    if config_path and checkpoint.get("config_hash"):
        current_hash = _config_hash(config_path)
        if current_hash != checkpoint["config_hash"]:
            logger.warning(
                f"Config changed since checkpoint! "
                f"Checkpoint: {checkpoint['config_hash']}, Current: {current_hash}. "
                f"Starting fresh."
            )
            return None

    logger.info(
        f"Checkpoint loaded: iter={checkpoint['iteration']}, "
        f"best={checkpoint['best_score']:.4f}, "
        f"saved at {checkpoint['timestamp']}"
    )
    return checkpoint
