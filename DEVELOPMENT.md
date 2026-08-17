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

## Why fixed intents, not CommonQuerySkill

"What is the capital of France" LOOKS like a natural fit for OVOS's
Common Query pipeline (multiple knowledge skills bid with a
confidence score, best answer wins - used by Wolfram Alpha,
Wikipedia, WordNet for genuinely open trivia questions). Considered
and rejected for this package:

- The phrasing here is bounded and predictable (a natural fit for a
  fixed Padatious template with a `{country}` slot), not the kind of
  wildly-varied open trivia phrasing Common Query is designed for.
- This package's curated, offline, verified dataset should be
  AUTHORITATIVE for its own domain - fixed intents run before Common
  Query in the OVOS pipeline and always win deterministically, rather
  than this package's accurate offline answer possibly losing a
  confidence race to an online source's (e.g. Wolfram Alpha's, which
  requires an API key and internet) answer to the same question.
- Matches the precedent of `ovos-skill-convert`/`ovos-skill-tuning-fork`/
  `ovos-skill-nato-alphabet`/`ovos-skill-morse-code` - none of the
  existing "authoritative reference" utility skills in this project
  family use Common Query either.

Worth revisiting if broader phrasing coverage becomes a real need -
Common Query as a FALLBACK behind the fixed intents (not a
replacement) would be the way to do that without giving up
determinism for the phrasings we do cover.

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
