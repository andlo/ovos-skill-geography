"""Every vocabulary line must be a plain phrase: ovos-workshop reads .voc
lines as templates, and one bad line (e.g. "code -> name", an unbalanced
angle bracket) makes the whole skill fail to load (0.0.6 did, in Emkay)."""
from pathlib import Path

LOCALE = Path(__file__).resolve().parents[1] / "locale"


def test_voc_lines_are_plain_phrases():
    bad = []
    for voc in LOCALE.glob("*/*.voc"):
        for n, line in enumerate(voc.read_text(encoding="utf-8").splitlines(), 1):
            if any(c in line for c in "<>{}") or "->" in line:
                bad.append(f"{voc.relative_to(LOCALE)}:{n}: {line}")
    assert not bad, "\n".join(bad)


def test_country_voc_has_only_countries():
    for voc in LOCALE.glob("*/Country.voc"):
        lines = voc.read_text(encoding="utf-8").splitlines()
        assert 150 < len(lines) < 260, f"{voc}: {len(lines)} lines"
