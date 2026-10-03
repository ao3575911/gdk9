import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { readdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";
import { reduceBuffer, reduce_buffer } from "./reducer.ts";
import { literalSymbol, isBindMarker } from "./symbols.ts";
import { generateTransitionTable, lookupTransition } from "./fsm.ts";
import { GDK9_GRAMMAR, GRAMMAR_SHA256, loadGrammar } from "./grammar.ts";
import { Session } from "./session.ts";
import { runConformance, runVector } from "./conformance.ts";
import { CONFORMANCE_VECTORS, type ConformanceVector } from "./vectors.ts";

type HarvestedExample = {
  source: string;
  buffer: Array<string | { kind: "literal"; value: string }>;
  mode: string | null;
  receipt: string;
};

function harvestReductionExamples(markdown: string): HarvestedExample[] {
  const fence = markdown.match(/```([\s\S]*?)```/);
  if (!fence) return [];
  const lines = fence[1]!.split("\n").map((l) => l.trim()).filter(Boolean);
  const examples: HarvestedExample[] = [];
  for (const line of lines) {
    const match = line.match(/^reduce_buffer\((.*)\) => (.*)$/);
    if (!match) continue;
    const [, call, rawReceipt] = match;
    const modeMatch = call!.match(/,\s*"([A-Za-z0-9]+)"\s*$/);
    const mode = modeMatch ? modeMatch[1]! : null;
    const listMatch = call!.match(/\[(.*)\]/);
    if (!listMatch) continue;
    const inner = listMatch[1]!.trim();
    const buffer: HarvestedExample["buffer"] = [];
    if (inner) {
      const parts = inner.split(",").map((p) => p.trim());
      for (const part of parts) {
        const lit = part.match(/^literal\("((?:\\.|[^"])*)"\)$/);
        if (lit) {
          buffer.push({ kind: "literal", value: lit[1]! });
          continue;
        }
        const str = part.match(/^"((?:\\.|[^"])*)"$/);
        if (str) buffer.push(str[1]!);
      }
    }
    examples.push({ source: line, buffer, mode, receipt: rawReceipt ?? "" });
  }
  return examples;
}

describe("reduce_buffer", () => {
  it("is a single function identity", () => {
    assert.equal(reduceBuffer, reduce_buffer);
  });

  it("is the only implication algebra", () => {
    assert.equal(reduceBuffer(["C", "C", ".", "3", "3"]), "CC→33");
    assert.equal(reduceBuffer(["A", "B"]), "AB");
    assert.equal(reduceBuffer(["A", ".", "B", ".", "C"]), "A→B.C");
    assert.equal(reduceBuffer([".", "B"]), "→B");
    assert.equal(reduceBuffer(["A", "."]), "A→");
    assert.equal(reduceBuffer([]), "");
    assert.equal(reduceBuffer(["A", "B"], "X"), "X(AB)");
    assert.equal(reduceBuffer(["A", ".", "B"], "X"), "X(A→B)");
    assert.equal(reduceBuffer(["A", literalSymbol("."), "B"]), "A.B");
  });

  it("does not treat escaped literal dot as bind", () => {
    assert.equal(isBindMarker(literalSymbol(".")), false);
    assert.equal(isBindMarker("."), true);
  });
});

describe("fsm isolation", () => {
  it("does not import reducer", () => {
    const src = readFileSync(new URL("./fsm.ts", import.meta.url), "utf8");
    assert.equal(src.includes("reduceBuffer"), false);
    assert.equal(src.includes("reducer"), false);
  });

  it("MODE+BIND is ERROR", () => {
    const table = generateTransitionTable(GDK9_GRAMMAR);
    const rule = lookupTransition(table, "MODE", "BIND");
    assert.deepEqual(rule, { next: "ERROR", action: "noop" });
  });
});

describe("docs harvest", () => {
  it("asserts fenced REDUCTION.md examples against reduce_buffer", () => {
    const markdown = readFileSync(join(process.cwd(), "docs/REDUCTION.md"), "utf8");
    const examples = harvestReductionExamples(markdown);
    assert.ok(examples.length >= 8);
    for (const example of examples) {
      const actual = reduceBuffer(example.buffer, example.mode);
      assert.equal(actual, example.receipt, example.source);
    }
  });

  it("freeze docs are present", () => {
    const reduction = readFileSync(join(process.cwd(), "docs/REDUCTION.md"), "utf8");
    const syntax = readFileSync(join(process.cwd(), "docs/SYNTAX.md"), "utf8");
    const grammar = readFileSync(join(process.cwd(), "docs/GRAMMAR.md"), "utf8");
    assert.match(reduction, /reduce_buffer/);
    assert.match(syntax, /BIND/);
    assert.match(grammar, /MODE \+ BIND/);
  });
});

describe("conformance vectors", () => {
  it("all session vectors pass", () => {
    const results = runConformance();
    const failures = results.filter((r) => !r.passed);
    assert.deepEqual(failures, []);
    assert.ok(CONFORMANCE_VECTORS.some((v) => v.id === "gdk9-vector-001"));
  });

  it("vector-001 emits CC→33", () => {
    const session = new Session(loadGrammar());
    const result = session.process(["C", "C", ".", "3", "3", "SPACE"]);
    assert.equal(result.emitted, "CC→33");
    assert.equal(result.state, "IDLE");
  });

  it("JSON vector files pass independently", () => {
    const dir = join(process.cwd(), "public/conformance/vectors");
    const files = readdirSync(dir).filter((name) => name.endsWith(".json")).sort();
    assert.ok(files.length >= 15);
    const ids = new Set<string>();
    for (const file of files) {
      const vector = JSON.parse(readFileSync(join(dir, file), "utf8")) as ConformanceVector;
      ids.add(vector.id);
      const result = runVector(vector);
      assert.equal(result.passed, true, `${vector.id} ${JSON.stringify(result.actual)}`);
    }
    for (const vector of CONFORMANCE_VECTORS) {
      assert.ok(ids.has(vector.id), `missing JSON for ${vector.id}`);
    }
  });

  it("v1.1 MODE+BIND pin does not emit", () => {
    const result = runVector({
      id: "pin-mode-bind",
      tokens: ["X", ":", "A", ".", "B"],
      mode_start: null,
      receipt: null,
      final_state: "ERROR",
      emits: false,
    });
    assert.equal(result.passed, true);
    assert.equal(result.actual.receipt, null);
  });
});

describe("grammar freeze", () => {
  it("YAML sha256 matches the frozen constant", () => {
    const yaml = readFileSync(join(process.cwd(), "grammar/gdk9-v1.1.0.yaml"));
    const digest = createHash("sha256").update(yaml).digest("hex");
    assert.equal(digest, GRAMMAR_SHA256);
    const published = readFileSync(join(process.cwd(), "public/grammar/gdk9-v1.1.0.yaml"));
    assert.equal(createHash("sha256").update(published).digest("hex"), GRAMMAR_SHA256);
  });
});

describe("single receipt path", () => {
  it("session emit equals reduceBuffer of the same buffer", () => {
    const session = new Session(loadGrammar(), { autoCommit: false });
    session.process(["C", "C", ".", "3", "3"], false);
    const snap = session.snapshot();
    const fromRho = reduceBuffer(snap.buffer, snap.mode);
    session.process(["SPACE"]);
    assert.equal(session.snapshot().lastOutput, fromRho);
    assert.equal(fromRho, "CC→33");
  });
});
