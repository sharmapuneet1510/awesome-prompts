# Prompt Preflight — Optional Local-Model Prompt Hook — Design Specification

**Date:** September 20, 2026
**Status:** Approved by the user, 2026-09-20; amended the same day (see *Amendments*). The eval-set labels and model downloads still need separate approval at plan Task 4 (see *Model Selection*).
**Version:** 1.0

Claims in this document carry the RULE 12 labels: **FACT** (verified, sourced), **INFERENCE** (reasoned, not yet measured), **PROPOSAL** (awaiting approval), **DECISION** (approved by the user).

---

## Executive Summary

Add an **optional** Claude Code `UserPromptSubmit` hook, the *Prompt Preflight*, that inspects each prompt before Claude processes it. It has two tiers: fast heuristics (the existing `tools/token_optimizer`), and — only if the user opts in — a small language model served locally by Ollama. It can:

1. tell the user a question is basic enough that a web search would do;
2. give Claude a sharper restatement of the request, as advisory context;
3. tell the user when a prompt is too vague to act on.

It never rewrites the prompt (a hook cannot), never blocks by default, fails open on every error, and by default never sends a prompt off the machine. It is installed only by an opt-in wizard that asks at every step and is fully reversible.

---

## Problem Statement

- Users spend tokens and turns on questions a search answers in seconds, and on vague prompts that produce wrong work.
- This repo already has a regex analyzer, `tools/token_optimizer`, but nothing wires it into a hook. **FACT** (35 tests pass; no file in `hooks/` or `.claude/hooks/` imports it).
- The analyzer alone cannot separate a basic how-to from real work. **FACT** — probe of 8 prompts, 2026-09-20:

| Prompt | Analyzer routes to | Score | Right answer |
|---|---|---|---|
| what is the capital of France | web_search | 27 | web search ✔ |
| what is the latest version of react | web_search | 28 | web search ✔ |
| how do I reverse a list in python | claude | 37 | web search ✘ |
| explain the difference between TCP and UDP | claude | 30 | web search ✘ |
| fix bug | skip | 20 | too vague ✔ |
| make it better | skip | 27 | too vague ✔ |
| Refactor OrderService.submit() to use idempotency keys and add tests | claude | 38 | real work ✔ |
| why does my python script say ModuleNotFoundError … | claude | 42 | real work ✔ |

  All scores fall between 20 and 42, so the score does not discriminate. The sample is small (8) and is a probe, not a benchmark.
- The only existing `UserPromptSubmit` hook, `hooks/promptshield-check.sh`, never fires as wired. **FACT** — given a hook-style stdin payload containing `DROP TABLE` it printed "✅ Prompt passed security validation"; it reads `$1`, which Claude Code does not set. Fixing it is out of scope.

---

## Requirements

Each requirement is testable; the traceability matrix is in *Testing*.

| ID | Requirement |
|---|---|
| **R1** | **Opt-in.** Nothing is installed, downloaded, started, or edited without an explicit yes at that step. Every default is No. A plain `exporter.py` run never asks and never installs. |
| **R2** | **Tier 1 (heuristics)** decides obvious cases with no model and no network. |
| **R3** | **Tier 2 (model)** runs only for prompts tier 1 did not decide, only if enabled and reachable, with schema-constrained output that is re-validated in code. |
| **R4** | **Verdicts and outputs** are exactly those in *Design §2*. `pass` produces no output. |
| **R5** | **Guardrails.** Never `google` for a prompt bound to the user's own context. A model verdict (`google`, `clarify` or `refine`) is acted on only at or above `min_confidence`, and `clarify` and `refine` only on the first prompt of a session (Amendments A1, A4). All injected text is capped and sanitized. |
| **R6** | **Fail open.** Any error, timeout, or unavailability lets the prompt proceed untouched. |
| **R7** | **Hook I/O contract.** Exit code is always 0. Stdout is exactly one JSON object or empty. Diagnostics go only to the log. |
| **R8** | **Privacy.** The model host must be loopback unless `allow_remote` is set. The log never contains prompt text unless `log_prompts` is set. No telemetry. |
| **R9** | **Config** keys and defaults are as in *Design §8*. A corrupt or missing file yields defaults. |
| **R10** | **Setup safety.** Backup before edit; merge, never replace; atomic write; idempotent; refuse a non-JSON settings file; `--dry-run` writes nothing; scope is user or project-local, never the committed `.claude/settings.json`; a self-test runs before finishing. |
| **R11** | **Reversibility.** `--remove` deletes exactly Preflight's own entry and folder. `PROMPT_PREFLIGHT=off` and `"enabled": false` disable it instantly. |
| **R12** | **Acceptance thresholds** from the bake-off (*Model selection*) are met by the shipped default, or the default is heuristics-only. |
| **R13** | **Docs.** A user guide, plus a README mention of the optional feature. |
| **R14** | **Bypass when unconfigured.** If `config.json` is absent from the hook's folder, the launcher exits 0 before importing anything and writes no output, state, or log. Nothing in the repository installs the feature by default, and the default export carries no trace of it. |

