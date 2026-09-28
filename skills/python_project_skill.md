---
name: Python Project Skill
version: 1.0
description: >
  Set up and maintain a Python project's build, dependencies, and tooling:
  uv with a committed lockfile, pyproject.toml as the single config file,
  src layout, dependency groups, ruff for lint and format, strict mypy,
  pytest with coverage and warnings-as-errors, pip-audit, a locked CI, a
  wheel build, and a slim non-root Docker image. Every file here was run with
  uv, Python 3.14, and Docker on 2026-09-28. Language idioms live in
  python_advanced_skill.
applies_to: [python, packaging, uv, pyproject, build, ci, docker]
tags: [python, uv, pyproject, ruff, mypy, pytest, coverage, pip-audit, hatchling, docker]
---

# Python Project Skill — v1.0

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | Starting a Python project, adding tooling to one, fixing dependency or packaging problems, or containerising it — `implementer:build`, `implementer:pipeline`, `implementer:docker` |
| **Skip when** | Writing the Python code itself — `python_advanced_skill`. API routes — `backend_skill` |
| **Inputs** | Python version floor, app or library, runtime dependencies, where it deploys |
| **Produces** | `pyproject.toml`, `uv.lock`, `.python-version`, `src/` layout, tests, CI commands, `Dockerfile`, `.dockerignore` |
| **Steps** | 1. `uv init --package` (§1) → 2. Dependencies and groups (§2) → 3. Tool config in `pyproject.toml` (§3) → 4. CI with `--locked` (§4) → 5. Audit (§5) → 6. Build / image (§6, §7) |
| **Done when** | `uv sync --locked`, ruff, format check, `mypy`, and `pytest --cov` all pass in CI from a clean checkout |
| **Senior defaults** | One file: `pyproject.toml` — no `setup.py`, `setup.cfg`, `requirements.txt`, `.flake8` · commit `uv.lock`; CI uses `--locked` · src layout so tests run against the installed package · dev tools in `[dependency-groups]`, not runtime deps · `mypy --strict` from day one · pytest `filterwarnings = ["error"]` · secrets via `pydantic-settings` + `SecretStr` · image: two stages, `--no-dev`, non-root |
| **Load on demand** | §1 layout · §2 dependencies · §3 pyproject · §4 CI · §5 security · §6 packaging · §7 Docker · §8 troubleshooting |
| **Run report** | `html_report_skill` — adds: Dependency changes · Tool results (ruff, mypy, pytest, audit) |
| **Pairs with** | `python_advanced_skill`, `backend_skill`, `test_skill`, `project_setup_skill`, `security_audit_skill` |

---

## 1. Layout

```bash
uv init --package --build-backend hatch orders   # src layout, console script, hatchling
cd orders
uv add "pydantic>=2.13" "pydantic-settings>=2.15"
uv add --dev pytest pytest-cov pytest-randomly hypothesis ruff mypy pip-audit
```

```text
orders/
├── pyproject.toml     ← dependencies AND every tool's config
├── uv.lock            ← exact versions for every platform — commit it
├── .python-version    ← the interpreter uv uses locally
├── src/orders/        ← the package; importable only once installed
│   ├── __init__.py
│   ├── money.py
│   ├── settings.py
│   └── cli.py
├── tests/
├── Dockerfile
└── .dockerignore
```

**Why `src/`**: with a flat layout, `import orders` in tests picks up the
working directory, so tests pass even when the packaged wheel is missing a
module. With `src/`, tests import the installed package — what users get.

## 2. Dependencies

| Kind | Where | Rule |
|---|---|---|
| Runtime | `[project] dependencies` | Lower bounds (`>=2.13`); no upper caps in an app — the lockfile pins |
| Development | `[dependency-groups] dev` | Test, lint, type-check, audit tools. Never shipped |
| Optional features of a library | `[project.optional-dependencies]` | `pip install orders[postgres]` |
| Exact versions | `uv.lock` | Generated. Never edit by hand |

```bash
uv add httpx                   # adds to dependencies, updates uv.lock, syncs .venv
uv add --dev respx             # dev group
uv lock --upgrade-package httpx # upgrade one package deliberately
uv tree                        # who depends on what
```

A **library** publishes to others: keep bounds wide (`>=`), test against the
lowest supported versions too. An **application** is deployed: the lockfile is
the contract.

## 3. `pyproject.toml`

The exact file from the verified example — ruff clean, `mypy --strict` clean,
6 tests passing in random order with warnings as errors, 100% branch coverage.

```toml
[project]
name = "orders"
version = "0.1.0"
description = "Order totals and settings — example for python_project_skill"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.13",
    "pydantic-settings>=2.15",
]

[project.scripts]
orders = "orders.cli:main"

[dependency-groups]
dev = [
    "pytest>=9.1",
    "pytest-cov>=7.1",
    "pytest-randomly>=5.0",
    "hypothesis>=6.168",
    "ruff>=0.16",
    "mypy>=2.3",
    "pip-audit>=2.10",
]

[build-system]
requires = ["hatchling>=1.32"]
build-backend = "hatchling.build"

# ---------------------------------------------------------------- ruff
[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E", "W",   # pycodestyle
    "F",        # pyflakes
    "I",        # isort
    "B",        # bugbear — includes B006 mutable defaults
    "UP",       # pyupgrade
    "SIM",      # simplify
    "S",        # bandit security checks
    "RUF",      # ruff-specific
    "PT",       # pytest style
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]   # assert is how pytest works

# ---------------------------------------------------------------- mypy
[tool.mypy]
strict = true
python_version = "3.12"
plugins = ["pydantic.mypy"]
files = ["src", "tests"]

# ---------------------------------------------------------------- pytest
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--import-mode=importlib",
]
xfail_strict = true
filterwarnings = ["error"]

# ---------------------------------------------------------------- coverage
[tool.coverage.run]
branch = true
source = ["orders"]

[tool.coverage.report]
fail_under = 90
show_missing = true
skip_covered = true
exclude_also = ["if TYPE_CHECKING:", "raise NotImplementedError"]
```

