import { create } from "zustand";
import { loadGrammar } from "./grammar.ts";
import { receiptEnvelope, type ReceiptEnvelope } from "./receipt.ts";
import { Session, type SessionSnapshot } from "./session.ts";

export type TapeEntry = {
  token: string;
  class: string;
  action: string;
  output: string | null;
};

export type KeySuiteState = {
  snapshot: SessionSnapshot;
  lastReceipt: ReceiptEnvelope | null;
  tape: TapeEntry[];
  focused: boolean;
  feed: (token: string) => void;
  feedChars: (text: string) => void;
  bind: () => void;
  mode: () => void;
  commit: () => void;
  rollback: () => void;
  abort: () => void;
  reset: () => void;
  setFocused: (focused: boolean) => void;
};

function freshSession() {
  return new Session(loadGrammar(), { autoCommit: false });
}

let session = freshSession();

export const useKeySuite = create<KeySuiteState>((set, get) => ({
  snapshot: session.snapshot(),
  lastReceipt: null,
  tape: [],
  focused: true,
  setFocused: (focused) => set({ focused }),
  feed: (token) => {
    const entry = session.processToken(token);
    const snapshot = session.snapshot();
    const tape = [
      ...get().tape,
      {
        token: entry.token,
        class: entry.event_class,
        action: entry.action,
        output: entry.output,
      },
    ].slice(-24);
    set({
      snapshot,
      tape,
      lastReceipt:
        entry.output != null
          ? receiptEnvelope(entry.output, true)
          : snapshot.state === "ERROR"
            ? receiptEnvelope(null, false)
            : get().lastReceipt,
    });
  },
  feedChars: (text) => {
    for (const ch of text) {
      if (ch === " " || ch === "\n" || ch === "\t") get().commit();
      else get().feed(ch);
    }
  },
  bind: () => get().feed("."),
  mode: () => get().feed(":"),
  commit: () => get().feed("SPACE"),
  rollback: () => get().feed("BACKSPACE"),
  abort: () => {
    session = freshSession();
    set({ snapshot: session.snapshot(), lastReceipt: null, tape: [] });
  },
  reset: () => {
    session = freshSession();
    set({ snapshot: session.snapshot(), lastReceipt: null, tape: [] });
  },
}));
