from dataclasses import dataclass
from typing import List, Optional
from .symbol import SymbolRegistry


@dataclass
class PatternElement:
    symbol_id: int
    phase: Optional[int]


@dataclass
class Rule:
    pattern: List[PatternElement]
    replacement: List[PatternElement]
    priority: int


def _parse_sequence(s: str, registry: SymbolRegistry) -> List[PatternElement]:
    elements: List[PatternElement] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch.isspace() or ch == '+':
            i += 1
            continue
        j = i
        while j < n and not s[j].isspace() and s[j] != '+':
            j += 1
        token = s[i:j]
        k = len(token)
        while k > 0 and token[k - 1].isdigit():
            k -= 1
        name = token[:k]
        phase: Optional[int] = None
        if k < len(token):
            phase_str = token[k:]
            if phase_str:
                phase_int = int(phase_str)
                if phase_int not in (0, 1):
                    raise ValueError("Invalid phase value: " + token)
                phase = phase_int
        if not name:
            raise ValueError("Invalid token without symbol name: " + token)
        idx = registry.get_or_register(name)
        elements.append(PatternElement(idx, phase))
        i = j
    return elements


def parse_rules(text: str, registry: SymbolRegistry) -> List[Rule]:
    rules: List[Rule] = []
    priority_counter = 0
    lines = text.splitlines()
    
    declared_defaults: dict[int, int] = {}
    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        lower = line.lower()
        if lower.startswith('idempotent'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                names = parts[1].split(',')
                for name in names:
                    name = name.strip()
                    if name:
                        registry.set_idempotent(name)
            continue
        if lower.startswith('default_phase') or lower.startswith('phase'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                pairs = parts[1].split(',')
                for pair in pairs:
                    pair = pair.strip()
                    if not pair:
                        continue
                    if '=' not in pair:
                        raise ValueError("Invalid default phase declaration: " + pair)
                    sym, ph = pair.split('=', 1)
                    sym = sym.strip()
                    ph = ph.strip()
                    if not ph.isdigit():
                        raise ValueError("Invalid phase value: " + ph)
                    phase_int = int(ph)
                    if phase_int not in (0, 1):
                        raise ValueError("Invalid phase value: " + ph)
                    
                    idx = registry.get_or_register(sym)
                    existing = declared_defaults.get(idx)
                    if existing is not None and existing != phase_int:
                        raise ValueError(f"Conflicting default phase for symbol {sym}")
                    declared_defaults[idx] = phase_int
                    registry.set_default_phase(sym, phase_int)
            continue
        if '->' in line:
            parts = line.split('->', 1)
            lhs = parts[0].strip()
            rhs_and_priority = parts[1].strip()
            if not lhs or not rhs_and_priority:
                raise ValueError("Rule must have non-empty pattern and replacement: " + line)
            
            priority_value: Optional[int] = None
            if 'priority=' in rhs_and_priority:
                rhs_part, pr = rhs_and_priority.split('priority=', 1)
                rhs_and_priority = rhs_part.strip()
                pr = pr.strip()
                if pr:
                    try:
                        priority_value = int(pr.split()[0])
                    except Exception:
                        raise ValueError("Invalid priority value in rule: " + line)
            elif ' priority ' in rhs_and_priority:
                tokens = rhs_and_priority.split()
                if tokens[-2].lower() == 'priority':
                    try:
                        priority_value = int(tokens[-1])
                    except Exception:
                        raise ValueError("Invalid priority value in rule: " + line)
                    rhs_and_priority = ' '.join(tokens[:-2])
            pattern = _parse_sequence(lhs, registry)
            replacement = _parse_sequence(rhs_and_priority, registry)
            pr_value = priority_counter if priority_value is None else priority_value
            rules.append(Rule(pattern, replacement, pr_value))
            if priority_value is None:
                priority_counter += 1
            continue
        raise ValueError(f"Invalid rule line at {line_no}: {line}")
    rules.sort(key=lambda r: r.priority)
    return rules