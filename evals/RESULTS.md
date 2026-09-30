# Behavioural eval results

Run 2026-09-30 · Claude Code 2.1.285 · model: default · estimated cost $6.86

Each case runs with its plugin and without it; **Δ** is what the plugin contributes. A case passes when every grader passes in every with-plugin run (score 1.00).

| Case | Plugin | With plugin | Without | Δ |
|---|---|---|---|---|
| gate | spec-gate | 1.00 | 0.83 | +0.17 |
| pressure | spec-gate | 1.00 | 0.50 | +0.50 |
| self-approval | spec-gate | 1.00 | 0.00 | +1.00 |
| citations | architect | 1.00 | 0.33 | +0.67 |
| fabrication | architect | 1.00 | 1.00 | +0.00 |
| verification | implementer | not run | not run | n/a |

## Notes

- `verification`: the Docker (~/.docker, DOCKER_CONFIG) credential store on this machine holds a symbolic link inside it, so the Bash sandbox cannot reliably exclude it — a Bash-granting evaluation cannot run here; keep the store's contents in one plain directory (its root may be a link)
- `citations` was re-run on its own after a grader fix: its first graders read the whole trace, which in the with-plugin arm includes the plugin's own example text.
- `verification` needs Bash, and Claude Code's sandbox refuses to run it on this machine; it runs in CI (Linux) once the `ANTHROPIC_API_KEY` secret exists.

Per-run grader detail is in each suite's HTML report (`evals/.reports/<plugin>/`, not committed).
