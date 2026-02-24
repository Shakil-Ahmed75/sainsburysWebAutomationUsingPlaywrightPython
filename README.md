# Sainsbury's Web Automation Framework

A Playwright + Python test automation framework for [sainsburys.co.uk](https://www.sainsburys.co.uk), built on the **Page Object Model (POM)** pattern.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| [Playwright](https://playwright.dev/python/) | Browser automation |
| [pytest](https://pytest.org/) | Test runner |
| [Allure](https://allurereport.org/) | HTML reporting |
| [PyYAML](https://pyyaml.org/) | Config management via `config.yaml` |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable loading |
| GitHub Actions | CI/CD pipeline |

---

## Project Structure

```
sainsburysWebAutomationUsingPlaywrightPython/
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD pipeline
├── config/
│   ├── config.yaml          # Environment configs (dev / staging / prod)
│   └── settings.py          # Typed config loader
├── pages/
│   ├── basePage.py          # Reusable base class for all POMs
│   ├── homePage.py          # Home page POM
│   ├── groceriesPage.py     # Groceries page POM
│   └── loginPage.py         # Login page POM
├── tests/
│   └── e2e/
│       └── testLoginError.py  # Add-to-trolley → login error flow
├── utils/
│   ├── helpers.py           # Path helpers, random data generators
│   └── logger.py            # Centralised logging setup
├── reports/                 # Generated at runtime (git-ignored)
│   ├── screenshots/
│   ├── videos/
│   ├── traces/
│   ├── allure-results/
│   └── test_run.log
├── conftest.py              # Fixtures: browser, page, POMs, failure hooks
├── pytest.ini               # pytest configuration
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd sainsburysWebAutomationUsingPlaywrightPython

python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### 3. Run Tests

```bash
# Run all tests (dev environment, headed)
pytest

# Run against a specific environment
pytest --env=staging

# Run headless
pytest --headless=true

# Run with a different browser
pytest --browser-type=firefox

# Generate and view Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## Environment Configuration

Set `TEST_ENV` in `.env` or pass `--env` to pytest:

| Env | Headless | Slow Mo |
|-----|----------|---------|
| `dev` | `false` | `100ms` |
| `staging` | `true` | `0ms` |
| `prod` | `true` | `0ms` |

All environment settings live in `config/config.yaml`.

---

## Test Markers

| Marker | Description |
|--------|-------------|
| `e2e` | Full end-to-end user flows |
| `auth` | Authentication-related tests |
| `regression` | Full regression suite |
| `slow` | Tests that take a long time to run |

```bash
pytest -m e2e
pytest -m auth
pytest -m "not slow"
```

---

## What Gets Captured on Failure

Configured in `config.yaml` under `reporting`:

- **Screenshot** — saved to `reports/screenshots/`
- **Video** — saved to `reports/videos/`
- **Playwright Trace** — saved to `reports/traces/` (open with `playwright show-trace <file.zip>`)
- **Log file** — `reports/test_run.log`

---

## Current Test Coverage

### `tests/e2e/testLoginError.py`

End-to-end scenario verifying the unauthenticated add-to-trolley flow:

1. Navigate to `sainsburys.co.uk`
2. Click the **Groceries** menu item
3. Scroll to a product and click **Add**
4. Verify the login page is displayed
5. Submit invalid credentials
6. Assert the exact error message is shown:
   > *"That email or password doesn't look right. Please try again or reset your password below. Too many failed attempts will lock your account."*

---

## CI/CD — GitHub Actions

The workflow at `.github/workflows/ci.yml` runs automatically:

| Trigger | What runs |
|---------|-----------|
| Push / PR to `main` or `develop` | Full E2E suite |
| Nightly at 02:00 UTC | Full E2E suite on Chromium |
| Manual (`workflow_dispatch`) | Choose environment (`dev` / `staging` / `prod`) and suite (`e2e` / `regression` / `all`) |

**Artifacts uploaded per run (retained 14 days):**
- Screenshots, traces, and HTML reports — one set per browser
- Allure results — merged and published to **GitHub Pages** on `main`

To trigger manually from the GitHub UI: **Actions → Sainsbury's UI Automation → Run workflow**.

---

## Adding New Pages

1. Create `pages/yourPage.py` extending `BasePage`
2. Define selectors as class-level constants
3. Add action and assertion methods
4. Register a pytest fixture in `conftest.py`
5. Write tests in `tests/`

---

## Adding New Tests

```python
import pytest
from pages.homePage import HomePage

@pytest.mark.e2e
class TestExample:
    def test_something(self, homePage: HomePage):
        homePage.open()
        homePage.assertPageLoaded()
```
