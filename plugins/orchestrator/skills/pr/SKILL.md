---
name: pr
description: Package deliverables + create GitHub PR + sync artifacts
disable-model-invocation: true
---

Role and rules: read ${CLAUDE_PLUGIN_ROOT}/reference/agent.md and ${CLAUDE_PLUGIN_ROOT}/reference/rules.md for the sections this function needs.

# orchestrator:pr

**Input:** All generated code + artifacts + context

**Output:**
- GitHub PR created
- Artifacts synced to `.claude/`
- Completion report

**Steps:**
1. Create feature branch
2. Commit each task (5 commits total)
3. Final commit: docs + context artifacts
4. Create PR with detailed description
5. Export agents/skills to `.claude/`
6. Sync task-completion.json
7. Update CLAUDE.md + AGENTS.md
8. Generate completion report

**NEMESIS gate (optional).** Before step 1, if `docs/nemesis/nemesis.yml` exists, is not `enabled: false`, and
`auto_activate.production_release` matches this release, run `orchestrator:nemesis target=<release tag or branch>
trigger=policy` and stop on a `DEFEATED`, `CHALLENGED` or `INSUFFICIENT EVIDENCE` verdict; on `SURVIVED WITH
CONDITIONS`, put its conditions in the PR description. After two consecutive blocking
results (`DEFEATED`, `CHALLENGED` or `INSUFFICIENT EVIDENCE`) for the same release (count the reports in
`docs/nemesis/` whose `change` header matches it), stop and hand the decision to a human. Skip this when the file is absent, and
when you are yourself running as a NEMESIS challenger.
