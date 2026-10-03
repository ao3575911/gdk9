import pytest
from pathlib import Path
from gdk9.rewrite.symbol import SymbolRegistry
from gdk9.rewrite.rules import parse_rules
from gdk9.rewrite.runtime import Reactor


RULESETS = Path(__file__).resolve().parent / "rulesets"


def load_reactor(filename: str):
    found = RULESETS / filename
    if not found.exists():
        # ruleset5.txt and ruleset6.txt were never committed to Symbol-Rewrite-Reactor.
        pytest.skip(f"{filename} is not in the repo")
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