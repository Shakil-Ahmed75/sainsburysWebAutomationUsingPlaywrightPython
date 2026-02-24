import logging
from playwright.sync_api import Page
from pages.basePage import BasePage

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """Page Object for Sainsbury's Home Page (www.sainsburys.co.uk)."""

    # ------------------------------------------------------------------ #
    #  Selectors — verified against live site Feb 2026
    # ------------------------------------------------------------------ #
    searchInput      = "#term"
    groceriesNavLink = "nav a[href*='gol-ui/groceries']:not([href*='c:']):not([href*='oauth'])"
    signInLink       = "a:has-text('Sign in'), a[href*='login']"

    def __init__(self, page: Page, baseUrl: str, timeout: int = 30000):
        super().__init__(page, baseUrl, timeout)

    # ------------------------------------------------------------------ #
    #  Actions
    # ------------------------------------------------------------------ #

    def open(self) -> "HomePage":
        """Navigate to the Sainsbury's home page and dismiss cookie banner."""
        self.navigate("/")
        self.page.wait_for_timeout(3000)
        self.acceptCookies()
        return self

    def assertPageLoaded(self) -> None:
        """Verify the main search bar is visible — confirms the page loaded."""
        logger.info("Asserting Home page is loaded")
        self.assertVisible(self.searchInput)

    def clickGroceries(self) -> None:
        """Click the Groceries link in the top navigation bar."""
        logger.info("Clicking Groceries nav link")
        self.page.locator(self.groceriesNavLink).first.click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)
        self.acceptCookies()
        self.page.wait_for_timeout(2000)
        self.acceptCookies()

    def searchFor(self, query: str) -> "HomePage":
        """Type a query in the main search bar and press Enter."""
        logger.info(f"Searching for: '{query}'")
        self.fill(self.searchInput, query)
        self.pressEnter(self.searchInput)
        return self

    def clickSignIn(self) -> None:
        logger.info("Clicking Sign In link")
        self.click(self.signInLink)
