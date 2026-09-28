# Contributing to awesome-prompts

Thank you for your interest in contributing! This guide explains how to set up your environment, run tests, and submit changes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you start, ensure you have:

- **Git** (for cloning and version control)
- **Python 3.11+** (for Python tests and tools)
- **Node.js 20+** (for archify and TypeScript tests)
- **npm** (comes with Node.js)

Check your versions:

```bash
git --version
python --version
node --version
npm --version
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sharmapuneet1510/awesome-prompts.git
cd awesome-prompts
```

### 2. Install Python Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov
```

### 3. Install Node/TypeScript Dependencies

```bash
cd archify
npm install
cd ..
```

---

## Running Tests

### Python Tests

Run all Python tests:

```bash
pytest tests/ -v
```

Run a specific test file:

```bash
pytest tests/test_token_optimizer.py -v
```

Run with coverage report:

```bash
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html to view coverage
```

Run a single test:

```bash
pytest tests/test_token_optimizer.py::test_name -v
```

### TypeScript/Node Tests

Navigate to archify and run tests:

```bash
cd archify
npm test
cd ..
```

### Archify Schema Validation

Validate all example diagrams:

```bash
cd archify
for file in examples/*.json; do
  echo "Validating $file..."
  cat "$file" | node bin/archify.mjs validate
done
cd ..
```

### All Tests (CI-like)

Run everything locally before submitting a PR:

```bash
# Python tests
pytest tests/ -v --cov=.

# TypeScript tests
cd archify && npm test && cd ..

# Archify validation
cd archify
for file in examples/*.json; do
  cat "$file" | node bin/archify.mjs validate || exit 1
done
cd ..

echo "✅ All tests passed"
```

---

## Making Changes

### Create a Feature Branch

```bash
git checkout -b feat/your-feature-name
# or for bug fixes:
git checkout -b fix/bug-description
```

### Conventional Commit Messages

Use clear, descriptive commit messages following this format:

```
<type>(<scope>): <subject>

<body (optional)>

Fixes #<issue-number>
```

**Types:**
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation
- `refactor` — code refactoring (no feature change)
- `test` — adding tests
- `chore` — build, dependencies, etc.

**Examples:**

```bash
git commit -m "feat(archify): add PNG export support"
git commit -m "fix(validator): handle edge case in sequence ordering"
git commit -m "docs: add setup instructions to CONTRIBUTING.md"
```

### Write Tests

If you add features or fix bugs, include tests:

**Python:**
```bash
# Create test file in tests/
# Name it test_feature.py
# Follow existing patterns
pytest tests/test_feature.py -v
```

**TypeScript:**
```bash
# Update archify/tests/validator.test.ts
npm test --prefix archify
```

### Update Documentation

If your change affects user-facing behavior:
- Update relevant `.md` files in `docs/`
- Update `ARCHIFY.md` if it's diagram-related
- Update inline code comments

---

## Submitting Changes

### Before You Submit

1. ✅ All tests pass locally
2. ✅ Code is linted and formatted
3. ✅ Commit messages are clear
4. ✅ You've tested edge cases
5. ✅ Documentation is updated

### Create a Pull Request

1. Push your branch:

```bash
git push origin feat/your-feature-name
```

2. Open a PR on GitHub:
   - Title: Clear, concise description
   - Description: Why this change? Link related issues (#123)
   - Include test results in description

3. Wait for CI to pass:
   - Python tests (3.11, 3.12)
   - TypeScript tests (Node 20, 22)
   - Schema validation (archify examples)
   - Security checks (trivy)

4. Address review feedback:
   - Push new commits to update the PR
   - Comment on review notes
   - Resolve conversations once addressed

---

## Code Style

### Python

Follow PEP 8:
```bash
# Check style
pylint your_file.py

# Auto-format
black your_file.py
```

Key rules:
- 4 spaces for indentation (not tabs)
- Max line length: 100 characters
- Use type hints where possible
- Write docstrings for functions/classes

### TypeScript

Follow the archify conventions:
```bash
cd archify
npm run lint
npm run format
```

Key rules:
- 2 spaces for indentation
- Use `const` by default (not `let` or `var`)
- Use arrow functions for callbacks
- Write JSDoc comments for exported functions
- No `any` types (use proper TypeScript types)

### JSON

Keep JSON clean:
- 2 spaces for indentation
- Alphabetical key order when helpful
- Comments only in documentation (not in actual JSON files)

---

## Troubleshooting

### Issue: Python tests import errors

**Problem:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Node tests fail but npm install succeeded

**Problem:** Stale node_modules

**Solution:**
```bash
cd archify
rm -rf node_modules package-lock.json
npm install
npm test
cd ..
```

### Issue: Archify validation fails on examples

**Problem:** `cat examples/architecture-example.json | node bin/archify.mjs validate` returns errors

**Solution:**
```bash
# Check if schema.ts exists
ls archify/schema/schema.ts

# Rebuild if needed
npm run build --prefix archify

# Revalidate
cat archify/examples/architecture-example.json | node archify/bin/archify.mjs validate
```

### Issue: git commit fails with hook errors

**Problem:** Pre-commit or commit hooks are failing

**Solution:**
```bash
# Check .git/hooks/
ls -la .git/hooks/

# If hooks are preventing commits, review them first
# Then proceed with:
git commit --no-verify  # Only if you're sure it's safe
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Run all Python tests | `pytest tests/ -v` |
| Run archify tests | `npm test --prefix archify` |
| Check Python coverage | `pytest tests/ --cov=.` |
| Format Python code | `black .` |
| Format TypeScript | `npm run format --prefix archify` |
| Validate archify examples | `cd archify && for f in examples/*.json; do cat "$f" \| node bin/archify.mjs validate; done` |
| Create feature branch | `git checkout -b feat/name` |
| Push changes | `git push origin feat/name` |

---

## Questions or Issues?

- Check [existing issues](https://github.com/sharmapuneet1510/awesome-prompts/issues)
- Open a [new issue](https://github.com/sharmapuneet1510/awesome-prompts/issues/new) with details
- Start a [discussion](https://github.com/sharmapuneet1510/awesome-prompts/discussions)

---

## Code of Conduct

Be respectful, inclusive, and constructive. We value all contributions!

---

Thank you for contributing! 🎉
