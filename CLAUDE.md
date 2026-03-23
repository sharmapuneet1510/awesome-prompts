# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

A collection of AI/LLM prompt templates and agent definitions for software engineering workflows, plus a Python-based code parser for field derivation analysis in multi-module Maven repositories.

## Structure

- **Root `.txt` files** — Standalone prompt templates for various tasks: code review, codebase mapping, email writing, test generation, tracing/lineage, user story creation, production issue investigation, and HTML report generation.
- **`multi-module-github-copilot-chat-agents/`** — GitHub Copilot chat agent definitions (`.md` files) for Jira-driven workflows: code review, git review, Jira documentation, Jira implementation, and Jira-MR sync review. Uses `.agent-handoff/current.json` for shared state between agents and `.agent-sessions/jira/<KEY>/` for per-Jira work.
- **`parser/`** — Python tool that extracts field derivation logic from Java (AST) and XSLT/XML files across multi-module repos, outputting JSON and MD5 audit files.

## Parser Commands

```bash
# Install dependencies
pip install -r parser/requirements.txt

# Run the orchestrator (requires local repo paths)
python parser/orcastrator.py
```

Key dependencies: `javalang` (Java AST parsing), `lxml` (XML/XSLT parsing), `networkx` (graph analysis), `pydantic` (data models).

## Copilot Agent Conventions

From `.github/copilot-instructions.md`:
- Only write files inside the current workspace.
- Use `.agent-handoff/current.json` as shared handoff state between agents.
- Store per-Jira work under `.agent-sessions/jira/<KEY>/`.
- Prefer existing patterns in `gateway-*` modules; do not invent new frameworks.
- Keep changes minimal with safe logging and error handling consistent with existing code style.
