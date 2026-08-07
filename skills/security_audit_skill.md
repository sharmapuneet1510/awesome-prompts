---
name: Security Audit Skill
version: 1.0
description: >
  OWASP Top 10-driven security audit methodology with severity grading and
  fix-example discipline. Complements code_review_skill.md's general review process.
applies_to: [java, python, javascript, react, security]
tags: [security, owasp, audit, vulnerability]
---

# Security Audit Skill — v1.0

## 1. Audit Scope

A security audit is a focused pass, distinct from a general code review: look specifically for exploitable weaknesses, not style or structure. Walk every external-input entry point (HTTP handlers, message consumers, file uploads, CLI args) and every trust boundary (auth, tenant isolation, admin vs. user).

## 2. OWASP Top 10 Checklist (Web/API Context)

For each finding, note: category, file:line, severity, and a concrete fix.

1. **Broken Access Control** — missing authorization checks, IDOR (object references not scoped to the requesting user/tenant), privilege escalation paths.
2. **Cryptographic Failures** — secrets/PII in plaintext, weak hashing (MD5/SHA1 for passwords instead of bcrypt/argon2), hardcoded keys.
3. **Injection** — string-concatenated SQL/NoSQL/OS commands, unescaped template output (XSS), unsafe deserialization.
4. **Insecure Design** — missing rate limiting on auth endpoints, no account lockout, business logic that trusts client-side validation alone.
5. **Security Misconfiguration** — verbose error messages leaking stack traces to clients, default credentials, permissive CORS (`*` with credentials).
6. **Vulnerable Components** — outdated dependencies with known CVEs; check lockfiles against an advisory database.
7. **Auth Failures** — session tokens that don't expire, predictable session IDs, missing MFA on privileged actions.
8. **Data Integrity Failures** — unsigned/unverified deserialization, CI/CD pipelines pulling unpinned dependencies.
9. **Logging/Monitoring Failures** — auth failures and privilege changes not logged; secrets logged in plaintext.
10. **SSRF** — server-side requests built from user-supplied URLs without an allowlist.

## 3. Severity Grading

- **Critical** — remotely exploitable, no auth required, leads to data breach or full compromise (e.g., unauthenticated SQLi, broken access control on admin routes).
- **High** — exploitable with some precondition (authenticated user, specific role) but still leads to significant impact (IDOR exposing other users' data).
- **Medium** — requires a harder-to-reach precondition or has limited impact (reflected XSS behind an unusual input path).
- **Low** — defense-in-depth gaps (missing security headers, verbose but non-sensitive error messages).

## 4. Fix Discipline

Every finding needs a concrete fix, not just "sanitize input":
- Injection → parameterized queries / prepared statements, not string escaping.
- Broken access control → check ownership/tenant scope server-side on every request, not just at the UI layer.
- Secrets → move to a secrets manager / environment variable, rotate the exposed value, add a pre-commit secret scanner.

## 5. Checklist

✅ Every external-input entry point walked
✅ Every trust boundary checked for authorization enforcement
✅ Findings graded by actual exploitability, not just "it's a smell"
✅ Each finding has file:line and a concrete fix, not a vague recommendation
✅ Dependency versions checked against known CVEs
✅ No secrets/PII in logs or error responses

---
> Inspired by ideas from [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) (GPL-3.0) — content rewritten, not copied. See `CREDITS.md`.
