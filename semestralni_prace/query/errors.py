"""Výjimky dotazovacího jazyka."""


class QueryError(Exception):
    """Vadný dotaz (syntaxe, prázdný dotaz, samotná negace, ...)."""
