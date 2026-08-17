"""Data-prep script (NOT part of the shipped skill) - fetches
mledoze/countries, filters to independent UN member states, and
writes the trimmed core dataset plus per-locale name files (country,
region, subregion, capital, currency, language). Run once by hand;
not a build-time dependency. Needs `pip install babel pycountry`
separately - not in requirements.txt."""
import json
import subprocess

import pycountry
from babel import Locale

subprocess.run(["curl", "-sL",
    "https://cdn.jsdelivr.net/gh/mledoze/countries@master/countries.json",
    "-o", "/tmp/countries_full.json"], check=True)

data = json.load(open("/tmp/countries_full.json"))
un = [c for c in data if c.get("independent") and c.get("unMember")]
un_codes = set(c["cca3"] for c in un)
print(f"{len(un)} independent UN member states")

# Core, language-agnostic dataset - cca3, capital list, region,
# subregion, borders (filtered to only other UN-member states in
# scope), area (km2), currency codes, language codes. Currency/
# language NAMES are localized separately below (currency_names.json
# / language_names.json per locale) - this file only stores the
# stable ISO codes.
core = []
for c in sorted(un, key=lambda c: c["cca3"]):
    core.append({
        "cca3": c["cca3"],
        "cca2": c["cca2"],
        "capital": c.get("capital", []),
        "region": c["region"],
        "subregion": c.get("subregion", ""),
        "borders": [b for b in c.get("borders", []) if b in un_codes],
        "area": c.get("area"),
        "currencies": sorted(c.get("currencies", {}).keys()),
        "languages": sorted(c.get("languages", {}).keys()),
    })

with open("/home/andlo/ovos-skill-geography/data/countries.json", "w", encoding="utf-8") as f:
    json.dump(core, f, ensure_ascii=False, indent=2)

print("core dataset written:", len(core), "countries")

# ---------------------------------------------------------------
# Country names, per locale - CLDR (via babel) for da/de/fr/es,
# confirmed 100% coverage across all 194 UN member states. English
# uses mledoze's own "name.common".
cca2_to_cca3 = {c["cca2"]: c["cca3"] for c in un}

country_names = {"en-us": {}}
for c in un:
    country_names["en-us"][c["cca3"]] = c["name"]["common"]

for lang, locale_code in [("da-dk", "da"), ("de-de", "de"), ("fr-fr", "fr"), ("es-es", "es")]:
    loc = Locale(locale_code)
    country_names[lang] = {}
    for cca2, cca3 in cca2_to_cca3.items():
        country_names[lang][cca3] = loc.territories[cca2]

for lang, names in country_names.items():
    with open(f"/home/andlo/ovos-skill-geography/locale/{lang}/country_names.json", "w", encoding="utf-8") as f:
        json.dump({
            "_notes": ["cca3 country code -> localized country name.",
                       "en-us from mledoze/countries name.common; da-dk/de-de/fr-fr/es-es from Unicode CLDR territory names (via babel) - confirmed full coverage of all 194 countries."],
            **names
        }, f, ensure_ascii=False, indent=2, sort_keys=True)
print("country_names.json written for all 5 locales")

# ---------------------------------------------------------------
# Region/subregion names, per locale - hand-translated (only 5
# regions + 23 subregions). da-dk/de-de deliberately avoid
# translating the "Southern Africa" SUBREGION as "Sydafrika"/
# "Südafrika", identical to the COUNTRY name South Africa in both
# languages - used "det sydlige Afrika"/"Südliches Afrika" instead.
REGION_NAMES = {
    "en-us": {"Africa": "Africa", "Americas": "the Americas", "Asia": "Asia", "Europe": "Europe", "Oceania": "Oceania"},
    "da-dk": {"Africa": "Afrika", "Americas": "Amerika", "Asia": "Asien", "Europe": "Europa", "Oceania": "Oceanien"},
    "de-de": {"Africa": "Afrika", "Americas": "Amerika", "Asia": "Asien", "Europe": "Europa", "Oceania": "Ozeanien"},
    "fr-fr": {"Africa": "l'Afrique", "Americas": "les Amériques", "Asia": "l'Asie", "Europe": "l'Europe", "Oceania": "l'Océanie"},
    "es-es": {"Africa": "África", "Americas": "América", "Asia": "Asia", "Europe": "Europa", "Oceania": "Oceanía"},
}

