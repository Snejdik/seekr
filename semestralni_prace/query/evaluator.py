"""Vyhodnocení stromu dotazu nad posting listy indexu.

Modul zná jen strom (nodes.py) a rozhraní indexu. Neřeší parsování ani tokenizaci.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from .errors import QueryError
from .nodes import And, Node, Not, Or, Phrase, Term


class IndexLike(Protocol):
    """Minimální rozhraní, které od indexu (část 2) potřebuju.

    Vrací {doc_id: [pozice slova v dokumentu]}; neznámý term = prázdný dict.
    """

    def get_postings(self, term: str) -> Mapping[Any, Sequence[int]]: ...


def _phrase_docs(terms: tuple[str, ...], index: IndexLike) -> set:
    """Dokumenty, kde jsou slova fráze na po sobě jdoucích pozicích."""
    postings = [index.get_postings(t) for t in terms]
    docs = set(postings[0]).intersection(*postings[1:])
    result = set()
    for doc in docs:
        # možné začátky fráze = pozice prvního slova
        starts = set(postings[0][doc])
        for offset, p in enumerate(postings[1:], start=1):
            # k-té slovo musí být přesně o k pozic za začátkem
            starts &= {pos - offset for pos in p[doc]}
            if not starts:
                break
        if starts:
            result.add(doc)
    return result


def evaluate(node: Node, index: IndexLike) -> set:
    """Vrátí množinu doc_id, které vyhovují stromu dotazu."""
    if isinstance(node, Term):
        return set(index.get_postings(node.text))
    if isinstance(node, Phrase):
        return _phrase_docs(node.terms, index)
    if isinstance(node, Or):
        result: set = set()
        for child in node.children:
            result |= evaluate(child, index)
        return result
    if isinstance(node, And):
        positives = [c for c in node.children if not isinstance(c, Not)]
        negatives = [c.child for c in node.children if isinstance(c, Not)]
        if not positives:
            raise QueryError(
                "Dotaz obsahuje jen negace — přidej aspoň jeden kladný term."
            )
        result = evaluate(positives[0], index)
        for child in positives[1:]:
            if not result:
                break
            result &= evaluate(child, index)
        for child in negatives:
            if not result:
                break
            result -= evaluate(child, index)
        return result
    raise QueryError(
        "Samotná negace nejde vyhodnotit — přidej aspoň jeden kladný term."
    )
