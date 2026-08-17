"""
skill OVOS Geography
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

Geography facts for the 194 independent UN member states - capital,
continent/region, land borders, area, currency, and official
language(s). Fully offline: all data is bundled as static JSON (see
data/countries.json and CREDITS.md for sourcing/licensing), no
external lookups at runtime.

This is a UTILITY skill, not an educational one -
ovos-skill-geography-practice depends on this package directly for
its quiz mode's data and name-lookup functions, the same relationship
ovos-skill-unit-practice has with ovos-skill-convert. Module-level
data (CORE_DATA, COUNTRY_NAMES, etc) and helper functions are the
public API sibling skills import; see README.md and DEVELOPMENT.md.

Fixed Padatious intents are the primary path, so this package's own
curated offline dataset is authoritative for its own domain rather
than competing on confidence score against online sources (e.g.
Wolfram Alpha) for the same question - see DEVELOPMENT.md. A narrow
@common_query safety net (handle_common_query()) exists ALONGSIDE the
intents, not instead of them: live testing found that a platform-
level semantic router (ovos-m2v-pipeline-high) can intercept a
well-formed question before this skill's own Padatious intent gets a
chance, on installations where pipeline confidence tuning differs
from ours - a skill can't ship or control that per-instance config,
so Common Query participation is the portable fallback. See
DEVELOPMENT.md "Common Query as a safety net, not a replacement".
"""

import json
from pathlib import Path

from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler, common_query

SKILL_ROOT = Path(__file__).resolve().parent
DATA_DIR = SKILL_ROOT / "data"
LOCALE_DIR = SKILL_ROOT / "locale"

ARTICLE_PREFIXES = {
    "fr-fr": ["l'", "la ", "le ", "les "],
    "de-de": ["der ", "die ", "das "],
    "es-es": ["el ", "la ", "los ", "las "],
}


def strip_article(raw, lang):
    """Strips a common leading article a spoken country name may
    carry in some languages ('la France', 'die Türkei', 'el Perú')
    but that isn't part of the stored CLDR name itself. A pragmatic
    simplification, not full grammatical parsing - see DEVELOPMENT.md.
    Defined early (before the data-loading below) since the region/
    subregion reverse-lookup construction needs it immediately."""
    lang = lang.lower()
    raw = raw.strip()
    lower = raw.lower()
    for prefix in ARTICLE_PREFIXES.get(lang, []):
        if lower.startswith(prefix):
            return raw[len(prefix):].strip()
    return raw

def _load_core_data():
    """data/countries.json -> {cca3: {cca3, cca2, capital, region,
    subregion, borders, area, currencies (codes), languages (codes)}}."""
    path = DATA_DIR / "countries.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        countries = json.load(f)
    return {c["cca3"]: c for c in countries}


CORE_DATA = _load_core_data()
ALL_COUNTRY_CODES = list(CORE_DATA.keys())


def _load_locale_json(filename):
    """locale/<lang>/<filename> -> {lang: {...}}, "_notes" dropped -
    same convention ovos-skill-math-practice uses for its alias JSON."""
    merged = {}
    if not LOCALE_DIR.is_dir():
        return merged
    for lang_dir in sorted(LOCALE_DIR.iterdir()):
        if not lang_dir.is_dir():
            continue
        path = lang_dir / filename
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        lang = lang_dir.name.lower()
        merged[lang] = {k: v for k, v in data.items() if not k.startswith("_")}
    return merged


COUNTRY_NAMES = _load_locale_json("country_names.json")
REGION_NAMES = _load_locale_json("region_names.json")
SUBREGION_NAMES = _load_locale_json("subregion_names.json")
CURRENCY_NAMES = _load_locale_json("currency_names.json")
LANGUAGE_NAMES = _load_locale_json("language_names.json")
_CAPITAL_NAMES_RAW = _load_locale_json("capital_names.json")
CAPITAL_NAMES = {lang: data.get("capitals", {}) for lang, data in _CAPITAL_NAMES_RAW.items()}


def _reverse_lookup(name_dict):
    return {name.strip().lower(): code for code, name in name_dict.items()}


