"""Práce s textem: čtení souborů, normalizace, tokenizace

Index je bez diakritiky a v malých písmenech, např. "Žluťoučký kůň" -> "zlutoucky", "kun".

Odchylka od pořadí - nejdřív normalizace, pak tokenizace. Samotná slova hledáme v originálním textu a jednotlivě normalizujeme.
Výsledek se nemění, ale offset původního textu využijeme pro výřez a zvýrazněný nalezených slov.
Podtržítko odděluje slova, UTF-16 soubory skončí jako binární (nulové bajty).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import (
    BinaryFileError,
    EmptyFileError,
    FileInfo,
    UnreadableFileError,
)

ENCODING = "utf-8-sig"  # ta sig verze je lepší, protože je schopna vyhodit BOM (neviditelný znak) na začátku souboru
_CHUNK = (
    1024 * 1024
)  # velikost chunku pro čtení souboru po částech, 1 MB je výhodný, RAM toto množství zvládne a Python nemusí sahat do disku mnohokrát
_WORD = re.compile(
    r"(?:[^\W_]|[\u0300-\u036f])+"
)  # jeden či více znaků v podobě písmena (včetně českých), číslice a diakritiky bez _

# ČTENÍ SOUBORŮ


def read_text(
    path: Path | str,
) -> str:  # otevře soubor, přečte bajty a zjistí stav (prázdný, binární)
    """Přečte textový soubor a vrátí jeho obsah.

    Prázdný, binární nebo nečitelný soubor skončí vlastní chybou
    (FileReadError a její potomci).
    """
    p = Path(path)
    try:
        with p.open("rb") as f:  # rb - r = read, b = binární režim
            data = f.read()
    except OSError as exc:
        raise UnreadableFileError(p, f"nelze otevřít ({exc.strerror or exc})")

    if not data.strip():  # strip = odstranění bílých znaků
        raise EmptyFileError(p, "soubor je prázdný")
    if (
        b"\x00" in data
    ):  # pokud projdou všechny podmínky, data se převedou na text z binární podoby
        raise BinaryFileError(p, "binární soubor (obsahuje nulové bajty)")
    try:
        return data.decode(ENCODING)
    except UnicodeDecodeError as exc:
        raise UnreadableFileError(p, "není platné UTF-8") from exc


def fingerprint(path: Path | str) -> FileInfo:
    """Velikost, čas změny a SHA-256 souboru (čtení po blocích)"""
    p = Path(path)
    try:
        st = p.stat()  # vrací detailní metadata o souboru, či složce
        digest = hashlib.sha256()  # vytvoří objekt pro alg. SHA-256 pro tvorbu hashe
        with p.open("rb") as f:
            while chunk := f.read(
                _CHUNK
            ):  # CHUNK - blok dat o velikosti 1 MB a posune kurzor
                digest.update(
                    chunk
                )  # postupně přidává data do probíhajícího výpočtu hashe
    except OSError as exc:
        raise UnreadableFileError(p, f"nelze otevřít ({exc.strerror or exc})") from exc
    return FileInfo(
        path=p.as_posix(), size=st.st_size, mtime=st.st_mtime, sha256=digest.hexdigest()
    )  # hexdigest vrací vypočítaný hash jako text


# posix() převede cestu na obyčejný text a převede \ na / - hodí se, protože cesta pak vypadá stejně na všech OS
# mtime = čas poslední úpravy obsahu souboru
