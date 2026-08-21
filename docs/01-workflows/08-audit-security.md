# 08 — Audit Security

**Find the abuse paths, then keep them checked.** A one-off audit decays; the
security suite is what makes it stick.

Covers [SDLC](sdlc-playbook.md) stages 11–12.

---

## When to use this

- Before a first production release.
- After adding a trust boundary — new input surface, new integration, new auth path.
- Periodically, on a schedule you set rather than when you remember.
- When a PR touches authentication, authorisation, input handling, or secrets.

## Prerequisites

Read access to the code. `docs/project-context/` helps but is not required.

---

## The chain

```
quality:security path=./src         → OWASP audit, severity-graded findings
    ↓
(architect:adr)                     ← for each accepted mitigation  ◆ GATE
    ↓
implementer:full                    → fixes + tests
    ↓
quality:qa suite=security           → ◆ turn findings into standing scenarios
```

The last step is what separates an audit from a security practice.

---

## What `quality:security` covers

Authentication · authorisation · injection risks · API security · data
protection · infrastructure hardening — graded by severity, mapped to OWASP
categories.

Findings are FACT (what is there, with `file:line`) plus PROPOSAL (what to do).
The agent does not silently apply security fixes; a mitigation is a decision,
and decisions belong to you.

---

## Turning findings into a suite

Each accepted mitigation becomes a `SEC-n` row in
`docs/project-context/quality/security.md`, mapped to its OWASP category:

```
| SEC-7 | Given an authenticated non-admin user, when they request
          /admin/users, then a 403 is returned | OWASP A01 | yes |
          tests/security/test_authz.py | 2026-08-21 |
```

Without this, the next audit re-discovers the same class of issue and you have
no evidence anything improved.

---

## Security decisions need ADRs

Almost always. A mitigation changes a contract, a dependency, or a failure mode
by definition. Decision Type: `Security`.

The `Consequences → Accepted` field matters more here than anywhere else:
security decisions have real costs — latency, friction, operational burden — and
recording what you knowingly accepted is what stops it being relitigated every
quarter.

Equally, a **decision not to fix** deserves an ADR. "We accept this risk because
X" is a decision, and an undocumented accepted risk is indistinguishable from an
oversight.

---

## Artifacts

| Path | From |
|---|---|
| Security audit report, severity-graded | `quality:security` |
| `docs/project-context/quality/security.md` — `SEC-n` rows | `quality:qa` |
| `docs/adr/` — Decision Type `Security` | `architect:adr` |
| `docs/project-context/technical-debt.md` — accepted risks | Via ADR consequences |

---

## Reference

`skills/security_audit_skill.md` — OWASP Top 10 checklist, severity grading,
fix discipline.

---

## Worked example

[../04-examples/quality.md](../04-examples/quality.md) — security audit scenario.
