"""Tests for the public module-level lookup functions - the actual
reuse surface ovos-skill-geography-practice imports directly."""


def test_resolve_country_case_insensitive():
    from geography_skill import resolve_country
    assert resolve_country("france", "en-us") == "FRA"
    assert resolve_country("France", "en-us") == "FRA"


def test_resolve_country_unknown_returns_none():
    from geography_skill import resolve_country
    assert resolve_country("Narnia", "en-us") is None


def test_resolve_country_strips_french_article():
    from geography_skill import resolve_country
    assert resolve_country("la France", "fr-fr") == "FRA"
    assert resolve_country("l'Allemagne", "fr-fr") == "DEU"


def test_country_name_roundtrips():
    from geography_skill import country_name, resolve_country
    assert country_name("FRA", "en-us") == "France"
    assert resolve_country(country_name("FRA", "da-dk"), "da-dk") == "FRA"


def test_capital_entry_south_africa_has_three_capitals():
    from geography_skill import capital_entry
    entry = capital_entry("ZAF", "en-us")
    assert len(entry["all"]) == 3
    assert "Pretoria" in entry["all"]


def test_currency_names_for_france_is_euro():
    from geography_skill import currency_names_for
    assert currency_names_for("FRA", "en-us") == ["Euro"]
    assert currency_names_for("FRA", "da-dk") == ["euro"]


def test_language_names_for_france_is_french():
    from geography_skill import language_names_for
    assert language_names_for("FRA", "en-us") == ["French"]
    assert language_names_for("FRA", "da-dk") == ["fransk"]
