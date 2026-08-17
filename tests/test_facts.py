"""Tests for the 6 facts intent handlers, en-us locale."""
from unittest.mock import MagicMock


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_capital_of_known_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_capital_of(_msg(country="France"))
    skill.speak_dialog.assert_called_once_with(
        "capital_of", {"country": "France", "capital": "Paris"})


def test_capital_of_unknown_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_capital_of(_msg(country="Narnia"))
    skill.speak_dialog.assert_called_once_with(
        "country_not_understood", {"country": "Narnia"})


def test_capital_of_multi_capital_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_capital_of(_msg(country="South Africa"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "capital_of_multi"
    assert "Pretoria" in data["capitals"]


def test_continent_of_known_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_continent_of(_msg(country="Kenya"))
    skill.speak_dialog.assert_called_once_with(
        "continent_of", {"country": "Kenya", "continent": "Africa"})


def test_borders_of_lists_neighbors(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_borders_of(_msg(country="France"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "borders_of"
    assert "Germany" in data["countries"]


def test_borders_of_island_nation(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_borders_of(_msg(country="Antigua and Barbuda"))
    skill.speak_dialog.assert_called_once_with(
        "borders_of_none", {"country": "Antigua and Barbuda"})


def test_area_of_known_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_area_of(_msg(country="France"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "area_of"
    assert data["country"] == "France"
    assert data["area"] == 551695


def test_area_of_unknown_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_area_of(_msg(country="Narnia"))
    skill.speak_dialog.assert_called_once_with(
        "country_not_understood", {"country": "Narnia"})


def test_currency_of_known_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_currency_of(_msg(country="France"))
    skill.speak_dialog.assert_called_once_with(
        "currency_of", {"country": "France", "currencies": "Euro"})


def test_language_of_known_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_language_of(_msg(country="France"))
    skill.speak_dialog.assert_called_once_with(
        "language_of", {"country": "France", "languages": "French"})


def test_language_of_unknown_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_language_of(_msg(country="Narnia"))
    skill.speak_dialog.assert_called_once_with(
        "country_not_understood", {"country": "Narnia"})