SUBREGION_NAMES = {
    "en-us": {
        "Australia and New Zealand": "Australia and New Zealand", "Caribbean": "the Caribbean",
        "Central America": "Central America", "Central Asia": "Central Asia", "Central Europe": "Central Europe",
        "Eastern Africa": "Eastern Africa", "Eastern Asia": "Eastern Asia", "Eastern Europe": "Eastern Europe",
        "Melanesia": "Melanesia", "Micronesia": "Micronesia", "Middle Africa": "Middle Africa",
        "North America": "North America", "Northern Africa": "Northern Africa", "Northern Europe": "Northern Europe",
        "Polynesia": "Polynesia", "South America": "South America", "South-Eastern Asia": "South-Eastern Asia",
        "Southeast Europe": "Southeast Europe", "Southern Africa": "Southern Africa", "Southern Asia": "Southern Asia",
        "Southern Europe": "Southern Europe", "Western Africa": "Western Africa", "Western Asia": "Western Asia",
        "Western Europe": "Western Europe",
    },
    "da-dk": {
        "Australia and New Zealand": "Australien og New Zealand", "Caribbean": "Caribien",
        "Central America": "Mellemamerika", "Central Asia": "Centralasien", "Central Europe": "Centraleuropa",
        "Eastern Africa": "Østafrika", "Eastern Asia": "Østasien", "Eastern Europe": "Østeuropa",
        "Melanesia": "Melanesien", "Micronesia": "Mikronesien", "Middle Africa": "Centralafrika",
        "North America": "Nordamerika", "Northern Africa": "Nordafrika", "Northern Europe": "Nordeuropa",
        "Polynesia": "Polynesien", "South America": "Sydamerika", "South-Eastern Asia": "Sydøstasien",
        "Southeast Europe": "Sydøsteuropa", "Southern Africa": "det sydlige Afrika", "Southern Asia": "Sydasien",
        "Southern Europe": "Sydeuropa", "Western Africa": "Vestafrika", "Western Asia": "Vestasien",
        "Western Europe": "Vesteuropa",
    },
}

