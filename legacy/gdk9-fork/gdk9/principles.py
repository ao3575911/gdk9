from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from .errors import ConfigError


@dataclass
class Principle:
  name: str
  description: str
  symbol_energy: Dict[str, int] = field(default_factory=dict)
  letter_mode: str = "a1z26"  # a1z26 or codepoint
  number_mode: str = "digital_root"  # digital_root
  normalize_zero_to_nine: bool = True
  weights: Dict[str, int] = field(default_factory=lambda: {"letter": 1, "digit": 1, "symbol": 1})
  harmonics: bool = True

  @staticmethod
  def default() -> "Principle":
    # Prefer official bundled mapping if present
    try:
      here = Path(__file__).parent
      official = here / 'data' / 'official.json'
      if official.exists():
        data = json.loads(official.read_text(encoding='utf-8'))
        return Principle(
          name=data.get("name", "Gdk9 Official"),
          description=data.get("description", "Official Gdk9 mapping."),
          symbol_energy=data.get("symbol_energy", {}),
          letter_mode=data.get("letter_mode", "a1z26"),
          number_mode=data.get("number_mode", "digital_root"),
          normalize_zero_to_nine=bool(data.get("normalize_zero_to_nine", True)),
          weights=data.get("weights", {"letter": 1, "digit": 1, "symbol": 1}),
          harmonics=bool(data.get("harmonics", True)),
        )
    except Exception:
      pass
    return Principle(
      name="Ninefold Grid",
      description=(
        "Default Gdk9 principle: A1Z26 letters, digital-root numbers, "
        "custom symbol energies, zero maps to nine."
      ),
      symbol_energy={
        ".": 1,
        ",": 2,
        "!": 3,
        "?": 4,
        ":": 5,
        ";": 6,
        "-": 7,
        "_": 8,
        "*": 9,
        "#": 5,
        "+": 4,
        "=": 6,
        "@": 8,
        "$": 7,
        "%": 5,
        "&": 9,
        "/": 3,
        "\\": 3,
        "(": 2,
        ")": 2,
        "[": 2,
        "]": 2,
        "{": 2,
        "}": 2,
        "<": 1,
        ">": 1,
        "|": 1,
        "~": 9,
        "^": 8,
      },
      weights={"letter": 1, "digit": 1, "symbol": 1},
      harmonics=True,
    )


def load_principle(path: Optional[str]) -> Principle:
  if not path:
    return Principle.default()
  p = Path(path)
  if not p.exists():
    raise ConfigError(f"Principle file not found: {path}")
  try:
    if p.suffix.lower() in {".json"}:
      data = json.loads(p.read_text(encoding="utf-8"))
    elif p.suffix.lower() in {".yml", ".yaml"}:
      try:
        import yaml  # type: ignore
      except Exception as exc:  # pragma: no cover - optional dep
        raise ConfigError(
          "YAML support requires PyYAML; install it or use JSON."
        ) from exc
      data = yaml.safe_load(p.read_text(encoding="utf-8"))
    else:
      raise ConfigError("Unsupported principle file type. Use .json or .yml/.yaml")
  except json.JSONDecodeError as exc:
    raise ConfigError(f"Invalid JSON in principle file: {exc}") from exc

  try:
    pr = Principle(
      name=data.get("name", "Custom Principle"),
      description=data.get("description", ""),
      symbol_energy=data.get("symbol_energy", {}),
      letter_mode=data.get("letter_mode", "a1z26"),
      number_mode=data.get("number_mode", "digital_root"),
      normalize_zero_to_nine=bool(data.get("normalize_zero_to_nine", True)),
      weights=data.get("weights", {"letter": 1, "digit": 1, "symbol": 1}),
      harmonics=bool(data.get("harmonics", True)),
    )
  except Exception as exc:
    raise ConfigError(f"Invalid principle schema: {exc}") from exc
  # basic validation
  if not isinstance(pr.symbol_energy, dict):
    raise ConfigError("symbol_energy must be a mapping of symbol->int")
  for k, v in pr.symbol_energy.items():
    if not isinstance(k, str) or len(k) != 1:
      raise ConfigError("symbol_energy keys must be single-character strings")
    if not isinstance(v, int):
      raise ConfigError("symbol_energy values must be integers")
  if pr.letter_mode not in {"a1z26", "codepoint"}:
    raise ConfigError("letter_mode must be 'a1z26' or 'codepoint'")
  if pr.number_mode not in {"digital_root"}:
    raise ConfigError("number_mode must be 'digital_root'")
  return pr
