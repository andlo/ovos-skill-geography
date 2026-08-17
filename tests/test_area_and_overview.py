"""Tests for resolve_area(), countries_in_area(), and
render_country_overview() - the new region/subregion + combined-
sentence functions added for teach-mode support in
ovos-skill-geography-practice."""


def test_resolve_area_recognizes_a_region():
    from geography_skill import resolve_area
    assert resolve_area("Europe", "en-us") == ("region", "Europe")


def test_resolve_area_recognizes_a_subregion():
    from geography_skill import resolve_area
    assert resolve_area("Northern Europe", "en-us") == ("subregion", "Northern Europe")


def test_resolve_area_unknown_returns_none():
    from geography_skill import resolve_area
    assert resolve_area("Narnia", "en-us") is None


def test_resolve_area_case_insensitive_and_strips_article():
    from geography_skill import resolve_area
    assert resolve_area("europe", "en-us") == ("region", "Europe")
    assert resolve_area("l'Europe", "fr-fr") == ("region", "Europe")


def test_countries_in_area_region_matches_core_data():
    from geography_skill import countries_in_area, CORE_DATA
    codes = countries_in_area("region", "Europe")
    assert len(codes) > 0
    assert all(CORE_DATA[c]["region"] == "Europe" for c in codes)


def test_countries_in_area_subregion_is_a_subset_of_region():
    from geography_skill import countries_in_area
    subregion_codes = set(countries_in_area("subregion", "Northern Europe"))
    region_codes = set(countries_in_area("region", "Europe"))
    assert subregion_codes <= region_codes
    assert len(subregion_codes) < len(region_codes)


def test_render_country_overview_includes_borders():
    from geography_skill import render_country_overview
    dialog_name, data = render_country_overview("FRA", "en-us")
    assert dialog_name == "about_country"
    assert data["country"] == "France"
    assert data["continent"] == "Europe"
    assert data["capital"] == "Paris"
    assert "Germany" in data["countries"]


def test_render_country_overview_no_borders_uses_different_dialog():
    from geography_skill import render_country_overview
    dialog_name, data = render_country_overview("ATG", "en-us")  # Antigua and Barbuda, island nation
    assert dialog_name == "about_country_no_borders"
    assert "countries" not in data
