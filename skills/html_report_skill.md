---
name: HTML Run Report Skill
version: 1.0
description: >
  The one shared contract for the HTML report a skill writes at the end of a run
  that changed something: a single self-contained page outlining what was asked,
  what was done step by step, every artifact touched, decisions and their labels,
  gates passed or blocked, and what is left open. Defined once; every other
  skill's Quick Card names only the sections it adds.
applies_to: [all-skills, reporting, html]
tags: [report, html, run-summary, audit-trail]
---

# HTML Run Report Skill — v1.0

## Quick Card

> Read this card first. Load a numbered section only when the task needs it.

| | |
|---|---|
| **Use when** | A skill run created, modified, or deleted files, or the caller passed `report=html` |
| **Skip when** | Pure Q&A, a dry run, or `report=none`. Never write a report for a run that changed nothing |
| **Inputs** | The run's step log, the list of touched paths, any labelled claims, gate results |
| **Produces** | `docs/reports/<YYYY-MM-DD>-<skill>-<topic>.html` — one file, no external requests |
| **Steps** | 1. Keep a step log while working → 2. At the end, fill §3 template → 3. Escape every interpolated value → 4. Link artifacts, do not paste them |
| **Done when** | All seven core sections present (empty ones say "None"), page opens offline, passes the §5 checklist |
| **Load on demand** | §2 outline · §3 template · §4 token rules · §5 checklist |
| **Pairs with** | Every skill. `adr_skill` and RULE 12 for the claim labels |

---

## 1. When a Report Is Written

| Run | Report |
|---|---|
| Changed files | HTML, by default |
| Caller passed `report=md` | Same outline as Markdown, same path with `.md` |
| Caller passed `report=none` | None |
| Read-only analysis the caller will share | HTML only if asked |
| Skill whose deliverable is already HTML (`jira_html_report_skill`, `multi_review_html_skill`, `ba_create_skill`, `context_builder_skill` design.html, `code_review_skill`) | No second report. The deliverable reuses §3's `<head>` tokens so every page looks like one family |

## 2. The Outline

Seven core sections, always in this order. A skill adds its own sections
between 5 and 6; its Quick Card's **Run report** row names them.

| # | Section | Contents | Limit |
|---|---|---|---|
| 1 | **Header** | Title, `skill vX.Y`, invocation (`agent:function args`), date, outcome pill: `Done` · `Partial` · `Blocked` | one line each |
| 2 | **Summary** | What was asked, what was done, the result | ≤ 4 sentences |
| 3 | **What was done** | Ordered steps, each with status (`done` · `skipped` · `failed`) and a one-line detail | one row per step |
| 4 | **Artifacts** | Path (linked, relative) · action (`created` · `modified` · `deleted`) · purpose | every touched path |
| 5 | **Decisions & claims** | Each substantive claim labelled `FACT` (with file:line) · `INFERENCE` · `PROPOSAL` · `DECISION` | RULE 12 |
| — | *Skill-specific sections* | As named in the skill's Quick Card | — |
| 6 | **Gates & checks** | Check · result · evidence (command run, count, test name) | only checks actually run |
| 7 | **Open items** | Follow-ups, risks, questions awaiting a human | "None" if none |

A report states only what happened. A check that did not run is absent from §6,
not marked passed. A skipped step says why.

## 3. Template

A filled example lives in this repository at `docs/04-examples/html-run-report.html`.

