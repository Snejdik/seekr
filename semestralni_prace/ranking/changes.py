"""Zmeny souboru a aktualizace indexu."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ChangeStatus(Enum):
    """Stav zmeny souboru."""

    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


@dataclass(frozen=True)
class UpdateSummary:
    """Souhrn aktualizaci."""

    added: tuple[str, ...] = field(default_factory=tuple)
    modified: tuple[str, ...] = field(default_factory=tuple)
    deleted: tuple[str, ...] = field(default_factory=tuple)
    unchanged: int = 0
