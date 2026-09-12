# Prove gate

As of 2026-09-12, **green CI on `main` is the prove gate** for every later GDk9 idea.

## What “proved” means

A change is not done when it looks right in a chat. It is done when:

1. It lands on (or is proposed against) `https://github.com/ao3575911/gdk9`
2. GitHub Actions **CI** on that commit is green — Python **3.9–3.12**, extras `dev` and `dev,secure`
3. Critical lint passes: `ruff check gdk9 --select E9,F63,F7,F82`
4. `python -m pytest -q` passes

Workflow: `.github/workflows/ci.yml`.

## Local equivalent

```bash
pip install -e ".[dev,secure]"
ruff check gdk9 --select E9,F63,F7,F82
python -m pytest -q
```

## Research discipline

- Prefer the smallest experiment that could **fail**.
- Do not claim SOTA, new energy laws, or KeySuite equivalence without a prove path above.
- Kernel demos (`gdk9 kernel …`) are research smoke — delightful, energy-conserving, and CI-backed — not marketing.
- Conserved-search vs naive join experiment: [`docs/EXPERIMENT_CONSERVE_SEARCH.md`](EXPERIMENT_CONSERVE_SEARCH.md) (pytest: `tests/experiment/test_conserve_vs_naive.py`).