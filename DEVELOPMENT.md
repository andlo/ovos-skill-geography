# Development

## Architecture at a glance

A UTILITY skill: fixed intents (`capital_of`, `continent_of`,
`borders_of`, `area_of`, `currency_of`, `language_of`), no quiz/teach
logic - that's `ovos-skill-geography-practice`'s job, which depends
on this package.

**Public API, not just intent handlers.** The actual reuse surface is
the module-level data (`CORE_DATA`, `COUNTRY_NAMES`, `CAPITAL_NAMES`,
`REGION_NAMES`, `SUBREGION_NAMES`, `CURRENCY_NAMES`, `LANGUAGE_NAMES`)
and plain functions (`resolve_country`, `country_name`,
`capital_entry`, `region_name`, `subregion_name`,
`currency_names_for`, `language_names_for`, `strip_article`) - all
take `lang` explicitly rather than reading `self.lang`, so
`geography-practice` (or any sibling skill) can call them directly
without needing an instance of this skill's class. Every intent
handler is a thin wrapper around these.

## Why fixed intents are the primary path - and Common Query the safety net, not a replacement

"What is the capital of France" LOOKS like a natural fit for OVOS's
Common Query pipeline (multiple knowledge skills bid with a
confidence score, best answer wins - used by Wolfram Alpha,
Wikipedia, WordNet for genuinely open trivia questions). Fixed
Padatious intents are still the primary path here:

- The phrasing here is bounded and predictable (a natural fit for a
  fixed Padatious template with a `{country}` slot), not the kind of
  wildly-varied open trivia phrasing Common Query is designed for.
- This package's curated, offline, verified dataset should be
  AUTHORITATIVE for its own domain - a fixed intent match is
  deterministic in a way a confidence-scored bid against Wolfram
  Alpha or Wikipedia isn't.
- Matches the precedent of `ovos-skill-convert`/`ovos-skill-tuning-fork`/
  `ovos-skill-nato-alphabet`/`ovos-skill-morse-code` - none of the
  existing "authoritative reference" utility skills in this project
  family use Common Query as their PRIMARY path either.

**Revised, from live testing on real hardware, not just reading
code:** the original version of this section claimed fixed intents
"run before Common Query and always win deterministically" - that
turned out to be incomplete. It's only true for utterances that clear
`ovos-padatious-pipeline-plugin-high`'s confidence threshold (0.95 by
default); anything below that falls through to whatever pipeline
stage is configured NEXT on that specific instance, which is
per-instance config a skill can't ship or control. On live testing,
`ovos-m2v-pipeline-high` (a semantic classifier that recognizes
question-shaped utterances and routes them to Common Query) sits
between `padatious-high` and `padatious-medium` in a stock-ish
pipeline config, and confidently intercepted "what is the capital of
France" before this package's own medium-confidence Padatious match
ever ran - Common Query then answered from an unrelated source.

Reordering the LOCAL pipeline config fixes it for one machine, but
doesn't help anyone installing this skill elsewhere with whatever
pipeline ordering THEIR instance has. The portable fix, implemented
now rather than left as a "worth revisiting" note: also register as
a Common Query participant (`@common_query`-decorated
`handle_common_query()`), deliberately narrow (capital/continent/
"about" only - not area/currency/language/borders, whose phrasing is
distinctive enough that a generic semantic router is unlikely to
misclassify it the same way), reusing the SAME dialog files the real
intents use via `self.resources.load_dialog_file()` so there's one
wording, not two. `_match_cq_pattern()` is deliberately simple
substring matching against a small per-language pattern list, not
full NLU - a safety net for cases the platform's own routing failed
to hand us properly, not a second implementation of intent parsing.

## The data pipeline (data/build_data.py)

One-off script, not part of the shipped skill (`pip install babel
pycountry` separately - not in `requirements.txt`). Regenerates
`data/countries.json` and every `locale/*/*.json` name file from
scratch.

1. Fetch `mledoze/countries`, filter to `independent and unMember`
   (194 states).
2. Write the trimmed core dataset - capital(s), region, subregion,
   borders (filtered to only reference other countries in this same
   194-country scope), area, currency codes, language codes.
3. Country names: en-us from mledoze's `name.common`; da/de/fr/es
   from CLDR (`babel.Locale(...).territories`) - confirmed 100%
   coverage before relying on it.
