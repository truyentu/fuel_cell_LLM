"""
Logging setup for Level 2 Engine.
"""

import logging
import sys
from pathlib import Path


def setup_logger(output_dir: str, level: int = logging.INFO) -> logging.Logger:
    """Configure root logger with console + file handlers."""
    root = logging.getLogger("engine")
    root.setLevel(level)
    root.handlers.clear()

    fmt = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    # Console (stderr — tqdm-friendly)
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(fmt)
    root.addHandler(console)

    # File
    log_dir = Path(output_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_dir / "run.log", mode="a", encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    root.info(f"Logger initialized. Output: {log_dir / 'run.log'}")
    return root
