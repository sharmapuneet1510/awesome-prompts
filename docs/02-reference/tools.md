# Tool Reference

**Python utilities** in `tools/`. Unlike agents and skills, these are real
programs you run.

Requires Python 3 — see [../00-getting-started/installation.md](../00-getting-started/installation.md).

---

## Most used

| Tool | Does | Guide |
|---|---|---|
| `exporter.py` | Export skills, agents, functions, hooks, and prompts to 8 platforms | [../01-workflows/14-export-to-platforms.md](../01-workflows/14-export-to-platforms.md) |
| `context_builder.py` | Scan a project → `architecture.md`, `tech-stack.md`, `context.json`, `design.html` | [../01-workflows/04-understand-a-codebase.md](../01-workflows/04-understand-a-codebase.md) |
| `requirement_parser.py` | Parse requirements from free text, Jira, files, or auto-detect | [../03-guides/requirement-input.md](../03-guides/requirement-input.md) |
| `task_generator.py` | Break requirements into task specifications | [../01-workflows/03-feature-from-requirement.md](../01-workflows/03-feature-from-requirement.md) |
| `github_sync.py` | Create GitHub PRs with generated code | [../01-workflows/13-ship-a-release.md](../01-workflows/13-ship-a-release.md) |

---

## Export

| Tool | Does |
|---|---|
| `exporter.py` | The main export tool. `--list`, `--dry-run`, `--target`, `--skills`, `--agents`, `--prompts`, `--clean` |
| `interactive_exporter.py` | Multi-select UI for choosing agents and skills |
| `config_generator.py` | Platform config files with hook registrations |
| `migrate_instructions.py` | Migrate instruction files between formats |

---

## Analysis & context

| Tool | Does |
|---|---|
| `context_builder.py` | Project scanning and context generation |
| `generate_design_html.py` | Interactive HTML visualisation — architecture, tech stack, file tree, API endpoints |
| `project_detector.py` | Distinguish new projects from existing ones |
| `graphify_integrator.py` | Knowledge graphs with token caching |

---

## Requirements & tasks

| Tool | Does |
|---|---|
| `requirement_parser.py` | Requirements from any input form |
| `task_generator.py` | Task specifications from requirements |
| `task_tracker.py` | Task completion tracking |

---

## Code review

| Tool | Does |
|---|---|
| `code_review_generator.py` | Review generation pipeline |
| `code_review_reporter.py` | HTML report output |

---

## Maintenance

| Tool | Does |
|---|---|
| `skill_validator.py` | Validate skill file structure |
| `fix_code_blocks.py` | Repair malformed code fences |
| `python_detect.py` | Cross-platform Python detection — `python` vs `python3` |
| `update_checker.py` | Check for repository updates |
| `feedback_analyzer.py`, `feedback_processor.py` | Feedback collection |

---

## Libraries

### `token_optimizer/`

Query analysis before dispatch: multi-dimensional scoring (clarity, context,
feasibility), web-search detection, intent classification, token estimation, and
routing recommendations.

```python
from token_optimizer import QueryAnalyzer

analyzer = QueryAnalyzer()
result = analyzer.analyze("your query here")
print(result.feedback.recommendation)   # 'claude', 'web_search', …
```

Install with `pip install -e token_optimizer/`. 35 tests in
`tests/test_token_optimizer.py`. Full documentation in `token_optimizer/README.md`.

### `parser/`

Field derivation analysis for multi-module Maven repositories. Dependencies:
`javalang`, `lxml`, `networkx`, `pydantic`.

```bash
pip install -r parser/requirements.txt
python3 parser/orcastrator.py
```

---

## A note on `python` vs `python3`

On macOS `python` frequently does not exist. Every example here uses `python3`.
`python_detect.py` exists because this bites often enough to warrant a utility.

---

## See also

- `tools/README.md` — full CLI documentation
- [../03-guides/](../03-guides/) — task-oriented guides
