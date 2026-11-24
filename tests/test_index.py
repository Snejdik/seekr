from semestralni_prace.index.inverted_index import InvertedIndex
from semestralni_prace.models import Token


def test_add_document_stores_positions():
    index = InvertedIndex()
    tokens = [
        Token("python", 0),
        Token("je", 1),
        Token("skvely", 2),
        Token("python", 3),
    ]
    index.add_document(0, "a.txt", tokens)

    assert index.get_postings("python") == {0: [0, 3]}
    assert index.get_postings("je") == {0: [1]}


def test_unknown_term_returns_empty():
    index = InvertedIndex()
    assert index.get_postings("java") == {}


def test_doc_count():
    index = InvertedIndex()
    index.add_document(0, "a.txt", [Token("a", 0)])
    index.add_document(1, "b.txt", [Token("b", 0)])
    assert index.doc_count() == 2
