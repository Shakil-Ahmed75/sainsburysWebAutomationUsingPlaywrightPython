import random
import string
from datetime import datetime
from pathlib import Path


def generateRandomString(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def generateRandomEmail() -> str:
    return f"test_{generateRandomString(6)}@example.com"


def generateRandomPassword(length: int = 12) -> str:
    """Generate a random password with mixed characters that will always fail Sainsbury's login."""
    chars = string.ascii_letters + string.digits + "!@#$"
    return "".join(random.choices(chars, k=length))


def getTimestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def getScreenshotPath(testName: str, baseDir: str = "reports/screenshots") -> str:
    path = Path(baseDir)
    path.mkdir(parents=True, exist_ok=True)
    timestamp = getTimestamp()
    return str(path / f"{testName}_{timestamp}.png")


def getVideoPath(testName: str, baseDir: str = "reports/videos") -> str:
    path = Path(baseDir)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def ensureDir(directory: str) -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path
