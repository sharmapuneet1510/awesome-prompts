# Spec gate enforced by hooks — Design

**Issue:** #54 (part of #68) · **Date:** 2026-09-29 · **Status:** Draft — awaiting review

## Problem

RULE 11 (spec gate) and RULE 11a (ADR gate) exist only as text the model is
asked to obey:

1. **Nothing enforces a gate.** No hook stops the model writing source code.
2. **The model approves itself.** It decides the user approved, then writes
   `Status: Approved`. Nothing records the human's approval separately.
3. **The model decides what is trivial** and therefore exempt.
4. **The gate is defined differently in different files** (RULE 11: all three
   spec files; `implementer_agent.md` ~L328: design + tasks; `full.md`: none).
5. **`implementer` STEP 0 offers "free text"** and continues to build.

## Goal and success criteria

1. With no approved `tasks.md`, an edit to a gated source path is **blocked by a
   hook**, not by the model's choice.
2. The model **cannot mark something approved by editing a file**.
3. **One gate definition**, referenced everywhere else.
4. A test pipes sample `PreToolUse` JSON into the hook and checks the block
   and allow paths.
5. The README states what is enforced and what is still an instruction.

## Decisions (agreed 2026-09-29)

| Question | Decision |
|---|---|
| Delivery | A new hand-written `spec-gate` plugin in the marketplace |
| Activation | Opt-in per project: no `.spec-gate.json` → every hook allows everything |
| Approval | Recorded by a hook from user-typed text, bound to the file's SHA-256 |
| Trivial work | A user-typed bypass valid until the user's next message, logged |
| Config format | JSON (`.spec-gate.json`), parsed by the standard library |

## Threat model and its limit

The hooks stop the model from **approving by editing a file**, from **writing
approval markers**, from **touching the approval record**, and from **editing
gated source through the file tools** while the gate is closed. They also deny
the **recognisable** shell forms of the same writes.

They do not stop a model that deliberately disguises a write in a shell
command (for example, a Python one-liner that builds the path at run time). The
README and the skill say so. Stronger isolation (sandboxing the Bash tool) is
out of scope.

## Components

```text
plugins/spec-gate/                          hand-written, not generated
  .claude-plugin/plugin.json
  hooks/hooks.json                          PreToolUse + UserPromptSubmit → scripts/gate.py
  scripts/gate.py                           standard library only
  skills/approve/SKILL.md                   /spec-gate:approve <file>
  skills/trivial/SKILL.md                   /spec-gate:trivial <reason>
  skills/status/SKILL.md                    /spec-gate:status
  README.md                                 what it enforces, what it doesn't, setup

<project>/.spec-gate.json                   opt-in config (the user writes it)
<project>/.spec-gate/approvals.json         written only by the hook
<project>/.spec-gate/log.jsonl              written only by the hook
```

All three skills set `disable-model-invocation: true`. Their bodies tell Claude
to report the result the hook added to context; they perform no action
themselves.

### `.spec-gate.json`

```json
{
  "source": ["src/**", "app/**"],
  "exempt": ["specs/**", "docs/**", "tests/**"],
  "spec_dir": "specs"
}
```

| Key | Default when omitted | Meaning |
|---|---|---|
| `source` | required | Globs of gated paths, relative to the project root |
| `exempt` | `["specs/**", "docs/**", "tests/**"]` | Always editable; checked before `source` |
| `spec_dir` | `"specs"` | Where `<feature>/{requirements,design,tasks}.md` live |

A file that is missing means "not active". A file that doesn't parse, or has no
`source`, makes the gate **deny** gated-looking edits with a message naming the
config error. A broken config must not silently turn enforcement off.

### `.spec-gate/approvals.json`

```json
{
  "active_feature": "checkout-retry",
  "approvals": {
    "specs/checkout-retry/requirements.md": {"sha256": "…", "at": "2026-09-29T10:02:11Z", "prompt": "/spec-gate:approve specs/checkout-retry/requirements.md"},
    "docs/adr/ADR-0012-idempotency.md":     {"sha256": "…", "at": "…", "prompt": "…", "status": "Accepted"}
  },
  "bypass": {"reason": "fix typo in error message", "session_id": "…", "opened_at": "…"}
}
```

## Behaviour

### `UserPromptSubmit`

The hook reads the prompt text and acts only on these forms. Everything else
passes through unchanged.

| Prompt | Action |
|---|---|
| `/spec-gate:approve <path>` | Approve (below) |
| `/spec-gate:trivial <reason>` | Open a bypass for this session until the next user prompt; append to `log.jsonl` |
| `/spec-gate:status` | Add context: active feature, each approval and whether its hash still matches, open bypass |
| any other prompt | Close any open bypass |

**Approve `<path>`**, relative to the project root:

- **Spec file** `specs/<feature>/{requirements,design,tasks}.md`:
  1. The previous files in the chain must already be approved with matching
     hashes: `design.md` needs `requirements.md`, and `tasks.md` needs both.
     Otherwise refuse and say which file is missing.
  2. Replace an existing `Status: Draft` or `Status: Proposed` line with
     `Status: Approved`. If the file has no status line, append
     `Status: Approved` as its last line.
  3. Store the SHA-256 of the resulting bytes. Approving `tasks.md` also sets
     `active_feature`.
- **ADR** `docs/adr/*.md`: ensure the file contains `Status: Accepted`
  (replacing a `Status: Proposed` line if present), then store the hash with
  `"status": "Accepted"`.
- **Any other path, or a missing file:** refuse, and say why.

The result, approved or refused and why, is returned as `additionalContext`,
so Claude reports it. A missing or broken `.spec-gate.json` makes `approve`
refuse: there is nothing to enforce.

### `PreToolUse`

