# Prompt Preflight

An **optional** Claude Code hook that looks at each prompt before Claude does. **It is off unless you set it
up:** nothing installs it by default, and until you do, no hook exists for Claude Code to run. It can tell you a
question is basic enough for a web search and, if you also choose a small local model, give Claude a
sharper restatement of a vague request and tell you when a prompt is too vague to act on. It runs on your
machine, only when you set it up, and it
never gets in your way: if anything goes wrong it steps aside and your prompt goes through untouched.

Design and decisions: [the design spec](../superpowers/specs/2026-09-20-prompt-preflight-hook-design.md).

## What you will see

| Verdict | You see | Claude sees |
|---|---|---|
| `google` — a search would answer it | `Prompt Preflight: quick lookup — try Google: "python reverse list"` | nothing; the prompt goes through |
| `clarify` — too vague to act on (needs a model) | `Prompt Preflight: this may be too vague to act on. Missing: which file; the expected outcome` | the same gaps, so it asks you |
| `refine` — real work that could be sharper (needs a model) | nothing | an advisory restatement, labelled as coming from a small local model |
| `pass` — clear as written | nothing | nothing |

Silence is the default: it speaks only when it has something useful to say. Without a model (the default)
only the `google` line is ever shown.

The hook cannot rewrite your prompt (Claude Code does not allow that), so refinements are advisory
context and your original prompt always stays authoritative.

**When it stays out of the way.** It leaves a prompt untouched if it starts with `/`, `!` or `#`, is
shorter than `min_words` words, is longer than `skip_over_chars` characters, or contains `[raw]`. It
never says "try Google" about your own code or work (a code block, a file path, a stack trace, "my",
"this repo", "now", "the same", a task verb such as "write" or "fix", or a code word such as "test",
"build" or "endpoint"), which is also why it speaks up rarely, and it only speaks up about `clarify` and `refine` on the **first prompt of a
session**, because a later prompt usually depends on the conversation, which a small model cannot see.

## Set it up

```bash
python3 tools/prompt_preflight/setup.py            # interactive
python3 tools/prompt_preflight/setup.py --dry-run  # show exactly what would change; writes nothing
```

"This project only" means the project directory the wizard is run for: the current directory, or the one you
pass with `--project <dir>`. Use the same `--project <dir>` (and `--scope`) for `--update` and `--remove`
later, or they will look in the wrong place. The interactive export passes the project it exported to.

It is also offered, defaulting to No, at the end of `python3 tools/exporter.py --interactive`. A plain
`exporter.py` run never asks about it and never installs it.

The wizard asks before every step and does nothing you decline:

1. explains what it does and what stays on your machine;
2. checks for Ollama, and asks before starting it;
3. lets you pick a model (or heuristics-only), and asks before downloading one;
4. asks where to install: **this project only** (`.claude/settings.local.json`, private to you) or
   **all your projects** (`~/.claude/settings.json`). It never edits a committed `.claude/settings.json`;
5. shows the exact settings diff and asks to confirm;
6. installs, then runs a self-test on three sample prompts.

`--yes` answers the install questions for a scripted run: it never starts Ollama, never chooses a model on its own (name one with `--model`), and never edits a settings file that is not valid JSON.

Restart Claude Code afterwards so it loads the hook.

**What it changes:** one hook entry in the settings file you chose (a `.bak-<timestamp>` copy is made
first, your other settings are kept, and a settings file that is not valid JSON is refused, not
overwritten), and a `prompt-preflight/` folder next to it.

## Models: heuristics-only or a small local model

**Heuristics-only is the default, and no model is recommended.** We measured four local models on a
60-prompt labelled set (Apple M2, 24 GB, 2026-09-21): the best small model, `qwen2.5:1.5b`, got 48% of prompts right
against a bar of 80% (an 8B model got 50%, and was too slow), so none qualified as a default. The model
tier is therefore **experimental**: it works, and on the 10 guardrail prompts (requests that need your own
code) no model ever said "try Google", but on a small model it is not yet accurate enough to recommend.
The two smallest models did say "try Google" for 2 of the 45 prompts that were not lookups (4.4%): inside
the 5% limit we set, but not zero. Advise mode and the runtime guardrails limit the harm of such a slip; it
is one line of text, not a block. The full table is in the design spec, under "Bake-off results".

