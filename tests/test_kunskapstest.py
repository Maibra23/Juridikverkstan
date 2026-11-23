"""Tester för Kunskapstest som nav (sidor/9_Kunskapstest.py).

Sidan körs via streamlit_app.py och switch_page, av samma skäl som i
tests/test_hem.py: ingångspunkten ger st.page_link den sidkontext den behöver.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from utils.navigation import övningsmoduler

APP = str(Path(__file__).resolve().parent.parent / "streamlit_app.py")
SIDA = "sidor/9_Kunskapstest.py"


def _kor(session: dict | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=60)
    for nyckel, varde in (session or {}).items():
        at.session_state[nyckel] = varde
    at.switch_page(SIDA)
    at.run()
    assert not at.exception, [str(e.value) for e in at.exception]
    return at


def _modullankar(at: AppTest) -> list[str]:
    """Etiketterna på huvudytans sidlänkar (sidopanelens länkar räknas bort)."""
    return [p.label for p in at.main.get("page_link")]


@pytest.fixture(scope="module")
def tom() -> AppTest:
    return _kor()


def test_varje_modulrad_ar_en_lank_i_appens_ordning(tom: AppTest):
    lankar = _modullankar(tom)
    ordning = [m.namn for m in övningsmoduler()]
    assert lankar, "Inga modullänkar ritades"
    assert lankar == [n for n in ordning if n in lankar]


def test_tomlage_visar_notis_och_listan(tom: AppTest):
    assert _modullankar(tom)
    texter = " ".join(str(h.proto) for h in tom.main.get("html"))
    assert "inte besvarat några quizfrågor" in texter


def test_rad_visar_andel_efter_svar():
    # Nyckeln är densamma som utils.quiz._resultatbok använder.
    at = _kor({"quiz_resultat": {"Avtalsrätt": {"f1": True, "f2": False, "f3": True}}})
    bildtexter = [c.value for c in at.main.caption]
    assert any("3 av" in t and "2 av 3 rätt (67\u00a0%)" in t for t in bildtexter), bildtexter