def _reverse_lookup_article_stripped(name_dict, lang):
    """Like _reverse_lookup(), but also strips a leading article from
    the STORED name before using it as a key - region/subregion names
    for fr-fr/es-es bake the article in for natural speech output
    (e.g. "l'Europe", not "Europe"), unlike country names which are
    always bare. Without this, resolve_area() stripping the incoming
    query's article would never match the stored key. Applied to both
    sides so "Europe" and "l'Europe" both resolve the same way."""
    return {strip_article(name, lang).strip().lower(): code for code, name in name_dict.items()}


COUNTRY_NAME_TO_CODE = {lang: _reverse_lookup(names) for lang, names in COUNTRY_NAMES.items()}
REGION_NAME_TO_KEY = {lang: _reverse_lookup_article_stripped(names, lang) for lang, names in REGION_NAMES.items()}
SUBREGION_NAME_TO_KEY = {lang: _reverse_lookup_article_stripped(names, lang) for lang, names in SUBREGION_NAMES.items()}

# ---------------------------------------------------------------
# Public, reusable lookup functions - plain functions (not skill
# methods) so ovos-skill-geography-practice (and any other sibling
# skill) can import and call them directly with its OWN self.lang,
# without needing an instance of this skill's class. This is the
# actual dependency surface, same relationship
# ovos-skill-unit-practice has with ovos-skill-convert.
# ---------------------------------------------------------------

def resolve_country(raw, lang):
    """Exact match only (after stripping a leading article) - a wrong
    country is a more confusing wrong answer than a slightly
    mis-parsed one, same philosophy as ovos-skill-math-practice's
    operation resolution."""
    if not raw:
        return None
    lang = lang.lower()
    lookup = COUNTRY_NAME_TO_CODE.get(lang) or COUNTRY_NAME_TO_CODE.get("en-us", {})
    return lookup.get(strip_article(raw, lang).lower())


def country_name(cca3, lang):
    lang = lang.lower()
    names = COUNTRY_NAMES.get(lang) or COUNTRY_NAMES.get("en-us", {})
    return names.get(cca3, cca3)


def capital_entry(cca3, lang):
    """Returns {"primary": localized name, "all": [every capital,
    unlocalized - only South Africa has more than one]} or None."""
    lang = lang.lower()
    capitals = CAPITAL_NAMES.get(lang) or CAPITAL_NAMES.get("en-us", {})
    return capitals.get(cca3)


def region_name(region, lang):
    lang = lang.lower()
    names = REGION_NAMES.get(lang) or REGION_NAMES.get("en-us", {})
    return names.get(region, region)


def subregion_name(subregion, lang):
    lang = lang.lower()
    names = SUBREGION_NAMES.get(lang) or SUBREGION_NAMES.get("en-us", {})
    return names.get(subregion, subregion)


def currency_names_for(cca3, lang):
    """Returns a list of localized currency names for this country
    (usually one; a few countries use more than one currency)."""
    lang = lang.lower()
    names = CURRENCY_NAMES.get(lang) or CURRENCY_NAMES.get("en-us", {})
    codes = CORE_DATA.get(cca3, {}).get("currencies", [])
    return [names.get(code, code) for code in codes]


def language_names_for(cca3, lang):
    """Returns a list of localized official language names for this
    country (some countries have several official languages)."""
    lang = lang.lower()
    names = LANGUAGE_NAMES.get(lang) or LANGUAGE_NAMES.get("en-us", {})
    codes = CORE_DATA.get(cca3, {}).get("languages", [])
    return [names.get(code, code) for code in codes]


def resolve_area(raw, lang):
    """Resolves a spoken region OR subregion name (e.g. 'Europe' or
    'Northern Europe') to ('region', key) or ('subregion', key), or
    None if not recognized. Tries region names first (the 5 top-level
    continents), then subregions (the 23 finer-grained ones) - a name
    can't be both, so order only matters for which error path an
    unrecognized name falls through, not for correctness."""
    if not raw:
        return None
    lang = lang.lower()
    stripped = strip_article(raw, lang).strip().lower()
    region_lookup = REGION_NAME_TO_KEY.get(lang) or REGION_NAME_TO_KEY.get("en-us", {})
    if stripped in region_lookup:
        return ("region", region_lookup[stripped])
    subregion_lookup = SUBREGION_NAME_TO_KEY.get(lang) or SUBREGION_NAME_TO_KEY.get("en-us", {})
    if stripped in subregion_lookup:
        return ("subregion", subregion_lookup[stripped])
    return None


