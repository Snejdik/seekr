"""Sdílené datové třídy a vlastní výjimky projektu."""

# IMPORTY (CLI zachytává jen SearchEngineError)
from __future__ import annotations

from dataclasses import dataclass, field


# VÝJIMKY
class SearchEngineError(
    Exception
):  # hierarchické, kdo chytí tuto výjimku, chytí i konkrétní chyby pod ní
    """Společný základ všech chyb vyhledávače"""


class FileReadError(SearchEngineError):
    """Soubor nelze přečíst. Nese cestu, případně důvod."""

    def __init__(self, path: object, reason: str) -> None:
        self.path = str(path)
        self.reason = reason
        super().__init__(f"{self.path}: {reason}")


class EmptyFileError(FileReadError):
    """Soubor je prázdný, nebo obsahuje neviditelné znaky."""


class BinaryFileError(FileReadError):
    """Soubor je binární (obsahuje nulové bajty)"""


class UnreadableFileError(FileReadError):
    """ "Soubor nelze otevřít nebo dekódovat jako UTF-8."""


# DATOVÉ TŘÍDY
@dataclass(frozen=True)  # frozen true = objekt se po vytvoření nedá měnit
class Token:  # Tokenizace, index i fráze
    """ "Normalizovaný termín a jeho pořadí v dokumentu (od 0)."""

    term: str
    position: int


@dataclass(frozen=True)
class FileInfo:  # otisk souboru. Metadata do indexu a detekce změn
    """Otisk souboru pro metadata indexu a detekci změn"""

    path: str
    size: int
    mtime: float
    sha256: str


@dataclass(frozen=True)
class Snippet:  # seznam dvojic ke zvýraznění
    """Výběr textu a pozice (start, konec) slov ke zvýraznění"""

    text: str
    highlights: list[tuple[int, int]] = field(
        default_factory=list
    )  # default_factory = pro každý nový objekt se vytvoří nový prázdný seznam


@dataclass(frozen=True)
class SearchResult:
    """Jeden výsledek hledání."""

    path: str
    score: float
    snippet: Snippet | None = None


@dataclass  # není frozen, protože se v průběhu indexace plní
class IndexReport:  # souhrn indexace pro výpis v CLI
    """ "Souhrn indexace pro výpis v CLI."""

    indexed: int = 0
    skipped: list[tuple[str, str]] = field(default_factory=list)
    unique_words: int = 0
    seconds: float = 0.0

    # Jaké výjimky, dataclassy využijí (mohou využít) ostatní části projektu:
    # 1 - všechno z models.py
    # 2 - Token, FileInfo, SearchEngineError (metadata dokumentu: cesta, velikost, čas změny a hash, základ pro vlastní chyby, ...)
    # 3 - SearchEngineError (základ pro chyby dotazu - nevyvážené uvozovky, prázdný dotaz, ...)
    # 4 - FileInfo, SearchEngineError (porovnání otisku souboru na disku s uloženým otiskem, chyby aktualizace, ...)