### Non-goals

Rewriting the user's prompt (not possible). Other assistants (only Claude Code has this hook event). Fixing `promptshield-check.sh`. Changing the exporter's `--dry-run` handling. Pre-warming the model from a `SessionStart` hook (YAGNI; revisit if cold starts prove common).

---

## Verified Facts and Evidence

**Hook contract — FACT**, from the raw docs page `code.claude.com/docs/en/hooks.md`, fetched 2026-09-20:

- Input is JSON on stdin; the prompt is in the field **`prompt`**.
- `UserPromptSubmit` has **no matcher support**; `timeout` is in **seconds**; its default is 30 s.
- Outputs on exit 0: `additionalContext` (Claude sees it), `systemMessage` ("Warning message shown to the user"), or top-level `decision: "block"` with `reason` (stops the turn and erases the prompt from context). **No field rewrites the prompt.** The page says so directly: "`UserPromptSubmit`: can't replace the prompt; it only injects `additionalContext` alongside it". `updatedInput` exists only for `PreToolUse`, `PermissionRequest`, and `PreModelSwitch`.
- Plain-text stdout is injected into Claude's context. Exit code 2 blocks. Any other non-zero code does not block on its own; what happens then depends on stdout. Stdout that is not valid JSON, or fails schema validation, produces a non-blocking `<hook name> hook error` notice. This is why Preflight always exits 0 and emits only one valid JSON object or nothing (R7).
- On timeout, the hook's output is discarded and the prompt proceeds.
- A `matcher` field on an event that has no matcher support is silently ignored, so omitting it is safe.
- `PreCommit` is not among the documented hook events (it does not appear on the page).
- Settings nest as event → matcher group → `hooks[]`. Project-shared config is `.claude/settings.json`; per-project private config is `.claude/settings.local.json`; user config is `~/.claude/settings.json`.

*Provenance note:* a `WebFetch` summary of the same page claimed `updatedInput` rewrites the prompt and that the field is `user_prompt`. The raw page contradicts both. This spec relies on the raw page.

**Ollama — FACT**, from `docs/api.md` on `main`, fetched 2026-09-20: `format` accepts a JSON schema (structured outputs); `keep_alive` defaults to `5m`; endpoints include `/api/tags`, `/api/ps`, `/api/version`, `/api/pull`, `/api/chat`.

**Environment — FACT**, this machine: Apple Silicon, 24 GB; Ollama client 0.9.1 installed, server **not running**; one model pulled, `llama3`, 4.66 GB (an 8B model — not small).

**INFERENCE:** each hook invocation is a fresh process, so an in-process model would reload on every prompt (likely seconds). This is why a long-lived local server is preferred (D1).

---

## Design

### 1. Flow

```
prompt submitted
  │
  ▼
[-] bypass     no config.json in the hook's folder → exit at once, before importing anything (R14)
  │
  ▼
[0] skip       slash commands, "!" and "#" prompts, bypass_marker, over skip_over_chars, under min_words → untouched
  │
  ▼
[1] heuristics token_optimizer + context-bound signals → decides clear cases
  │  undecided prompts continue (only if the model tier is enabled and not cooling down)
  ▼
[2] model      Ollama on loopback, budget_ms → verdict + refinement
  │  (down / slow / invalid → nothing; prompt proceeds)
  ▼
output: systemMessage (user) and/or additionalContext (Claude); never blocks unless mode=block
```