def countries_in_area(kind, key):
    """kind: 'region' or 'subregion' (as returned by resolve_area()).
    Returns every cca3 code whose CORE_DATA[cca3][kind] == key."""
    return [cca3 for cca3, c in CORE_DATA.items() if c[kind] == key]


def render_country_overview(cca3, lang):
    """Builds the combined 'X is on the Y continent, with capital Z,
    and borders A, B, C' sentence used by both the 'tell me about
    {country}' fact intent here AND ovos-skill-geography-practice's
    teach mode - one sentence-builder, not two independently drifting
    copies. Returns (dialog_name, data) rather than speaking directly,
    since the two callers use different OVOSSkill instances."""
    lang = lang.lower()
    name = country_name(cca3, lang)
    continent = region_name(CORE_DATA[cca3]["region"], lang)
    entry = capital_entry(cca3, lang)
    capital = entry["primary"] if entry else "?"
    borders = CORE_DATA[cca3]["borders"]
    if borders:
        countries = ", ".join(country_name(b, lang) for b in borders)
        return "about_country", {"country": name, "continent": continent, "capital": capital, "countries": countries}
    return "about_country_no_borders", {"country": name, "continent": continent, "capital": capital}


# ---------------------------------------------------------------
# Common Query safety net - see DEVELOPMENT.md "Common Query as a
# safety net, not a replacement". Deliberately narrow: only the
# three simplest single-entity facts (capital, continent, the
# combined "about" overview) - NOT area/currency/language/borders,
# whose phrasing is distinctive enough that a generic semantic
# router is unlikely to misclassify them as bare trivia questions
# the way "what is the capital of X" gets misclassified.
# ---------------------------------------------------------------
CQ_PATTERNS = {
    "en-us": [
        ("what is the capital of ", "", "capital"),
        ("what's the capital of ", "", "capital"),
        ("what continent is ", " in", "continent"),
        ("what region is ", " in", "continent"),
        ("tell me about ", "", "about"),
        ("what do you know about ", "", "about"),
    ],
    "da-dk": [
        ("hvad er hovedstaden i ", "", "capital"),
        ("hvad hedder hovedstaden i ", "", "capital"),
        ("hvilket kontinent er ", " i", "continent"),
        ("hvilken verdensdel er ", " i", "continent"),
        ("fortæl mig om ", "", "about"),
        ("hvad ved du om ", "", "about"),
    ],
    "de-de": [
        ("was ist die hauptstadt von ", "", "capital"),
        ("wie heißt die hauptstadt von ", "", "capital"),
        ("auf welchem kontinent liegt ", "", "continent"),
        ("in welchem kontinent liegt ", "", "continent"),
        ("erzähl mir etwas über ", "", "about"),
        ("was weißt du über ", "", "about"),
    ],
    "fr-fr": [
        ("quelle est la capitale de ", "", "capital"),
        ("quelle est la capitale du ", "", "capital"),
        ("sur quel continent se trouve ", "", "continent"),
        ("dans quel continent se trouve ", "", "continent"),
        ("parle-moi de ", "", "about"),
        ("que sais-tu sur ", "", "about"),
    ],
    "es-es": [
        ("cuál es la capital de ", "", "capital"),
        ("cuál es la capital del ", "", "capital"),
        ("en qué continente está ", "", "continent"),
        ("en qué continente se encuentra ", "", "continent"),
        ("háblame de ", "", "about"),
        ("qué sabes sobre ", "", "about"),
    ],
}


def _match_cq_pattern(phrase, lang):
    """Returns (country_raw, kind) if phrase matches one of our
    prefix[...suffix] patterns for this language, else (None, None).
    Deliberately simple substring matching, not full NLU - a safety
    net for cases the platform's own routing failed to hand us
    properly, not a second implementation of intent parsing."""
    lang = lang.lower()
    stripped = phrase.strip().rstrip("?").strip()
    lower = stripped.lower()
    for prefix, suffix, kind in CQ_PATTERNS.get(lang, []):
        if lower.startswith(prefix) and (not suffix or lower.endswith(suffix)):
            end = len(stripped) - len(suffix) if suffix else len(stripped)
            country_raw = stripped[len(prefix):end].strip()
            if country_raw:
                return country_raw, kind
    return None, None


