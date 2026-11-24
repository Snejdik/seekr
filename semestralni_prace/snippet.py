"""Výřez textu kolem první shody a pozice slov ke zvýraznění."""

from __future__ import annotations

import re
from collections.abc import (
    Iterable,  # Iterable[str] - Cokoliv obsahující texty, co se dá projít cyklem - je schopen přijmout set, list, tuple i generátor
)

from .models import Snippet
from .text import iter_tokens


def make_snippet(
    text: str, terms: Iterable[str], width: int = 160
) -> Snippet:  # 160 bývá standart, např vyhledávač Google, pokud nezadáme vlastní číslo
    """Výřez kolem první shody a pozice všech nalezených slov ve výřezu.

    Termíny musí být normalizované. Bez shody se vrátí začátek textu.
    Odřádkování se mění na mezery (znak na znak, offsety zůstanou platné).
    Samotné zvýraznění neprovádí, to řeší CLI (barvy v terminálu) a GUI (tagy ve widgetu Text)."""

    wanted = set(
        terms
    )  # seznam hledaných výrazů převede na množinu, množina je řádově rychlejší než běžný seznam
    matches = [(s, e) for tok, s, e in iter_tokens(text) if tok.term in wanted]
    # list comprehension - prochází tokeny (jednotlivá slova) v textu, fce iter_tokens pro každé slovo vrací 3 údaje(samotný objekt tokenu a index kde slovo zač. + konč.) - tvoří nový seznam
    # je textová podoba aktuálního slova tok.term v naší množině wanted
    if matches:  # pokud se slovo našlo
        first = matches[0][0]  # matches[0] je první shoda a [0] je začátek s
        start = max(
            0, first - width // 4
        )  # posun začátek o čtvrtinu šířky před slovo, aby byl vidět kontext před ním
        # max zajistí, že index >= 0, pokud slovo hned na začátku
    else:
        start = 0  # úplný začátek textu
    end = min(
        len(text), start + width
    )  # konec náhledu nastaví, aby měl width, min zajistí, aby konec nepřetekl za délku celého textu
    start = max(
        0, end - width
    )  # pojistka, když se slovo našlo až na konci, výřez by byl kratší než width, proto dojde k posunu start víc doleva, proto má náhled plnou šířku

    chunk = re.sub(
        r"\s", " ", text[start:end]
    )  # z článku vyřízne část od start po end (\s - bílý znak a sub - "najít a nahradit" mezerou)
    prefix = (
        "..." if start > 0 else ""
    )  # začíná úryvek úplně na začátku? - pokud je text před úryvkem, uloží se ... do prefixu
    suffix = (
        "..." if end < len(text) else ""
    )  # je text za úryvkem? - pokud ano, uloží se do suffixu ...
    shift = (
        len(prefix) - start
    )  # původní pozice slov jsou počítané od začátku, ale náš náhled začíná až od start, proto se odečítá (posun o 3/0 kvůli prefixu)
    # shift je číslo, o které posuneme KAŽDOU pozici kvůli náhledu, který je sestaven z (prefix + chunk + suffix)
    highlights = [
        (s + shift, min(e, end) + shift) for s, e in matches if s >= start and s < end
    ]  # nový seznam souřadnic, filtr na slova uvnitř náhledu, nový začátek i konec

    return Snippet(
        prefix + chunk + suffix, highlights
    )  # výsledek se zabalí do finálního objektu
