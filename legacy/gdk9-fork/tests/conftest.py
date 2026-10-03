"""Test configuration for pytest.

Ensures the repository root is on sys.path so test imports like
`from gdk9 ...` resolve when running pytest directly.
"""

import os
import sys


def _ensure_repo_root_on_path() -> None:
  repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
  if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


_ensure_repo_root_on_path()

