"""Modulsida: Kunskapstest.

Samlar studentens quizresultat per modul och leder vidare till nästa
handling. Varje modul med quizfrågor visas i appens egen ordning som en rad
med länk till modulen, hur många frågor som är besvarade, andel rätt och en
framstegsstapel. Frågorna och rättningen ligger i modulerna; den här sidan
läser bara resultaten ur session_state.
"""

from __future__ import annotations

import streamlit as st

from utils.navigation import övningsmoduler
from utils.quiz import alla_resultat
from utils.scenarier import ladda_modul, lista_moduler
from utils.texter import andel_text
from utils.ui import (
    footer_note,
    hero,
    render_info,
    section_heading,
)


def antal_fragor_per_modul() -> dict[str, int]:
    """Visningsnamn till antal quizfrågor. Trasiga scenariofiler hoppas över."""
    antal: dict[str, int] = {}
    for stem in lista_moduler():
        try:
            modul = ladda_modul(stem)
        except Exception:  # noqa: BLE001 (en trasig fil ska inte fälla sidan)
            continue
        antal[modul.modul] = len(modul.flervalsfragor)
    return antal


def modulrad_text(ratt: int, besvarade: int, antal: int) -> str:
    """Radens text: "3 av 8 besvarade, 2 av 3 rätt (67 %)"."""
    if not besvarade:
        return f"0 av {antal} besvarade"
    return f"{besvarade} av {antal} besvarade, {andel_text(ratt, besvarade)}"


st.html(
    hero(
        eyebrow="KUNSKAPSTEST",
        title="Dina resultat per modul",
        lead=(
            "Här samlas resultaten från de quizfrågor du besvarat i modulerna. "
            "Öppna en modul för att öva vidare. Varje quiz rättas deterministiskt "
            "och varje lagrum verifieras mot appens lagrumsregister."
        ),
    )
)

resultat = alla_resultat()
antal_fragor = antal_fragor_per_modul()

st.html(section_heading("MODULER", "Öva vidare"))
if not resultat:
    # Listan visas ändå, så att sidan aldrig blir en återvändsgränd.
    render_info(
        "Du har inte besvarat några quizfrågor ännu. Välj en modul nedan och "
        "börja öva, så visas dina resultat här."
    )

for modul in övningsmoduler():
    antal = antal_fragor.get(modul.namn, 0)
    if not antal or modul.sida is None:
        continue
    ratt, besvarade = resultat.get(modul.namn, (0, 0))
    with st.container(border=True):
        st.page_link(modul.sida, label=modul.namn)
        st.caption(modulrad_text(ratt, besvarade, antal))
        st.progress(min(besvarade / antal, 1.0))

st.html(footer_note())
