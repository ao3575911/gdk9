from typing import List, Tuple
from .rules import Rule, PatternElement
from .symbol import SymbolRegistry


class Reactor:
    def __init__(self, rules: List[Rule], registry: SymbolRegistry, global_phase_toggle: bool = False):
        self.rules = sorted(rules, key=lambda r: r.priority)
        self.registry = registry
        self.global_phase_toggle = global_phase_toggle

    def _match(self, pattern: List[PatternElement], seq: List[Tuple[int, int]], pos: int) -> bool:
        if pos + len(pattern) > len(seq):
            return False
        for j, elem in enumerate(pattern):
            sid, phase = seq[pos + j]
            if sid != elem.symbol_id:
                return False
            if elem.phase is not None and phase != elem.phase:
                return False
        return True

    def _instantiate(self, replacement: List[PatternElement]) -> List[Tuple[int, int]]:
        out: List[Tuple[int, int]] = []
        for elem in replacement:
            phase = elem.phase if elem.phase is not None else self.registry.get_default_phase(elem.symbol_id)
            out.append((elem.symbol_id, phase))
        return out

    def _collapse(self, seq: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if not seq:
            return []
        out: List[Tuple[int, int]] = [seq[0]]
        for sid, phase in seq[1:]:
            last_sid, last_phase = out[-1]
            if self.registry.is_idempotent(sid) and sid == last_sid:
                continue
            out.append((sid, phase))
        return out

    def run(self, input_symbols: List[str], max_iters: int = 1000) -> List[Tuple[int, int]]:
        seq: List[Tuple[int, int]] = []
        for name in input_symbols:
            sid = self.registry.get_or_register(name)
            phase = self.registry.get_default_phase(sid)
            seq.append((sid, phase))
        seen = set()
        for _ in range(max_iters):
            changed = False
            i = 0
            new_seq: List[Tuple[int, int]] = []
            while i < len(seq):
                matched = False
                for rule in self.rules:
                    if self._match(rule.pattern, seq, i):
                        repl = self._instantiate(rule.replacement)
                        new_seq.extend(repl)
                        i += len(rule.pattern)
                        matched = True
                        changed = True
                        break
                if not matched:
                    new_seq.append(seq[i])
                    i += 1
            new_seq = self._collapse(new_seq)
            if self.global_phase_toggle:
                tmp = []
                for sid, phase in new_seq:
                    tmp.append((sid, 1 - phase))
                new_seq = tmp
            if not changed:
                return new_seq
            key = tuple(new_seq)
            if key in seen:
                return new_seq
            seen.add(key)
            if new_seq == seq:
                return new_seq
            seq = new_seq
        return seq


def run_reactor(rules: List[Rule], registry: SymbolRegistry, input_symbols: List[str], max_iters: int = 1000, global_phase_toggle: bool = False) -> List[str]:
    reactor = Reactor(rules, registry, global_phase_toggle)
    result = reactor.run(input_symbols, max_iters)
    return [registry.id_to_name[sid] for sid, _ in result]