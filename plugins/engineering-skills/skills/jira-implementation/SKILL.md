---
name: jira-implementation
description: '"Implement PROJ-123" — one Jira ticket, end to end, to a PR ready to merge. `implementer:full`, `orchestrator:build`'
---

# Jira Implementation Skill — v1.0

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | "Implement PROJ-123" — one Jira ticket, end to end, to a PR ready to merge. `implementer:full`, `orchestrator:build` |
| **Skip when** | Many tickets into one spec — `jira_incremental_spec_generator_skill`. Writing tickets — `ba_create_skill`. Backlog report — `jira_html_report_skill` |
| **Inputs** | Ticket key; Jira access (Atlassian MCP server or REST API token); a git repository with `AGENTS.md` or a known build command |
| **Produces** | Branch, code + tests, ADR / spec where the class needs them, PR with the criteria matrix, Jira comment + transitions, run report |
| **Steps** | 1. Read the ticket (§1) → 2. Classify and route (§2) → 3. Pass the gates (§3) → 4. Implement test-first (§4) → 5. Verify (§5) → 6. PR (§6) → 7. Write back to Jira (§7) |
| **Done when** | Every acceptance criterion maps to a passing named test; the build command is green; PR open and reviewed; ticket *In Review* with the PR linked — *Done* only after a human merges |
| **Senior defaults** | No testable acceptance criteria, no code — send it back · the ticket's class decides the gates, not its size estimate · one criterion → at least one test, written first and seen failing · the ticket key in the branch, every commit, and the PR title · scope that grows past the ticket becomes a new ticket, not a bigger PR · confirm every Jira write · never merge, never mark *Done* before the merge |
| **Load on demand** | §0 access · §1 read · §2 classify · §3 gates · §4 implement · §5 verify · §6 PR · §7 write-back · §8 stop conditions · §9 anti-patterns |
| **Run report** | `html_report_skill` — adds: Criteria matrix (AC → test → result) · Jira writes (what, when, confirmed by) · Gates passed |
| **Pairs with** | `spec_driven_development_skill`, `adr_skill`, `test_skill`, `debugging_skill`, `project_setup_skill`, `database_skill`, `traceability_skill`, `code_review_skill` |

---

## 0. Jira Access

Use whichever the environment provides; do not ask the user for a token if an
MCP server is already connected.

| Access | Read | Write |
|---|---|---|
| Atlassian MCP server | its issue-fetch tool | its comment and transition tools |
| REST API v3 (`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` in the environment) | `GET /rest/api/3/issue/{key}?expand=renderedFields` | `POST /rest/api/3/issue/{key}/comment` · `GET` then `POST /rest/api/3/issue/{key}/transitions` |

```bash
curl -sf -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123?expand=renderedFields" > .jira/PROJ-123.json
```

- The token never appears in commands you print, logs, the PR, or the run report.
- Transition IDs differ per workflow — list them with `GET …/transitions` and pick by name; never hard-code an ID.
- Cache the ticket under `.jira/` (git-ignored) so later steps do not re-fetch it.

## 1. Read the Ticket

Collect, in this order:

| Field | Why |
|---|---|
| Summary, description | What is asked |
| Acceptance criteria (a field or a section of the description) | What "done" means — the tests come from here |
| Issue type, labels, components | Input to §2 |
| Linked issues (blocks / is blocked by / relates) | A blocking ticket not *Done* stops the run (§8) |
| Parent epic, subtasks | Context; subtasks may already split the work |
| Comments, newest first | Late decisions often live here, not in the description |
| Attachments (designs, samples) | Read them; note what could not be read |

Write the result to `docs/tickets/PROJ-123.md`, labelled per RULE 12:

```markdown
# PROJ-123 — <summary>

**Type:** Story · **Class:** feature (§2) · **Branch:** feature/PROJ-123-<slug>

## Acceptance Criteria
| ID | Criterion (Given / When / Then) | Source |
|---|---|---|
| AC1 | Given a cart with items, when checkout is retried within 60 s, then only one charge is created | description |
| AC2 | Given a failed charge, when the user retries, then a new charge is attempted | comment 2026-09-20 |

## Facts from the ticket
FACT: <quoted or paraphrased, with the field it came from>

## Assumptions
INFERENCE: <what you are assuming and why> — confirm before §4

## Open questions
- <question> — blocks AC<n>
```

