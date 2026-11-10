<<<<<<< HEAD
# seekr
Frayerska semestralni prace
=======
# Semestralni prace

## Spusteni

Nainstaluj [uv](https://docs.astral.sh/uv/) a pak:

```bash
git clone https://github.com/Snejdik/seekr.git
cd seekr
uv sync
uv run python -m semestralni_prace.main
```

## Vyvoj

Po prvnim `git clone` zapni pre-commit hook (jednou):

```bash
uv run pre-commit install
```

Pri kazdem `git commit` se pak sam spusti `ruff` a `pytest`.

| Co | Prikaz |
| --- | --- |
| Testy | `uv run pytest` |
| Kontrola kodu | `uv run ruff check .` |
| Formatovani | `uv run ruff format .` |
| Vsechny hooky rucne | `uv run pre-commit run --all-files` |
| Pridat knihovnu | `uv add <balicek>` |
| Pridat vyvojovy nastroj | `uv add --dev <balicek>` |

Po `uv add` commitni `pyproject.toml` i `uv.lock`.
>>>>>>> c49f142 (initial commit)
