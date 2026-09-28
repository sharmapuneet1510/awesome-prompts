---
name: Project Setup Skill
version: 1.0
description: >
  Before the first line of feature code, decide and write down how the project
  is built: the stack, one library per use case (with the reason and the
  rejected alternative), project coding rules, the instructions file AI
  assistants read, the scaffolding (build, lint, format, CI, dependency
  updates, secret scanning), and an ADR for each major choice — then stop for
  approval. Library catalog checked against PyPI, npm, and Maven Central on
  2026-09-28.
applies_to: [project-setup, architecture, java, python, typescript, react, all-languages]
tags: [project-setup, tech-stack, libraries, conventions, scaffolding, agents-md, dependency-policy]
---

# Project Setup Skill — v1.0

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | A new project, or an existing one with no written stack and library decisions — before `implementer:build` writes feature code. `orchestrator:ideate`, `orchestrator:plan`, `architect:design` |
| **Skip when** | The project already has approved `docs/project-setup/` files — follow them; propose changes through an ADR |
| **Inputs** | The requirement, team skills, deployment target, constraints (mandated DB, cloud, licences); `instructions/java_project_intake.md` or `python_project_intake.md` answers |
| **Produces** | `docs/project-setup/stack.md`, `libraries.md`, `rules.md` · `AGENTS.md` (plus `CLAUDE.md` importing it) · ADR per major choice · scaffolded build, lint, test, CI |
| **Steps** | 1. Intake (§1) → 2. Stack (§2) → 3. One library per use case (§3–§4) → 4. Rules (§5) → 5. `AGENTS.md` (§6) → 6. ADRs (§7) → 7. Scaffold (§8) → 8. **Stop for approval** (§9) |
| **Done when** | All three setup files at `Status: Approved`; a fresh clone builds and tests green with one command |
| **Senior defaults** | One library per use case — two JSON libraries is a bug · framework-managed versions (BOM, Boot, Django) beat "latest" · standard library first · every choice names the alternative it rejected · a library must have released within 12 months and carry an allowed licence · the instructions file lists commands, not philosophy |
| **Load on demand** | §1 intake · §2 stack · §3 selection rules · §4 catalog (Java · Python · TypeScript · cross-cutting) · §5 rules · §6 AGENTS.md · §7 ADRs · §8 scaffold · §9 gate |
| **Run report** | `html_report_skill` — adds: Decisions table (use case → choice → rejected) · Scaffold checks |
| **Pairs with** | `maven_skill`, `python_project_skill`, `adr_skill`, `spec_driven_development_skill`, `project_context_skill`, `security_audit_skill` |

---

## 1. Intake

Answer these before choosing anything. Where the repository has an intake form
(`instructions/java_project_intake.md`, `instructions/python_project_intake.md`),
use it.

| Question | Decides |
|---|---|
| What does it do, for whom, at what load? | Sync vs async, need for a queue, caching |
| What already exists that it must talk to? | Protocols, auth, the database you may not choose |
| What does the team already run and know? | Language and framework — a familiar stack beats a better one nobody can operate |
| Where does it run? | Container, VM (Ansible), serverless; cloud services available |
| What data, how much, how long kept? | Database, migrations tool, partitioning, retention |
| Regulatory constraints? | Audit logging, encryption, licence allowlist, data residency |
| Who will maintain it in two years? | Favour boring, widely known libraries |

## 2. Stack

`docs/project-setup/stack.md`:

```markdown
# Stack — <project>

**Status:** Draft

| Layer | Choice | Version policy | Why | ADR |
|---|---|---|---|---|
| Language | Java 21 (LTS) | LTS only | Team knows it; virtual threads for I/O | ADR-0001 |
| Framework | Spring Boot 4.1 | Minor upgrades each quarter | Mature, BOM-managed ecosystem | ADR-0001 |
| Build | Maven 3.9 + wrapper | Wrapper pins it | `maven_skill` | — |
| Database | PostgreSQL 17 | Managed service | Relational data, strong consistency | ADR-0002 |
| Messaging | none yet | — | No async requirement in MVP | — |
| Runtime | Container on Kubernetes | — | Platform standard | ADR-0003 |
| Frontend | React + TypeScript (Vite) | — | Team standard | ADR-0004 |
```