**The testability check.** Each criterion must name an observable outcome a
test can assert. "Checkout should be robust" is not testable; "a retried
checkout creates one charge" is. If any criterion fails the check, or there
are none, stop and hand the open questions to `ba:clarify` — do not invent
criteria and implement them.

## 2. Classify and Route

The class decides which skills load and which gates apply. A ticket can be
more than one class (a feature that needs a column is *feature* + *schema
change*) — apply every matching row.

| Class | Signals | Load | Gates (§3) |
|---|---|---|---|
| **New project** | No repository yet, or no build; "set up", "bootstrap", "new service" | `project_setup_skill` + `maven_skill` or `python_project_skill` | Setup files approved |
| **Schema change** | New table or column, index, migration, data backfill | `database_skill`; `mssql_advanced_skill` on SQL Server | `Database` ADR; expand → migrate → contract plan |
| **Feature** | Story; new behaviour | Language skill (`java_advanced_skill`, `python_advanced_skill`, `react_advanced_skill`), `backend_skill` / `frontend_skill`, `test_skill` | Spec chain (RULE 11); ADR if a contract, dependency, or failure mode changes (RULE 11a) |
| **Bug** | Bug type; "fails", "wrong", stack trace | `debugging_skill`, `test_skill` | Reproduced by a failing test before any fix |
| **Chore** | Dependency bump, config, rename, docs | The build skill for the stack | None beyond the build — RULE 11 exempts trivial work |

Write the class and the reason into `docs/tickets/PROJ-123.md`. If the
signals disagree (a "bug" that is really missing behaviour), classify by what
the code change will be and say so.

## 3. Gates

Run only the gates the class requires, in this order. Each gate ends with an
explicit user approval; "looks fine" to a summary is not approval of a file
the user has not seen.

1. **Blockers** — every *is blocked by* link is *Done*. If not, stop (§8).
2. **Analysis** — `architect:analyse jira=PROJ-123` for anything but a chore or a new project: how the affected code works today (FACT with `file:line`), options, and the decisions required.
3. **ADR** — each decision from the analysis that changes a contract, data shape, dependency, or failure mode → `architect:adr`, approved to *Accepted* (`adr_skill`). A new project's stack choices are ADRs via `project_setup_skill` §7.
4. **Spec chain** — feature: `requirements.md` → `design.md` → `tasks.md`, each `Status: Approved` (`spec_driven_development_skill`). Every task cites an AC ID. Small features may keep all three short; they may not skip them.
5. **Setup** — new project: `docs/project-setup/` files approved and the scaffold green (`project_setup_skill` §9) before any feature code.

Record each gate and who approved it in the run report.

## 4. Implement

```bash
git switch -c feature/PROJ-123-single-charge-on-retry     # bug/PROJ-123-… for bugs, chore/… for chores
```

Move the ticket to *In Progress* now (§7 — confirmed first).

For each task, in order:

1. **Test first.** Write the test for the task's criterion, named after it, and run it: it must fail, for the reason you expect. A test that passes before the code exists tests nothing.

   ```java
   @Test
   void givenRetryWithin60s_whenCheckout_thenOneCharge_AC1() { … }
   ```
   ```python
   def test_given_retry_within_60s_when_checkout_then_one_charge_ac1() -> None: ...
   ```

2. **Minimum code** to pass it, following the loaded language skill and the project's `rules.md`.
3. **Run the whole suite**, not only the new test.
4. **Commit** — the key in every subject:

   ```text
   feat(PROJ-123): charge once per checkout attempt window (AC1)
   ```

Schema changes ship their migration in the same PR as the code that needs it.
Bugs: the first commit is the failing regression test, the second the fix —
the history then proves the test caught the bug.

Stay inside the ticket. A refactor the code "needs" but the criteria do not
is a new ticket (§8), unless it is required to make a criterion pass.

## 5. Verify