class Geography(OVOSSkill):
    """Thin wrapper around the module-level lookup functions above -
    each handler just resolves the country slot and speaks a dialog.
    All the actual logic is in the reusable functions, not here."""

    @common_query()
    def handle_common_query(self, phrase, lang):
        """Safety net for when the platform's own routing (e.g. a
        semantic classifier like ovos-m2v-pipeline-high) sends a
        well-formed question to Common Query BEFORE our own
        Padatious intents get a chance - discovered via live testing,
        not assumed. Reuses the SAME dialog files the real intents
        use (via self.resources.load_dialog_file()), so the answer
        text is identical either way - one wording, not two."""
        country_raw, kind = _match_cq_pattern(phrase, lang)
        if country_raw is None:
            return None
        cca3 = resolve_country(country_raw, lang)
        if cca3 is None:
            return None
        name = country_name(cca3, lang)

        if kind == "capital":
            entry = capital_entry(cca3, lang)
            if not entry:
                return None
            if len(entry["all"]) > 1:
                answer = self.resources.load_dialog_file(
                    "capital_of_multi", {"country": name, "capitals": ", ".join(entry["all"])})[0]
            else:
                answer = self.resources.load_dialog_file(
                    "capital_of", {"country": name, "capital": entry["primary"]})[0]
        elif kind == "continent":
            answer = self.resources.load_dialog_file(
                "continent_of", {"country": name, "continent": region_name(CORE_DATA[cca3]["region"], lang)})[0]
        else:  # "about"
            dialog_name, data = render_country_overview(cca3, lang)
            answer = self.resources.load_dialog_file(dialog_name, data)[0]

        return answer, 0.8

    @intent_handler("capital_of.intent")
    def handle_capital_of(self, message):
        country_raw = message.data.get("country")
        cca3 = resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        name = country_name(cca3, self.lang)
        entry = capital_entry(cca3, self.lang)
        if entry and len(entry["all"]) > 1:
            self.speak_dialog("capital_of_multi", {"country": name, "capitals": ", ".join(entry["all"])})
        else:
            self.speak_dialog("capital_of", {"country": name, "capital": entry["primary"] if entry else None})

    @intent_handler("continent_of.intent")
    def handle_continent_of(self, message):
        country_raw = message.data.get("country")
        cca3 = resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        name = country_name(cca3, self.lang)
        self.speak_dialog("continent_of", {
            "country": name, "continent": region_name(CORE_DATA[cca3]["region"], self.lang)})

    @intent_handler("borders_of.intent")
    def handle_borders_of(self, message):
        country_raw = message.data.get("country")
        cca3 = resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        name = country_name(cca3, self.lang)
        borders = CORE_DATA[cca3]["borders"]
        if not borders:
            self.speak_dialog("borders_of_none", {"country": name})
            return
        names = [country_name(b, self.lang) for b in borders]
        self.speak_dialog("borders_of", {"country": name, "countries": ", ".join(names)})

    @intent_handler("area_of.intent")
    def handle_area_of(self, message):
        country_raw = message.data.get("country")
        cca3 = resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        name = country_name(cca3, self.lang)
        area = CORE_DATA[cca3].get("area")
        if area is None:
            self.speak_dialog("area_of_unknown", {"country": name})
            return
        self.speak_dialog("area_of", {"country": name, "area": round(area)})

    @intent_handler("currency_of.intent")
    def handle_currency_of(self, message):
        country_raw = message.data.get("country")
        cca3 = resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        name = country_name(cca3, self.lang)
        currencies = currency_names_for(cca3, self.lang)
        if not currencies:
            self.speak_dialog("currency_of_unknown", {"country": name})
            return
        self.speak_dialog("currency_of", {"country": name, "currencies": ", ".join(currencies)})

    @intent_handler("language_of.intent")
    def handle_language_of(self, message):
        country_raw = message.data.get("country")
        cca3 = resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        name = country_name(cca3, self.lang)
        languages = language_names_for(cca3, self.lang)
        if not languages:
            self.speak_dialog("language_of_unknown", {"country": name})
            return
        self.speak_dialog("language_of", {"country": name, "languages": ", ".join(languages)})

    @intent_handler("about_country.intent")
    def handle_about_country(self, message):
        """'tell me about France' - the combined continent+capital+
        borders overview, one sentence. Shares render_country_overview()
        with ovos-skill-geography-practice's teach mode rather than
        each maintaining its own copy of the same sentence-builder."""
        country_raw = message.data.get("country")
        cca3 = resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        dialog_name, data = render_country_overview(cca3, self.lang)
        self.speak_dialog(dialog_name, data)
