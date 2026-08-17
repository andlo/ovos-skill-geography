# Data credits and licensing

## Country/capital/region/area/currency/language data

Source: [mledoze/countries](https://github.com/mledoze/countries),
licensed under the **Open Database License (ODbL-1.0)**.

This skill bundles a trimmed subset (`data/countries.json`): country
code, capital name(s), region, subregion, land borders, area, and
currency/language CODES (not names - see below) for the 194
independent UN member states.

Per the ODbL, this derivative attributes the source and is itself
made available under ODbL-1.0 for `data/countries.json`, consistent
with the ODbL's share-alike requirement. This does NOT extend to the
skill's own code, which remains GPL-3.0-or-later per `LICENSE`.

## Country, currency, and language NAMES (localized)

`locale/*/country_names.json`, `currency_names.json`, and
`language_names.json` (da-dk, de-de, fr-fr, es-es) are sourced from
**Unicode CLDR** (Common Locale Data Repository), via the
[Babel](https://babel.pocoo.org/) Python library (BSD-3-Clause), and
[pycountry](https://github.com/pycountry/pycountry) (LGPL-2.1, used
only for ISO 639-3-to-639-1 language code mapping) - both used only
as one-off data-generation tools (see `data/build_data.py`), not
runtime dependencies of the shipped skill. en-us country names use
mledoze/countries' own `name.common` field.

Coverage: country names 194/194 (100%), currency names 142/145
(98%), language names ~120/139 (86-89%) - the remainder (obscure
regional/minority languages CLDR doesn't have translated) fall back
to mledoze's own English name rather than a guessed translation.

## Region/subregion names (localized)

Hand-translated (only 5 regions and 23 subregions). Not sourced from
CLDR or any external database.

## Capital names (localized)

**Partial, best-effort.** No CLDR-equivalent authoritative source
exists for city names at this scale. `locale/*/capital_names.json`
defaults to mledoze/countries' own spelling, overridden only for
well-known cases curated by hand - not exhaustive or verified
per-entry. **Corrections and additions are a good fit for OVOS
Translate.**

## A similar, non-functional prior skill

[OVOSHatchery/ovos-skill-countries](https://github.com/OVOSHatchery/ovos-skill-countries)
covers similar ground but depends on the `restcountries.eu` API,
which has been offline since 2021 (superseded by the paid/rate-limited
`restcountries.com`) - it's unlikely to work as installed today, and
even if fixed would require an internet connection and only supports
English. This skill was built as a working, fully offline,
multi-language alternative rather than a fix to that one.

## Population data

Not included - figures go stale quickly and this skill doesn't
currently disclose "as of" dates for bundled data.

## Timezone data

Not included - the current `mledoze/countries` schema doesn't have a
`timezones` field (the old `restcountries.eu` API did, but that's the
same dead API referenced above). No alternative source has been
identified yet.
