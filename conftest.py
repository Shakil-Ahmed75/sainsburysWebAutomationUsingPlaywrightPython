import pytest
import logging
from pathlib import Path
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config.settings import loadConfig, Config
from utils.logger import setupLogger
from utils.helpers import getScreenshotPath, getVideoPath, ensureDir

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
#  CLI Options
# ------------------------------------------------------------------ #

def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Target environment: dev | staging | prod",
    )
    parser.addoption(
        "--browser-type",
        action="store",
        default=None,
        help="Browser: chromium | firefox | webkit",
    )
    parser.addoption(
        "--headless",
        action="store",
        default=None,
        help="Run headless: true | false",
    )


# ------------------------------------------------------------------ #
#  Session-scoped Config
# ------------------------------------------------------------------ #

@pytest.fixture(scope="session")
def config(request: pytest.FixtureRequest) -> Config:
    env = request.config.getoption("--env", default=None)
    cfg = loadConfig(env)

    browserOverride = request.config.getoption("--browser-type", default=None)
    headlessOverride = request.config.getoption("--headless", default=None)

    if browserOverride:
        cfg.environment.browser = browserOverride
    if headlessOverride is not None:
        cfg.environment.headless = headlessOverride.lower() == "true"

    setupLogger(cfg.logging.level, cfg.logging.log_file)
    logger.info(f"Running tests in environment: '{cfg.env_name}'")
    logger.info(f"Base URL: {cfg.environment.base_url}")
    logger.info(f"Browser: {cfg.environment.browser} | Headless: {cfg.environment.headless}")

    ensureDir("reports/screenshots")
    ensureDir("reports/videos")
    ensureDir("reports/traces")
    ensureDir(cfg.reporting.allure_results_dir)

    return cfg


# ------------------------------------------------------------------ #
#  Playwright + Browser (Session scope for speed)
# ------------------------------------------------------------------ #

@pytest.fixture(scope="session")
def playwrightInstance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwrightInstance: Playwright, config: Config) -> Browser:
    browserType = getattr(playwrightInstance, config.environment.browser)
    b = browserType.launch(
        headless=config.environment.headless,
        slow_mo=config.environment.slow_mo,
        args=["--disable-blink-features=AutomationControlled"],
    )
    yield b
    b.close()


# ------------------------------------------------------------------ #
#  Context and Page (Function scope — isolated per test)
# ------------------------------------------------------------------ #

@pytest.fixture(scope="function")
def context(browser: Browser, config: Config, request: pytest.FixtureRequest) -> BrowserContext:
    videoDir = getVideoPath(request.node.name)

    ctxOptions = {
        "viewport": {
            "width": config.environment.viewport.width,
            "height": config.environment.viewport.height,
        },
        "locale": "en-GB",
        "timezone_id": "Europe/London",
        "record_video_dir": videoDir if config.reporting.video_on_failure else None,
    }

    if config.reporting.trace_on_failure:
        ctxOptions["record_har_path"] = None

    ctx: BrowserContext = browser.new_context(**ctxOptions)

    if config.reporting.trace_on_failure:
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield ctx

    testFailed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False

    if config.reporting.trace_on_failure and testFailed:
        tracePath = f"reports/traces/{request.node.name}.zip"
        ctx.tracing.stop(path=tracePath)
        logger.info(f"Trace saved: {tracePath}")
    elif config.reporting.trace_on_failure:
        ctx.tracing.stop()

    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, config: Config) -> Page:
    p = context.new_page()
    p.set_default_timeout(config.environment.timeout)
    p.set_default_navigation_timeout(config.environment.timeout)
    yield p
    p.close()


# ------------------------------------------------------------------ #
#  Screenshot on failure hook
# ------------------------------------------------------------------ #

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    outcome = yield
    report = outcome.get_result()
    item.rep_call = report

    if report.when == "call" and report.failed:
        pageFixture = item.funcargs.get("page")
        configFixture = item.funcargs.get("config")

        if pageFixture and configFixture and configFixture.reporting.screenshot_on_failure:
            screenshotPath = getScreenshotPath(item.name)
            try:
                pageFixture.screenshot(path=screenshotPath, full_page=True)
                logger.info(f"Failure screenshot saved: {screenshotPath}")

                try:
                    import allure
                    with open(screenshotPath, "rb") as f:
                        allure.attach(f.read(), name="Failure Screenshot", attachment_type=allure.attachment_type.PNG)
                except ImportError:
                    pass

            except Exception as e:
                logger.warning(f"Could not take screenshot: {e}")


# ------------------------------------------------------------------ #
#  Page Object Fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def homePage(page: Page, config: Config):
    from pages.homePage import HomePage
    return HomePage(page, config.environment.base_url, config.environment.timeout)


@pytest.fixture
def groceriesPage(page: Page, config: Config):
    from pages.groceriesPage import GroceriesPage
    return GroceriesPage(page, config.environment.base_url, config.environment.timeout)


@pytest.fixture
def loginPage(page: Page, config: Config):
    from pages.loginPage import LoginPage
    return LoginPage(page, config.environment.base_url, config.environment.timeout)
