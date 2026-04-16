import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging():
    """Configure rotating file logging and quiet noisy uvicorn warnings."""
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "hermes_run.log"

    # Rotating file handler: 5 files x 5MB
    handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(fmt)

    root = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        root.addHandler(handler)
    root.setLevel(logging.INFO)

    # Quiet common uvicorn warnings (e.g., unsupported upgrade requests)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("uvicorn.asgi").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)