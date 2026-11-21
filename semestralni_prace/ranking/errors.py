from semestralni_prace.models import SearchEngineError


class RankingError(SearchEngineError):
    """Err. pri vypoctu relevance nebo pri aktualizaci indexu"""
