import copy
import re
from pathlib import Path

from prompt_preflight.config import DEFAULTS
from prompt_preflight.hook import MAX_MODEL_BUDGET_MS
from prompt_preflight.decide import Decision
from prompt_preflight.output import build_output

COVERS = ["R13"]

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs" / "03-guides" / "prompt-preflight.md"
GUIDES_INDEX = ROOT / "docs" / "03-guides" / "README.md"
README = ROOT / "README.md"


def relative_links(path):
    text = path.read_text(encoding="utf-8")
    targets = re.findall(r"\]\(([^)\s]+)\)", text)
    return [t.split("#")[0] for t in targets if not t.startswith(("http://", "https://", "mailto:", "#"))]


def test_every_relative_link_in_the_guide_resolves():
    assert GUIDE.exists()
    missing = [t for t in relative_links(GUIDE) if t and not (GUIDE.parent / t).exists()]
    assert missing == []


def test_the_guide_documents_every_config_key():
    guide = GUIDE.read_text(encoding="utf-8")
    assert [key for key in DEFAULTS if "`%s`" % key not in guide] == []


def test_the_guide_states_the_real_model_budget_cap():
    assert "`%d`" % MAX_MODEL_BUDGET_MS in GUIDE.read_text(encoding="utf-8")


def test_the_guide_covers_the_verdicts_and_the_ways_to_turn_it_off_or_undo_it():
    guide = GUIDE.read_text(encoding="utf-8")
    for needle in ("`google`", "`clarify`", "`refine`", "`pass`", "PROMPT_PREFLIGHT=off", "--remove", "--dry-run", "--update", '"enabled": false', "does nothing at all"):
        assert needle in guide, needle


def test_the_guide_quotes_the_messages_the_hook_really_prints():
    guide = GUIDE.read_text(encoding="utf-8")
    cfg = copy.deepcopy(DEFAULTS)
    google = build_output(Decision("google", 1, google_query="python reverse list"), cfg)["systemMessage"]
    clarify = build_output(Decision("clarify", 2, missing=["which file", "the expected outcome"]), cfg)["systemMessage"]
    assert google in guide and clarify in guide


def test_the_readme_and_the_guides_index_link_to_the_guide():
    # Only the new links are checked here; an unrelated broken README link is not this feature's failure.
    assert "(docs/03-guides/prompt-preflight.md)" in README.read_text(encoding="utf-8")
    assert "(prompt-preflight.md)" in GUIDES_INDEX.read_text(encoding="utf-8")
    assert GUIDE.exists()