The matcher is `Write|Edit|MultiEdit|NotebookEdit|Bash`. When
`.spec-gate.json` is absent, the hook allows the call without reading the input
further.

**File tools** (`tool_input.file_path` or `notebook_path`, made relative to the
project root):

1. **Deny** if the path is under `.spec-gate/`.
2. **Deny** if the path is a spec file (`<spec_dir>/**`) or an ADR (`docs/adr/**`)
   and the new content adds a line matching `^\s*\**Status:\**\s*(Approved|Accepted)\b`
   that the file didn't already have. Content means `content` (Write),
   `new_string` (Edit), each edit's `new_string` (MultiEdit) or `new_source`
   (NotebookEdit). Only the hook writes approval markers.
3. **Allow** if the path matches `exempt`.
4. If the path matches `source`:
   - **allow** if a bypass is open for this `session_id`;
   - **allow** if `active_feature` is set and all three of its spec files are
     approved with matching hashes;
   - **otherwise deny**, with a message that names what is missing and the exact
     command to type, e.g.
     `Blocked by spec-gate: specs/checkout-retry/tasks.md is not approved. When you have reviewed it, type: /spec-gate:approve specs/checkout-retry/tasks.md`.
5. **Allow** anything else.

**Bash** (`tool_input.command`), best effort:

- **Deny** a command that mentions `.spec-gate/` or `.spec-gate.json`.
- **Deny** a command that would add an approval marker: `Status: Approved` or
  `Status: Accepted` together with a write form.
- While the gate would deny a source edit, **deny** a command that names a path
  matching `source` together with a write form: `>`, `>>`, `tee`, `sed -i`,
  `perl -i`, `cp … <path>`, `mv … <path>`, `truncate`, `rm`.
- **Allow** everything else.

A denial is returned as `{"hookSpecificOutput": {"hookEventName": "PreToolUse",
"permissionDecision": "deny", "permissionDecisionReason": "<message>"}}` with
exit code 0. An internal error in the hook (such as an unreadable approvals
file) **denies** gated calls with the error in the reason, so a crash cannot
open the gate.

### Precondition to verify first

The docs don't list `UserPromptSubmit`'s input fields, or say whether a typed
`/spec-gate:approve …` reaches it before skill expansion. The first
implementation task checks this with a real headless Claude Code run and
records the input field that carries the text. If typed commands don't reach
`UserPromptSubmit`, the same logic moves to `UserPromptExpansion`, which the
docs describe for typed commands. Nothing else in the design changes.

## One gate definition

`skills/spec_driven_development_skill.md` gains a `## The Gate` section, the
only full statement. It covers:

- **The chain:** `requirements.md` → `design.md` → `tasks.md`, approved in order.
- **What counts as approval:**
  - with spec-gate active, a user-typed `/spec-gate:approve`;
  - otherwise, an explicit approval message from the user in the conversation.
  - Never the model's inference.
- **ADRs:** `Status: Accepted` follows the same approval rule.
- **Trivial work:** exempt only through `/spec-gate:trivial` (with spec-gate) or
  the user's explicit say-so (without it).
- **Enforcement:** what spec-gate enforces, and its limit.

These keep a one-line rule plus a link to that section instead of restating it:

- RULE 11 and 11a in `instructions/master_instruction_set.md`
- `agents/implementer_agent.md` (~L328 and ~L1680)
- `agents/architect_agent.md` (~L258)
- `agents/orchestrator_agent.md` (~L94)
- `agents/implementer/functions/build.md` and `full.md` (which currently has none)
- `agents/README.md` (~L55)

`implementer_agent.md` STEP 0's "a) Free text description" routes to
`orchestrator:plan` rather than continuing to build.

## README

The gate paragraph and the "six gates" section say what is true:

- With `spec-gate` installed and `.spec-gate.json` present, the spec gate, the
  approval markers and ADR acceptance are **enforced by hooks**, with the shell
  limit stated.
- Without it, and for the remaining gates, they are **instructions** the model
  follows.

"refusal, not a warning" is kept only where it is true.

## Marketplace and exporter

- `plugins/spec-gate/` is hand-written. `tools/claude_plugins.py` treats any
  plugin directory without a generated counterpart as hand-written: it doesn't
  prune it, and it lists it in `marketplace.json`, taking the description from
  its own `plugin.json`.
- The freshness test compares generated plugins only.

## Verification

- **`tests/tools/test_spec_gate.py`**: pipes real hook JSON into `gate.py` as a
  subprocess, in a temporary project.
  - **No config:** allow everything.
  - **Gating:** an unapproved source edit is denied; the approved chain allows
    it; exempt paths are allowed.
  - **Approval record:** edits to `.spec-gate/**` are denied; a model-written
    marker is denied (Write, Edit, MultiEdit); approval is void after the file
    is edited.
  - **Chain order:** approving `design.md` before `requirements.md` is refused.
  - **Bypass:** opens on `/spec-gate:trivial`, closes on the next prompt, and
    doesn't carry over to another session.
  - **Config errors:** a broken config denies.
  - **ADRs:** approving an ADR writes `Accepted`.
  - **Bash:** denied and allowed examples for each write form.
  - **Errors:** a hook failure denies.
- **Content test:** every gate-referencing file points to
  `spec_driven_development_skill.md#the-gate` and no longer restates the chain.
- **`claude plugin validate --strict plugins/spec-gate`** passes, in pytest and
  in the CI job.
- **One headless Claude Code check** (task 1) of the `UserPromptSubmit` input.

## Out of scope

- Behavioural evals of the gate under pressure (#60).
- Mechanically detecting "decision-bearing" changes (RULE 11a) and enforcing the
  other gates.
- Sandboxing the Bash tool.
- Non-Claude assistants: the other exporters are unchanged.
