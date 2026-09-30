# spec-gate

Enforces the spec-driven gate with Claude Code hooks. The gate itself is
defined in [spec_driven_development_skill.md](https://github.com/sharmapuneet1510/awesome-prompts/blob/main/skills/spec_driven_development_skill.md#the-gate).

## Turn it on in a project

Install the plugin (`/plugin install spec-gate@awesome-prompts`), then add
`.spec-gate.json` at the project root. Without that file the hooks do nothing.

    {"source": ["src/**", "app/**"], "exempt": ["specs/**", "docs/**", "tests/**"], "spec_dir": "specs"}

## What you type

| Command | Effect |
|---|---|
| `/spec-gate:approve specs/<feature>/requirements.md` | Records your approval (then `design.md`, then `tasks.md`, in that order). Approving `tasks.md` makes that feature active |
| `/spec-gate:approve docs/adr/ADR-0012-….md` | Marks the ADR `Status: Accepted` |
| `/spec-gate:trivial <reason>` | Lets a small change through until your next message; the reason is logged |
| `/spec-gate:status` | What is approved, and whether gated edits are allowed |

## What it enforces

- Edits to `source` paths are blocked until the active feature's
  requirements, design and tasks are approved — and each approval still
  matches the file's content. Edit an approved file and its approval is void.
- Only the hook writes `Status: Approved` / `Status: Accepted` into spec
  files and ADRs; an edit by Claude that would add one is blocked.
- `.spec-gate.json` and `.spec-gate/` (the approval record) are off-limits to
  Claude's file tools and to shell commands that mention them.
- A broken `.spec-gate.json` or a hook error blocks gated edits rather than
  letting them through.

## What it doesn't

Shell commands are checked for the common write forms — `>`, `>>`, `1>`, `&>`,
`>|`, `tee`, `sed -i`, `perl -i`, `cp`, `mv`, `ln`, `rm`, `truncate`, also behind
`env`, `sudo`, `xargs` or a subshell — resolved from the shell's current
directory, and any shell command that mentions `spec-gate` is refused (so a
nested `claude -p "/spec-gate:approve …"` can't approve). Paths are compared
ignoring case, as macOS and Windows filesystems do. Not detected: a write
disguised in a script (for example a Python one-liner that builds the path at
run time), and other rewriting commands such as `git checkout -- <file>`,
`git restore`, `git apply` or `patch`. The gate stops Claude approving its own
work and editing gated code through its file tools; it is not a sandbox.
