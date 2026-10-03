import pytest
from pathlib import Path
from srr.symbol import SymbolRegistry
from srr.rules import parse_rules
from srr.runtime import Reactor


def load_reactor(filename: str):
    base = Path(__file__).resolve()
    found = None
    for parent in base.parents:
        candidate = parent / filename
        if candidate.exists():
            found = candidate
            break
    if found is None:
        raise FileNotFoundError(filename)
    text = found.read_text()
    registry = SymbolRegistry()
    rules = parse_rules(text, registry)
    return Reactor(rules, registry), registry


def test_ruleset5_pairs():
    reactor, registry = load_reactor("ruleset5.txt")
    cases = [
        (['R', 'S'], 'R'),
        (['S', 'R'], 'R'),
        (['P', 'R'], 'P'),
        (['R', 'P'], 'P'),
        (['S', 'P'], 'S'),
        (['P', 'S'], 'S'),
    ]
    for seq, expected in cases:
        result = reactor.run(seq)
        names = [registry.id_to_name[sid] for sid, _ in result]
        assert "".join(names) == expected


def test_ruleset6_transitions():
    reactor, registry = load_reactor("ruleset6.txt")
    result = reactor.run(['ON', 'REQ'])
    names = [registry.id_to_name[sid] for sid, _ in result]
    assert names == ['ON']
    result = reactor.run(['ON', 'REQ', 'SIG'])
    names = [registry.id_to_name[sid] for sid, _ in result]
    assert names == ['OFF']
    result = reactor.run(['OFF', 'REQ', 'SIG'])
    names = [registry.id_to_name[sid] for sid, _ in result]
    assert names == ['ON']
    result = reactor.run(['ON', 'REQ', 'SIG', 'REQ', 'SIG'])
    names = [registry.id_to_name[sid] for sid, _ in result]
    assert names == ['ON']


def test_ruleset7_arithmetic():
    reactor, registry = load_reactor("ruleset7.txt")
    cases = [
        (['one', 'plus', 'one'], 'two'),
        (['one', 'plus', 'two'], 'three'),
        (['two', 'plus', 'one'], 'three'),
        (['two', 'plus', 'two'], 'four'),
        (['two', 'plus', 'three'], 'five'),
        (['three', 'plus', 'two'], 'five'),
        (['one', 'plus', 'three'], 'four'),
        (['three', 'plus', 'one'], 'four'),
    ]
    for seq, expected in cases:
        result = reactor.run(seq)
        names = [registry.id_to_name[sid] for sid, _ in result]
        assert "".join(names) == expected


def test_empty_input():
    registry = SymbolRegistry()
    rules = parse_rules("", registry)
    reactor = Reactor(rules, registry)
    result = reactor.run([])
    assert result == []


def test_long_idempotent_collapse():
    registry = SymbolRegistry()
    rules = parse_rules("idempotent: X", registry)
    reactor = Reactor(rules, registry)
    seq = ['X'] * 1000
    result = reactor.run(seq)
    assert len(result) == 1
    assert registry.id_to_name[result[0][0]] == 'X'