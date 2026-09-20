"""Test configuration for pytest.

Ensures the repository root is on sys.path so test imports like
`from gdk9 ...` resolve when running pytest directly.
"""

import os
import sys

import pytest


def _ensure_repo_root_on_path() -> None:
  repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
  if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


_ensure_repo_root_on_path()


def pytest_configure(config: pytest.Config) -> None:
  config.addinivalue_line(
    "markers",
    "egglog: requires optional egglog extra (pip install '.[egglog]'); skips if missing",
  )
