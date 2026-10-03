export const BIND_ARROW = "\u2192";
export const BIND_GLYPH = ".";
export const MODE_SHIFT_GLYPH = ":";
export const ESCAPE_GLYPH = "_";

export type LiteralSymbol = { readonly kind: "literal"; readonly value: string };
export type BindMarker = { readonly kind: "bind"; readonly value: typeof BIND_GLYPH };
export type BufferedSymbol = string | LiteralSymbol | BindMarker;

export type EventClass =
  | "CONTENT"
  | "BIND"
  | "MODE_SHIFT"
  | "COMMIT"
  | "ROLLBACK"
  | "ABORT"
  | "INVALID";

export type RuntimeEvent = {
  class: EventClass;
  value: BufferedSymbol;
  token: string;
};

export function literalSymbol(value: string): LiteralSymbol {
  return { kind: "literal", value };
}

export function isLiteralSymbol(symbol: BufferedSymbol): symbol is LiteralSymbol {
  return typeof symbol === "object" && symbol.kind === "literal";
}

export function symbolText(symbol: BufferedSymbol): string {
  if (typeof symbol === "string") return symbol;
  return symbol.value;
}

export function isBindMarker(symbol: BufferedSymbol): boolean {
  if (typeof symbol === "object") return symbol.kind === "bind";
  return symbol === BIND_GLYPH;
}

function inRange(token: string, rangeSpec: string): boolean {
  return (
    token.length === 1 &&
    rangeSpec.length === 3 &&
    rangeSpec[1] === "-" &&
    rangeSpec.charCodeAt(0) <= token.charCodeAt(0) &&
    token.charCodeAt(0) <= rangeSpec.charCodeAt(2)
  );
}

export type SymbolGrammar = {
  content: string[];
  syntax: { bind: string; mode_shift: string };
  commit: string[];
  control: { rollback: string; abort: string };
  escape: { literal: string; note?: string };
};

export function classifyToken(
  token: string,
  symbols: SymbolGrammar,
  literal = false,
): RuntimeEvent {
  if (literal) {
    return { class: "CONTENT", value: literalSymbol(token), token };
  }

  const exact: Record<string, EventClass> = {
    [symbols.syntax.bind]: "BIND",
    [symbols.syntax.mode_shift]: "MODE_SHIFT",
    [symbols.control.rollback]: "ROLLBACK",
    [symbols.control.abort]: "ABORT",
  };
  for (const commit of symbols.commit) exact[commit] = "COMMIT";

  const eventClass = exact[token];
  if (eventClass) {
    return { class: eventClass, value: token, token };
  }
  if (symbols.content.some((spec) => inRange(token, spec))) {
    return { class: "CONTENT", value: token, token };
  }
  return { class: "INVALID", value: token, token };
}
