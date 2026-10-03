from __future__ import annotations

import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


PROJECT_FILES = [
  "pyproject.toml",
  "README.md",
  "AGENTS.md",
  "Makefile",
]

INCLUDE_DIRS = [
  "gdk9",
  "docs",
  "tests",
]


def collect_files() -> list[Path]:
  root = Path(".").resolve()
  files: list[Path] = []
  for f in PROJECT_FILES:
    p = root / f
    if p.exists():
      files.append(p)
  for d in INCLUDE_DIRS:
    dp = root / d
    if dp.exists():
      for path in dp.rglob("*"):
        if path.is_file():
          if path.suffix == ".pyc":
            continue
          parts = set(path.parts)
          if "__pycache__" in parts or ".venv" in parts or "dist" in parts:
            continue
          files.append(path)
  return files


def main() -> int:
  dist = Path("dist")
  dist.mkdir(exist_ok=True)
  zip_path = dist / "gdk9-project.zip"
  files = collect_files()
  with ZipFile(zip_path, "w", ZIP_DEFLATED) as z:
    for f in files:
      arcname = f.relative_to(Path(".").resolve())
      z.write(f, arcname)
  print(zip_path)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
