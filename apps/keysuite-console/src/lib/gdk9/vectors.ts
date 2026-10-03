export type ConformanceVector = {
  id: string;
  tokens: string[];
  mode_start: string | null;
  receipt: string | null;
  final_state: "IDLE" | "COMPOSE" | "MODE" | "ERROR";
  emits: boolean;
  notes?: string;
};

export const CONFORMANCE_VECTORS: ConformanceVector[] = [
  {
    id: "gdk9-vector-001",
    tokens: ["C", "C", ".", "3", "3", "SPACE"],
    mode_start: null,
    receipt: "CC→33",
    final_state: "IDLE",
    emits: true,
    notes: "basic implication",
  },
  {
    id: "gdk9-vector-002",
    tokens: ["A", "B", "SPACE"],
    mode_start: null,
    receipt: "AB",
    final_state: "IDLE",
    emits: true,
    notes: "plain composition",
  },
  {
    id: "gdk9-vector-003",
    tokens: ["A", "B", "BACKSPACE", "SPACE"],
    mode_start: null,
    receipt: "A",
    final_state: "IDLE",
    emits: true,
    notes: "rollback before commit",
  },
  {
    id: "gdk9-vector-004",
    tokens: ["A", "ESC"],
    mode_start: null,
    receipt: null,
    final_state: "IDLE",
    emits: false,
    notes: "abort clears volatile state",
  },
  {
    id: "gdk9-vector-005",
    tokens: ["X", ":", "A", "B", "SPACE"],
    mode_start: null,
    receipt: "X(AB)",
    final_state: "IDLE",
    emits: true,
    notes: "mode-scoped reduction",
  },
  {
    id: "gdk9-vector-006",
    tokens: ["A", ".", "B", ".", "C", "SPACE"],
    mode_start: null,
    receipt: "A→B.C",
    final_state: "IDLE",
    emits: true,
    notes: "first bind marker is the implication boundary",
  },
  {
    id: "gdk9-vector-007",
    tokens: ["A", "_", ".", "B", "SPACE"],
    mode_start: null,
    receipt: "A.B",
    final_state: "IDLE",
    emits: true,
    notes: "escaped bind marker is literal content",
  },
  {
    id: "gdk9-vector-008",
    tokens: ["A", "B", "DONE"],
    mode_start: null,
    receipt: "AB",
    final_state: "IDLE",
    emits: true,
    notes: "DONE is an explicit commit token",
  },
  {
    id: "gdk9-vector-009",
    tokens: ["A", ".", "B", "DONE"],
    mode_start: null,
    receipt: "A→B",
    final_state: "IDLE",
    emits: true,
    notes: "DONE commits implication output",
  },
  {
    id: "gdk9-vector-010",
    tokens: ["X", ":", "A", "B", "DONE"],
    mode_start: null,
    receipt: "X(AB)",
    final_state: "IDLE",
    emits: true,
    notes: "DONE commits mode-scoped output",
  },
  {
    id: "gdk9-vector-011",
    tokens: ["@"],
    mode_start: null,
    receipt: null,
    final_state: "ERROR",
    emits: false,
    notes: "undeclared @ → ERROR",
  },
  {
    id: "gdk9-vector-013",
    tokens: ["A", ".", "SPACE"],
    mode_start: null,
    receipt: "A→",
    final_state: "IDLE",
    emits: true,
    notes: "empty right side",
  },
  {
    id: "gdk9-vector-014",
    tokens: ["X", ":", "A", ".", "B"],
    mode_start: null,
    receipt: null,
    final_state: "ERROR",
    emits: false,
    notes: "v1.1 pin: MODE + BIND → ERROR",
  },
  {
    id: "gdk9-vector-015",
    tokens: ["SPACE"],
    mode_start: null,
    receipt: null,
    final_state: "IDLE",
    emits: false,
    notes: "IDLE commit: no emit",
  },
  {
    id: "gdk9-vector-016",
    tokens: ["A", "_", ".", "B"],
    mode_start: null,
    receipt: "A.B",
    final_state: "IDLE",
    emits: true,
    notes: "escape then commit (auto-commit at finalize)",
  },
  {
    id: "gdk9-vector-012-session",
    tokens: ["A", "BACKSPACE", ".", "B", "SPACE"],
    mode_start: null,
    receipt: "→B",
    final_state: "IDLE",
    emits: true,
    notes: "empty left via COMPOSE; IDLE+BIND is unspecified → ERROR",
  },
];

export type ReducerExample = {
  buffer: string[];
  mode: string | null;
  receipt: string;
  literals?: number[];
};
