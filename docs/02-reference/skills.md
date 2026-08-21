# Skill Reference

**35 skills.** Reusable implementation modules that agents dispatch to. A skill
knows *how*; an [agent](agents.md) decides *what*.

Skills are never invoked directly by users — agents load them. Source:
`skills/*.md`.

---

## Governance & knowledge

These five form one system and are read together. `adr_skill` is the root —
everything else reads from it.

| Skill | Owns |
|---|---|
| `adr_skill` | Engineering Decision Records: 13-field template, seven-state lifecycle, ten decision types, supersede chain, ID allocation, trigger rule |
| `current_tech_spec_skill` | Current Technical Specification as a projection of Accepted ADRs; Final Implementation Record |
| `project_context_skill` | The 14-node shared knowledge tree and its ownership matrix |
| `traceability_skill` | The eight-hop chain and its 18 validation checks |
| `spec_driven_development_skill` | The requirements → design → tasks gate (RULE 11) |

See [../01-workflows/05-record-a-decision.md](../01-workflows/05-record-a-decision.md).

---

## Generation

| Skill | Produces |
|---|---|
| `backend_skill` | REST APIs (FastAPI, Spring Boot) |
| `frontend_skill` | React components and hooks |
| `database_skill` | SQL schema and migrations (PostgreSQL, MySQL, MSSQL) |
| `test_skill` | Unit, integration, and E2E tests (JUnit 5, pytest, Jest) |
| `code_documentation_skill` | Javadoc, docstrings, JSDoc |

---

## Language & framework standards

| Skill | Covers |
|---|---|
| `java_advanced_skill` | Java 17/21 idioms and patterns |
| `spring_advanced_skill` | Spring Framework and Spring Boot internals |
| `python_advanced_skill` | Python 3.11+, async, typing |
| `react_advanced_skill` | React 18+, TypeScript, hooks |
| `mssql_advanced_skill` | T-SQL patterns and optimisation |
| `apache_camel_skill` | Integration and EIP patterns |
| `apache_pulsar_skill` | Messaging, producers, consumers |
| `logger_skill` | SLF4J, Logback, structured logging |
| `lombok_skill` | Annotations and boilerplate reduction |
| `opentelemetry_skill` | Tracing, metrics, observability |

---

## Quality & analysis

| Skill | Covers |
|---|---|
| `code_review_skill` | Six-phase PR analysis with scoring |
| `code_health_skill` | Issue taxonomy and severity scoring |
| `code_formatting_skill` | Style standards |
| `security_audit_skill` | OWASP Top 10, severity grading, fix discipline |
| `debugging_skill` | Reproduce → isolate → hypothesise → fix → regression-test |
| `refactoring_skill` | Safe, reversible structural change |
| `error_handling_skill` | Exception handling and recovery patterns |
| `oop_skill` | OOP pillars, SOLID, design patterns |
| `multi_review_html_skill` | Batch PR review HTML with sidebar tabs |

---

## Context & requirements

| Skill | Covers |
|---|---|
| `context_builder_skill` | Project architecture and tech-stack analysis |
| `ba_create_skill` | Plain-text requirements → Jira JSON + BDD HTML cards |
| `jira_html_report_skill` | Parse Jira exports → HTML backlog |
| `jira_incremental_spec_generator_skill` | Read Jira incrementally → book-format specification |

---

## Meta

| Skill | Covers |
|---|---|
| `agent_skill_design_skill` | Authoring new skills in this repository |
| `mcp_server_skill` | Tool minimisation, least-privilege scoping, schema clarity |

---

## Why skills instead of tech-specific agents

Before v4.0.0 there was an agent per stack. Each duplicated the others' testing
guidance, documentation rules, and error handling.

Now one implementer detects the stack and loads the matching skill:

```
implementer:build
    ↓ detect stack
    ├─ Java?       → java_advanced_skill + spring_advanced_skill
    ├─ Python?     → python_advanced_skill
    ├─ React?      → react_advanced_skill
    ├─ SQL?        → database_skill + mssql_advanced_skill
    └─ all         → code_documentation_skill + test_skill + error_handling_skill
```

Adding a language means adding a skill, not an agent.

---

## Writing a new skill

Read `skills/agent_skill_design_skill.md` first. In short: YAML frontmatter with
`name`, `version`, and `description`; state what the skill owns and what it
refuses; embed templates inline rather than in a separate directory; register it
in `skills/README.md`.

Skills export to all eight platforms automatically — see
[../01-workflows/14-export-to-platforms.md](../01-workflows/14-export-to-platforms.md).

---

## See also

- `skills/README.md` — the canonical index with per-skill "used by"
- [agents.md](agents.md) · [functions.md](functions.md)
