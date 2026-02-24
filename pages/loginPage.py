import logging
from playwright.sync_api import Page, expect
from pages.basePage import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Page Object for Sainsbury's Login / Sign In Page.

    After clicking 'Add' on the Groceries page, unauthenticated users are
    redirected to:  https://account.sainsburys.co.uk/gol/login?login_challenge=...

    Selectors verified against live site Feb 2026:
      - Email    : input[type='email']  (name='username', id='username')
      - Password : input[type='password'] (id='password')
      - Submit   : button[type='submit']  (text = 'Log in')
      - Error    : [data-testid='notification-message']  (role='alert')
    """

    # ------------------------------------------------------------------ #
    #  Selectors
    # ------------------------------------------------------------------ #
    emailInput    = "input[type='email'], input[name='username'], input[id='username']"
    passwordInput = "input[type='password'], input[name='password'], input[id='password']"
    signInBtn     = "button[type='submit'], button:has-text('Log in'), button:has-text('Sign in')"
    errorMessage  = "[data-testid='notification-message']"
    pageHeading   = "h1"

    # URL pattern that matches both possible login domains
    loginUrlPattern = "**/login**"

    # Exact error text from the live site (U+2019 right single quotation mark)
    invalidCredentialsError = (
        "That email or password doesn\u2019t look right. "
        "Please try again or reset your password below. "
        "Too many failed attempts will lock your account."
    )

    def __init__(self, page: Page, baseUrl: str, timeout: int = 2000):
        super().__init__(page, baseUrl, timeout)

    # ------------------------------------------------------------------ #
    #  Navigation
    # ------------------------------------------------------------------ #

    def open(self) -> "LoginPage":
        self.navigate("/user/login")
        self.acceptCookies()
        return self

    def waitForLoginPage(self) -> None:
        """Wait for the login page URL — works for both sainsburys.co.uk and account.sainsburys.co.uk."""
        logger.info("Waiting for login page URL")
        self.page.wait_for_url(self.loginUrlPattern, timeout=self.timeout)
        self.page.wait_for_load_state("domcontentloaded")
        logger.info(f"Login page URL confirmed: {self.page.url}")

    # ------------------------------------------------------------------ #
    #  Actions
    # ------------------------------------------------------------------ #

    def enterEmail(self, email: str) -> None:
        logger.info(f"Entering email: {email}")
        self.fill(self.emailInput, email)

    def enterPassword(self, password: str) -> None:
        logger.info("Entering password")
        self.fill(self.passwordInput, password)

    def clickSignIn(self) -> None:
        logger.info("Clicking Sign In / Log in button")
        self._dismissOnetrust()
        self.page.locator(self.signInBtn).first.click()
        self.page.wait_for_timeout(500)

    def login(self, email: str, password: str) -> None:
        """Complete login flow."""
        self.enterEmail(email)
        self.enterPassword(password)
        self.clickSignIn()

    # ------------------------------------------------------------------ #
    #  Assertions
    # ------------------------------------------------------------------ #

    def assertLoginPageLoaded(self) -> None:
        """Verify email input, password input and submit button are all visible."""
        logger.info("Asserting Login page is loaded")
        self.assertVisible(self.emailInput)
        self.assertVisible(self.passwordInput)
        self.assertVisible(self.signInBtn)

    def assertErrorMessageDisplayed(self, expectedText: str = "") -> None:
        self.assertVisible(self.errorMessage)
        if expectedText:
            self.assertContainsText(self.errorMessage, expectedText)

    def assertInvalidCredentialsError(self) -> None:
        """Assert the exact error shown after a failed login attempt.

        Locator : getByTestId('notification-message')
        Expected: "That email or password doesn't look right. Please try again
                   or reset your password below. Too many failed attempts will
                   lock your account."
        """
        logger.info("Asserting invalid credentials error message is displayed")
        errorLocator = self.page.get_by_test_id("notification-message")
        expect(errorLocator).to_be_visible(timeout=self.timeout)
        expect(errorLocator).to_contain_text(self.invalidCredentialsError)
        logger.info(f"Error message validated: '{self.invalidCredentialsError}'")

    def assertNoErrorDisplayed(self) -> None:
        self.assertHidden(self.errorMessage)
