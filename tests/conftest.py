"""Shared pytest fixtures for the geography skill test suite."""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("geography_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
sys.modules["geography_skill"] = _module
_spec.loader.exec_module(_module)

Geography = _module.Geography


@pytest.fixture
def skill(monkeypatch):
    s = Geography.__new__(Geography)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-geography.test"
    s.status = MagicMock()
    s._bus = MagicMock()
    monkeypatch.setattr(Geography, "lang", "en-us", raising=False)
    s.res_dir = str(Path(__file__).resolve().parents[1])
    s._lang_resources = {}
    return s
