"""Strom dotazu."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Term:
    text: str


@dataclass(frozen=True)
class Phrase:
    terms: tuple[str, ...]


@dataclass(frozen=True)
class Not:
    child: Term | Phrase


@dataclass(frozen=True)
class And:
    children: tuple[Node, ...]


@dataclass(frozen=True)
class Or:
    children: tuple[Node, ...]


Node = Term | Phrase | Not | And | Or
