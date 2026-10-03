from __future__ import annotations

import ast
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..errors import ConfigError, InputError
from ..imply import make_fusion, make_split, Rule, apply_rule
from ..state import set_rule, set_symbol
from ..principles import Principle


DEFAULT_PLUGIN_DIRS: List[Path] = [
  Path.cwd() / "plugins",
  Path(os.path.expanduser("~/.gdk9/plugins")),
]
DEFAULT_PLUGIN_CONFIG = Path(os.path.expanduser("~/.gdk9/plugins.json"))


@dataclass
class LoadedPlugin:
  name: str
  version: str
  description: str
  rules: List[Rule]
  symbol_energy: Dict[str, int]
  symbols: Dict[str, float]
  source: Path


def _read_text(path: Path) -> str:
  try:
    return path.read_text(encoding='utf-8')
  except Exception as exc:
    raise ConfigError(f"Failed to read plugin at {path}: {exc}")


def _parse_yaml_or_json(text: str, path: Path) -> Dict[str, Any]:
  # Try JSON first (valid YAML subset)
  try:
    return json.loads(text)
  except json.JSONDecodeError:
    pass
  # Try YAML if available
  try:
    import yaml  # type: ignore
    return yaml.safe_load(text)
  except Exception as exc:
    raise ConfigError(
      f"Unsupported or invalid plugin file {path.name}; install PyYAML or use JSON-compatible YAML."
    ) from exc


def _parse_python_literal_plugin(text: str, path: Path) -> Dict[str, Any]:
  """Read a Python plugin file and extract PLUGIN literal via AST without executing code."""
  try:
    tree = ast.parse(text, filename=str(path))
  except SyntaxError as exc:
    raise ConfigError(f"Invalid Python plugin syntax: {exc}") from exc
  plugin_node: Optional[ast.AST] = None
  for node in tree.body:
    if isinstance(node, ast.Assign):
      for target in node.targets:
        if isinstance(target, ast.Name) and target.id == 'PLUGIN':
          plugin_node = node.value
          break
  if plugin_node is None:
    raise ConfigError("Python plugin must define a top-level PLUGIN = {...} mapping")
  try:
    data = ast.literal_eval(plugin_node)  # type: ignore[arg-type]
  except Exception as exc:
    raise ConfigError("PLUGIN must be a literal mapping; no dynamic code allowed") from exc
  if not isinstance(data, dict):
    raise ConfigError("PLUGIN must be a mapping")
  return data


def find_plugin(name_or_path: str, base_dirs: Optional[Iterable[Path]] = None) -> Path:
  p = Path(name_or_path)
  # If direct path provided
  if p.exists():
    if p.is_dir():
      for cand in [p / 'plugin.json', p / 'plugin.yaml', p / 'plugin.yml', p / 'plugin.py']:
        if cand.exists():
          return cand
    return p
  search_dirs = list(base_dirs or DEFAULT_PLUGIN_DIRS)
  suffixes = ['.json', '.yaml', '.yml', '.py']
  for d in search_dirs:
    # file plugin
    for s in suffixes:
      candidate = d / f"{name_or_path}{s}"
      if candidate.exists():
        return candidate
    # directory plugin
    dir_candidate = d / name_or_path
    if dir_candidate.is_dir():
      for cand in [dir_candidate / 'plugin.json', dir_candidate / 'plugin.yaml', dir_candidate / 'plugin.yml', dir_candidate / 'plugin.py']:
        if cand.exists():
          return cand
  raise ConfigError(f"Plugin '{name_or_path}' not found in: " + ", ".join(str(x) for x in search_dirs))


def _validate_symbol_energy(se: Any) -> Dict[str, int]:
  if se is None:
    return {}
  if not isinstance(se, dict):
    raise ConfigError("symbol_energy must be a mapping of symbol->int")
  out: Dict[str, int] = {}
  for k, v in se.items():
    if not isinstance(k, str) or len(k) != 1:
      raise ConfigError("symbol_energy keys must be single-character strings")
    if not isinstance(v, int):
      raise ConfigError("symbol_energy values must be integers")
    out[k] = int(v)
  return out


def _validate_symbols(sym: Any) -> Dict[str, float]:
  if sym is None:
    return {}
  if not isinstance(sym, dict):
    raise ConfigError("symbols must be a mapping of name->float")
  out: Dict[str, float] = {}
  for k, v in sym.items():
    if not isinstance(k, str) or not k:
      raise ConfigError("symbols keys must be names")
    try:
      out[k] = float(v)
    except Exception:
      raise ConfigError("symbols values must be numeric")
  return out