1. **Build command** from `AGENTS.md` (`./mvnw verify`, `uv run pytest --cov`, `npm test && npm run build`) — green from a clean state.
2. **Criteria matrix** — every AC has at least one test, every test passed in the run you are reporting:

   | AC | Test | Result |
   |---|---|---|
   | AC1 | `CheckoutServiceTest.givenRetryWithin60s_whenCheckout_thenOneCharge_AC1` | ✅ pass |
   | AC2 | `CheckoutServiceTest.givenFailedCharge_whenRetry_thenNewAttempt_AC2` | ✅ pass |

   An AC with no test is not done, whatever the code does.
3. **Review** — `quality:review` (`code_review_skill`); fix what it finds, re-run step 1.
4. **Traceability** — `ba:trace` when the project keeps the full chain (`traceability_skill`).

Paste real output. "Tests pass" without the command and its result is a claim, not evidence.

## 6. Pull Request

```bash
git push -u origin feature/PROJ-123-single-charge-on-retry
gh pr create --title "PROJ-123: Charge once per checkout retry window" --body-file .jira/PROJ-123-pr.md
```

PR body:

```markdown
## PROJ-123 — Charge once per checkout retry window
<Jira link>

### What changed
- <one line per behaviour change, not per file>

### Acceptance criteria
| AC | Test | Result |
|---|---|---|
| AC1 | `…_AC1` | ✅ |

### Decisions
- ADR-0012 — idempotency key on charge requests (Accepted)

### Migration
- V7__charges_add_idempotency_key.sql — expand step; contract follows in PROJ-131

### How to verify
`./mvnw verify` · manual: <steps, if any>
```

Keep the PR to the ticket. Reviewers approve a diff they can hold in their head.

## 7. Write Back to Jira

Jira is shared: a comment or transition is seen by the whole team at once.
**Show the exact text or transition to the user and send it only on a yes**,
unless the user authorised Jira writes for this run up front — then list each
one in the run report.

| When | Write |
|---|---|
| Work starts (§4) | Transition → *In Progress*; assign to the user if unassigned and they agree |
| PR opened (§6) | Comment: PR link + criteria matrix + ADR links · transition → *In Review* |
| Blocked (§8) | Comment: what blocks, what is needed, from whom |
| After a human merges | Transition → *Done* (or the workflow's equivalent); comment with the merge commit |

Use the workflow's own transition names; if the project's workflow has no
*In Review*, use its nearest state and say so. Never transition to *Done* on
an open PR — the ticket would claim work that main does not contain.

## 8. Stop Conditions

Stop, tell the user, and (after confirmation) comment on the ticket when:

| Condition | Do |
|---|---|
| No testable acceptance criteria | Open questions → `ba:clarify`; no code |
| A blocking ticket is not *Done* | Name it; wait |
| The change contradicts an *Accepted* ADR | Propose a superseding ADR (`adr_skill`); do not work around it |
| Scope grows beyond the criteria | Propose a new ticket with the extra scope; finish this one as written |
| Tests fail that this change did not touch | Report them with output; do not "fix" unrelated tests to get green |
| A criterion needs data, access, or a decision you do not have | Ask; do not stub it and call it done |

## 9. Anti-Patterns

| Don't | Do |
|---|---|
| Implement from the summary line | Read description, criteria, comments, and links |
| Invent criteria for a vague ticket | Send it back with specific questions |
| Write tests after the code, to match it | Write each test first and watch it fail |
| One test called `testCheckout` for four criteria | One named test per criterion, at least |
| Mix a refactor, a dependency bump, and the feature in one PR | One ticket, one PR; the rest become tickets |
| Transition to *Done* when the PR opens | *In Review* on open; *Done* after merge |
| Post to Jira without showing the user | Confirm every write, or list pre-authorised ones |
| Paste the API token into a command shown to the user | Read it from the environment |

## 10. Checklist

✅ Ticket read in full: description, criteria, comments, links, attachments
✅ Every criterion testable, or the ticket sent back
✅ Class recorded with reason; matching skills loaded
✅ Gates for the class passed and approved: analysis, ADR, spec chain, setup
✅ Branch and every commit carry the ticket key
✅ Each criterion has a named test that failed first and passes now
✅ Build command green from a clean state; output captured
✅ `quality:review` findings fixed
✅ PR open with criteria matrix, ADR links, migration notes
✅ Jira writes confirmed; ticket *In Review* with the PR linked
✅ *Done* only after a human merged
✅ Run report written (`html_report_skill`)
