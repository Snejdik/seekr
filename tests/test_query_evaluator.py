"""Testy evaluátoru nad ručně postaveným indexem a ručně postavenými stromy.

Nepotřebují index (část 2), tokenizer (část 1) ani parser.
"""

from collections import defaultdict

import pytest

from semestralni_prace.query.errors import QueryError
from semestralni_prace.query.evaluator import evaluate
from semestralni_prace.query.nodes import And, Not, Or, Phrase, Term


class FakeIndex:
    """Ručně postavený index: {term: {doc_id: [pozice]}}."""

    def __init__(self, docs: dict[int, str]) -> None:
        self._postings: dict[str, dict[int, list[int]]] = defaultdict(dict)
        for doc_id, text in docs.items():
            for pos, word in enumerate(text.split()):
                self._postings[word].setdefault(doc_id, []).append(pos)

    def get_postings(self, term):
        return self._postings.get(term, {})


DOCS = {
    1: "python generator a iterator v python",
    2: "java iterator tutorial",
    3: "python a java srovnani",
    4: "learning python",
    5: "generator basics",
}


@pytest.fixture
def index():
    return FakeIndex(DOCS)


# ------------------------------------------------------------------
# Test: Term, And, Or, Not


def test_term(index):
    assert evaluate(Term("python"), index) == {1, 3, 4}


def test_unknown_term(index):
    assert evaluate(Term("neexistuje"), index) == set()


def test_and_is_intersection(index):
    assert evaluate(And((Term("python"), Term("iterator"))), index) == {1}


def test_or_is_union(index):
    assert evaluate(Or((Term("python"), Term("java"))), index) == {1, 2, 3, 4}


def test_and_with_not_is_difference(index):
    tree = And((Term("python"), Not(Term("java"))))
    assert evaluate(tree, index) == {1, 4}


def test_not_may_come_first(index):
    tree = And((Not(Term("java")), Term("python")))
    assert evaluate(tree, index) == {1, 4}


def test_and_with_unknown_term(index):
    assert evaluate(And((Term("python"), Term("neexistuje"))), index) == set()


def test_or_with_unknown_term(index):
    assert evaluate(Or((Term("python"), Term("neexistuje"))), index) == {1, 3, 4}


def test_term_and_its_negation_is_empty(index):
    assert evaluate(And((Term("python"), Not(Term("python")))), index) == set()


def test_not_combined_with_or(index):
    # java -python OR generator
    tree = Or((And((Term("java"), Not(Term("python")))), Term("generator")))
    assert evaluate(tree, index) == {1, 2, 5}


def test_evaluate_does_not_modify_index(index):
    evaluate(And((Term("python"), Not(Term("java")))), index)
    assert set(index.get_postings("python")) == {1, 3, 4}


# ------------------------------------------------------------------
# Test: Phrase


def test_phrase_in_order(index):
    assert evaluate(Phrase(("python", "generator")), index) == {1}


def test_phrase_in_wrong_order(index):
    assert evaluate(Phrase(("generator", "python")), index) == set()


def test_phrase_requires_consecutive_positions(index):
    # v dokumentu 1 jsou oba termy, ale "a" je mezi nimi
    assert evaluate(Phrase(("generator", "iterator")), index) == set()
    assert evaluate(And((Term("generator"), Term("iterator"))), index) == {1}


def test_phrase_does_not_cross_document_boundary(index):
    # doc 4 končí "python", doc 5 začíná "generator"
    result = evaluate(Phrase(("python", "generator")), index)
    assert 4 not in result
    assert 5 not in result


def test_phrase_of_three_words(index):
    assert evaluate(Phrase(("generator", "a", "iterator")), index) == {1}
    assert evaluate(Phrase(("generator", "a", "tutorial")), index) == set()


def test_phrase_with_repeated_word(index):
    # "python" je v dokumentu 1 na pozicích 0 a 5, fráze začíná na 0
    assert evaluate(Phrase(("python", "generator")), index) == {1}


def test_phrase_with_unknown_word(index):
    assert evaluate(Phrase(("python", "neexistuje")), index) == set()


def test_negated_phrase(index):
    tree = And((Term("python"), Not(Phrase(("python", "generator")))))
    assert evaluate(tree, index) == {3, 4}


# ------------------------------------------------------------------
# Test: chyby


def test_lone_not_raises(index):
    with pytest.raises(QueryError):
        evaluate(Not(Term("java")), index)


def test_and_of_only_negations_raises(index):
    with pytest.raises(QueryError):
        evaluate(And((Not(Term("java")), Not(Term("python")))), index)
