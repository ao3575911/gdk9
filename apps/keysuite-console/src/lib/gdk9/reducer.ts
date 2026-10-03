import { BIND_ARROW, isBindMarker, symbolText, type BufferedSymbol } from "./symbols.ts";

function joinSymbols(buffer: BufferedSymbol[]): string {
  return buffer.map(symbolText).join("");
}

/**
 * ρ(B, μ) — the only reduction. First-bind split, U+2192, optional mode(core) wrap.
 * Pure function of (buffer, mode). No I/O.
 */
export function reduceBuffer(buffer: BufferedSymbol[], mode: string | null = null): string {
  const bindIndex = buffer.findIndex(isBindMarker);
  const result =
    bindIndex >= 0
      ? joinSymbols(buffer.slice(0, bindIndex)) + BIND_ARROW + joinSymbols(buffer.slice(bindIndex + 1))
      : joinSymbols(buffer);
  return mode ? `${mode}(${result})` : result;
}

export const reduce_buffer = reduceBuffer;