def _build_rules(data: Dict[str, Any]) -> List[Rule]:
  rules: List[Rule] = []
  raw = data.get('rules', [])
  if raw is None:
    raw = []
  if not isinstance(raw, list):
    raise ConfigError("rules must be a list")
  for r in raw:
    if not isinstance(r, dict):
      raise ConfigError("each rule must be a mapping")
    rtype = r.get('type')
    name = r.get('name')
    if rtype not in {'fusion', 'split'}:
      raise ConfigError("rule type must be 'fusion' or 'split'")
    if not isinstance(name, str) or not name:
      raise ConfigError("rule name must be a non-empty string")
    if rtype == 'fusion':
      arity = int(r.get('arity', 2))
      out_name = str(r.get('out', 'AUTO'))
      rules.append(make_fusion(name, out_name, arity))
    else:
      out_a = str(r.get('out_a', 'OUT_A'))
      out_b = str(r.get('out_b', 'OUT_B'))
      ratio = float(r.get('ratio', 0.5))
      rules.append(make_split(name, out_a, out_b, ratio))
  return rules


def _run_checks(plugin: LoadedPlugin, tol: float = 1e-9) -> None:
  checks = _coalesce_checks(plugin.source)
  if not checks:
    return
  # Build ephemeral symbol table from provided checks
  for chk in checks:
    rule_name = chk.get('rule')
    inputs = chk.get('inputs', [])
    if not isinstance(inputs, list) or not isinstance(rule_name, str):
      raise ConfigError("check must include 'rule' and list 'inputs'")
    # Build temporary symbol energies
    symbols: Dict[str, float] = {}
    for s in inputs:
      if not isinstance(s, dict) or 'name' not in s or 'energy' not in s:
        raise ConfigError("each input must be a mapping with name and energy")
      symbols[str(s['name'])] = float(s['energy'])
    # Find corresponding rule
    prule = None
    for r in plugin.rules:
      if r.name == rule_name:
        prule = r
        break
    if prule is None:
      raise ConfigError(f"check references unknown rule: {rule_name}")
    names = [str(s['name']) for s in inputs]
    res = apply_rule(prule, symbols, names, tol=tol)
    # Energy conservation validation is guaranteed by apply_rule; still assert sums
    ein = sum(symbols[n] for n in names)
    eout = sum(o['energy'] for o in res.get('outputs', []))
    if abs(ein - eout) > tol:
      raise ConfigError("energy conservation failed in plugin checks")


def _coalesce_checks(path: Path) -> List[Dict[str, Any]]:
  # Try to read a sibling checks file for directory plugins
  parent = path.parent
  if parent.is_dir():
    for cand in [parent / 'checks.json', parent / 'checks.yaml', parent / 'checks.yml']:
      if cand.exists():
        data = _parse_yaml_or_json(_read_text(cand), cand)
        arr = data.get('checks', data if isinstance(data, list) else [])
        if isinstance(arr, list):
          return arr  # type: ignore[return-value]
  # Inline checks may be embedded in same file (handled in load_plugin)
  return []


def load_plugin(path: Path) -> LoadedPlugin:
  text = _read_text(path)
  if path.suffix.lower() in {'.json', '.yaml', '.yml'}:
    data = _parse_yaml_or_json(text, path)
  elif path.suffix.lower() == '.py':
    data = _parse_python_literal_plugin(text, path)
  else:
    raise ConfigError("Unsupported plugin type; use .json, .yml/.yaml, or .py")
  if not isinstance(data, dict):
    raise ConfigError("plugin root must be a mapping")
  name = str(data.get('name') or path.stem)
  version = str(data.get('version') or '0.1')
  description = str(data.get('description') or '')
  symbol_energy = _validate_symbol_energy(data.get('symbol_energy'))
  symbols = _validate_symbols(data.get('symbols'))
  rules = _build_rules(data)
  plugin = LoadedPlugin(name=name, version=version, description=description, rules=rules, symbol_energy=symbol_energy, symbols=symbols, source=path)
  # Optional inline checks
  inline_checks = data.get('checks')
  if isinstance(inline_checks, list):
    # temporarily write inline checks into sibling to reuse runner
    pass  # run via direct loop below
  # Run inline checks if provided
  if isinstance(inline_checks, list) and inline_checks:
    for chk in inline_checks:
      if not isinstance(chk, dict):
        raise ConfigError("check entries must be mappings")
      rule_name = chk.get('rule')
      inputs = chk.get('inputs', [])
      if not isinstance(inputs, list) or not isinstance(rule_name, str):
        raise ConfigError("check must include 'rule' and list 'inputs'")
      symbols_map: Dict[str, float] = {}
      for s in inputs:
        if not isinstance(s, dict) or 'name' not in s or 'energy' not in s:
          raise ConfigError("each input must be a mapping with name and energy")
        symbols_map[str(s['name'])] = float(s['energy'])
      rule_obj = next((r for r in plugin.rules if r.name == rule_name), None)
      if rule_obj is None:
        raise ConfigError(f"check references unknown rule: {rule_name}")
      names = [str(s['name']) for s in inputs]
      res = apply_rule(rule_obj, symbols_map, names, tol=1e-9)
      ein = sum(symbols_map[n] for n in names)
      eout = sum(o['energy'] for o in res.get('outputs', []))
      if abs(ein - eout) > 1e-9:
        raise ConfigError("energy conservation failed in plugin checks")
  # Also attempt to run sibling checks files
  _run_checks(plugin)
  return plugin


