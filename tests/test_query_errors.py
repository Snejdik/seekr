from semestralni_prace.models import SearchEngineError
from semestralni_prace.query.errors import QueryError


def test_query_error_is_search_engine_error():
    # CLI zachytává jen SearchEngineError, QueryError pod ni musí patřit
    assert issubclass(QueryError, SearchEngineError)
    assert isinstance(QueryError("prázdný dotaz"), SearchEngineError)