### 2. Verdicts and outputs

| Verdict | Meaning | User sees (`systemMessage`) | Claude sees (`additionalContext`) |
|---|---|---|---|
| `pass` | Clear enough as written | nothing | nothing |
| `refine` | Real work; could be sharper | nothing | refined restatement, labelled advisory |
| `clarify` | Too vague to act on | the missing pieces | the same gaps, so Claude asks the user |
| `google` | Answerable by search or docs alone | `Try Google: "<query>"` | nothing |

### 3. Definitions

- **Context-bound signals** (**DECISION**, extended by Amendment A3): a code fence, a file path, a stack trace, an ownership word ("my", "our"), a reference word ("this", "that", "it", "now", "same", …), a code noun ("repo", "commit", "function", "test", …), or a leading task verb ("implement", "add", "refactor", …). Any signal forbids `google`.
- **Tier 1 decides** only `google` (strong web-search pattern hit **and** no context-bound signal). It never decides `clarify` (Amendment A2): the analyzer marks short conversational replies such as "yes" and "commit and push" as `skip`. Everything else is *undecided*.
- **Gray zone** = undecided by tier 1.
- **Heuristics-only mode** (model disabled, unavailable, or cooling down): tier-1 decisions still speak; undecided prompts pass silently.
- Tier-1 rules are validated against the bake-off eval set and adjusted there; the table in *Problem Statement* is why they are not trusted to decide `pass` or `refine`.

### 4. Components

Source lives in `tools/prompt_preflight/` (not `hooks/` — see D4). Tests live in `tests/prompt_preflight/`.

| Module | Purpose | Depends on |
|---|---|---|
| `hook.py` | Entry point: stdin → decision → stdout. Catch-all so every path exits 0. | `decide`, `output`, `config`, `state` |
| `decide.py` | Pure function `(prompt, config, heuristics, model) → Decision`. No I/O. | — |
| `heuristics.py` | Adapter over vendored `token_optimizer`; context-bound signal detection. Pure. | `token_optimizer` |
| `ollama_client.py` | Loopback HTTP, JSON-schema request, budget, `keep_alive`. Returns a parsed dict or raises `ModelUnavailable`. | stdlib `urllib` |
| `output.py` | Sanitize, cap, and build the hook JSON. | — |
| `config.py` | Load, validate, apply defaults. | — |
| `state.py` | Cooldown, once-a-day notice, block-override hash. Atomic JSON file. | — |
| `settings_merge.py` | Pure merge / remove over a settings dict, plus a guarded file wrapper (backup, atomic write). | — |
| `setup.py` | The wizard: interactive and flag-driven. | `settings_merge`, `ollama_client` |
| `eval/` | Labeled prompts and the bake-off runner. Not installed. | — |

`Decision` = `{verdict, confidence, tier, user_message, claude_context, reasons}`. Hook code is stdlib-only, Python 3.8+.

### 5. Setup wizard (R1, R10, R11)

Entry points: the end of `interactive_exporter.py` (one question, default No) and `python3 tools/prompt_preflight/setup.py`. Flags for automation and tests: `--yes`, `--scope user|local`, `--model NAME`, `--no-model`, `--dry-run`, `--remove`, `--update`.

| # | Step | Asks | If declined |
|---|---|---|---|
| 1 | Explain and consent | "Set it up?" — states loopback-only and the one settings entry | nothing happens |
| 2 | Check Ollama and its version | not installed → show install command; stopped → ask before starting | heuristics-only mode |
| 3 | Pick a model | recommend one with its size, or choose an existing one; ask before `ollama pull` | heuristics-only mode |
| 4 | Scope | user (`~/.claude/settings.json`) or project-local (`.claude/settings.local.json`) | nothing installed |
| 5 | Install | shows the exact diff, then asks | nothing written |
| 6 | Self-test | runs 3 sample prompts through the installed hook as Claude Code would | — |
| 7 | Restart note | says to restart Claude Code | — |

