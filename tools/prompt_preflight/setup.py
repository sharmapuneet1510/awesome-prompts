"""Optional setup wizard for the Prompt Preflight hook. Nothing happens without a yes.

    python3 tools/prompt_preflight/setup.py                 interactive
    python3 tools/prompt_preflight/setup.py --dry-run       show exactly what would change
    python3 tools/prompt_preflight/setup.py --remove        undo the install

Run as a script, or import it as `prompt_preflight.setup` with `tools/` on sys.path.
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

if __package__ in (None, ""):  # started as a script: make `prompt_preflight` importable
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prompt_preflight import __version__, defaults, settings_merge as sm  # noqa: E402
from prompt_preflight.config import DEFAULTS, is_loopback, load_config  # noqa: E402
from prompt_preflight.ollama_client import open_no_proxy  # noqa: E402

PACKAGE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = PACKAGE_DIR.parent
INSTALL_NAME = "prompt-preflight"
SELF_TEST_PROMPTS = (
    "what is the capital of France",
    "make the app work better please",
    "write a python function that parses iso dates from log lines",
)
COPY_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "eval", "README.md", "setup.py", "pyproject.toml")

INTRO = """Prompt Preflight (optional)
  Checks each prompt before Claude sees it: tells you when a web search would do, and can add a
  sharper restatement of vague or under-specified requests.
  - Your prompts go only to a model on this machine (127.0.0.1). Nothing is sent anywhere else.
  - It changes one settings file (backed up first) and adds a folder. `--remove` undoes both.
  - It can never block you by default, and it fails open if anything goes wrong."""


# ---------- I/O helpers ----------------------------------------------------------------------


class ConsoleIO:
    def say(self, text: str = "") -> None:
        print(text)

    def ask_yes_no(self, question: str, default: bool = False) -> bool:
        try:
            answer = input("%s [%s] " % (question, "Y/n" if default else "y/N")).strip().lower()
        except EOFError:
            return default
        return default if not answer else answer in ("y", "yes")

    def choose(self, question: str, options: Sequence[str], default: int = 0) -> int:
        print(question)
        for number, option in enumerate(options, 1):
            print("  %d) %s" % (number, option))
        while True:
            try:
                answer = input("Choice [%d]: " % (default + 1)).strip()
            except EOFError:
                return default
            if not answer:
                return default
            if answer.isdigit() and 1 <= int(answer) <= len(options):
                return int(answer) - 1


class RealOllama:
    """Talks to a local Ollama. All HTTP is loopback and ignores proxy settings."""

    def __init__(self, host: str = "127.0.0.1:11434") -> None:
        self._host = host

    def installed(self) -> bool:
        return shutil.which("ollama") is not None

    def _get(self, path: str) -> Optional[Dict[str, Any]]:
        import urllib.request

        try:
            with open_no_proxy(urllib.request.Request("http://%s%s" % (self._host, path)), 2.0) as response:
                return json.loads(response.read().decode("utf-8"))
        except (OSError, ValueError):
            return None

    def is_running(self) -> bool:
        return self._get("/api/version") is not None

    def models(self) -> List[Dict[str, Any]]:
        body = self._get("/api/tags") or {}
        return [{"name": m["name"], "size": m.get("size", 0)} for m in body.get("models", []) if "name" in m]

    def pull(self, name: str) -> bool:
        return subprocess.run(["ollama", "pull", name]).returncode == 0

    def start(self) -> bool:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        for _ in range(20):
            if self.is_running():
                return True
            time.sleep(0.5)
        return False


# ---------- locations and files --------------------------------------------------------------


def paths_for(scope: str, home: str, project: str) -> Tuple[Path, Path]:
    """(install dir, settings file). Never the committed .claude/settings.json."""
    base = Path(home) / ".claude" if scope == "user" else Path(project) / ".claude"
    return base / INSTALL_NAME, base / ("settings.json" if scope == "user" else "settings.local.json")


def command_for(install_dir: Path) -> str:
    """The settings entry. `|| true` matters: if the install folder is ever deleted by hand, python exits 2
    for the missing script, and for a UserPromptSubmit hook exit 2 blocks every prompt."""
    return 'python3 "%s" || true' % (install_dir / "hook.py")


def build_config(model: str, env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    cfg = copy.deepcopy(DEFAULTS)
    cfg["model"] = model
    seeded = (env if env is not None else os.environ).get("OLLAMA_HOST", "")
    if seeded and is_loopback(seeded):
        cfg["ollama_host"] = seeded
    if model:
        cfg["budget_ms"] = defaults.RECOMMENDED_BUDGET_MS
    cfg["installed_version"] = __version__
    return cfg


def copy_files(install_dir: Path) -> None:
    install_dir.mkdir(parents=True, exist_ok=True)
    for name in ("prompt_preflight", "token_optimizer"):
        target = install_dir / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(TOOLS_DIR / name, target, ignore=COPY_IGNORE)
    shutil.copy2(PACKAGE_DIR / "launcher.py", install_dir / "hook.py")
    (install_dir / ".gitignore").write_text("*\n", encoding="utf-8")


def _read_config(path: Path) -> Optional[Dict[str, Any]]:
    """The parsed config object, or None if the file is missing or is not a JSON object."""
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return cfg if isinstance(cfg, dict) else None


def write_config(install_dir: Path, model: str) -> Optional[Path]:
    """Install: keep the user's edits to an existing config and set the model and version; otherwise write
    defaults. A config that exists but cannot be parsed is copied aside first (returned), never just replaced."""
    path = install_dir / "config.json"
    cfg = _read_config(path)
    saved: Optional[Path] = None
    if cfg is None:
        if path.exists():
            saved = path.with_name("config.json.bak-%s" % time.strftime("%Y%m%d%H%M%S"))
            shutil.copy2(path, saved)
        cfg = build_config(model)
    else:
        cfg["model"] = model
    cfg["installed_version"] = __version__
    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return saved


def refresh_config(install_dir: Path) -> str:
    """Update: stamp the version into an existing valid config and touch nothing else. Never creates one
    (no config.json means the hook is bypassed, and an update must not switch it on). Returns
    "kept", "missing" or "unreadable"."""
    path = install_dir / "config.json"
    cfg = _read_config(path)
    if cfg is None:
        return "unreadable" if path.exists() else "missing"
    cfg["installed_version"] = __version__
    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return "kept"


# ---------- model choice ---------------------------------------------------------------------


@dataclass
class ModelPlan:
    name: str = ""  # "" = heuristics-only
    pull: bool = False
    start_ollama: bool = False


def _choose_model(args: argparse.Namespace, io: Any, ollama: Any) -> ModelPlan:
    """Gather consent for the model steps. Nothing is downloaded or started here."""
    if args.no_model:
        return ModelPlan()
    installed = ollama.installed()
    if not installed:
        io.say("Ollama is not installed (https://ollama.com/download, or `brew install ollama`).")
        io.say("Continuing in heuristics-only mode; re-run this setup after installing it.")
        return ModelPlan()
    if args.yes and not args.model:
        return ModelPlan()  # --yes answers the install questions; a model is only ever chosen on purpose
    running = ollama.is_running()
    start = False
    if not running and not args.yes:
        start = io.ask_yes_no("Ollama is installed but not running. Start it now?", False)
    have = {m["name"]: m["size"] for m in ollama.models()} if running else {}

    if args.model:
        if not running and not start:
            io.say("Ollama is not running: %s will work once Ollama is running and `ollama pull %s` is done." % (args.model, args.model))
        return ModelPlan(args.model, pull=args.model not in have and (running or start), start_ollama=start)
    if not running and not start:
        io.say("Ollama is not running: heuristics-only mode.")
        return ModelPlan()

    options: List[str] = []
    plans: List[ModelPlan] = []
    for name, size in have.items():
        options.append("Use %s (already downloaded, %.1f GB)" % (name, size / 1e9))
        plans.append(ModelPlan(name, False, start))
    recommended = defaults.RECOMMENDED_MODEL
    if recommended and recommended not in have:
        size = defaults.RECOMMENDED_MODEL_SIZE_GB
        options.append("Download %s (recommended%s)" % (recommended, ", %.1f GB" % size if size else ""))
        plans.append(ModelPlan(recommended, True, start))
    options.append("Heuristics only (no model)")
    plans.append(ModelPlan())
    default = len(plans) - 1
    if recommended:
        default = next((i for i, p in enumerate(plans) if p.name == recommended), default)
    return plans[io.choose("Which model should Preflight use?", options, default)]


# ---------- install / update / remove --------------------------------------------------------


def _show_plan(io: Any, install_dir: Path, settings_path: Path, plan: ModelPlan, before: sm.Settings, after: sm.Settings) -> None:
    io.say("")
    io.say("This will:")
    io.say("  - copy Preflight into %s" % install_dir)
    io.say("  - edit %s (a backup is made first):" % settings_path)
    for line in sm.diff_text(before, after, settings_path.name).splitlines():
        io.say("      " + line)
    if plan.start_ollama:
        io.say("  - start Ollama in the background")
    if plan.pull:
        io.say("  - download the model %s with `ollama pull`" % plan.name)
    io.say("  - model: %s" % (plan.name or "none (heuristics-only)"))


def _self_test(install_dir: Path, io: Any) -> bool:
    """Run sample prompts through the exact command written to settings, as Claude Code would."""
    command = command_for(install_dir)
    state, log = install_dir / "state.json", install_dir / "preflight.log"
    existed = (state.exists(), log.exists())
    cfg = load_config(str(install_dir / "config.json"))
    first = SELF_TEST_PROMPTS[0]
    # A kept config can legitimately silence the lookup advice; that must not read as a broken install.
    expects_advice = cfg["enabled"] and cfg["notify"]["google"] and len(first.split()) >= cfg["min_words"] and len(first) <= cfg["skip_over_chars"]
    env = {k: v for k, v in os.environ.items() if k != "PROMPT_PREFLIGHT"}
    # The command ends in `|| true`, so its exit code is always 0: what proves the install is that the files
    # exist, `python3` resolves the way Claude Code will resolve it, and every answer is empty or one JSON object.
    ready = (install_dir / "hook.py").exists() and (install_dir / "prompt_preflight" / "hook.py").exists()
    ready = ready and shutil.which("python3", path=env.get("PATH")) is not None
    clean, advised = True, False
    io.say("")
    io.say("Self-test:")
    try:
        for index, prompt in enumerate(SELF_TEST_PROMPTS):
            payload = json.dumps({"hook_event_name": "UserPromptSubmit", "session_id": "self-test-%d" % index, "prompt": prompt})
            try:
                done = subprocess.run(command, shell=True, input=payload.encode(), capture_output=True, timeout=30, env=env)
            except subprocess.TimeoutExpired:
                io.say('  "%s" -> TIMED OUT after 30 seconds' % prompt)
                clean = False
                continue
            text = done.stdout.decode("utf-8", "replace").strip()
            note = "silent (no advice)"
            if text:
                try:
                    parsed = json.loads(text)
                    if not isinstance(parsed, dict):
                        raise ValueError
                    note = parsed.get("systemMessage", "adds context for Claude")
                except ValueError:
                    note, clean = "INVALID OUTPUT", False
            io.say('  "%s" -> %s' % (prompt, note))
            if index == 0:
                advised = "Google" in text
        if not expects_advice:
            io.say("  (advice is switched off in config.json, so the first prompt is expected to be silent)")
        passed = ready and clean and (advised or not expects_advice)
    finally:
        for path, was_there in zip((state, log), existed):
            if not was_there and path.exists():
                path.unlink()
    return passed


def _warn_if_not_ignored(io: Any, project: str, settings_path: Path) -> None:
    if not shutil.which("git"):
        return
    checked = subprocess.run(["git", "-C", project, "check-ignore", "-q", str(settings_path)], capture_output=True)
    if checked.returncode == 1:
        io.say("")
        io.say("Note: %s is not git-ignored. Add it to .gitignore so personal tooling is not committed." % settings_path)


def _install(args: argparse.Namespace, io: Any, ollama: Any, home: str, project: str) -> int:
    io.say(INTRO)
    io.say("")
    if not args.yes and not io.ask_yes_no("Set up the Prompt Preflight?", False):
        io.say("Nothing was installed.")
        return 0
    plan = _choose_model(args, io, ollama)
    scope = args.scope
    if not scope:
        scope = "local" if args.yes else ["local", "user"][
            io.choose(
                "Where should it be installed?",
                ["This project only (.claude/settings.local.json, private to you)", "All my projects (~/.claude/settings.json)"],
                0,
            )
        ]
    install_dir, settings_path = paths_for(scope, home, project)
    before = sm.read_settings(str(settings_path))
    after = sm.add_hook(before, command_for(install_dir))
    _show_plan(io, install_dir, settings_path, plan, before, after)
    if args.dry_run:
        io.say("")
        io.say("Dry run: nothing was written, downloaded, or started.")
        return 0
    if not args.yes and not io.ask_yes_no("Install?", False):
        io.say("Nothing was installed.")
        return 0

    model = plan.name
    if plan.start_ollama and not ollama.start():
        io.say("Could not start Ollama: continuing in heuristics-only mode.")
        model = ""
    elif plan.pull and not ollama.pull(plan.name):
        io.say("Could not download %s: continuing in heuristics-only mode." % plan.name)
        model = ""

    copy_files(install_dir)
    saved_config = write_config(install_dir, model)
    backup = sm.write_settings(str(settings_path), after)
    io.say("")
    io.say("Installed to %s" % install_dir)
    if saved_config:
        io.say("The existing config.json was not a valid JSON object; it was copied to %s and replaced with defaults." % saved_config)
    if backup:
        io.say("Backed up your settings to %s" % backup)
    if scope == "local":
        _warn_if_not_ignored(io, project, settings_path)
    if not _self_test(install_dir, io):
        io.say("")
        io.say("The self-test failed: the hook did not answer as expected. Run `--remove` to undo the install.")
        return 3
    io.say("")
    io.say("Done. Restart Claude Code so it loads the hook. Turn it off any time with PROMPT_PREFLIGHT=off.")
    return 0


def _scopes(args: argparse.Namespace) -> List[str]:
    return [args.scope] if args.scope else ["local", "user"]


def _remove(args: argparse.Namespace, io: Any, home: str, project: str) -> int:
    found = []
    for scope in _scopes(args):
        install_dir, settings_path = paths_for(scope, home, project)
        settings = sm.read_settings(str(settings_path))
        if sm.has_hook(settings) or install_dir.exists():
            found.append((scope, install_dir, settings_path, settings))
    if not found:
        io.say("Nothing to remove: no Prompt Preflight install found.")
        return 0
    for scope, install_dir, settings_path, settings in found:
        io.say("Found the %s install: %s" % (scope, install_dir))
        if sm.has_hook(settings):
            for line in sm.diff_text(settings, sm.remove_hook(settings), settings_path.name).splitlines():
                io.say("    " + line)
    if args.dry_run:
        io.say("Dry run: nothing was removed.")
        return 0
    if not args.yes and not io.ask_yes_no("Remove it?", False):
        io.say("Nothing was removed.")
        return 0
    for scope, install_dir, settings_path, settings in found:
        if sm.has_hook(settings):
            backup = sm.write_settings(str(settings_path), sm.remove_hook(settings))
            if backup:
                io.say("Backed up your settings to %s" % backup)
        if install_dir.is_symlink():
            install_dir.unlink()  # rmtree refuses a symlink; remove the link, not what it points at
        elif install_dir.exists():
            shutil.rmtree(install_dir)
    io.say("Removed. Restart Claude Code to unload the hook.")
    return 0


def _update(args: argparse.Namespace, io: Any, home: str, project: str) -> int:
    targets = [paths_for(s, home, project)[0] for s in _scopes(args)]
    targets = [t for t in targets if (t / "hook.py").exists()]
    if not targets:
        io.say("Nothing to update: no Prompt Preflight install found.")
        return 0
    for install_dir in targets:
        if args.dry_run:
            io.say("Would refresh the code in %s (config kept)." % install_dir)
            continue
        copy_files(install_dir)
        outcome = refresh_config(install_dir)
        if outcome == "kept":
            io.say("Updated %s (config kept)." % install_dir)
        elif outcome == "missing":
            io.say("Updated the code in %s. It has no config.json, so the hook stays switched off." % install_dir)
        else:
            io.say("Updated the code in %s. config.json is not a valid JSON object, so it was left exactly as it is." % install_dir)
    return 0


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optional setup for the Prompt Preflight hook.")
    parser.add_argument("--scope", choices=("user", "local"), help="user: all projects; local: this project only")
    parser.add_argument("--project", help="project directory for --scope local (default: current directory)")
    parser.add_argument("--home", help="home directory for --scope user (default: your home)")
    parser.add_argument("--model", help="Ollama model to use (downloaded only if you also confirm or pass --yes)")
    parser.add_argument("--no-model", action="store_true", help="heuristics-only, no model")
    parser.add_argument("--yes", action="store_true", help="answer yes to install questions; never starts Ollama")
    parser.add_argument("--dry-run", action="store_true", help="show what would change and write nothing")
    parser.add_argument("--remove", action="store_true", help="remove Preflight")
    parser.add_argument("--update", action="store_true", help="refresh the installed code, keeping config")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None, io: Any = None, ollama: Any = None) -> int:
    args = parse_args(argv)
    io = io or ConsoleIO()
    home = os.path.abspath(os.path.expanduser(args.home or "~"))  # the hook command must not depend on the cwd
    project = os.path.abspath(args.project or os.getcwd())
    try:
        if args.remove:
            return _remove(args, io, home, project)
        if args.update:
            return _update(args, io, home, project)
        return _install(args, io, ollama or RealOllama(), home, project)
    except sm.SettingsError as exc:
        io.say("Stopped. Nothing was changed: %s" % exc)
        return 1
    except (OSError, subprocess.TimeoutExpired) as exc:
        io.say("Stopped: %s. Fix that and run the setup again (it is safe to repeat), or run `--remove`." % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
