"""Golden numeric contract for gdk9.dcg letter class / energy / 4D vector.

Loads tests/fixtures/dcg_golden.json and asserts each pinned field against
the live public API. No new maths — values must match gdk9/dcg.py as-is.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gdk9.dcg import symmetry_class, sym_energy, vectorize, word_sym_energy, word_vector

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "dcg_golden.json"
ABS_TOL = 1e-12

EXPECTED_WORDS = (
    "FWEM",
    "Hello",
    "The quick brown fox jumps over the lazy dog",
)
EXPECTED_API = (
    "symmetry_class",
    "sym_energy",
    "vectorize",
    "word_sym_energy",
    "word_vector",
)


def _load_fixture() -> dict:
    with FIXTURE_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def golden() -> dict:
    return _load_fixture()


def test_fixture_schema_and_pinned_words(golden: dict) -> None:
    assert golden["source_module"] == "gdk9.dcg"
    assert golden["source_file"] == "gdk9/dcg.py"
    assert golden["api"] == list(EXPECTED_API)
    words = [entry["word"] for entry in golden["words"]]
    assert words == list(EXPECTED_WORDS)


@pytest.mark.parametrize("idx", range(len(EXPECTED_WORDS)))
def test_word_aggregates_match_live(golden: dict, idx: int) -> None:
    entry = golden["words"][idx]
    word = entry["word"]
    assert entry["word_sym_energy"] == pytest.approx(word_sym_energy(word), abs=ABS_TOL)
    assert list(entry["word_vector"]) == pytest.approx(list(word_vector(word)), abs=ABS_TOL)


@pytest.mark.parametrize("idx", range(len(EXPECTED_WORDS)))
def test_letter_fields_match_live(golden: dict, idx: int) -> None:
    entry = golden["words"][idx]
    letters = [ch for ch in entry["word"] if ch.isalpha()]
    assert [item["char"] for item in entry["letters"]] == letters
    for item in entry["letters"]:
        ch = item["char"]
        assert item["symmetry_class"] == symmetry_class(ch)
        assert item["sym_energy"] == pytest.approx(sym_energy(ch), abs=ABS_TOL)
        assert list(item["vectorize"]) == pytest.approx(list(vectorize(ch)), abs=ABS_TOL)