4. Region/subregion names: hand-translated (28 terms total). da/de
   deliberately avoid translating the "Southern Africa" SUBREGION the
   same way as the South Africa COUNTRY name (they collide in both
   languages) - see the disambiguation in `SUBREGION_NAMES`.
5. Currency names: CLDR (`loc.currencies.get(code)`) - 142/145 codes
   covered, 3 obscure ones fall back to the raw ISO code.
6. Language names: CLDR + `pycountry` for 639-3-to-639-1 mapping
   (`resolve_language_name()`) - ~120/139 codes covered, the rest
   fall back to mledoze's own English name, never a guessed
   translation.
7. Capital names: hand-curated override dict per language for
   well-known cases, falling back to mledoze's own spelling - see
   "Capital names" below.

## Capital names: the weak link, and how to improve it

Same situation as `ovos-skill-geography-practice` had before the
split (this is where that logic actually lives now). Edit
`CAPITAL_OVERRIDES` in `data/build_data.py` (keyed by cca3), then
re-run the script - don't hand-edit `locale/*/capital_names.json`
directly. Good fit for OVOS Translate contributions.

## Adding a new locale

1. Add the language code to `data/build_data.py`'s locale loops
   (country/currency/language names, `SUBREGION_NAMES`,
   `CAPITAL_OVERRIDES`) and confirm CLDR coverage before relying on
   it (`babel.Locale(code).territories` / `.currencies` /
   `.languages`).
2. Hand-translate `REGION_NAMES`/`SUBREGION_NAMES` (28 terms).
3. Re-run `data/build_data.py`.
4. Add `locale/<new-lang>/` intent/dialog/`skill.json` files,
   mirroring an existing locale exactly (6 intents, 12 dialogs).
5. Add the language to `LOCALES` in `tests/test_data_loading.py`.
6. If `ovos-skill-geography-practice` should support the new locale
   too, add its own intent/dialog/vocab files there as well - it
   doesn't automatically inherit locale support from this package,
   only the underlying data/lookup functions.

## Setup
```bash
git clone https://github.com/andlo/ovos-skill-geography.git
cd ovos-skill-geography
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```

## Running tests
```bash
pytest tests/ -v
```
`tests/test_data_loading.py` checks data INTEGRITY across all 5
locales (every country has a capital/region/subregion/area, borders
never dangle, every name file has full coverage of the codes actually
used). `tests/test_lookup_functions.py` covers the public reuse
surface directly - the functions `geography-practice` imports.
`tests/test_facts.py` covers the 6 intent handlers.

## Versioning

`version.py` follows `VERSION_MAJOR.VERSION_MINOR.VERSION_BUILD[aVERSION_ALPHA]`,
same convention as the rest of this project family.

## Releasing

Releases are tag-triggered (`v*`):
```bash
git add version.py
git commit -m "chore: bump version to 0.0.X"
git tag vX.Y.Z
git push && git push --tags
```
Triggers `.github/workflows/test.yml` then `.github/workflows/publish.yml`
(PyPI via trusted publishing - needs a one-time per-package browser
setup on PyPI before the first tagged release).

## Style / conventions

- License: GPL-3.0-or-later for the skill's own code. The bundled
  dataset in `data/countries.json` is itself ODbL-1.0 - see
  CREDITS.md, a different license than the code around it.
- `locale/<lang-code>/` layout, `skill.json` inside each locale
  folder.
- Present design changes for review before implementing.

**Region/subregion resolution for teach mode.** `resolve_area(raw,
lang)` resolves a spoken region OR subregion name to `("region", key)`
/ `("subregion", key)`, and `countries_in_area(kind, key)` returns
every country code in it - added specifically so
`ovos-skill-geography-practice`'s teach mode ("teach me about
Europe") can pull a country list without duplicating region-name
resolution. Note: fr-fr/es-es region/subregion names bake the article
into the stored name itself (e.g. "l'Europe", for natural speech
output), unlike country names which are always bare - both the
stored name AND the incoming query are run through `strip_article()`
before comparison, so "Europe" and "l'Europe" both resolve correctly
(see `_reverse_lookup_article_stripped()`; this bit a first version
of the tests before being caught and fixed).

**`render_country_overview(cca3, lang)`** builds the combined
"X is on the Y continent, with capital Z, and borders A, B, C"
sentence used by both this package's own `about_country.intent` AND
geography-practice's teach mode - one sentence-builder, not two
independently-drifting copies. Returns `(dialog_name, data)` rather
than speaking directly, since the two callers are different OVOSSkill
instances with their own `speak_dialog()`.
