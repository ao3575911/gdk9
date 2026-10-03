import { loadGrammar } from "./grammar.ts";
import { Session } from "./session.ts";
import { CONFORMANCE_VECTORS, type ConformanceVector } from "./vectors.ts";

export type VectorResult = {
  id: string;
  passed: boolean;
  expected: { receipt: string | null; state: string; emits: boolean };
  actual: { receipt: string | null; state: string; emits: boolean };
  notes?: string;
};

export function runVector(vector: ConformanceVector): VectorResult {
  const session = new Session(loadGrammar(), {
    autoCommit: true,
    modeStart: vector.mode_start,
  });
  const result = session.process(vector.tokens);
  const emitted = result.receipts.length > 0;
  const receipt = emitted ? result.receipts[result.receipts.length - 1]! : null;
  const passed =
    result.state === vector.final_state &&
    emitted === vector.emits &&
    (vector.emits ? receipt === vector.receipt : true);
  return {
    id: vector.id,
    passed,
    expected: { receipt: vector.receipt, state: vector.final_state, emits: vector.emits },
    actual: { receipt, state: result.state, emits: emitted },
    notes: vector.notes,
  };
}

export function runConformance(vectors: ConformanceVector[] = CONFORMANCE_VECTORS): VectorResult[] {
  return vectors.map(runVector);
}