def list_available(base_dirs: Optional[Iterable[Path]] = None) -> List[str]:
  names: List[str] = []
  for d in (base_dirs or DEFAULT_PLUGIN_DIRS):
    if not d.exists():
      continue
    for p in d.iterdir():
      if p.is_file() and p.suffix.lower() in {'.json', '.yaml', '.yml', '.py'}:
        names.append(p.stem)
      elif p.is_dir() and any((p / f"plugin{ext}").exists() for ext in ('.json', '.yaml', '.yml', '.py')):
        names.append(p.name)
  return sorted(list(set(names)))


def apply_plugin(plugin: LoadedPlugin, principle: Principle, state: Dict[str, Any]) -> Tuple[Principle, Dict[str, Any], Dict[str, Any]]:
  # Merge symbol_energy into principle (override existing)
  if plugin.symbol_energy:
    merged = dict(principle.symbol_energy)
    merged.update(plugin.symbol_energy)
    principle.symbol_energy = merged
  # Seed symbols into state
  actor = f"plugin:{plugin.name}"
  if plugin.symbols:
    for k, v in plugin.symbols.items():
      set_symbol(state, k, float(v), actor=actor)
  # Add rules (avoid overwriting existing rules with same name)
  rules = state.setdefault('rules', {})
  added = 0
  for r in plugin.rules:
    if r.name not in rules:
      set_rule(state, r.name, r.to_json(), actor=actor)
      added += 1
  return principle, state, {"rules_added": added, "symbols_added": len(plugin.symbols), "symbol_energy_updates": len(plugin.symbol_energy)}


def _load_config(path: Path = DEFAULT_PLUGIN_CONFIG) -> Dict[str, Any]:
  if not path.exists():
    return {"enabled": [], "paths": {}}
  try:
    return json.loads(path.read_text(encoding='utf-8'))
  except Exception as exc:
    raise ConfigError(f"Failed to read plugin config {path}: {exc}")


def _save_config(cfg: Dict[str, Any], path: Path = DEFAULT_PLUGIN_CONFIG) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp = path.with_suffix(path.suffix + '.tmp')
  tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
  tmp.replace(path)


def enable_plugin(name: str, resolved_path: Path, config_path: Path = DEFAULT_PLUGIN_CONFIG) -> None:
  cfg = _load_config(config_path)
  enabled = cfg.setdefault('enabled', [])
  if name not in enabled:
    enabled.append(name)
  cfg.setdefault('paths', {})[name] = str(resolved_path)
  _save_config(cfg, config_path)


def disable_plugin(name: str, config_path: Path = DEFAULT_PLUGIN_CONFIG) -> None:
  cfg = _load_config(config_path)
  enabled = cfg.setdefault('enabled', [])
  if name in enabled:
    enabled.remove(name)
  cfg.get('paths', {}).pop(name, None)
  _save_config(cfg, config_path)


def reset_config(config_path: Path = DEFAULT_PLUGIN_CONFIG) -> None:
  """Reset plugin configuration to defaults (no enabled plugins)."""
  _save_config({"enabled": [], "paths": {}}, config_path)


def auto_boot(principle: Principle, state: Dict[str, Any]) -> Tuple[Principle, Dict[str, Any], List[str]]:
  cfg = _load_config(DEFAULT_PLUGIN_CONFIG)
  enabled = cfg.get('enabled', [])
  loaded: List[str] = []
  for name in enabled:
    pstr = cfg.get('paths', {}).get(name)
    path = Path(pstr) if pstr else find_plugin(name)
    plugin = load_plugin(path)
    principle, state, _ = apply_plugin(plugin, principle, state)
    loaded.append(plugin.name)
  return principle, state, loaded