| Setting | Why |
|---|---|
| ruff `S` (bandit) | Catches `subprocess(shell=True)`, hard-coded passwords, `pickle` on untrusted input |
| ruff `B` | Includes B006, mutable default arguments |
| `mypy strict` + `pydantic.mypy` | Types checked everywhere; Pydantic models understood |
| `--strict-markers`, `--strict-config` | A typo in a marker or config key fails instead of being ignored |
| `--import-mode=importlib` | No `sys.path` insertion — tests cannot import the package by accident |
| `filterwarnings = ["error"]` | A `DeprecationWarning` fails the suite today, not the upgrade in six months |
| coverage `branch = true`, `fail_under` | Both sides of every `if`; a gate, not a report |

Settings from the environment, secrets masked:

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Values come from ORDERS_* environment variables or a local .env file."""

    model_config = SettingsConfigDict(env_prefix="ORDERS_", env_file=".env")

    database_url: str = "sqlite:///orders.db"
    api_token: SecretStr
```

The example test asserts the token never appears in `repr(settings)`.
Add `.env` to `.gitignore` and `.dockerignore`.

## 4. CI

```bash
uv sync --locked                 # fails if uv.lock does not match pyproject.toml
uv run ruff check
uv run ruff format --check
uv run mypy
uv run pytest --cov
```

`--locked` is the point: verified on the example, adding a dependency to
`pyproject.toml` without re-locking made `uv sync --locked` fail with
*"The lockfile at `uv.lock` needs to be updated, but `--locked` was provided."*
Cache `~/.cache/uv` keyed on `uv.lock`.

Locally, the same checks run on commit through `pre-commit` (ruff and ruff-format
hooks), so CI rarely finds what the developer could have.

## 5. Dependency Security

```bash
uv export --format requirements-txt --no-emit-project -o requirements-audit.txt
uv run pip-audit -r requirements-audit.txt --disable-pip
```

`--disable-pip` audits the exact locked versions without installing anything;
it requires the hashes that `uv export` writes by default (without them
pip-audit refuses: *"--disable-pip flag can only be used with a hashed
requirements files"*). Run it in CI and on a schedule — new CVEs appear for
versions you already ship.

## 6. Packaging

```bash
uv build            # dist/orders-0.1.0-py3-none-any.whl and .tar.gz
uv publish          # prefer trusted publishing from CI over API tokens
```

Version once, in `[project] version`. Console scripts in `[project.scripts]`;
`uv run orders 1.50 2.25` ran the example's entry point.

## 7. Docker

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /app
# dependencies first: this layer is cached until uv.lock changes
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY README.md ./
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

FROM python:3.13-slim
RUN useradd --create-home --uid 10001 app
COPY --from=build --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
USER app
ENTRYPOINT ["orders"]
```

```text
.venv
dist
.git
__pycache__
.mypy_cache
.ruff_cache
.pytest_cache
.coverage
.env
```

Verified: the image printed the right total, ran as uid 10001, held only the
virtual environment under `/app` (no source tree), contained none of pytest,
ruff, or mypy, and was 153 MB. The dependency layer is rebuilt only when
`uv.lock` changes. Pin the uv image tag, as with any base image.

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Tests pass locally, the installed package fails with `ModuleNotFoundError` | Flat layout — tests imported the working directory | `src/` layout; `--import-mode=importlib` |
| `uv sync --locked` fails in CI | `pyproject.toml` changed without `uv lock` | Run `uv lock`, commit `uv.lock` |
| Resolution fails after adding a package | Incompatible bounds | `uv tree`, then relax the lower bound or pin the shared dependency |
| Different results on the CI Python | `.python-version` and `requires-python` disagree | Test the floor version in CI too |
| Suite fails on a `DeprecationWarning` after an upgrade | `filterwarnings = ["error"]` doing its job | Fix the call site; ignore a specific warning by message only if the fix is upstream |
| Image contains pytest or ruff | Missing `--no-dev` | `uv sync --locked --no-dev` in the build stage |

## 9. Checklist

✅ `pyproject.toml` is the only config file; `uv.lock` committed
✅ `src/` layout; console scripts declared
✅ Runtime and dev dependencies separated; dev tools in `[dependency-groups]`
✅ ruff (with `B`, `S`, `UP`), ruff format, `mypy --strict` pass
✅ pytest strict markers/config, warnings as errors, random order, branch coverage gate
✅ CI uses `uv sync --locked`
✅ `pip-audit` on the locked set, in CI and scheduled
✅ Secrets from the environment via `SecretStr`; `.env` ignored by git and Docker
✅ Image: two stages, `--no-dev`, non-root, pinned base and uv tags