## 3. Choosing a Library

A library enters `libraries.md` only if it passes all of these:

| Check | Rule | How to check |
|---|---|---|
| Need | The standard library or the framework cannot do it reasonably | Look first |
| One per use case | No second library for the same job | Scan `libraries.md` |
| Maintained | A release in the last 12 months, issues answered | Registry (commands below) |
| Managed version | If the framework's BOM manages it, use that version | `spring-boot-dependencies` pins Flyway, Jackson, JUnit, Testcontainers… |
| Licence | On the allowlist (MIT, Apache-2.0, BSD, ISC, MPL-2.0); GPL/AGPL/SSPL need sign-off | Package metadata |
| Security | No open critical CVEs; history of prompt fixes | `pip-audit`, `npm audit`, OWASP dependency-check |
| Weight | Transitive dependency count proportionate to the job | `mvn dependency:tree`, `uv tree`, `npm ls` |

```bash
pip index versions <pkg>                     # or: curl https://pypi.org/pypi/<pkg>/json
npm view <pkg> version time.modified license
./mvnw versions:display-dependency-updates   # for everything already in the POM
```

## 4. Catalog — One Choice per Use Case

Starting points, not mandates: each was checked for a 2026 release (or noted)
on 2026-09-28. Record the project's actual choices in `libraries.md` with why
and what was rejected.

### Java / Spring Boot

| Use case | Choice | Rejected / notes |
|---|---|---|
| Web / REST | Spring Web MVC (Boot starter) | WebFlux only for genuinely streaming workloads; virtual threads cover blocking I/O |
| Validation | Jakarta Bean Validation (Hibernate Validator, Boot-managed) | Hand-written checks in controllers |
| JSON | Jackson — the Boot-managed version (3.x under Boot 4) | Gson — a second JSON library |
| Persistence | Spring Data JPA (Hibernate) · jOOQ for SQL-heavy code · `JdbcClient` for simple access | MyBatis alongside JPA — two ORMs |
| Migrations | Flyway (Boot-managed) | Liquibase is equally good — pick one; hand-run SQL |
| HTTP client | Spring `RestClient` with HTTP interfaces | Feign, raw `HttpURLConnection` |
| Resilience | Resilience4j (retry, circuit breaker, bulkhead) | Hand-rolled retry loops |
| Object mapping | MapStruct (compile-time) | ModelMapper (reflection, runtime errors) |
| Boilerplate | Java records first; Lombok only where a record cannot fit (`lombok_skill`) | Lombok on JPA entities with `@Data` |
| Cache | Caffeine (local) · Spring Data Redis (shared) | Guava cache |
| Scheduled jobs across instances | ShedLock | `@Scheduled` alone on multiple pods — runs N times |
| Messaging | Spring for Apache Kafka · Spring for Apache Pulsar (`apache_pulsar_skill`) | — |
| Logging | SLF4J + Logback; Boot structured logging (`logging.structured.format.console`) for JSON | Log4j2 alongside Logback |
| Metrics / tracing | Micrometer + OpenTelemetry (`opentelemetry_skill`) | Vendor agents baked into the image |
| API docs | springdoc-openapi — major matching Boot (3.x for Boot 4) | Hand-maintained OpenAPI YAML drifting from code |
| Security | Spring Security; OAuth2 resource server for JWT | Custom filter chains parsing tokens |
| Unit tests | JUnit Jupiter + AssertJ + Mockito (all Boot-managed) | Hamcrest alongside AssertJ |
| Integration tests | Testcontainers (Boot-managed) | H2 standing in for PostgreSQL |
| HTTP stubs | WireMock | Mocking `RestClient` internals |
| Architecture rules | ArchUnit | Rules that live only in a wiki |
| Build and quality | Maven + Enforcer, Spotless, Error Prone, SpotBugs, JaCoCo, PIT (`maven_skill`, `test_skill`) | — |

### Python / FastAPI

