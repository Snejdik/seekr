"""Práce s textem: čtení souborů, normalizace, tokenizace

Index je bez diakritiky a v malých písmenech, např. "Žluťoučký kůň" -> "zlutoucky", "kun".

Odchylka od pořadí - nejdřív normalizace, pak tokenizace. Samotná slova hledáme v originálním textu a jednotlivě normalizujeme.
Výsledek se nemění, ale offset původního textu využijeme pro výřez a zvýrazněný nalezených slov.
Podtržítko odděluje slova, UTF-16 soubory skončí jako binární (nulové bajty).
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Iterator
from pathlib import Path

from .models import (
    BinaryFileError,
    EmptyFileError,
    FileInfo,
    Token,
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


# NORMALIZACE A TOKENIZACE
def normalize_term(word: str) -> str:
    """Malá písmena a odstranění diakritiky"""
    decomposed = unicodedata.normalize(
        "NFD", word.lower()
    )  # lower převede všechna písmena proměnné word na malá
    # unicodedata.normalize(...) - sjednocuje způsob, jakým jsou znaky uložené v paměti, NFD = Normalization Form D - Canonical Decompositon
    # znaky s diakritikou se rozdělí na základní znak a kombinující diakritické znaménko
    return "".join(
        c for c in decomposed if not unicodedata.combining(c)
    )  # propojí základní znaky do jednoho slova


def iter_tokens(
    text: str,
) -> Iterator[
    tuple[Token, int, int]
]:  # ty 2 int jsou indexy - počáteční a koncový index
    """Generátor (token, start, konec) s offsety do původního textu."""
    position = 0  # počítadlo pořadí platných slov
    for m in _WORD.finditer(
        text
    ):  # podle regulární výrazu _WORD prohledá všechna slova
        term = normalize_term(m.group())
        if term:  # "Zbyl tu neprázdný řetězec?"
            yield (
                Token(term, position),
                m.start(),
                m.end(),
            )  # z funkce udělá generátor, díky yield vrací výsledky postupně
            position += 1


# m.end() - index znaku za koncem slova v původním textu


def tokenize(
    text: str,
) -> list[Token]:  # wrapper pro iter_tokens, zkrátka vyhodí indexy
    """Tokeny s pozicemi 0, 1, 2, ... (pro index)."""
    return [tok for tok, _, _ in iter_tokens(text)]


# _ tu reprezentuje "ignorování" hodnoty a první hodnotu uloží do proměnné tok
# tok for tok - list comprehension = posbírá generované obj. tok a zabalí je do 1 seznamu.
