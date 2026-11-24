"""Obrácený index: ke každému slovu si pamatuje, kde se vyskytuje."""


class InvertedIndex:
    def __init__(self):
        # slovo -> {číslo dokumentu: [pozice slova v dokumentu]}
        self.postings = {}
        # číslo dokumentu -> cesta k souboru
        self.documents = {}

    def add_document(self, doc_id, path, tokens):
        """Přidá dokument do indexu."""
        self.documents[doc_id] = path

        for token in tokens:
            if token.term not in self.postings:
                self.postings[token.term] = {}
            if doc_id not in self.postings[token.term]:
                self.postings[token.term][doc_id] = []
            self.postings[token.term][doc_id].append(token.position)

    def get_postings(self, term):
        """Vrátí {doc_id: [pozice]} pro slovo. Neznámé slovo = prázdný slovník."""
        return self.postings.get(term, {})

    def doc_count(self):
        """Počet dokumentů v indexu."""
        return len(self.documents)