| Use case | Choice | Rejected / notes |
|---|---|---|
| Web / REST | FastAPI + Uvicorn | Flask plus hand-rolled validation |
| Models and validation | Pydantic v2 | Marshmallow alongside Pydantic |
| Settings | pydantic-settings, secrets as `SecretStr` | `os.environ[...]` scattered through code |
| ORM | SQLAlchemy 2.x | Two ORMs |
| Migrations | Alembic | Hand-run SQL |
| DB driver | psycopg 3 (sync and async) · asyncpg for async-only hot paths | psycopg2 in new code |
| HTTP client | httpx (sync and async; latest release Dec 2024 — mature, still the default) | requests in async code |
| Retries | tenacity | Hand-rolled loops |
| Auth | PyJWT + pwdlib (Argon2) (`backend_skill`) | python-jose, passlib — unmaintained |
| Logging | structlog (JSON in prod) | print, ad-hoc `logging` formats |
| Background jobs | Celery (mature, many brokers) · Dramatiq (simpler) | Threads in the web process |
| CLI | Typer | argparse for anything with subcommands |
| Tests | pytest, pytest-cov, pytest-randomly, Hypothesis, respx (httpx stubs), testcontainers, time-machine | unittest-style classes, freezegun (slower) |
| Tooling | uv, ruff, mypy, pre-commit, pip-audit (`python_project_skill`) | pip-tools + black + isort + flake8 — four tools for one job |
| Observability | opentelemetry-sdk + instrumentation packages | — |

### TypeScript / React

| Use case | Choice | Rejected / notes |
|---|---|---|
| Build / dev server | Vite | Create React App — unmaintained |
| Language | TypeScript, `strict: true` | JavaScript with JSDoc types |
| Routing | React Router | Two routers |
| Server state | TanStack Query | Server data copied into Redux or `useState` |
| Client state | Zustand, only when component state is not enough | Redux for a small app |
| Forms + validation | react-hook-form + Zod (schemas shared with API types) | Formik |
| Styling | Tailwind CSS | Mixing three styling systems |
| Unit / component tests | Vitest + Testing Library + user-event | Enzyme |
| Network stubs | MSW | Mocking `fetch` inside components |
| E2E | Playwright | Cypress alongside Playwright |
| Lint / format | ESLint + typescript-eslint + Prettier, **or** Biome alone | Both setups at once |

### Cross-cutting

