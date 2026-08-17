"""Tests for the Common Query safety net (_match_cq_pattern,
handle_common_query) - see DEVELOPMENT.md for why this exists."""
from unittest.mock import MagicMock, patch


def _fake_resources():
    m = MagicMock()
    m.load_dialog_file = MagicMock(
        side_effect=lambda name, data: [f"{name}:" + ",".join(f"{k}={v}" for k, v in data.items())])
    return m


def test_match_cq_pattern_capital(skill):
    from geography_skill import _match_cq_pattern
    assert _match_cq_pattern("what is the capital of France", "en-us") == ("France", "capital")


def test_match_cq_pattern_continent_has_suffix(skill):
    from geography_skill import _match_cq_pattern
    assert _match_cq_pattern("what continent is Kenya in", "en-us") == ("Kenya", "continent")


def test_match_cq_pattern_about(skill):
    from geography_skill import _match_cq_pattern
    assert _match_cq_pattern("tell me about Japan", "en-us") == ("Japan", "about")


def test_match_cq_pattern_no_match(skill):
    from geography_skill import _match_cq_pattern
    assert _match_cq_pattern("play some music", "en-us") == (None, None)


def test_handle_common_query_capital(skill):
    with patch.object(type(skill), "resources", property(lambda self: _fake_resources())):
        answer, confidence = skill.handle_common_query("what is the capital of France", "en-us")
    assert "capital=Paris" in answer
    assert confidence == 0.8


def test_handle_common_query_unknown_country_returns_none(skill):
    result = skill.handle_common_query("what is the capital of Narnia", "en-us")
    assert result is None


def test_handle_common_query_non_matching_phrase_returns_none(skill):
    result = skill.handle_common_query("play some music", "en-us")
    assert result is None


def test_handle_common_query_about_reuses_render_country_overview(skill):
    with patch.object(type(skill), "resources", property(lambda self: _fake_resources())):
        answer, confidence = skill.handle_common_query("tell me about France", "en-us")
    assert "France" in answer
    assert confidence == 0.8
