"""Tester för utils/texter.py: central texthjälp för användarsynliga strängar."""

from __future__ import annotations

import pytest

from utils.texter import andel_text, antal_med_enhet, kedja_etikett, uppraknad


def test_antal_med_enhet_singular():
    assert (
        antal_med_enhet(1, "genomfört rättsfall", "genomförda rättsfall")
        == "1 genomfört rättsfall"
    )


def test_antal_med_enhet_plural():
    assert (
        antal_med_enhet(3, "genomfört rättsfall", "genomförda rättsfall")
        == "3 genomförda rättsfall"
    )


def test_antal_med_enhet_noll_ar_plural():
    assert (
        antal_med_enhet(0, "genomfört rättsfall", "genomförda rättsfall")
        == "0 genomförda rättsfall"
    )


def test_antal_med_enhet_negativt_ger_fel():
    import pytest

    with pytest.raises(ValueError):
        antal_med_enhet(-1, "fall", "fall")


# --- uppraknad, kedja_etikett, andel_text ------------------------------------


@pytest.mark.parametrize(
    ("delar", "vantat"),
    [
        ([], ""),
        (["a"], "a"),
        (["a", "b"], "a och b"),
        (["a", "b", "c"], "a, b och c"),
        (["a", "", "c"], "a och c"),
    ],
)
def test_uppraknad(delar, vantat):
    assert uppraknad(delar) == vantat


def test_kedja_etikett():
    assert kedja_etikett(("Civilrätt", "Förmögenhetsrätt", "Avtalsrätt")) == (
        "Civilrätt / Förmögenhetsrätt / Avtalsrätt"
    )


def test_kedja_etikett_egen_avdelare():
    assert kedja_etikett(["a", "b"], avdelare=" > ") == "a > b"


def test_andel_text_avrundar_och_har_hart_mellanslag():
    assert andel_text(2, 3) == "2 av 3 rätt (67\u00a0%)"


def test_andel_text_alla_ratt():
    assert andel_text(5, 5) == "5 av 5 rätt (100\u00a0%)"


def test_andel_text_noll_besvarade_ger_fel():
    with pytest.raises(ValueError):
        andel_text(0, 0)


def test_andel_text_fler_ratt_an_besvarade_ger_fel():
    with pytest.raises(ValueError):
        andel_text(4, 3)
