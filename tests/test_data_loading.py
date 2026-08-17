"""Data-integrity tests for CORE_DATA and the per-locale name files
(country, region, subregion, capital, currency, language)."""
import pytest

LOCALES = ["en-us", "da-dk", "de-de", "fr-fr", "es-es"]


def test_core_data_has_194_un_member_states():
    from geography_skill import CORE_DATA
    assert len(CORE_DATA) == 194


def test_every_country_has_capital_region_subregion_and_area():
    from geography_skill import CORE_DATA
    for cca3, c in CORE_DATA.items():
        assert c["capital"], f"{cca3} has no capital"
        assert c["region"], f"{cca3} has no region"
        assert c["subregion"], f"{cca3} has no subregion"
        assert c["area"] is not None, f"{cca3} has no area"


def test_borders_never_reference_a_country_outside_core_data():
    from geography_skill import CORE_DATA
    for cca3, c in CORE_DATA.items():
        for b in c["borders"]:
            assert b in CORE_DATA, f"{cca3} borders {b}, which isn't in CORE_DATA"


@pytest.mark.parametrize("lang", LOCALES)
def test_country_names_cover_every_country(lang):
    from geography_skill import CORE_DATA, COUNTRY_NAMES
    assert set(COUNTRY_NAMES[lang].keys()) == set(CORE_DATA.keys())


@pytest.mark.parametrize("lang", LOCALES)
def test_capital_names_cover_every_country(lang):
    from geography_skill import CORE_DATA, CAPITAL_NAMES
    capitals = CAPITAL_NAMES[lang]
    assert set(capitals.keys()) == set(CORE_DATA.keys())
    for cca3, entry in capitals.items():
        assert entry["primary"], f"{lang}/{cca3} has no primary capital name"


@pytest.mark.parametrize("lang", LOCALES)
def test_region_and_subregion_names_cover_every_region_used(lang):
    from geography_skill import CORE_DATA, REGION_NAMES, SUBREGION_NAMES
    regions_used = set(c["region"] for c in CORE_DATA.values())
    subregions_used = set(c["subregion"] for c in CORE_DATA.values())
    assert regions_used <= set(REGION_NAMES[lang].keys())
    assert subregions_used <= set(SUBREGION_NAMES[lang].keys())


@pytest.mark.parametrize("lang", LOCALES)
def test_currency_names_cover_every_currency_code_used(lang):
    from geography_skill import CORE_DATA, CURRENCY_NAMES
    codes_used = set()
    for c in CORE_DATA.values():
        codes_used.update(c["currencies"])
    assert codes_used <= set(CURRENCY_NAMES[lang].keys())


@pytest.mark.parametrize("lang", LOCALES)
def test_language_names_cover_every_language_code_used(lang):
    from geography_skill import CORE_DATA, LANGUAGE_NAMES
    codes_used = set()
    for c in CORE_DATA.values():
        codes_used.update(c["languages"])
    assert codes_used <= set(LANGUAGE_NAMES[lang].keys())


def test_southern_africa_subregion_is_disambiguated_from_south_africa_country():
    from geography_skill import COUNTRY_NAMES, SUBREGION_NAMES
    assert COUNTRY_NAMES["da-dk"]["ZAF"] != SUBREGION_NAMES["da-dk"]["Southern Africa"]
    assert COUNTRY_NAMES["de-de"]["ZAF"] != SUBREGION_NAMES["de-de"]["Southern Africa"]