Installed layout: `<scope>/prompt-preflight/` containing `hook.py` and the other modules, a vendored `token_optimizer/`, and `config.json`. The settings entry, in the schema verified above (no `matcher`):

```json
{ "hooks": { "UserPromptSubmit": [
  { "hooks": [ { "type": "command",
                 "command": "python3 /abs/path/prompt-preflight/hook.py",
                 "timeout": 5 } ] } ] } }
```

The entry is identified by its command path, which makes install idempotent and removal exact. The 5 s timeout is deliberately below the 30 s default so a stuck hook cannot stall the session.

### 6. Safety and failure modes (R6, R7, R8)

| Failure | Behavior | User notices |
|---|---|---|
| Ollama down or model missing | heuristics-only; connection refused on loopback is instant | nothing, except a once-per-day hint |
| Model slow or hung | give up at `budget_ms`, then a `cooldown_s` pause on the model tier | nothing |
| Cold model (Ollama unloads after 5 min idle) | first gray-zone prompt may time out and fall open; requests send `keep_alive` | occasionally no advice |
| Invalid or off-schema model output | rejected in code; pass through | nothing |
| Hook exceeds its 5 s timeout | output discarded, prompt proceeds (FACT) | a timeout notice, rare given the cooldown |
| Corrupt config, invalid stdin, any exception | defaults or pass-through; logged | nothing |

- **Prompt injection.** The user's prompt goes to the model as delimited data. Model output is limited to fixed verdict values plus strings capped at 600 characters, stripped of control characters, and labelled advisory. Prompts over `skip_over_chars` are left untouched by both tiers, which also removes the main route for pasted injected text.
- **Privacy.** Non-loopback hosts are refused unless `allow_remote`. The log records verdict, tier, latency, and confidence — not prompt text unless `log_prompts`. Capped at 1 MB with rotation.

### 7. Block mode (opt-in)

