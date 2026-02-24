import logging
from playwright.sync_api import Page
from pages.basePage import BasePage

logger = logging.getLogger(__name__)


class GroceriesPage(BasePage):
    """
    Page Object for Sainsbury's Groceries section (gol-ui/groceries).

    Real selectors verified against live site Feb 2026:
      - Search input : input[placeholder="Search Sainsbury's"]  (type=search)
    """

    groceriesUrl = "/gol-ui/groceries"

    # Search bar — multiple selectors for resilience across site updates
    searchInput = "input[placeholder=\"Search Sainsbury's\"], input[type='search'], input[data-testid*='search'], input[name='search']"

    # URL fragment that confirms we are on the Groceries SPA
    groceriesUrlPattern = "**/gol-ui/**"

    def __init__(self, page: Page, baseUrl: str, timeout: int = 30000):
        super().__init__(page, baseUrl, timeout)

    # ------------------------------------------------------------------ #
    #  Navigation
    # ------------------------------------------------------------------ #

    def open(self) -> "GroceriesPage":
        self.navigate(self.groceriesUrl)
        self.page.wait_for_timeout(3000)
        self.acceptCookies()
        return self

    # ------------------------------------------------------------------ #
    #  Actions
    # ------------------------------------------------------------------ #

    def searchFor(self, query: str) -> None:
        """Type a query in the Groceries search bar and submit."""
        logger.info(f"Groceries search: '{query}'")
        search = self.page.locator(self.searchInput).first
        search.wait_for(state="visible", timeout=1000)
        search.fill(query)
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(4000)
        self.acceptCookies()
        logger.info(f"Search submitted — URL: {self.page.url}")

    def scrollAndClickAddButton(self) -> str:
        """Scroll down the Groceries landing page until an 'Add' button is found,
        then click it. Returns the product name (if readable) or an empty string.

        When an unauthenticated user clicks Add, the site redirects to login.
        """
        logger.info("Scrolling Groceries page to find an Add button")

        self.acceptCookies()
        self._dismissOnetrust()

        addSelectors = [
            "button[data-testid='add-button']",
            "button[data-testid='pd-add-to-trolley-button']",
            "button[aria-label*='Add']",
            "button[aria-label*='add']",
            "button:has-text('Add')",
        ]

        for scrollStep in range(1, 15):
            self.page.evaluate(f"window.scrollTo(0, {scrollStep * 400})")
            self.page.wait_for_timeout(700)

            for selector in addSelectors:
                locator = self.page.locator(selector).first
                try:
                    if locator.is_visible(timeout=1000):
                        productName = ""
                        ariaLabel = locator.get_attribute("aria-label") or ""
                        if ariaLabel.lower().startswith("add "):
                            productName = ariaLabel[4:].replace(" to trolley", "").strip()
                        if not productName:
                            try:
                                row = locator.locator("xpath=ancestor::li[1] | ancestor::article[1]").first
                                productName = row.inner_text(timeout=800).strip().split("\n")[0]
                            except Exception:
                                pass

                        logger.info(
                            f"Found Add button via '{selector}' at scroll step {scrollStep}"
                            + (f" — product: {productName}" if productName else "")
                        )
                        locator.scroll_into_view_if_needed()
                        self._dismissOnetrust()
                        locator.click()
                        self.page.wait_for_load_state("domcontentloaded")
                        self.page.wait_for_timeout(3000)
                        return productName
                except Exception:
                    continue

        raise RuntimeError(
            "No 'Add' button found on the Groceries page after scrolling. "
            "The page layout may have changed."
        )

    # ------------------------------------------------------------------ #
    #  Assertions
    # ------------------------------------------------------------------ #

    def assertOnGroceriesPage(self) -> None:
        """Verify we have landed on the Groceries SPA.
        Uses URL check first (reliable), then tries to find any search input as
        a secondary signal — tolerates layout changes on the live site.
        """
        logger.info("Asserting Groceries page is loaded")

        self.page.wait_for_url(self.groceriesUrlPattern, timeout=self.timeout)
        logger.info(f"Groceries URL confirmed: {self.page.url}")

        searchSelectors = [
            "input[placeholder=\"Search Sainsbury's\"]",
            "input[type='search']",
            "input[data-testid*='search']",
            "input[name='search']",
            "header",
        ]
        for selector in searchSelectors:
            try:
                self.page.locator(selector).first.wait_for(state="visible", timeout=2000)
                logger.info(f"Groceries page element confirmed via: {selector}")
                return
            except Exception:
                continue
        logger.warning("Could not confirm a specific Groceries element, but URL matched — proceeding")
