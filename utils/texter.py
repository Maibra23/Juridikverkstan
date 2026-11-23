"""Central texthjälp för användarsynliga strängar.

Samlar språklogik som annars dupliceras (och blir fel) ute i sidorna,
t.ex. svensk kongruensböjning av räknade enheter ("1 genomfört rättsfall"
men "3 genomförda rättsfall"). Språk-QA:n i tests/test_sprak.py och
tests/test_texter.py granskar texterna innan de når UI:t.
"""

from __future__ import annotations


def antal_med_enhet(antal: int, singular: str, plural: str) -> str:
    """Formatera ett antal med rätt böjd enhet: "1 genomfört rättsfall".

    ``singular`` används endast för exakt 1; 0 och alla andra antal får
    ``plural`` (svensk kongruens). Negativa antal är ett programfel.
    """
    if antal < 0:
        raise ValueError(f"Antal kan inte vara negativt: {antal}")
    enhet = singular if antal == 1 else plural
    return f"{antal} {enhet}"


def uppraknad(delar: list[str] | tuple[str, ...]) -> str:
    """Svensk uppräkning: "a", "a och b", "a, b och c".

    Ersätter kolon som allmän avgränsare. Kolon läses som en förklaring
    ("Svårighetsgrad: Grund: ca 10 min") och gör kedjan till en trasig mening.
    """
    delar = [d for d in delar if d]
    if not delar:
        return ""
    if len(delar) == 1:
        return delar[0]
    return f"{', '.join(delar[:-1])} och {delar[-1]}"


def kedja_etikett(delar: list[str] | tuple[str, ...], avdelare: str = " / ") -> str:
    """Foga ihop en hierarki till en etikett: "Civilrätt / Förmögenhetsrätt"."""
    return avdelare.join(d for d in delar if d)


def andel_text(ratt: int, besvarade: int) -> str:
    """Resultat med andel: "2 av 3 rätt (67 %)".

    Procenttecknet föregås av ett hårt mellanslag (U+00A0) så att det aldrig
    hamnar ensamt på en ny rad. Andelen avrundas till heltal.
    """
    if besvarade <= 0:
        raise ValueError("Andel kräver minst ett besvarat svar")
    if not 0 <= ratt <= besvarade:
        raise ValueError(f"Ogiltigt resultat: {ratt} av {besvarade}")
    procent = round(100 * ratt / besvarade)
    return f"{ratt} av {besvarade} rätt ({procent}\u00a0%)"
