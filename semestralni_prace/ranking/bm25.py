"""Vypocet relevance dokumentu pomoci algoritmu BM25 a stabilni razeni vysledku."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from semestralni_prace.models import SearchResult
from semestralni_prace.ranking.errors import RankingError


def compute_idf(total_docs: int, docs_with_term: int) -> float:
    """Spocita inverzni frekvenci dokumentu (IDF) pro jeden termin."""
    if total_docs <= 0 or docs_with_term <= 0:
        return 0.0
    return math.log(1.0 + (total_docs - docs_with_term + 0.5) / (docs_with_term + 0.5))


def bm25_score(
    query_terms: Sequence[str],
    term_freqs: Mapping[str, int],
    doc_freqs: Mapping[str, int],
    doc_length: int,
    avg_doc_length: float,
    total_docs: int,
    *,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    """Spocita BM25 skore jednoho dokumentu vuci zadanemu dotazu."""
    if k1 < 0:
        raise RankingError("Parametr k1 nesmi byt zaporny.")
    if not 0.0 <= b <= 1.0:
        raise RankingError("Parametr b musi byt v intervalu <0.0, 1.0>.")

    if total_docs <= 0 or doc_length <= 0 or avg_doc_length <= 0.0:
        return 0.0

    score = 0.0
    length_norm = 1.0 - b + b * (doc_length / avg_doc_length)

    for term in query_terms:
        tf = term_freqs.get(term, 0)
        if tf <= 0:
            continue
        df = doc_freqs.get(term, 0)
        idf = compute_idf(total_docs, df)
        numerator = tf * (k1 + 1.0)
        denominator = tf + k1 * length_norm
        score += idf * (numerator / denominator)

    return score


def rank_documents(
    query_terms: Sequence[str],
    candidate_paths: Sequence[str],
    doc_term_freqs: Mapping[str, Mapping[str, int]],
    doc_freqs: Mapping[str, int],
    doc_lengths: Mapping[str, int],
    avg_doc_length: float,
    total_docs: int,
    *,
    k1: float = 1.5,
    b: float = 0.75,
    # descending: bool = True,
) -> list[SearchResult]:
    """Dokumenty pomoci BM25 dostanou "skore" a seradi je sestupne (dle liba po uprave i vzestupne) podle skore."""
    results: list[SearchResult] = []

    for path in candidate_paths:
        score = bm25_score(
            query_terms=query_terms,
            term_freqs=doc_term_freqs.get(path, {}),
            doc_freqs=doc_freqs,
            doc_length=doc_lengths.get(path, 0),
            avg_doc_length=avg_doc_length,
            total_docs=total_docs,
            k1=k1,
            b=b,
        )
        results.append(SearchResult(path=path, score=score))

    # Stabilni razeni: nejvyssi skore prvni (-r.score), pripadne odkomentovat radek 66 descending pro nejmensi skore prvni (r.score)
    # a zmenit lambdu na (-r score if descending else r.score, r.path)
    # pri shode abecedne podle cesty (r.path)
    return sorted(results, key=lambda r: (-r.score, r.path))
