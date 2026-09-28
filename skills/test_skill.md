---
name: Comprehensive Testing Skill
version: 2.0
description: >
  Generate and run unit, integration, contract, and E2E tests with coverage and
  mutation reporting. AAA structure, given/when/then naming, deterministic
  tests, real dependencies at integration level, property-based tests for
  invariants, and mutation testing to prove the suite actually catches bugs.
applies_to: [java, python, typescript, react, testing]
tags: [testing, pytest, junit5, vitest, jest, playwright, testcontainers, property-based, mutation-testing]
---

# Comprehensive Testing Skill — v2.0

## Quick Card

> Read this card first. Load a numbered section only when the task needs it.

| | |
|---|---|
| **Use when** | New or changed code needs tests, or `implementer:test` / `implementer:full` / `quality:qa mode=generate` runs |
| **Skip when** | Planning scenarios only — `quality:qa` without `mode=generate` writes scenario rows, not test code |
| **Inputs** | The code under test, acceptance criteria (`AC-<REQ-n>.<m>`), coverage targets |
| **Produces** | `tests/unit/`, `tests/integration/`, `tests/e2e/`, coverage report; every AC mapped to a named test |
| **Steps** | 1. Map each AC to a test → 2. Unit-test logic with AAA → 3. Integration-test real boundaries → 4. E2E the critical journeys only → 5. Run coverage + mutation → 6. Fix gaps |
| **Done when** | All green, every AC has a test, coverage ≥ targets (§7), no test depends on time, order, or network luck |
| **Senior defaults** | Fakes over mocks for code you own · Testcontainers over H2/SQLite for DB tests · property tests for invariants · `userEvent.setup()`, query by role · no `sleep` — wait on conditions · mutation score, not line coverage, proves a suite |
| **Load on demand** | §1 pyramid · §2 anatomy · §3 backend · §4 frontend · §5 advanced · §6 determinism · §7 coverage · §8 commands |
| **Run report** | `html_report_skill` — adds: AC → test map · Coverage by layer · Mutation score |
| **Pairs with** | `python_advanced_skill`, `java_advanced_skill`, `react_advanced_skill`, `spec_driven_development_skill`, `traceability_skill` (T-6) |

---

## 1. Strategy — What Each Layer Proves

| Layer | Proves | Real or doubled | Share of suite | Location |
|---|---|---|---|---|
| Unit | Logic and edge cases of one unit | Collaborators faked | Most | `tests/unit/` |
| Integration | The unit works with the real DB, queue, HTTP client | Real, via Testcontainers | Some | `tests/integration/` |
| Contract | Two services agree on a request/response shape | Consumer-driven contract | At each service boundary | `tests/contract/` |
| E2E | A user journey works through the deployed stack | Nothing doubled | Few — critical paths only | `tests/e2e/` |

Push each check to the lowest layer that can prove it. An E2E test for a
validation rule is slow, flaky, and says nothing a unit test would not.

## 2. Test Anatomy

**AAA, every test** (master RULE 2):

```python
def test_given_existing_email_when_register_then_raises_duplicate():
    # Arrange
    service = UserService(InMemoryUserRepository())
    service.register("a@example.com", "hash")
    # Act / Assert
    with pytest.raises(DuplicateEmailError):
        service.register("a@example.com", "hash")
```

**Names state behaviour**: `given<State>_when<Action>_then<Outcome>` (Java),
`test_given_…_when_…_then_…` (Python), `it('shows error when API returns 500')` (JS).

**One behaviour per test.** Several asserts are fine if they describe one outcome.

**Minimum per unit** (RULE 2): happy path · edge case (empty, null) · error path · boundaries (0, −1, max, min).

## 3. Backend

### pytest

```python
# tests/unit/test_user_service.py
import pytest

from src.services.user_service import DuplicateEmailError, UserService
from tests.fakes import InMemoryUserRepository


@pytest.fixture
def service() -> UserService:
    return UserService(InMemoryUserRepository())


def test_given_new_email_when_register_then_returns_user_with_id(service):
    user = service.register("test@example.com", "hashed")

    assert user.email == "test@example.com"
    assert user.id is not None


def test_given_existing_email_when_register_then_raises_duplicate(service):
    service.register("test@example.com", "hashed")

    with pytest.raises(DuplicateEmailError):
        service.register("test@example.com", "hashed")


@pytest.mark.parametrize("email", ["", " ", "no-at-sign", "a@", "@b.com"])
def test_given_malformed_email_when_register_then_raises_value_error(service, email):
    with pytest.raises(ValueError):
        service.register(email, "hashed")
```

A hand-written fake (`InMemoryUserRepository`) exercises the real contract;
a `Mock()` only checks that you called what you expected to call. Reserve
mocks for code you do not own and cannot run.

### JUnit 5

