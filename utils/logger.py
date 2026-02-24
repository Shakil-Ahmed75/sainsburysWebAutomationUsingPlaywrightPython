import logging
import sys
from pathlib import Path


def setupLogger(level: str = "INFO", logFile: str = "reports/test_run.log") -> logging.Logger:
    logLevel = getattr(logging, level.upper(), logging.INFO)
    logPath = Path(logFile)
    logPath.parent.mkdir(parents=True, exist_ok=True)

    logFormat = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    dateFormat = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logLevel,
        format=logFormat,
        datefmt=dateFormat,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logPath, mode="a", encoding="utf-8"),
        ],
    )

    return logging.getLogger("sainsburys_automation")