- **Heuristics-only** needs nothing installed. It catches clear standalone lookups ("what is the capital
  of France") and never anything else.
- **With a model** it also tries the cases heuristics cannot: basic how-to questions, vague requests,
  and requests worth sharpening. It needs [Ollama](https://ollama.com/download) running locally, with a
  model that supports structured (JSON-schema) output. The wizard lists the models you already have and
  asks before starting Ollama; it recommends nothing to download, and downloads a model only if you name
  one with `--model` and confirm. Models are stored by Ollama on your machine, never in this repository.

If the model is slow, missing, or returns something unusable, Preflight falls back to heuristics-only,
pauses the model for `cooldown_s` seconds so you do not pay for repeated failures, and tells you **once a
day** that it is running heuristics-only.

## Configuration

`config.json` sits in the `prompt-preflight/` folder. Missing or invalid values fall back to the defaults.
Setup also stamps an `installed_version` key into it; it is bookkeeping, not a setting.

| Key | Default | Meaning |
|---|---|---|
| `enabled` | `true` | master switch (`PROMPT_PREFLIGHT=off` in the environment also disables it) |
| `mode` | `"advise"` | `"advise"`, or `"block"` (applies to the `google` verdict only) |
| `model` | `""` (heuristics-only) | Ollama model name; setup fills it in only if you choose a model |
| `ollama_host` | `"127.0.0.1:11434"` | must be loopback unless `allow_remote`; setup copies a loopback `OLLAMA_HOST` here once, and the variable is not read at run time |
| `budget_ms` | `2500` | time limit for one model call; the hook caps it at `4000` so a call always fits inside the 5-second hook timeout that setup writes into the settings entry |
| `min_confidence` | `0.7` | a model verdict below this is ignored |
| `notify` | all `true` | silence one verdict: `google`, `clarify`, or `refine` |
| `skip_over_chars` | `2000` | longer prompts are left untouched |
| `min_words` | `3` | shorter prompts are left untouched |
| `bypass_marker` | `"[raw]"` | a prompt containing it is left untouched |
| `keep_alive` | `"10m"` | how long Ollama keeps the model loaded |
| `cooldown_s` | `300` | model pause after a failure |
| `override_window_s` | `300` | in block mode, how long an identical resend is let through (1 to 86400) |
| `allow_remote` | `false` | allow a non-loopback model host (prompts then leave this machine) |
| `log_prompts` | `false` | include prompt text in the log |

**Block mode.** With `"mode": "block"` a `google` verdict stops the prompt and shows the suggestion;
sending the identical prompt again within `override_window_s` goes through, once: sending it a third time
is blocked again. If Preflight cannot save its
state (for example a read-only install folder) it never blocks: it shows the suggestion and lets the prompt
through.

## Privacy and safety

- Prompts go only to a model on this machine. A non-loopback `ollama_host` is refused unless you set
  `allow_remote`, and environment proxy settings are ignored, so a "localhost" request is never routed
  through a proxy.
- The log (`preflight.log`, rotated at 1 MB) records the verdict, tier, confidence and timing, never the prompt
  text unless you set `log_prompts`. There is no telemetry.
- The hook always exits 0 and prints either one JSON object or nothing, so it cannot produce a Claude Code
  "hook error" or inject stray text into your context. The settings entry ends in `|| true`, so even if you
  delete the `prompt-preflight/` folder by hand, the leftover entry is harmless (Python would otherwise exit
  with code 2 for the missing file, and Claude Code rejects a prompt when a hook exits 2). Run `--remove` to
  tidy the settings file.
- Text it hands to Claude is length-capped and stripped of control characters, and long prompts are never
  sent to the model.

## Turn it off, update, or remove it

```bash
PROMPT_PREFLIGHT=off claude                          # off for one run
python3 tools/prompt_preflight/setup.py --update     # refresh the installed code; your settings stay (only installed_version changes)
python3 tools/prompt_preflight/setup.py --remove     # remove the hook entry and the folder
# for a project other than the current directory, add: --project <dir>   (and --scope user|local if you used one)
```

Set `"enabled": false` in `config.json` to disable it without uninstalling. `--update` never creates a
`config.json` (an install without one stays switched off) and leaves one that is not valid JSON untouched.

**Not configured means bypassed.** With no `config.json` in its folder the hook does nothing at all: it exits
before importing anything, and it writes no state and no log.

## Troubleshooting

| Symptom | Check |
|---|---|
| No advice ever appears | Restart Claude Code after setup; check `PROMPT_PREFLIGHT` is not `off`; look at the newest lines of `prompt-preflight/preflight.log` |
| "running heuristics-only" notice | Ollama is not running, or the configured model is not downloaded; run `ollama list`, then `ollama pull <model>` |
| Advice stopped after one failure | The model is cooling down for `cooldown_s` seconds; it resumes by itself |
| The "running heuristics-only" notice or the same advice repeats on every prompt | The `prompt-preflight/` folder may be read-only, so Preflight cannot save its state; make it writable |
| It said "try Google" about something that needs your code | Add a note to the prompt, use `[raw]`, or set `notify.google` to `false`, and tell us: it is a guardrail gap |

## Measuring it

`tools/prompt_preflight/eval/` holds a 60-prompt labeled set and a runner. It scores the whole pipeline on
accuracy, on the false-`google` rate (telling you to search for something that needed your code), and on
latency.

```bash
python3 tools/prompt_preflight/eval/run_eval.py --baseline           # heuristics only, no model needed
python3 tools/prompt_preflight/eval/run_eval.py --model <ollama-model>
```

Measured on 2026-09-20 and 2026-09-21: heuristics-only scored 31.7% accuracy and never said "try Google"
for a prompt that was not a lookup. It is safe but limited. The small models we tried scored 32% to 48% and none met the 80% bar, so the
default stays heuristics-only; the design spec has the full table, and the runner lets you score any model
or prompt change the same way.
