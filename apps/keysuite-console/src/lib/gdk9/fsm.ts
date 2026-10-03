import type { EventClass } from "./symbols.ts";

export type FsmState = "IDLE" | "COMPOSE" | "MODE" | "ERROR";
export type FsmAction =
  | "append"
  | "mark_bind"
  | "set_mode"
  | "pop"
  | "clear"
  | "reduce_and_emit"
  | "noop";

export type TransitionRule = { next: FsmState; action: FsmAction };
export type TransitionTable = Record<FsmState, Partial<Record<EventClass, TransitionRule>>>;

export const REQUIRED_STATES: FsmState[] = ["IDLE", "COMPOSE", "MODE", "ERROR"];
export const ALLOWED_ACTIONS: readonly FsmAction[] = [
  "append",
  "clear",
  "mark_bind",
  "noop",
  "pop",
  "reduce_and_emit",
  "set_mode",
];

const JURISDICTION: Record<string, (grammar: GrammarLike) => boolean> = {
  CONTENT: (g) => Boolean(g.symbols?.content?.length),
  BIND: (g) => Boolean(g.symbols?.syntax?.bind),
  MODE_SHIFT: (g) => Boolean(g.symbols?.syntax?.mode_shift),
  COMMIT: (g) => Boolean(g.symbols?.commit?.length),
  ROLLBACK: (g) => Boolean(g.symbols?.control?.rollback),
  ABORT: (g) => Boolean(g.symbols?.control?.abort),
};

export type GrammarLike = {
  states?: string[];
  symbols?: {
    content?: string[];
    syntax?: { bind?: string; mode_shift?: string };
    commit?: string[];
    control?: { rollback?: string; abort?: string };
  };
  transitions?: Record<string, Record<string, { next: string; action: string }>>;
};

export function generateTransitionTable(grammar: GrammarLike): TransitionTable {
  const states = new Set(grammar.states ?? []);
  const missing = REQUIRED_STATES.filter((s) => !states.has(s));
  if (missing.length) {
    throw new Error(`GDk9 grammar missing required states: ${missing.sort().join(", ")}`);
  }

  const table = Object.fromEntries(REQUIRED_STATES.map((s) => [s, {}])) as TransitionTable;
  const spec = grammar.transitions;
  if (!spec) return table;

  for (const [state, rules] of Object.entries(spec)) {
    if (!states.has(state)) {
      throw new Error(`GDk9 grammar transition uses unknown state: ${state}`);
    }
    for (const [eventClass, rule] of Object.entries(rules)) {
      const hasJurisdiction = JURISDICTION[eventClass];
      if (!hasJurisdiction?.(grammar)) {
        throw new Error(`Transition ${state}.${eventClass} has no declared symbol jurisdiction`);
      }
      if (!states.has(rule.next)) {
        throw new Error(`Transition ${state}.${eventClass} uses unknown next state: ${rule.next}`);
      }
      if (!ALLOWED_ACTIONS.includes(rule.action as FsmAction)) {
        throw new Error(`Transition ${state}.${eventClass} uses unknown action: ${rule.action}`);
      }
      table[state as FsmState][eventClass as EventClass] = {
        next: rule.next as FsmState,
        action: rule.action as FsmAction,
      };
    }
  }
  return table;
}

/** Transition lookup only. Must never call ρ. */
export function lookupTransition(
  table: TransitionTable,
  state: FsmState,
  eventClass: EventClass,
): TransitionRule | null {
  return table[state]?.[eventClass] ?? null;
}
