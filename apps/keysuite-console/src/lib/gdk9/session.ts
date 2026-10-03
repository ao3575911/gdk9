import { loadGrammar, type LoadedGrammar } from "./grammar.ts";
import { lookupTransition, type FsmAction, type FsmState } from "./fsm.ts";
import { reduceBuffer } from "./reducer.ts";
import {
  BIND_GLYPH,
  classifyToken,
  ESCAPE_GLYPH,
  isLiteralSymbol,
  symbolText,
  type BufferedSymbol,
  type EventClass,
  type RuntimeEvent,
} from "./symbols.ts";

export type SessionError = {
  token: string;
  event_class: string;
  message: string;
  type: string;
};

export type TraceEntry = {
  type: "transition" | "escape" | "error";
  token: string;
  from_state: FsmState;
  event_class: string;
  to_state: FsmState;
  action: string;
  output: string | null;
  literal: boolean;
};

export type SessionSnapshot = {
  state: FsmState;
  buffer: BufferedSymbol[];
  bufferText: string;
  mode: string | null;
  escaped: boolean;
  error: SessionError | null;
  outputs: string[];
  lastOutput: string | null;
};

export type ProcessResult = {
  receipts: string[];
  state: FsmState;
  snapshot: SessionSnapshot;
  emitted: string | null;
  error: SessionError | null;
};

function stringifyBuffer(buffer: BufferedSymbol[]): string {
  return buffer.map(symbolText).join("");
}

export type SessionOptions = {
  autoCommit?: boolean;
  modeStart?: string | null;
};

/**
 * Session is the only module that consults the FSM and calls ρ.
 * fsm.ts must not import reducer.ts.
 */
export class Session {
  private grammar: LoadedGrammar;
  private state: FsmState = "IDLE";
  private buffer: BufferedSymbol[] = [];
  private mode: string | null = null;
  private escaped = false;
  private error: SessionError | null = null;
  private outputs: string[] = [];
  private trace: TraceEntry[] = [];
  autoCommit: boolean;

  constructor(grammar: LoadedGrammar = loadGrammar(), options?: SessionOptions) {
    this.grammar = grammar;
    this.autoCommit = options?.autoCommit ?? true;
    if (options?.modeStart) {
      this.mode = options.modeStart;
      this.state = "MODE";
    }
  }

  reset(): void {
    this.state = "IDLE";
    this.buffer = [];
    this.mode = null;
    this.escaped = false;
    this.error = null;
    this.outputs = [];
    this.trace = [];
  }

  snapshot(): SessionSnapshot {
    return {
      state: this.state,
      buffer: [...this.buffer],
      bufferText: stringifyBuffer(this.buffer),
      mode: this.mode,
      escaped: this.escaped,
      error: this.error,
      outputs: [...this.outputs],
      lastOutput: this.outputs.length ? this.outputs[this.outputs.length - 1]! : null,
    };
  }

  getTrace(): TraceEntry[] {
    return [...this.trace];
  }

  process(tokens: string[], finalize = true): ProcessResult {
    const before = this.outputs.length;
    for (const token of tokens) this.processToken(token);
    if (finalize) this.finalize();
    const receipts = this.outputs.slice(before);
    return {
      receipts,
      state: this.state,
      snapshot: this.snapshot(),
      emitted: receipts.length ? receipts[receipts.length - 1]! : null,
      error: this.error,
    };
  }

  processToken(token: string): TraceEntry {
    if (this.escaped) {
      const entry = this.applyEvent(classifyToken(token, this.grammar.symbols, true), true);
      this.escaped = false;
      return entry;
    }

    if (token === (this.grammar.symbols.escape.literal ?? ESCAPE_GLYPH)) {
      const entry: TraceEntry = {
        type: "escape",
        token,
        from_state: this.state,
        event_class: "ESCAPE",
        to_state: this.state,
        action: "escape_next",
        output: null,
        literal: false,
      };
      this.trace.push(entry);
      this.escaped = true;
      return entry;
    }

    return this.applyEvent(classifyToken(token, this.grammar.symbols, false), false);
  }

