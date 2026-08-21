# 11 — Set Up CI/CD

**Get it built, containerised, and deployed** — with a rollback path that exists
before you need it.

Covers [SDLC](sdlc-playbook.md) stage 10.

---

## When to use this

- A project needs a pipeline for the first time.
- Adding containerisation or infrastructure-as-code.
- Deployment strategy is changing.

## Prerequisites

- Code that builds and tests that pass locally. A pipeline around a broken build
  automates failure.

---

## The chain

```
implementer:pipeline        → CI/CD workflow
    ↓
implementer:docker          → Dockerfile, compose, image build
    ↓
implementer:iac             → Kubernetes manifests / infrastructure as code
    ↓
(architect:adr)             → deployment strategy + rollback  ◆ GATE
```

Order matters: the pipeline needs something to build, the image needs a build,
and the manifests need an image.

---

## What each produces

**`implementer:pipeline`** — CI workflow: build, test, lint, and the quality
gates that block a merge. Wire `quality:review` and the sanity suite in here;
gates a human has to remember are gates that get skipped.

**`implementer:docker`** — Dockerfile and compose configuration. Multi-stage
builds, non-root user, minimal base image.

**`implementer:iac`** — Kubernetes manifests or equivalent: resource limits,
health probes, config and secret handling, replica strategy.

---

## Deployment decisions need an ADR

Decision Type: `Deployment`. Specifically:

- Deployment strategy — blue/green, canary, rolling — and why this one.
- **The rollback mechanism, including data implications.** A schema migration
  that cannot be reversed makes rollback a fiction, and that is worth knowing
  before the first bad release, not during it.
- Environment topology and promotion rules.
- Secret management.

Section 10 of the Current Technical Specification is the rollback section, fed
by these ADRs.

---

## Wire the sanity suite into the pipeline

`docs/project-context/quality/sanity.md` holds scenarios that answer "is the
system fundamentally alive". The suite is constrained to **under five minutes**
specifically so it can run on every deploy.

If it grows past that budget, move scenarios to the integration suite rather
than accepting a slower gate — a sanity check nobody waits for is not a gate.

---

## Artifacts

| Path | From |
|---|---|
| CI workflow (`.github/workflows/`, or platform equivalent) | `implementer:pipeline` |
| `Dockerfile`, `docker-compose.yml` | `implementer:docker` |
| Kubernetes manifests / IaC | `implementer:iac` |
| `docs/adr/` — Decision Type `Deployment` | `architect:adr` |
| `docs/project-context/dependencies.md` | Updated on dependency change |

---

## Worked example

[../04-examples/implementer.md](../04-examples/implementer.md) — pipeline,
Docker, and Kubernetes for an auth service.

---

## Next

- [13 — Ship a release](13-ship-a-release.md)