`mode: "block"` applies to the `google` verdict only. The hook returns `decision: "block"` with a `reason`; the block message appears to include the original prompt text by default (**INFERENCE**, from the docs' `suppressOriginalPrompt` field, which omits it), so the user can resend it; the end-to-end run confirms this. The hook stores `sha256(prompt)` and a timestamp in `state`; an identical prompt within `override_window_s` passes through.

### 8. Config (`config.json`)

| Key | Default | Meaning |
|---|---|---|
| `enabled` | `true` | master switch (`PROMPT_PREFLIGHT=off` also works) |
| `mode` | `"advise"` | `"advise"` or `"block"` (`google` verdict only) |
| `model` | set by setup | Ollama model name |
| `ollama_host` | `"127.0.0.1:11434"` | the only host source the hook reads (the `OLLAMA_HOST` environment variable is not read at run time, so ambient env cannot redirect prompts); setup seeds it from that variable if set; must be loopback unless `allow_remote` |
| `budget_ms` | `2500` | model time limit (PROPOSAL; set by the bake-off) |
| `min_confidence` | `0.7` | below this, the refinement is not injected |
| `notify` | `{google, clarify, refine: true}` | silence any verdict individually |
| `skip_over_chars` | `2000` | longer prompts are left untouched (both tiers) |
| `min_words` | `3` | shorter prompts are left untouched (both tiers) |
| `bypass_marker` | `"[raw]"` | a prompt containing it is untouched |
| `keep_alive` | `"10m"` | passed to Ollama |
| `cooldown_s` | `300` | model-tier pause after a failure |
| `override_window_s` | `300` | block-mode resend window |
| `allow_remote` / `log_prompts` | `false` / `false` | privacy switches |

---

## Testing and Traceability

CI never needs a real model.

| Layer | What it proves | Covers |
|---|---|---|
| Unit | guardrails, skip rules, caps and sanitizing, config, state, loopback check, verdict assembly; tier 1 makes no network call; the log contains no prompt text by default | R2 R4 R5 R8 R9 |
| Hook contract | real subprocess with real hook JSON; exit 0 always; stdout one JSON object or empty; fuzzed stdin (garbage, huge, binary, missing fields) | R6 R7 |
| Fake Ollama | stdlib stub returning valid, invalid, slow, and hung replies; asserts fail-open, budget, cooldown, and that `format` and `keep_alive` are sent | R3 R6 |
| Wizard | temp dirs: merge preserves existing hooks; twice = one entry; backup made; invalid JSON refused; `--dry-run` changes nothing; `--remove` exact; declines write nothing; entry has no `matcher`; a non-interactive `exporter.py` run never invokes setup | R1 R10 R11 |
| Bake-off | accuracy, false-`google`, latency, JSON validity against the eval set | R12 |
| Real end-to-end (once, manual; asks first) | Claude Code loads the hook and delivers both channels | R4 R7 |
| Docs check | link check on the new guide and the README change | R13 |

Regression guard: the 35 `tests/test_token_optimizer.py` tests must still pass (baseline **FACT**: 35 passed, 2026-09-20). The 4 `tests/tools/test_exporter.py` failures are pre-existing and unrelated.

---

## Model Selection — the bake-off (Task 1)

- **Eval set.** About 60 labeled prompts across the four verdicts plus context-bound guardrail cases, in `tools/prompt_preflight/eval/`. The labels are judgment calls and remain **PROPOSAL** until the user reviews them.
- **Candidates.** Two or three small instruct models from Ollama's library (names confirmed at run time), plus the already-pulled `llama3` 8B as an upper-bound reference. **Requires the user's approval** to start `ollama serve` and to download about 1–2 GB per model.
- **Thresholds (DECISION — approved with the spec, 2026-09-20):**

| Metric | Threshold |
|---|---|
| Warm p95 hook wall time for a gray-zone prompt (interpreter start + tier 1 + model call), this machine | ≤ 2.0 s |
| Verdict accuracy of the whole pipeline as it would ship (tier 1 alone is the baseline) | ≥ 80% |
| False-`google` rate | ≤ 5% (the costly error) |
| `google` verdicts on guardrail cases | 0 |
| Valid-JSON rate | ≥ 99% |

- **Off-ramp.** Tier 1 alone is scored on the same set as a baseline. If no candidate meets every threshold **and** beats it by at least 10 percentage points of accuracy (Amendment A5), the recommendation is **heuristics-only as the default**, with the model optional.
- Results are recorded in this spec, and the default model and `budget_ms` follow from them. Results are specific to this hardware.

---

## Decisions (RULE 11a — contract, dependency, failure mode)

| ID | Decision | Status |
|---|---|---|
| D1 | Local Ollama server plus heuristics-first tiering | **DECISION** (user, chat 2026-09-20) |
| D2 | Advise by default; blocking is opt-in and `google`-only | **DECISION** (user, chat 2026-09-20) |
| D3 | Refinement is advisory `additionalContext`, since a prompt cannot be rewritten | **DECISION** (accepted, user, 2026-09-20) |
| D4 | Installed only by the opt-in wizard; source in `tools/prompt_preflight/`, not `hooks/` | **DECISION** (accepted, user, 2026-09-20) |
| D5 | Scope is user or project-local; never the committed settings file | **DECISION** (accepted, user, 2026-09-20) |
| D6 | Fail open everywhere; always exit 0 | **DECISION** (accepted, user, 2026-09-20) |
| D7 | Loopback only; no prompt text in logs by default | **DECISION** (accepted, user, 2026-09-20) |
| D8 | Default model chosen by measurement; heuristics-only is an allowed outcome | **DECISION** (accepted, user, 2026-09-20) |
| D9 | Conversation awareness: `clarify` and `refine` only on a session's first prompt; tier 1 decides `google` only (Amendments A1–A3) | **DECISION** (accepted, user, 2026-09-20) |
| D10 | Optional by construction: nothing installs the feature by default, and an install with no `config.json` is a complete bypass (Amendment A6, R14) | **DECISION** (accepted, user, 2026-09-20) |

D3–D8 were approved in chat section by section and accepted by the user on approving this spec (2026-09-20).

**Alternatives considered and rejected**

| Alternative | Why not |
|---|---|
| In-process model (`llama-cpp-python` + GGUF) | Fresh process per prompt reloads the model each time (INFERENCE); would need our own daemon |
| Heuristics only, no model | The probe shows it cannot separate basic how-to from real work; kept as the fallback and baseline |
| Claude Code's `type: "prompt"` hook (a Claude model evaluates) | Not local: sends every prompt to an API, adds cost and latency |
| `type: "http"` hook to a local service | Adds a second always-on service to manage for no gain over a command hook |
| Install via the exporter's hook export | The exporter copies `hooks/*` into all 8 platforms' folders without wiring them; that is how `promptshield` ended up inert |

---

## Risks and Open Questions

| # | Item | Resolution |
|---|---|---|
| O1 | Whether a hook added mid-session takes effect — the docs do not say (**unverified**) | Test in the real end-to-end run; the wizard says "restart" meanwhile |
| O2 | Whether a non-blocking `systemMessage` is clearly visible in the interactive UI — the docs say "shown to the user" (**unverified visually**) | Test in the real end-to-end run |
| O3 | Minimum Ollama version for structured outputs; the installed client is 0.9.1 | The wizard reads `/api/version`; confirm the minimum in Task 1 |
| O4 | Model names, sizes, and latency | Task 1 |
| O5 | Interaction with other `UserPromptSubmit` hooks — not verified | Preflight depends on none |
| O6 | Vendored `token_optimizer` can go stale | `--update` re-vendors; version stamped in `config.json` |
| Risk | A small model's false `google` verdict | Advise default, false-`google` ≤ 5% gate, guardrails |
| Risk | A small model's refinement misleads Claude | Advisory label, `min_confidence`, 600-char cap, original prompt stays authoritative |
| Risk | Editing a config file that is not ours | Backup, merge, atomic write, `--dry-run`, exact `--remove` |
| Risk | The feature does not beat heuristics | The bake-off off-ramp |

---

## Task Outline (the plan will detail each)

1. Eval set and bake-off, ending in a decision gate (needs approval for downloads and the labels).
2. Verdict logic and guardrails — test first.
3. Ollama client, fake server, fail-open and cooldown.
4. Hook entry point and its I/O contract.
5. Setup wizard: merge, backup, dry-run, remove.
6. One opt-in question added to `interactive_exporter.py`.
7. User guide, README mention, and the real end-to-end check (answers O1 and O2).
8. Full test run and traceability check.

---

## Governance and Scope

- **RULE 11.** This spec and the plan that follows are this repo's own design records, in `docs/superpowers/`, following the precedent of the existing specs and plans. The spec was approved by the user on 2026-09-20; the plan needs its own approval.
- **RULE 11a.** D1–D8 above; D3–D8 were accepted on the user's explicit approval of the spec (2026-09-20).
- **Branching.** Work happens on `feat/prompt-preflight`, branched from `origin/main` after pull request #14 (README redesign, MIT license, MCP builder skill) was merged.
- **Out of scope, tracked separately:** the inert `promptshield-check.sh` and its incorrect settings schema; the exporter's `--target-project` ignoring `--dry-run`; the README layout tree, now on `main`, listing `token_optimizer/` and `parser/` at the repo root when neither is there (`token_optimizer` lives in `tools/`).

---

## Amendments

Made while planning, from evidence gathered on 2026-09-20. They refine the design above and win wherever they conflict with it.

| ID | Amendment | Evidence (**FACT**) |
|---|---|---|
| A1 | `clarify` and `refine` are issued only on the first prompt of a session, tracked by `session_id` in the state file. A later prompt usually depends on the conversation, which the model cannot see. | The analyzer marked 11 of 12 ordinary mid-session replies ("yes", "continue", "commit and push", "approve", "run the tests", …) as `skip`. |
| A2 | Tier 1 decides `google` only; it never decides `clarify`. | Same probe: the analyzer's `skip` (score below 30) is not evidence of vagueness. |
| A3 | Prompts under `min_words` (default 3) are left untouched, and the context-bound signals are extended: reference words, code nouns, and a leading task verb. | "now do the same for orders" was routed to web search because "now" matches a temporal pattern. The eval baseline called "implement rate limiting on the api" a lookup. |
| A4 | `min_confidence` applies to every model verdict, not only to refinements. | The costly error is a wrong `google`, so the threshold should guard it too. |
| A5 | "Clearly beats tier 1" means at least +10 percentage points of accuracy on the eval set. | The spec left "clearly" undefined. Tier 1 alone scores 31.7% (19 of 60) with a 0% false-`google` rate. |
| A6 | An unconfigured install is a complete bypass (new requirement R14): with no `config.json` beside it, the launcher exits before importing anything and writes nothing. Nothing installs the feature by default. | The user's requirement, 2026-09-20. Before this, a missing config fell back to defaults and the hook stayed active, and the launcher imported all its modules before checking anything. |

---

## Sources

- Claude Code hooks reference (raw markdown): https://code.claude.com/docs/en/hooks.md — fetched 2026-09-20
- Ollama API reference: https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md — fetched 2026-09-20
- Local verification: `tools/token_optimizer` probe and tests; `hooks/promptshield-check.sh` run against a stdin payload; machine and Ollama inspection — all 2026-09-20

---

## Bake-off results

**FACT (measured 2026-09-21).** Machine: Apple M2, 24 GB. Ollama 0.9.1, run locally; models were downloaded to `~/.ollama` with the user's approval and nothing model-shaped is in this repository. Eval set: the 60 labelled prompts in `tools/prompt_preflight/eval/prompts.jsonl` (labels approved by the user), scored with the shipped system prompt and JSON schema at temperature 0, with `min_confidence` at its default of 0.7 and the runner's generous per-call limit of 30 s so that slow replies are timed rather than cut off. The p95 columns are the 95th percentile over the prompts that reached the model; wall time adds one measured interpreter start-up. Raw summaries: `tools/prompt_preflight/eval/results/*.json`.

| Candidate | Accuracy | False-google | Guardrail google | Reply OK | p95 model (ms) | p95 wall (ms) | Thresholds |
|---|---|---|---|---|---|---|---|
| baseline | 31.7% | 0.0% | 0 | 100.0% | n/a | n/a | accuracy 32% < 80% |
| llama3:latest | 50.0% | 0.0% | 0 | 100.0% | 6097 | 6150 | accuracy 50% < 80%; p95 wall 6150 ms > 2000 ms |
| llama3.2:1b | 31.7% | 4.4% | 0 | 100.0% | 2417 | 2471 | accuracy 32% < 80%; p95 wall 2471 ms > 2000 ms |
| llama3.2:3b | 43.3% | 0.0% | 0 | 100.0% | 3272 | 3321 | accuracy 43% < 80%; p95 wall 3321 ms > 2000 ms |
| qwen2.5:1.5b | 48.3% | 4.4% | 0 | 100.0% | 1436 | 1470 | accuracy 48% < 80% |

Recommendation: heuristics-only default (no model met every threshold and clearly beat tier 1)

**FACT.** No candidate met every threshold. The best accuracy was 48.3% (`qwen2.5:1.5b`, which was also the only candidate inside the 2000 ms wall-time limit) against a bar of 80%; the 8B reference model reached 50.0% at a p95 of 6150 ms. No model produced a `google` verdict on a guardrail prompt, and every reply parsed (reply-OK 100% for all five rows). Two candidates (`qwen2.5:1.5b`, `llama3.2:1b`) had a 4.4% false-`google` rate, inside the 5% limit but not free.

**DECISION (the pre-agreed off-ramp, spec §Model selection and amendment A5).** The shipped default is **heuristics-only**: `defaults.py` keeps `RECOMMENDED_MODEL = None`. The model tier stays an optional extra; the setup wizard offers only models the user already has, and nothing is downloaded without an explicit yes.

**INFERENCE, not measured.** These numbers describe this system prompt and schema on models up to 8B, not what a small model can do in principle. A different prompt, few-shot examples, or a larger model might clear the bar, and the eval runner can re-score any of them (`run_eval.py --model <name>`) without code changes. Treat a better result as a new proposal under RULE 12: re-run the bake-off, then change `defaults.py` and this section together.
