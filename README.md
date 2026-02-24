# Sainsbury's Web Automation Framework

A production-ready Playwright + Python test automation framework for [sainsburys.co.uk](https://www.sainsburys.co.uk), built on the **Page Object Model (POM)** pattern.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| [Playwright](https://playwright.dev/python/) | Browser automation |
| [pytest](https://pytest.org/) | Test runner |
| [Allure](https://allurereport.org/) | Rich HTML reporting |
| [pytest-html](https://pytest-html.readthedocs.io/) | Lightweight HTML reports |
| [pytest-xdist](https://pytest-xdist.readthedocs.io/) | Parallel test execution |
| [PyYAML](https://pyyaml.org/) | Config management |
| GitHub Actions | CI/CD pipeline |

---

## Project Structure

```
sainsburysWebAutomationUsingPlaywrightPython/
├── config/
│   ├── config.yaml          # Environment configs (dev/staging/prod)
│   └── settings.py          # Typed config loader
├── pages/
│   ├── base_page.py         # Reusable base class for all POMs
│   ├── home_page.py         # Home page POM
│   ├── search_results_page.py
│   ├── product_page.py
│   ├── trolley_page.py
│   └── login_page.py
├── tests/
│   └── e2e/                 # Full user flows
│       ├── test_search_flow.py
│       ├── test_add_to_trolley.py
│       └── test_login.py
├── utils/
│   ├── helpers.py           # Utility functions
│   └── logger.py            # Centralised logging setup
├── reports/                 # Generated at runtime (git-ignored)
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD pipeline
├── conftest.py              # Fixtures (browser, page, POMs, hooks)
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
# Edit .env with your settings
```

### 3. Run Tests

```bash
# E2E tests against staging, headless
pytest tests/e2e -m e2e --env=staging --headless=true

# Specific browser
pytest tests/e2e --browser-type=firefox --headless=true

# Parallel execution (4 workers)
pytest tests/e2e -n 4

# Generate Allure report
pytest tests/e2e --alluredir=reports/allure-results
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

---

## Test Markers

| Marker | Description |
|--------|-------------|
| `e2e` | Full end-to-end user flows |
| `auth` | Login/authentication tests |
| `regression` | Full regression suite |

```bash
# Run e2e tests
pytest -m e2e

# Exclude slow tests
pytest -m "not slow"

# Run auth tests
pytest -m auth
```

---

## Reporting

### Allure (recommended)

```bash
pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

### pytest-html

```bash
pytest tests/ --html=reports/html/report.html --self-contained-html
```

---

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

- **On every push / PR** → E2E tests
- **Nightly (02:00 UTC)** → Full E2E suite across Chromium, Firefox, WebKit
- **Manual trigger** → Choose environment + suite

Allure reports are automatically published to GitHub Pages on `main`.

---

## Adding New Pages

1. Create `pages/your_page.py` extending `BasePage`
2. Define selectors as class-level constants
3. Add action and assertion methods
4. Register a pytest fixture in `conftest.py`
5. Write tests in `tests/`

---

## Adding New Tests

```python
import pytest
from pages.home_page import HomePage

@pytest.mark.e2e
class TestExample:
    def test_something(self, home_page: HomePage):
        home_page.open()
        home_page.assert_page_loaded()
```
