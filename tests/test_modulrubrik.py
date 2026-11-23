"""Tester för modulsidornas rubrikrad (eyebrow) i utils/modulvy.py.

Rubrikraden visar var modulen sitter i rättssystemet, härledd ur
navigeringsträdet i utils/navigation.py, i stället för att upprepa titeln.
"""

from __future__ import annotations

from utils.modulvy import _modul_eyebrow


def test_avtalsratt_visar_hela_kedjan():
    assert _modul_eyebrow("Avtalsrätt", "AVTALSRÄTT") == (
        "CIVILRÄTT / FÖRMÖGENHETSRÄTT / KONTRAKTSRÄTT"
    )


def test_juridisk_metod_visar_sin_grupp():
    assert _modul_eyebrow("Juridisk metod", "JURIDISK METOD") == "START OCH METOD"


def test_led_som_upprepar_titeln_tas_bort():
    """Personrätt är både grupp och modul; raden ska inte upprepa titeln."""
    assert _modul_eyebrow("Personrätt", "PERSONRÄTT") == "CIVILRÄTT"


def test_okand_titel_faller_tillbaka_pa_undertiteln():
    assert _modul_eyebrow("Finns inte", "EGEN RAD") == "EGEN RAD"


def test_okand_titel_utan_undertitel_ger_modul():
    assert _modul_eyebrow("Finns inte") == "MODUL"
