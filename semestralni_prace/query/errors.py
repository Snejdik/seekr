"""Výjimky dotazovacího jazyka."""

from ..models import SearchEngineError


class QueryError(SearchEngineError):
    """Vadný dotaz (syntaxe, prázdný dotaz, samotná negace, ...).

    Dědí ze SearchEngineError, takže ji CLI zachytí společně s ostatními chybami.
    """
