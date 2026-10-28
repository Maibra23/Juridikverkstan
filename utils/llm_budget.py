"""Serverbaserad daglig LLM-anropsbudget.

Sessionstaket dör med sessionen, så på en publik deploy skulle någon
kunna tömma HF-tokenbudgeten genom att ladda om sidan. Denna modul
för en filbaserad daglig räknare (data/.llm_daily_usage.json) som delas
av alla sessioner på värden och inte kan nollställas från UI:t.

Dagstaket är dessutom uppdelat i timmar. Utan det kunde en enda besökare
som laddar om sidan några gånger förbruka hela dagens budget på några
minuter, och då förlorar alla studenter tutorn till nästa dag. Med ett
timtak (standard en sjättedel av dagstaket) kostar samma missbruk som mest
en timmes andel, och tutorn är tillbaka nästa timme. Appen har ingen
inloggning och värdens proxy gör IP-adressen opålitlig, så taket kan inte
ligga per besökare.

Räknaren är rådgivande, inte faktureringskritisk: vid filsystemfel
öppnar vi hellre (appen fortsätter fungera) och loggar problemet.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_DAILY_CALL_CAP = 300
MIN_HOURLY_CALL_CAP = 10

DAILY_CAP_MESSAGE = (
    "Dagens gemensamma budget för förklaringar är förbrukad. "
    "Rättning, quiz, lagrumslänkar och export fungerar som vanligt. "
    "Förklaringarna är tillgängliga igen i morgon."
)

HOURLY_CAP_MESSAGE = (
    "Många har bett om förklaringar den senaste timmen, så den gemensamma "
    "budgeten för den här timmen är förbrukad. Rättning, quiz, lagrumslänkar "
    "och export fungerar som vanligt. Prova igen nästa timme."
)


def _read_int_setting(key: str) -> str | None:
    raw = os.environ.get(key)
    if raw is None:
        try:
            import streamlit as st

            if key in st.secrets:
                raw = str(st.secrets[key])
        except Exception:
            raw = None
    return raw


def get_daily_cap() -> int:
    """Dagligt tak från inställningen LLM_DAILY_CAP, annars standardvärdet."""
    raw = _read_int_setting("LLM_DAILY_CAP")
    if raw is None:
        return DEFAULT_DAILY_CALL_CAP
    try:
        value = int(str(raw).strip())
    except ValueError:
        logger.warning("Ogiltigt LLM_DAILY_CAP %r, använder standardvärdet", raw)
        return DEFAULT_DAILY_CALL_CAP
    return max(0, value)


def get_hourly_cap() -> int:
    """Tak per klocktimme från LLM_HOURLY_CAP, annars en sjättedel av dagstaket."""
    standard = max(MIN_HOURLY_CALL_CAP, get_daily_cap() // 6)
    raw = _read_int_setting("LLM_HOURLY_CAP")
    if raw is None:
        return standard
    try:
        return max(0, int(str(raw).strip()))
    except ValueError:
        logger.warning("Ogiltigt LLM_HOURLY_CAP %r, använder standardvärdet", raw)
        return standard


def _usage_file() -> Path:
    """Sökväg till budgetfilen.

    LLM_BUDGET_FILE har högst prioritet (används i test och som /tmp-fallback
    på deployer där data/ är skrivskyddad).
    """
    custom = os.environ.get("LLM_BUDGET_FILE")
    if custom:
        return Path(custom)
    return Path(__file__).resolve().parent.parent / "data" / ".llm_daily_usage.json"


def _current_hour() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H")


def _read_usage() -> dict:
    """Läs dagens och timmens användning. Gammalt datum och korrupt fil nollställs."""
    today = date.today().isoformat()
    hour = _current_hour()
    fresh = {"date": today, "calls": 0, "hour": hour, "hour_calls": 0}
    path = _usage_file()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return fresh
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning("Kunde inte läsa budgetfilen %s: %s", path, exc)
        return fresh
    if not isinstance(raw, dict) or raw.get("date") != today:
        return fresh
    try:
        calls = max(0, int(raw.get("calls", 0)))
        hour_calls = max(0, int(raw.get("hour_calls", 0))) if raw.get("hour") == hour else 0
    except (TypeError, ValueError):
        return fresh
    return {"date": today, "calls": calls, "hour": hour, "hour_calls": hour_calls}


def get_daily_calls_used() -> int:
    """Antal LLM-anrop som registrerats idag över alla sessioner."""
    return _read_usage()["calls"]


def get_daily_calls_remaining() -> int:
    """Anrop kvar i dagens gemensamma budget. Aldrig negativt."""
    return max(0, get_daily_cap() - get_daily_calls_used())


def get_hourly_calls_remaining() -> int:
    """Anrop kvar den här klocktimmen. Aldrig negativt."""
    return max(0, get_hourly_cap() - _read_usage()["hour_calls"])


def get_calls_remaining() -> int:
    """Anrop som får göras just nu: det minsta av dagens och timmens rest."""
    return min(get_daily_calls_remaining(), get_hourly_calls_remaining())


def cap_message() -> str:
    """Meddelandet för det tak som är nått: dagens om det är slut, annars timmens."""
    return DAILY_CAP_MESSAGE if get_daily_calls_remaining() <= 0 else HOURLY_CAP_MESSAGE


def record_daily_call() -> None:
    """Registrera ett LLM-anrop i dagens och timmens gemensamma räknare.

    Fail open vid filsystemfel: budgeten skyddar kostnad, den får aldrig
    ta ner appen.
    """
    usage = _read_usage()
    usage = {**usage, "calls": usage["calls"] + 1, "hour_calls": usage["hour_calls"] + 1}
    path = _usage_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(usage), encoding="utf-8")
        tmp.replace(path)
    except OSError as exc:
        logger.warning("Kunde inte skriva budgetfilen %s: %s", path, exc)