| Use case | Choice | Notes |
|---|---|---|
| Relational database | PostgreSQL; SQL Server where mandated (`mssql_advanced_skill`, `mssql_dba_skill`) | `database_skill` for schema |
| Containers | Multi-stage builds, slim or distroless base, non-root | `python_project_skill` §7 |
| Cloud resources | Terraform or OpenTofu | Pick one |
| Host configuration | Ansible (`ansible_skill`) | — |
| CI | GitHub Actions (or the platform's standard) | One workflow per concern: build, security, release |
| Dependency updates | Renovate or Dependabot, grouped, weekly | Unreviewed auto-merge on majors |
| Secret scanning | gitleaks in pre-commit and CI | — |
| SBOM | CycloneDX | Attach to every release |

## 5. Project Rules

`docs/project-setup/rules.md` — short, specific, enforceable. Link to a skill
instead of restating it.

```markdown
# Rules — <project>

**Status:** Draft

## Layout
- Packages by feature (`orders/`, `billing/`), not by layer (`controllers/`, `services/`).
- Domain code has no framework imports; ArchUnit / import-linter enforces it.

## Code
- Language standards: `java_advanced_skill` / `python_advanced_skill` / `react_advanced_skill`.
- Errors: `error_handling_skill` — typed errors, no swallowed exceptions, one error response shape.
- Logging: JSON in prod, correlation ID on every line, no secrets or PII (`logger_skill`).

## Tests
- Every change ships with tests (`test_skill`); coverage floor 90% lines, gate in CI.
- Integration tests use Testcontainers, not in-memory substitutes.

## Dependencies
- Only libraries listed in `libraries.md`. Adding one = a PR that updates `libraries.md`.
- Versions from the framework BOM where it manages them.

## Git and review
- Trunk-based; short-lived branches; squash merge.
- Conventional commit subjects (`feat:`, `fix:`, `chore:`).
- Decision-bearing changes need an Accepted ADR first (RULE 11a).
```

## 6. `AGENTS.md` — What an AI Assistant Reads

Keep it under ~60 lines: an assistant reads it on every task. Commands and hard
rules only; link out for everything else. Put the content in `AGENTS.md`
(the convention most coding assistants read) and make `CLAUDE.md` the single
line `@AGENTS.md` — Claude Code imports the file at that path — so the two
never drift.

```markdown
# AGENTS.md — <project>

## Commands
- Build and test: `./mvnw verify`            <!-- or: uv run pytest --cov -->
- Format: `./mvnw spotless:apply`             <!-- or: uv run ruff format -->
- Run locally: `docker compose up -d && ./mvnw spring-boot:run`

## Layout
- `app/src/main/java/com/acme/orders/<feature>/` — one package per feature
- `docs/project-setup/` — stack, libraries, rules (read before adding a dependency)
- `docs/adr/` — decisions; do not contradict an Accepted ADR

## Rules
- Use only libraries in `docs/project-setup/libraries.md`.
- Every change includes tests; `./mvnw verify` must pass before you finish.
- No secrets in code, config, logs, or test fixtures — use environment variables.
- Do not edit generated files: `target/`, `uv.lock` by hand, migrations already applied.

## Never
- Add a dependency without updating `libraries.md`.
- Disable a test, a lint rule, or a quality gate to make a build pass.
```

## 7. ADRs for Major Choices

Language, framework, database, messaging, and deployment target each change a
contract or a dependency — `adr_skill`'s trigger rule — so each gets an ADR
with at least two real options. Library picks inside an approved stack are
recorded in `libraries.md`, not as ADRs, unless they change a contract.

## 8. Scaffold

| Piece | Java | Python | TypeScript |
|---|---|---|---|
| Build + lock | Maven wrapper, parent POM (`maven_skill`) | `uv init --package`, `uv.lock` (`python_project_skill`) | `npm create vite@latest`, `package-lock.json` |
| Format + lint | Spotless, Error Prone | ruff, ruff format | ESLint + Prettier or Biome |
| Types | compiler `-Xlint:all` | `mypy --strict` | `tsc --noEmit`, `strict` |
| Tests + coverage | Surefire, Failsafe, JaCoCo | pytest, pytest-cov | Vitest `--coverage` |
| Pre-commit | Spotless, gitleaks | ruff, gitleaks | lint-staged or Biome, gitleaks |
| CI | `./mvnw verify` | `uv sync --locked` + checks | `npm ci && npm test && npm run build` |

Always: `.editorconfig`, `.gitignore`, `README.md` with the three commands from
`AGENTS.md`, Renovate/Dependabot config, a CODEOWNERS file for `docs/adr/` and
`docs/project-setup/`.

**Acceptance test for the scaffold:** clone into an empty directory, run the one
build-and-test command, get green. Anything else a newcomer must do goes in the
README, or it is a bug.

## 9. The Gate

After writing `stack.md`, `libraries.md`, and `rules.md`, stop. Present the
three files and the ADRs, and ask for approval — the same checkpoint as
`spec_driven_development_skill`. Set `Status: Approved` only on an explicit
yes. `implementer:build` does not start feature code until they are approved.

After approval, `project_context_skill`'s `technical-context.md` and
`dependencies.md` are populated from these files.

## 10. Checklist

✅ Intake answered; constraints written down
✅ `stack.md`: every layer chosen, with version policy and ADR
✅ `libraries.md`: one library per use case, each with reason and rejected alternative
✅ Every library maintained (release within 12 months), licence allowed, version framework-managed where possible
✅ `rules.md` short and enforceable; links to skills instead of restating them
✅ `AGENTS.md` under ~60 lines; `CLAUDE.md` imports it with `@AGENTS.md`
✅ ADRs for language, framework, database, messaging, deployment
✅ Scaffold: build, lock, format, lint, types, tests, coverage gate, pre-commit, CI, dependency updates, secret scan, SBOM
✅ Fresh clone → one command → green
✅ All three setup files `Status: Approved` before feature code