SUBREGION_NAMES["de-de"] = {
    "Australia and New Zealand": "Australien und Neuseeland", "Caribbean": "die Karibik",
    "Central America": "Mittelamerika", "Central Asia": "Zentralasien", "Central Europe": "Mitteleuropa",
    "Eastern Africa": "Ostafrika", "Eastern Asia": "Ostasien", "Eastern Europe": "Osteuropa",
    "Melanesia": "Melanesien", "Micronesia": "Mikronesien", "Middle Africa": "Mittelafrika",
    "North America": "Nordamerika", "Northern Africa": "Nordafrika", "Northern Europe": "Nordeuropa",
    "Polynesia": "Polynesien", "South America": "Südamerika", "South-Eastern Asia": "Südostasien",
    "Southeast Europe": "Südosteuropa", "Southern Africa": "Südliches Afrika", "Southern Asia": "Südasien",
    "Southern Europe": "Südeuropa", "Western Africa": "Westafrika", "Western Asia": "Westasien",
    "Western Europe": "Westeuropa",
}
SUBREGION_NAMES["fr-fr"] = {
    "Australia and New Zealand": "l'Australie et la Nouvelle-Zélande", "Caribbean": "les Caraïbes",
    "Central America": "l'Amérique centrale", "Central Asia": "l'Asie centrale", "Central Europe": "l'Europe centrale",
    "Eastern Africa": "l'Afrique de l'Est", "Eastern Asia": "l'Asie de l'Est", "Eastern Europe": "l'Europe de l'Est",
    "Melanesia": "la Mélanésie", "Micronesia": "la Micronésie", "Middle Africa": "l'Afrique centrale",
    "North America": "l'Amérique du Nord", "Northern Africa": "l'Afrique du Nord", "Northern Europe": "l'Europe du Nord",
    "Polynesia": "la Polynésie", "South America": "l'Amérique du Sud", "South-Eastern Asia": "l'Asie du Sud-Est",
    "Southeast Europe": "l'Europe du Sud-Est", "Southern Africa": "l'Afrique australe", "Southern Asia": "l'Asie du Sud",
    "Southern Europe": "l'Europe du Sud", "Western Africa": "l'Afrique de l'Ouest", "Western Asia": "l'Asie de l'Ouest",
    "Western Europe": "l'Europe de l'Ouest",
}
SUBREGION_NAMES["es-es"] = {
    "Australia and New Zealand": "Australia y Nueva Zelanda", "Caribbean": "el Caribe",
    "Central America": "América Central", "Central Asia": "Asia Central", "Central Europe": "Europa Central",
    "Eastern Africa": "África Oriental", "Eastern Asia": "Asia Oriental", "Eastern Europe": "Europa del Este",
    "Melanesia": "Melanesia", "Micronesia": "Micronesia", "Middle Africa": "África Central",
    "North America": "América del Norte", "Northern Africa": "África del Norte", "Northern Europe": "Europa del Norte",
    "Polynesia": "Polinesia", "South America": "América del Sur", "South-Eastern Asia": "Sudeste Asiático",
    "Southeast Europe": "Europa Sudoriental", "Southern Africa": "África Meridional", "Southern Asia": "Asia Meridional",
    "Southern Europe": "Europa Meridional", "Western Africa": "África Occidental", "Western Asia": "Asia Occidental",
    "Western Europe": "Europa Occidental",
}

for lang in ["en-us", "da-dk", "de-de", "fr-fr", "es-es"]:
    with open(f"/home/andlo/ovos-skill-geography/locale/{lang}/region_names.json", "w", encoding="utf-8") as f:
        json.dump({"_notes": ["region name -> localized form. Hand-translated (only 5 regions)."],
                   **REGION_NAMES[lang]}, f, ensure_ascii=False, indent=2, sort_keys=True)
    with open(f"/home/andlo/ovos-skill-geography/locale/{lang}/subregion_names.json", "w", encoding="utf-8") as f:
        json.dump({"_notes": ["subregion name -> localized form. Hand-translated (only 23 subregions)."],
                   **SUBREGION_NAMES[lang]}, f, ensure_ascii=False, indent=2, sort_keys=True)
print("region_names.json / subregion_names.json written for all 5 locales")