  finalize(): void {
    if (this.error === null && this.escaped) {
      this.state = "ERROR";
      this.error = {
        token: this.grammar.symbols.escape.literal ?? ESCAPE_GLYPH,
        event_class: "ESCAPE",
        message: "Escape marker must be followed by a literal token",
        type: "TokenValidationError",
      };
      this.escaped = false;
      this.trace.push({
        type: "error",
        token: this.error.token,
        from_state: "ERROR",
        event_class: "ESCAPE",
        to_state: "ERROR",
        action: "error",
        output: null,
        literal: false,
      });
      return;
    }

    if (this.autoCommit && this.error === null && (this.state === "COMPOSE" || this.state === "MODE")) {
      this.applyEvent(classifyToken("SPACE", this.grammar.symbols, false), false);
    }
  }

  private applyEvent(event: RuntimeEvent, literal: boolean): TraceEntry {
    const from = this.state;

    if (event.class === "INVALID") {
      this.state = "ERROR";
      this.error = {
        token: event.token,
        event_class: "INVALID",
        message: "Token has no GDk9 jurisdiction or no valid transition",
        type: "TokenValidationError",
      };
      const entry: TraceEntry = {
        type: "error",
        token: event.token,
        from_state: from,
        event_class: "INVALID",
        to_state: "ERROR",
        action: "error",
        output: null,
        literal,
      };
      this.trace.push(entry);
      return entry;
    }

    const rule = lookupTransition(this.grammar.table, this.state, event.class);
    if (!rule) {
      this.state = "ERROR";
      this.error = {
        token: event.token,
        event_class: event.class,
        message: "Token has no GDk9 jurisdiction or no valid transition",
        type: "TokenValidationError",
      };
      const entry: TraceEntry = {
        type: "error",
        token: event.token,
        from_state: from,
        event_class: event.class,
        to_state: "ERROR",
        action: "error",
        output: null,
        literal,
      };
      this.trace.push(entry);
      return entry;
    }

    const output = this.applyAction(rule.action, event);
    this.state = rule.next;
    if (this.state === "ERROR") {
      this.error = {
        token: event.token,
        event_class: event.class,
        message: "Token has no GDk9 jurisdiction or no valid transition",
        type: "TokenValidationError",
      };
    } else {
      this.error = null;
    }

    const entry: TraceEntry = {
      type: "transition",
      token: event.token,
      from_state: from,
      event_class: event.class,
      to_state: this.state,
      action: rule.action,
      output,
      literal,
    };
    this.trace.push(entry);
    return entry;
  }

  private applyAction(action: FsmAction, event: RuntimeEvent): string | null {
    switch (action) {
      case "append":
        this.buffer.push(event.value);
        return null;
      case "mark_bind":
        this.buffer.push(BIND_GLYPH);
        return null;
      case "set_mode":
        this.mode = this.buffer.length ? stringifyBuffer(this.buffer) : null;
        this.buffer = [];
        return null;
      case "pop":
        if (this.buffer.length) this.buffer.pop();
        return null;
      case "clear":
        this.buffer = [];
        this.mode = null;
        this.escaped = false;
        this.error = null;
        return null;
      case "reduce_and_emit": {
        const receipt = reduceBuffer(this.buffer, this.mode);
        this.outputs.push(receipt);
        this.buffer = [];
        this.mode = null;
        this.escaped = false;
        this.error = null;
        return receipt;
      }
      case "noop":
        return null;
      default:
        return null;
    }
  }
}

export const Runtime = Session;

export function bufferDisplay(buffer: BufferedSymbol[]): Array<{ text: string; bind: boolean; literal: boolean }> {
  return buffer.map((symbol) => ({
    text: symbolText(symbol),
    bind: typeof symbol === "string" && symbol === BIND_GLYPH,
    literal: isLiteralSymbol(symbol),
  }));
}

export type { EventClass };