```java
@ParameterizedTest
@ValueSource(strings = {"", " ", "no-at-sign", "a@", "@b.com"})
void givenMalformedEmail_whenRegister_thenThrowsIllegalArgument(String email) {
    var service = new UserService(new InMemoryUserRepository());

    assertThatThrownBy(() -> service.register(email, "hashed"))
        .isInstanceOf(IllegalArgumentException.class);
}
```

## 4. Frontend

### Component tests — Vitest (or Jest) + React Testing Library

```typescript
// tests/components/LoginForm.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '../components/LoginForm';

it('calls onSuccess when submitted with valid credentials', async () => {
  const user = userEvent.setup();
  const handleSuccess = vi.fn();
  render(<LoginForm onSuccess={handleSuccess} />);

  await user.type(screen.getByLabelText(/email/i), 'test@example.com');
  await user.type(screen.getByLabelText(/password/i), 'password123');
  await user.click(screen.getByRole('button', { name: /log in/i }));

  expect(handleSuccess).toHaveBeenCalledOnce();
});
```

- `userEvent` comes from `@testing-library/user-event`, not `@testing-library/react`. Call `userEvent.setup()` once per test.
- Query as a user would: `getByRole` → `getByLabelText` → `getByText`. `getByTestId` is the last resort.
- Every data-driven component gets three more tests: loading, error, empty (see `react_advanced_skill` §5).
- Stub the network at the boundary with MSW, not by mocking `fetch` inside components.

### E2E — Playwright

Only the journeys that would page someone: sign-in, checkout, the one flow the business runs on.
Use web-first assertions (`await expect(page.getByRole('alert')).toBeVisible()`), which retry — never `waitForTimeout`.

## 5. Advanced Techniques

| Technique | Use it for | Tools |
|---|---|---|
| **Property-based** | Invariants over all inputs: round-trips, idempotency, ordering, totals | Hypothesis · jqwik · fast-check |
| **Real dependencies** | DB queries, migrations, message consumers — anything a fake would lie about | Testcontainers (Java, Python, Node) |
| **Contract** | Service A and B agree on a shape without a shared environment | Pact · Spring Cloud Contract |
| **Mutation** | Measuring whether the suite catches bugs, not just runs lines | mutmut · PIT · Stryker |
| **Snapshot** | Only for stable, reviewed output (serialised API payloads) — never whole component trees | built into Jest/Vitest |

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=0, max_value=10_000)))
def test_given_any_line_items_when_total_then_equals_sum_and_never_negative(amounts):
    order = Order(items=[Item(price_cents=a) for a in amounts])

    assert order.total_cents() == sum(amounts)
    assert order.total_cents() >= 0
```

## 6. Determinism

A flaky test is a failing test. Control every source of nondeterminism:

| Source | Control |
|---|---|
| Time | Inject a clock (`Clock` in Java, a `now` parameter or `freezegun`/`time-machine` in Python, `vi.useFakeTimers()` in JS) |
| Randomness | Seed it, or inject the generator |
| Network | Fake at the boundary (MSW, WireMock, `respx`); real only in integration via Testcontainers |
| Order | Tests share no state; each builds its own fixtures. Run with random order (`pytest-randomly`) to prove it |
| Waiting | Wait on a condition, never `sleep` / `Thread.sleep` / `waitForTimeout` |

A test that flakes is quarantined the same day, with an issue, and fixed or deleted within the sprint.

## 7. Coverage

| Layer | Floor |
|---|---|
| Backend (line + branch) | ≥ 95% |
| Frontend components | ≥ 85% |
| Acceptance criteria | 100% — every `AC-<REQ-n>.<m>` maps to a named test (`traceability_skill` T-6) |

Coverage is a floor, not a goal: a test with no assertion still covers its lines.
Where mutation testing is set up, a surviving mutant in changed code is a missing test.

## 8. Commands

```bash
# Backend
pytest tests/ -v -p randomly --cov=src --cov-branch --cov-report=term-missing --cov-report=html
mutmut run --paths-to-mutate src/             # changed modules only in CI

# Java
mvn verify                                     # JUnit 5 + JaCoCo
mvn org.pitest:pitest-maven:mutationCoverage

# Frontend
npx vitest run --coverage
npx stryker run

# E2E
npx playwright test
```

## 9. Checklist

✅ Every acceptance criterion maps to a named test
✅ AAA structure; names state given / when / then
✅ Happy path, edge, error, and boundary cases per unit
✅ Fakes for owned code; mocks only for code you cannot run
✅ Integration tests hit real dependencies (Testcontainers), not in-memory stand-ins
✅ No `sleep`; time, randomness, and network controlled
✅ Suite passes in random order
✅ Coverage floors met; no assertion-free tests
✅ Frontend: loading, error, and empty states tested; queries by role
✅ E2E limited to critical journeys
