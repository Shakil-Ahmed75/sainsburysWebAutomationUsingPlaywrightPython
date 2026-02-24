import logging

import pytest

from pages.groceriesPage import GroceriesPage
from pages.homePage import HomePage
from pages.loginPage import LoginPage
from utils.helpers import generateRandomEmail, generateRandomPassword

logger = logging.getLogger(__name__)


@pytest.mark.e2e
class TestAddToTrolleyLoginError:
    """
    TC:001 Verify user is redirected to login page when adding product
           and receives error for invalid credentials

    Steps:
      1. Navigate to https://www.sainsburys.co.uk/
      2. Click the 'Groceries' menu item in the top navigation
      3. On the Groceries page, scroll down to reveal products
      4. Click the 'Add' button for any product
      5. Verify that the login page is displayed
      6. Enter an invalid email and password
      7. Click the Login / Sign In button
      8. Validate the exact error message:
         "That email or password doesn't look right. Please try again or
          reset your password below. Too many failed attempts will lock
          your account."
    """

    @pytest.mark.parametrize("tc_id", ["TC:001"], ids=["TC:001"])
    def test_addProductTriggersLoginAndInvalidCredentialsError(
        self,
        tc_id: str,
        homePage: HomePage,
        groceriesPage: GroceriesPage,
        loginPage: LoginPage,
    ) -> None:
        logger.info(f"[{tc_id}] Verify user is redirected to login page when adding product and receives error for invalid credentials")

        invalidEmail    = generateRandomEmail()
        invalidPassword = generateRandomPassword()
        logger.info(f"Invalid test email    : {invalidEmail}")
        logger.info("Invalid test password : [generated — not logged]")

        # ------------------------------------------------------------------ #
        # Step 1 — Navigate to https://www.sainsburys.co.uk/
        # ------------------------------------------------------------------ #
        logger.info("Step 1: Navigating to Sainsbury's home page")
        homePage.open()
        homePage.assertPageLoaded()

        # ------------------------------------------------------------------ #
        # Step 2 — Click the 'Groceries' menu item
        # ------------------------------------------------------------------ #
        logger.info("Step 2: Clicking Groceries menu item")
        homePage.clickGroceries()
        groceriesPage.assertOnGroceriesPage()

        # ------------------------------------------------------------------ #
        # Step 3 & 4 — Scroll down on Groceries page and click Add
        # ------------------------------------------------------------------ #
        logger.info("Step 3 & 4: Scrolling Groceries page and clicking Add")
        productName = groceriesPage.scrollAndClickAddButton()
        if productName:
            logger.info(f"Add button clicked for product: '{productName}'")
        else:
            logger.info("Add button clicked (product name not captured)")

        # ------------------------------------------------------------------ #
        # Step 5 — Verify the login page is displayed
        #   Redirect goes to: account.sainsburys.co.uk/gol/login?login_challenge=...
        # ------------------------------------------------------------------ #
        logger.info("Step 5: Verifying login page is displayed")
        loginPage.waitForLoginPage()
        loginPage.acceptCookies()
        loginPage.assertLoginPageLoaded()

        # ------------------------------------------------------------------ #
        # Step 6 — Enter an invalid email and password
        # ------------------------------------------------------------------ #
        logger.info("Step 6: Entering invalid email and password")
        loginPage.enterEmail(invalidEmail)
        loginPage.enterPassword(invalidPassword)

        # ------------------------------------------------------------------ #
        # Step 7 — Click the Login button
        # ------------------------------------------------------------------ #
        logger.info("Step 7: Clicking the Log in button")
        loginPage.clickSignIn()

        # ------------------------------------------------------------------ #
        # Step 8 — Validate the exact error message
        #   Locator : getByTestId('notification-message')
        #   Expected: "That email or password doesn't look right..."
        # ------------------------------------------------------------------ #
        logger.info("Step 8: Validating the invalid-credentials error message")
        loginPage.assertInvalidCredentialsError()
        logger.info(
            "PASS — Error message confirmed: "
            f"'{loginPage.invalidCredentialsError}'"
        )
