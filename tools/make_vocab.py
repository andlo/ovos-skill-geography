"""Writes the Adapt vocabulary for "tell me about <country>" in every locale.

"tell me about {country}" as a Padatious template matched anything after
"tell me about", so "fortæl mig om Eiffeltårnet" got "I don't know a country
called Eiffeltårnet" instead of reaching Common Query (Wikipedia, wiki
offline). As an Adapt intent it needs a known country name:

    locale/<lang>/Country.voc        every name in country_names.json
    locale/<lang>/AboutCountry.voc   the phrases of about_country.intent

Run after changing country_names.json or the phrases:

    python tools/make_vocab.py
"""
import json
from pathlib import Path

LOCALE = Path(__file__).resolve().parents[1] / "locale"

# the phrases, without {country}; first written from the old about_country.intent
PHRASES = {
    "da-dk": ["fortæl mig om", "hvad ved du om"],
    "de-de": ["erzähl mir etwas über", "was weißt du über"],
    "en-us": ["tell me about", "what do you know about"],
    "es-es": ["háblame de", "qué sabes sobre"],
    "fr-fr": ["parle-moi de", "que sais-tu sur"],
    "kab": ["ini-yi-d kra ɣef", "dacu i tessneḍ ɣef"],
}

for lang, phrases in PHRASES.items():
    loc = LOCALE / lang
    # a language without its own names uses English's, as resolve_country does
    source = loc / "country_names.json"
    if not source.exists():
        source = LOCALE / "en-us" / "country_names.json"
    names = json.loads(source.read_text(encoding="utf-8"))
    words = []
    # only the countries: keys are cca3 codes ("DNK"); "_comment" and the
    # like are notes for people, and a line like "code -> name" is not a
    # valid vocabulary line (ovos-workshop refuses the whole skill for it)
    for key, value in names.items():
        if not (len(key) == 3 and key.isalpha() and key.isupper()):
            continue
        for name in (value if isinstance(value, list) else [value]):
            if name and name.lower() not in words:
                words.append(name.lower())
    (loc / "Country.voc").write_text("\n".join(sorted(words)) + "\n", encoding="utf-8")
    (loc / "AboutCountry.voc").write_text("\n".join(phrases) + "\n", encoding="utf-8")
    print(lang, len(words), "countries")
