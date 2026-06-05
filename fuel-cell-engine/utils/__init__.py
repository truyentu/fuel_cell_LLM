"""
Logging setup for Level 2 Engine.
Console (tqdm-friendly) + file handler.
"""

import logging
import sys
from pathlib import Path


def setup_logger(output_dir: str, level: int = logging.INFO) -> logging.Logger:
    """Configure root logger with console + file handlers."""
    root = logging.getLogger()
    root.setLevel(level)

    # Clear existing handlers
    root.handlers.clear()

    # Format
    fmt = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    # Console handler (stderr to not interfere with tqdm)
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(fmt)
    root.addHandler(console)

    # File handler
    log_dir = Path(output_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "run.log", mode="a", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    return root
