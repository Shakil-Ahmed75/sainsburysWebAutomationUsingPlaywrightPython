import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path(__file__).parent
PROJECT_ROOT = CONFIG_DIR.parent


@dataclass
class ViewportConfig:
    width: int = 1920
    height: int = 1080


@dataclass
class ReportingConfig:
    screenshot_on_failure: bool = True
    video_on_failure: bool = True
    trace_on_failure: bool = True
    allure_results_dir: str = "reports/allure-results"
    html_report_dir: str = "reports/html"


@dataclass
class RetryConfig:
    max_retries: int = 2
    retry_delay: int = 1


@dataclass
class LoggingConfig:
    level: str = "INFO"
    log_file: str = "reports/test_run.log"


@dataclass
class EnvironmentConfig:
    base_url: str = "https://www.sainsburys.co.uk"
    browser: str = "chromium"
    headless: bool = True
    slow_mo: int = 0
    timeout: int = 30000
    viewport: ViewportConfig = field(default_factory=ViewportConfig)


@dataclass
class Config:
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    env_name: str = "dev"


def loadConfig(env: Optional[str] = None) -> Config:
    configFile = CONFIG_DIR / "config.yaml"

    with open(configFile, "r") as f:
        raw = yaml.safe_load(f)

    envName = env or os.getenv("TEST_ENV") or raw.get("default_environment", "dev")
    envData = raw["environments"].get(envName, raw["environments"]["dev"])

    viewportData = envData.get("viewport", {})
    viewport = ViewportConfig(
        width=viewportData.get("width", 1920),
        height=viewportData.get("height", 1080),
    )

    environment = EnvironmentConfig(
        base_url=envData.get("base_url", "https://www.sainsburys.co.uk"),
        browser=envData.get("browser", "chromium"),
        headless=envData.get("headless", True),
        slow_mo=envData.get("slow_mo", 0),
        timeout=envData.get("timeout", 30000),
        viewport=viewport,
    )

    repData = raw.get("reporting", {})
    reporting = ReportingConfig(
        screenshot_on_failure=repData.get("screenshot_on_failure", True),
        video_on_failure=repData.get("video_on_failure", True),
        trace_on_failure=repData.get("trace_on_failure", True),
        allure_results_dir=repData.get("allure_results_dir", "reports/allure-results"),
        html_report_dir=repData.get("html_report_dir", "reports/html"),
    )

    retryData = raw.get("retry", {})
    retry = RetryConfig(
        max_retries=retryData.get("max_retries", 2),
        retry_delay=retryData.get("retry_delay", 1),
    )

    logData = raw.get("logging", {})
    loggingCfg = LoggingConfig(
        level=logData.get("level", "INFO"),
        log_file=logData.get("log_file", "reports/test_run.log"),
    )

    return Config(
        environment=environment,
        reporting=reporting,
        retry=retry,
        logging=loggingCfg,
        env_name=envName,
    )