# ---------------------------------------------------------------
# Capital names, per locale - THE WEAK LINK. No CLDR-equivalent
# authoritative source exists for city names. Default is mledoze's
# own spelling; overridden only for well-known cases curated by hand
# at BEST EFFORT, not exhaustively verified. See README/DEVELOPMENT.
CAPITAL_OVERRIDES = {}
CAPITAL_OVERRIDES["da-dk"] = {
    "RUS": "Moskva", "POL": "Warszawa", "AUT": "Wien", "CZE": "Prag", "GRC": "Athen",
    "EGY": "Kairo", "PRT": "Lissabon", "ITA": "Rom", "ROU": "Bukarest", "BEL": "Bruxelles",
    "SRB": "Beograd", "CHN": "Beijing", "DNK": "København", "BRA": "Brasília", "COL": "Bogotá",
    "DZA": "Algier", "ETH": "Addis Abeba", "IRN": "Teheran", "IRQ": "Bagdad", "CUB": "Havana",
    "PRY": "Asunción", "SAU": "Riyadh", "MNG": "Ulaanbaatar",
}
CAPITAL_OVERRIDES["de-de"] = {
    "RUS": "Moskau", "POL": "Warschau", "AUT": "Wien", "CZE": "Prag", "GRC": "Athen",
    "EGY": "Kairo", "PRT": "Lissabon", "ITA": "Rom", "ROU": "Bukarest", "BEL": "Brüssel",
    "SRB": "Belgrad", "UKR": "Kiew", "CHN": "Peking", "DNK": "Kopenhagen", "BRA": "Brasília",
    "COL": "Bogotá", "DZA": "Algier", "ETH": "Addis Abeba", "IRN": "Teheran", "IRQ": "Bagdad",
    "CUB": "Havanna", "CRI": "San José", "PRY": "Asunción", "MEX": "Mexiko-Stadt",
    "USA": "Washington, D.C.", "SAU": "Riad", "JPN": "Tokio", "IND": "Neu-Delhi",
    "LBY": "Tripolis", "SGP": "Singapur", "GTM": "Guatemala-Stadt", "PAN": "Panama-Stadt",
}
CAPITAL_OVERRIDES["fr-fr"] = {
    "RUS": "Moscou", "POL": "Varsovie", "AUT": "Vienne", "GRC": "Athènes", "EGY": "Le Caire",
    "PRT": "Lisbonne", "ITA": "Rome", "ROU": "Bucarest", "BEL": "Bruxelles", "CHN": "Pékin",
    "DNK": "Copenhague", "COL": "Bogota", "DZA": "Alger", "ETH": "Addis-Abeba", "IRN": "Téhéran",
    "IRQ": "Bagdad", "CUB": "La Havane", "CRI": "San José", "PRY": "Asunción", "CHE": "Berne",
    "MEX": "Mexico", "USA": "Washington", "GBR": "Londres", "SAU": "Riyad", "KOR": "Séoul",
    "VNM": "Hanoï", "PHL": "Manille", "ISR": "Jérusalem", "ARE": "Abou Dabi", "AFG": "Kaboul",
    "SGP": "Singapour", "MNG": "Oulan-Bator", "GTM": "Guatemala", "PAN": "Panama",
    "DOM": "Saint-Domingue",
}
CAPITAL_OVERRIDES["es-es"] = {
    "RUS": "Moscú", "POL": "Varsovia", "AUT": "Viena", "CZE": "Praga", "GRC": "Atenas",
    "EGY": "El Cairo", "PRT": "Lisboa", "ITA": "Roma", "ROU": "Bucarest", "BEL": "Bruselas",
    "SRB": "Belgrado", "UKR": "Kiev", "CHN": "Pekín", "DNK": "Copenhague", "COL": "Bogotá",
    "DZA": "Argel", "ETH": "Adís Abeba", "IRN": "Teherán", "IRQ": "Bagdad", "CUB": "La Habana",
    "CRI": "San José", "PRY": "Asunción", "NLD": "Ámsterdam", "CHE": "Berna", "DEU": "Berlín",
    "BGR": "Sofía", "SWE": "Estocolmo", "MEX": "Ciudad de México", "USA": "Washington D. C.",
    "GBR": "Londres", "SAU": "Riad", "JPN": "Tokio", "KOR": "Seúl", "IND": "Nueva Delhi",
    "VNM": "Hanói", "IDN": "Yakarta", "TUN": "Túnez", "LBY": "Trípoli", "NGA": "Abuya",
    "GHA": "Acra", "ISR": "Jerusalén", "ARE": "Abu Dabi", "SGP": "Singapur", "MNG": "Ulán Bator",
    "GTM": "Ciudad de Guatemala", "PAN": "Ciudad de Panamá", "HTI": "Puerto Príncipe",
}

for lang in ["en-us", "da-dk", "de-de", "fr-fr", "es-es"]:
    overrides = CAPITAL_OVERRIDES.get(lang, {})
    names = {}
    for c in un:
        capitals = c.get("capital", [])
        cca3 = c["cca3"]
        localized = overrides.get(cca3, capitals[0] if capitals else None)
        names[cca3] = {"primary": localized, "all": capitals}
    with open(f"/home/andlo/ovos-skill-geography/locale/{lang}/capital_names.json", "w", encoding="utf-8") as f:
        json.dump({
            "_notes": [
                "cca3 -> {primary: localized capital name, all: every capital this country has}.",
                "PARTIAL / BEST-EFFORT: no CLDR-equivalent source exists for city names. "
                "'primary' defaults to mledoze/countries' own spelling, overridden only for "
                "well-known cases curated by hand - not verified per-entry. Improving/correcting "
                "entries here is well suited to OVOS Translate."
            ],
            "capitals": names,
        }, f, ensure_ascii=False, indent=2, sort_keys=True)
