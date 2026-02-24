import logging
from typing import Optional
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class BasePage:
    """Base class for all Page Objects.
    Provides reusable, robust wrappers around Playwright actions
    with built-in logging and error handling.
    """

    def __init__(self, page: Page, baseUrl: str, timeout: int = 30000):
        self.page = page
        self.baseUrl = baseUrl
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    #  Navigation
    # ------------------------------------------------------------------ #

    def navigate(self, path: str = "") -> None:
        url = f"{self.baseUrl}{path}"
        logger.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded")

    # ------------------------------------------------------------------ #
    #  Actions
    # ------------------------------------------------------------------ #

    def click(self, selector: str, timeout: Optional[int] = None) -> None:
        logger.info(f"Clicking: {selector}")
        self.page.locator(selector).click(timeout=timeout or self.timeout)

    def fill(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        logger.info(f"Filling '{selector}' with '{value}'")
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout or self.timeout)
        locator.clear()
        locator.fill(value)

    def pressKey(self, selector: str, key: str) -> None:
        logger.info(f"Pressing '{key}' on '{selector}'")
        self.page.locator(selector).press(key)

    def pressEnter(self, selector: str) -> None:
        self.pressKey(selector, "Enter")

    # ------------------------------------------------------------------ #
    #  Assertions (Playwright expect)
    # ------------------------------------------------------------------ #

    def assertVisible(self, selector: str, timeout: Optional[int] = None) -> None:
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout or self.timeout)

    def assertHidden(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_hidden()

    def assertContainsText(self, selector: str, text: str) -> None:
        expect(self.page.locator(selector)).to_contain_text(text)

    # ------------------------------------------------------------------ #
    #  Cookie / Overlay Handling
    # ------------------------------------------------------------------ #

    def acceptCookies(self) -> None:
        """Accept cookie consent banner if present on Sainsbury's.
        Covers both the main site banner and the Groceries SPA banner.
        """
        cookieSelectors = [
            "button:has-text('Continue and accept')",
            "button:has-text('Accept all')",
            "button#onetrust-accept-btn-handler",
            "[data-testid='accept-all-cookies']",
            "button:has-text('Accept all cookies')",
            "button:has-text('Accept All Cookies')",
        ]
        for selector in cookieSelectors:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=1000):
                    locator.click()
                    self.page.wait_for_timeout(1000)
                    logger.info(f"Cookie banner accepted via: {selector}")
                    self._dismissOnetrust()
                    return
            except PlaywrightTimeoutError:
                continue

    def _dismissOnetrust(self) -> None:
        """Remove OneTrust consent SDK DOM elements that can intercept clicks."""
        try:
            self.page.evaluate(
                "document.querySelectorAll("
                "'#onetrust-consent-sdk, .onetrust-pc-dark-filter, #onetrust-pc-sdk'"
                ").forEach(el => el.remove())"
            )
        except Exception:
            pass
