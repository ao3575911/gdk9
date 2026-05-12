import pytest
from srr.symbol import SymbolRegistry
from srr.rules import parse_rules
from srr.runtime import Reactor, run_reactor

def build_reactor(rule_text: str):
    registry = SymbolRegistry()
    rules = parse_rules(rule_text, registry)
    return Reactor(rules, registry), registry

def test_multi_character_symbols():
    rules = "foo bar -> baz"
    registry = SymbolRegistry()
    rule_list = parse_rules(rules, registry)
    reactor = Reactor(rule_list, registry)
    result = reactor.run(["foo", "bar"])
    names = [registry.id_to_name[sid] for sid, _ in result]
    assert names == ["baz"]

def test_phase_annotations_and_default_phase():
    rules = "default_phase: A=1\nA1 -> B"
    reactor, registry = build_reactor(rules)
    result = reactor.run(["A"])
    names = [registry.id_to_name[sid] for sid, _ in result]
    assert names == ["B"]

def test_idempotent_collapse():
    rules = "idempotent: A"
    reactor, registry = build_reactor(rules)
    seq = ["A"] * 5
    result = reactor.run(seq)
    assert len(result) == 1
    assert registry.id_to_name[result[0][0]] == "A"

def test_directional_semantics():
    rules = "AB -> C"
    reactor, registry = build_reactor(rules)
    seq = ["B", "A"]
    result = reactor.run(seq)
    names = [registry.id_to_name[sid] for sid, _ in result]
    assert names == ["B", "A"]

def test_phase_toggle_cycle_detection():
    rules = "default_phase: A=0\nA0 -> A1\nA1 -> A0"
    reactor, registry = build_reactor(rules)
    seq = ["A"]
    result = reactor.run(seq)
    assert len(result) == 1
    assert registry.id_to_name[result[0][0]] == "A"

def test_priority_rules():
    rules = "A -> B priority=1\nA -> C priority=0"
    reactor, registry = build_reactor(rules)
    seq = ["A"]
    result = reactor.run(seq)
    names = [registry.id_to_name[sid] for sid, _ in result]
    assert names == ["C"]

def test_invalid_default_phase_declaration():
    with pytest.raises(ValueError):
        parse_rules("default_phase: A", SymbolRegistry())

def test_invalid_rule_line():
    with pytest.raises(ValueError):
        parse_rules("no arrow here", SymbolRegistry())

def test_invalid_token():
    with pytest.raises(ValueError):
        parse_rules("-> B", SymbolRegistry())

@pytest.mark.parametrize("n", list(range(1, 21)))
def test_idempotent_property(n):
    rules = "idempotent: X"
    reactor, registry = build_reactor(rules)
    seq = ["X"] * n
    result = reactor.run(seq)
    assert len(result) == 1
    assert registry.id_to_name[result[0][0]] == "X"