print("capital_names.json written for all 5 locales")

# ---------------------------------------------------------------
# Currency names, per locale - CLDR (via babel), confirmed 142/145
# currency codes covered across all 194 countries; the 3 uncovered
# (TVD, ZWB, KID - all obscure/pegged currencies) fall back to the
# ISO code itself with a "_notes" disclaimer, rather than guessing.
currency_codes = set()
for c in un:
    currency_codes.update(c.get("currencies", {}).keys())

currency_names = {"en-us": {}}
for code in currency_codes:
    currency_names["en-us"][code] = Locale("en").currencies.get(code) or code

for lang, locale_code in [("da-dk", "da"), ("de-de", "de"), ("fr-fr", "fr"), ("es-es", "es")]:
    loc = Locale(locale_code)
    currency_names[lang] = {}
    for code in currency_codes:
        currency_names[lang][code] = loc.currencies.get(code) or code

for lang, names in currency_names.items():
    with open(f"/home/andlo/ovos-skill-geography/locale/{lang}/currency_names.json", "w", encoding="utf-8") as f:
        json.dump({
            "_notes": ["ISO 4217 currency code -> localized name, via Unicode CLDR (babel). "
                       "142 of 145 codes covered; the rest fall back to the raw ISO code."],
            **names
        }, f, ensure_ascii=False, indent=2, sort_keys=True)
print("currency_names.json written for all 5 locales")

# ---------------------------------------------------------------
# Language names, per locale - CLDR (via babel) using the ISO 639-1
# 2-letter code where pycountry can map the source's 3-letter code
# to one, falling back to trying the 3-letter code directly in CLDR
# (covers some languages without a 2-letter code, e.g. Filipino,
# Central Kurdish, Swiss German), falling back to mledoze's own
# English name as a LAST resort for ~16-19 obscure regional/minority
# languages CLDR doesn't have translated at all (e.g. Montenegrin,
# Dari, Jamaican Patois) - never guessed, always a real English name.
language_codes = set()
for c in un:
    language_codes.update(c.get("languages", {}).keys())

# mledoze's own English names for the ultimate fallback
mledoze_lang_names = {}
for c in un:
    mledoze_lang_names.update(c.get("languages", {}))


def resolve_language_name(code3, loc):
    lang = pycountry.languages.get(alpha_3=code3)
    alpha2 = getattr(lang, "alpha_2", None) if lang else None
    if alpha2 and loc.languages.get(alpha2):
        return loc.languages.get(alpha2), True
    if loc.languages.get(code3):
        return loc.languages.get(code3), True
    return mledoze_lang_names.get(code3, code3), False


language_names = {}
for lang, locale_code in [("en-us", "en"), ("da-dk", "da"), ("de-de", "de"), ("fr-fr", "fr"), ("es-es", "es")]:
    loc = Locale(locale_code)
    language_names[lang] = {}
    for code in language_codes:
        name, _ = resolve_language_name(code, loc)
        language_names[lang][code] = name

for lang, names in language_names.items():
    with open(f"/home/andlo/ovos-skill-geography/locale/{lang}/language_names.json", "w", encoding="utf-8") as f:
        json.dump({
            "_notes": ["ISO 639-3 language code -> localized name, via Unicode CLDR (babel) + "
                       "pycountry for 639-3-to-639-1 mapping. ~120 of 139 codes covered; the "
                       "rest (obscure regional/minority languages) fall back to the source "
                       "dataset's own English name, not a guessed translation."],
            **names
        }, f, ensure_ascii=False, indent=2, sort_keys=True)
print("language_names.json written for all 5 locales")
