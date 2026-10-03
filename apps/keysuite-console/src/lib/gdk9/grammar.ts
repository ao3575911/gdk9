import { generateTransitionTable, type TransitionTable } from "./fsm.ts";
import type { SymbolGrammar } from "./symbols.ts";

export const STANDARD = "GDk9";
export const STANDARD_VERSION = "1.1.0";
export const GRAMMAR_ARTIFACT = "gdk9-v1.1.0.yaml";
export const GRAMMAR_SHA256 = "0c8974e76427799dc62ac6839057c8fff41d3ad7ae29c3e6c9d070dd9df1b7a7";

export type Gdk9Grammar = {
  version: string;
  artifact: string;
  standard: string;
  standard_version: string;
  keysuite_runtime_version: string;
  purpose: string;
  symbols: SymbolGrammar;
  states: Array<"IDLE" | "COMPOSE" | "MODE" | "ERROR">;
  event_classes: Record<string, { jurisdiction: string; description: string }>;
  actions: Record<string, string>;
  transitions: Record<string, Record<string, { next: string; action: string }>>;
  unspecified_event: "ERROR";
  conformance: {
    deterministic: boolean;
    emits_only_on_commit: boolean;
    reduction: "pure";
    mutation_scope: string;
  };
};

export const GDK9_GRAMMAR: Gdk9Grammar = {
  version: "1.1.0",
  artifact: GRAMMAR_ARTIFACT,
  standard: STANDARD,
  standard_version: STANDARD_VERSION,
  keysuite_runtime_version: "1.1.0",
  purpose: "Canonical machine-readable control surface for GDk9 v1.1.0 KeySuite runtime behavior.",
  symbols: {
    content: ["a-z", "A-Z", "0-9"],
    syntax: { mode_shift: ":", bind: "." },
    commit: ["SPACE", "ENTER", "TAB", "TIMEOUT", "DONE"],
    control: { rollback: "BACKSPACE", abort: "ESC" },
    escape: { literal: "_", note: "next event is CONTENT" },
  },
  states: ["IDLE", "COMPOSE", "MODE", "ERROR"],
  event_classes: {
    CONTENT: {
      jurisdiction: "symbols.content",
      description: "User-authored literal symbol accepted into the composition buffer.",
    },
    BIND: {
      jurisdiction: "symbols.syntax.bind",
      description: "Declares an implication boundary inside the buffer.",
    },
    MODE_SHIFT: {
      jurisdiction: "symbols.syntax.mode_shift",
      description: "Moves the current buffer into mode context and starts mode-scoped composition.",
    },
    COMMIT: {
      jurisdiction: "symbols.commit",
      description: "Atomically reduces and emits the current buffer when composition exists.",
    },
    ROLLBACK: {
      jurisdiction: "symbols.control.rollback",
      description: "Removes the most recent buffered symbol without emitting output.",
    },
    ABORT: {
      jurisdiction: "symbols.control.abort",
      description: "Clears volatile state and returns to IDLE.",
    },
  },
  actions: {
    append: "Append the event value to the active buffer.",
    mark_bind: "Append the canonical bind marker to the active buffer.",
    set_mode: "Store the active buffer as mode context and clear the active buffer.",
    pop: "Remove the final buffered symbol if one exists.",
    clear: "Reset state, mode, and buffer without output.",
    reduce_and_emit: "Run pure reduction and emit only at the commit boundary.",
    noop: "Preserve state without output.",
  },
  transitions: {
    IDLE: {
      CONTENT: { next: "COMPOSE", action: "append" },
      COMMIT: { next: "IDLE", action: "noop" },
      ABORT: { next: "IDLE", action: "noop" },
    },
    COMPOSE: {
      CONTENT: { next: "COMPOSE", action: "append" },
      BIND: { next: "COMPOSE", action: "mark_bind" },
      MODE_SHIFT: { next: "MODE", action: "set_mode" },
      COMMIT: { next: "IDLE", action: "reduce_and_emit" },
      ROLLBACK: { next: "COMPOSE", action: "pop" },
      ABORT: { next: "IDLE", action: "clear" },
    },
    MODE: {
      CONTENT: { next: "MODE", action: "append" },
      BIND: { next: "ERROR", action: "noop" },
      COMMIT: { next: "IDLE", action: "reduce_and_emit" },
      ROLLBACK: { next: "MODE", action: "pop" },
      ABORT: { next: "IDLE", action: "clear" },
    },
    ERROR: {
      ABORT: { next: "IDLE", action: "clear" },
    },
  },
  unspecified_event: "ERROR",
  conformance: {
    deterministic: true,
    emits_only_on_commit: true,
    reduction: "pure",
    mutation_scope: "volatile_buffer_until_commit",
  },
};

export type LoadedGrammar = Gdk9Grammar & { table: TransitionTable };

export function loadGrammar(grammar: Gdk9Grammar = GDK9_GRAMMAR): LoadedGrammar {
  if (grammar.states.join(",") !== "IDLE,COMPOSE,MODE,ERROR") {
    throw new Error("GDk9 grammar states must be IDLE, COMPOSE, MODE, ERROR");
  }
  if (grammar.unspecified_event !== "ERROR") {
    throw new Error("v1.1.0 unspecified events must map to ERROR");
  }
  const table = generateTransitionTable(grammar);
  return Object.assign(Object.create(null), grammar, { table }) as LoadedGrammar;
}

export const load_grammar = loadGrammar;
