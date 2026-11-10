# seekr

Frayerska semestralni prace.

## Instalace

Potrebujes [uv](https://docs.astral.sh/uv/). Pak:

```bash
git clone https://github.com/Snejdik/seekr.git
cd seekr
uv sync
uv run pre-commit install
```

`pre-commit install` staci udelat jednou. Pri kazdem `git commit` se pak
automaticky spusti `ruff` a `pytest`.

## Spusteni

```bash
uv run python -m semestralni_prace.main
```

## Prikazy

| Co | Prikaz |
| --- | --- |
| Testy | `uv run pytest` |
| Kontrola kodu | `uv run ruff check .` |
| Formatovani | `uv run ruff format .` |
| Pridat knihovnu | `uv add <balicek>` |
| Pridat vyvojovy nastroj | `uv add --dev <balicek>` |

Po `uv add` commitni `pyproject.toml` i `uv.lock`.

## Struktura

```
semestralni_prace/   zdrojovy kod
tests/               testy
pyproject.toml       zavislosti a nastaveni
```

# Rozdělení týmu
1. Miloš Bínek - Textová vrstva, CLI a GUI
2. Jakub Šnejda - Index a persistence
3. Tomáš Palounek - Dotazovací jazyk
4. Dominik Padyšák - Ranking a aktualizace indexu