# <img src='icon.png' card_color='#DB4062' width='50' height='50' style='vertical-align:bottom'/> Geography

Geography facts for the 194 independent UN member states - capital,
continent/region, land borders, area, currency, and official
language(s). Fully offline: all data is bundled as static JSON, no
external lookups at runtime. Available in English, Danish, German,
French, and Spanish.

[![Tests](https://github.com/andlo/ovos-skill-geography/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-geography/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-geography.svg)](https://pypi.org/project/ovos-skill-geography/)

- [Facts](#facts)
- [Usage](#usage)
- [A utility skill, not an educational one](#a-utility-skill-not-an-educational-one)
- [Data sourcing and licensing](#data-sourcing-and-licensing)
- [Known simplifications](#known-simplifications)
- [Install](#install)
- [Development](#development)

## Facts

- `"what is the capital of France"` - handles multi-capital countries
  (only South Africa in this dataset) by naming all of them.
- `"what continent is Kenya in"`
- `"what countries border Germany"` - explicit "doesn't share a
  border" response for island nations.
- `"how big is Brazil"` - area in square kilometers.
- `"what currency does Japan use"`
- `"what language do they speak in Egypt"` - handles countries with
  multiple official languages.
- `"tell me about Afghanistan"` - a combined overview in one sentence
  (continent, capital, and borders together) - shares its
  sentence-builder with `ovos-skill-geography-practice`'s teach mode,
  see DEVELOPMENT.md.

## Usage
```
"what is the capital of France"
"what continent is Kenya in"
"what countries border Germany"
"how big is Brazil"
"what currency does Japan use"
"what language do they speak in Egypt"
"hvad er hovedstaden i Frankrig"          (Danish)
"hvor stort er Brasilien"                 (Danish)
"was ist die hauptstadt von Frankreich"   (German)
"welche währung hat Japan"                (German)
"quelle est la capitale de la France"     (French)
"quelle langue parle-t-on en Égypte"      (French)
"cuál es la capital de Francia"           (Spanish)
"qué moneda usa Japón"                    (Spanish)
```

## A utility skill, not an educational one

This provides FACTS on demand - it doesn't quiz or teach.
[ovos-skill-geography-practice](https://github.com/andlo/ovos-skill-geography-practice)
depends on this package directly (imports its data and lookup
functions) for its quiz mode, the same relationship
`ovos-skill-unit-practice` has with `ovos-skill-convert`.

Deliberately uses fixed intents, not a `CommonQuerySkill` - this
package's curated offline dataset should always be authoritative for
its own domain, not compete on a confidence score against online
knowledge skills (e.g. Wolfram Alpha) for the same question. See
DEVELOPMENT.md for the full reasoning.

## Data sourcing and licensing

Country/capital/region/border/area/currency/language data from
[mledoze/countries](https://github.com/mledoze/countries)
(ODbL-1.0), trimmed to the 194 independent UN member states. Country/
currency/language names in da/de/fr/es come from Unicode CLDR (via
Babel + pycountry, used only as one-off data-generation tools, not
runtime dependencies). Region/subregion names are hand-translated.
**Full attribution and licensing details: [CREDITS.md](CREDITS.md)**,
including a note on a similar prior skill
([OVOSHatchery/ovos-skill-countries](https://github.com/OVOSHatchery/ovos-skill-countries))
that doesn't work today (dead API since 2021) and why this is a
fresh build rather than a fix to that one.

## Known simplifications

- **Capital names in da/de/fr/es are partial, best-effort** - no
  CLDR-equivalent source exists for city names. See CREDITS.md.
- **Language name coverage is ~86-89%** (CLDR + pycountry) - the
  remainder (obscure regional/minority languages) fall back to the
  source dataset's own English name rather than a guessed translation.
- **Spoken country names with a leading article** ("la France", "die
  Türkei") are handled with a simple prefix-strip
  (`ARTICLE_PREFIXES` in `__init__.py`), not full grammatical parsing.
- **No population or timezone data** - population figures go stale
  quickly; timezone isn't in the current source dataset's schema at
  all (see CREDITS.md).
- **Scope is 194 independent UN member states only.**

## Install
```bash
pip install ovos-skill-geography
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md).

## Category
**Information**

## Tags
#geography #reference #capitals #countries