Self-contained: inline CSS, no scripts, no fonts or images fetched. Collapsible
sections use `<details>`, so nothing depends on JavaScript. Replace every
`{{…}}`; **HTML-escape every value** (`& < > " '`) — reports quote code, paths,
and user text, and an unescaped value is an injection.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
<style>
:root{--bg:#fff;--fg:#1f2328;--muted:#59636e;--line:#d1d9e0;--card:#f6f8fa;
--accent:#0969da;--ok:#1a7f37;--warn:#9a6700;--bad:#cf222e}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--muted:#9198a1;
--line:#3d444d;--card:#151b23;--accent:#4493f8;--ok:#3fb950;--warn:#d29922;--bad:#f85149}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:960px;margin:0 auto;padding:24px 16px 64px}
header{border-bottom:1px solid var(--line);padding-bottom:16px;margin-bottom:8px}
h1{font-size:1.6rem;margin:0 0 6px}
.meta{color:var(--muted);font-size:.9rem;display:flex;flex-wrap:wrap;gap:6px 16px}
nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);
padding:8px 0;margin-bottom:16px;font-size:.9rem;display:flex;flex-wrap:wrap;gap:4px 14px;z-index:1}
nav a{color:var(--accent);text-decoration:none}
details{border:1px solid var(--line);border-radius:8px;margin:12px 0;background:var(--card)}
summary{cursor:pointer;padding:10px 14px;font-weight:600}
details>div{padding:0 14px 12px;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}
code{font:.88em ui-monospace,SFMono-Regular,Menlo,monospace}
.pill{display:inline-block;padding:1px 9px;border-radius:999px;font-size:.8rem;font-weight:600;border:1px solid currentColor}
.done,.pass,.created{color:var(--ok)}.partial,.skipped,.modified{color:var(--warn)}
.blocked,.failed,.fail,.deleted{color:var(--bad)}
.label{font:600 .75rem ui-monospace,monospace;padding:1px 6px;border-radius:4px;background:var(--line)}
ol.steps{margin:0;padding-left:1.4em}ol.steps li{margin:4px 0}
@media print{nav{display:none}details{break-inside:avoid}details:not([open])>div{display:block}}
</style>
</head>
<body><main>
<header>
  <h1>{{title}} <span class="pill {{outcome_class}}">{{outcome}}</span></h1>
  <div class="meta"><span><code>{{skill}} v{{version}}</code></span>
  <span><code>{{invocation}}</code></span><span>{{date}}</span></div>
</header>
<nav><a href="#summary">Summary</a><a href="#steps">What was done</a><a href="#artifacts">Artifacts</a>
<a href="#claims">Decisions</a><a href="#gates">Gates</a><a href="#open">Open items</a></nav>

<details id="summary" open><summary>Summary</summary><div><p>{{summary}}</p></div></details>

<details id="steps" open><summary>What was done ({{step_count}} steps)</summary><div>
<ol class="steps"><li><span class="pill done">done</span> {{step}} — {{detail}}</li></ol></div></details>

<details id="artifacts" open><summary>Artifacts ({{artifact_count}})</summary><div>
<table><tr><th>Path</th><th>Action</th><th>Purpose</th></tr>
<tr><td><a href="{{relative_path}}"><code>{{path}}</code></a></td><td class="created">created</td><td>{{purpose}}</td></tr>
</table></div></details>

<details id="claims"><summary>Decisions &amp; claims</summary><div>
<p><span class="label">FACT</span> {{claim}} <code>{{file}}:{{line}}</code></p></div></details>

<!-- skill-specific <details> sections go here -->

<details id="gates" open><summary>Gates &amp; checks</summary><div>
<table><tr><th>Check</th><th>Result</th><th>Evidence</th></tr>
<tr><td>{{check}}</td><td class="pass">pass</td><td><code>{{evidence}}</code></td></tr></table></div></details>

<details id="open" open><summary>Open items</summary><div><ul><li>{{item}}</li></ul></div></details>
</main></body></html>
```

## 4. Token Rules

- Write the report **once**, at the end, from the step log. Never rebuild it mid-run.
- **Link** artifacts; do not paste their contents. Quote at most 20 lines of code or diff per section.
- The template's `<head>` is fixed — copy it verbatim, do not restyle per run.
- Omit the `claims` section's body when there are no claims; write "None".
- One report per run. A multi-step function (`implementer:full`) writes one report covering all phases.

## 5. Checklist

✅ Written only because the run changed something (or was asked for)
✅ All seven core sections present, in order; empty ones say "None"
✅ Every interpolated value HTML-escaped
✅ No external requests — no CDN, font, image, or script URLs
✅ Every touched path listed in Artifacts with a relative link
✅ Only checks that actually ran appear in Gates, each with evidence
✅ Claims carry a RULE 12 label; every `FACT` cites file:line
✅ Outcome pill matches reality: `Blocked` if a gate refused
