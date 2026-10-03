import { useEffect, useRef } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GRAMMAR_ARTIFACT, GRAMMAR_SHA256, STANDARD, STANDARD_VERSION } from "@/lib/gdk9/grammar.ts";
import { useKeySuite } from "@/lib/gdk9/store.ts";

const EXAMPLES: Array<{ label: string; tokens: string[] }> = [
  { label: "CC.33", tokens: ["C", "C", ".", "3", "3", "SPACE"] },
  { label: "X:AB", tokens: ["X", ":", "A", "B", "SPACE"] },
  { label: "A.B.C", tokens: ["A", ".", "B", ".", "C", "SPACE"] },
  { label: "A_.B", tokens: ["A", "_", ".", "B", "SPACE"] },
  { label: "@", tokens: ["@"] },
];

export function KeySuiteConsole() {
  const { snapshot, lastReceipt, feed, bind, mode, commit, rollback, abort, reset } = useKeySuite();
  const inputRef = useRef<HTMLInputElement>(null);
  const displayValue = snapshot.escaped ? `${snapshot.bufferText}_` : snapshot.bufferText;
  const isError = snapshot.state === "ERROR";
  const receipt = lastReceipt?.commit ? lastReceipt.receipt : null;

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    const el = inputRef.current;
    if (!el || document.activeElement !== el) return;
    const end = el.value.length;
    el.setSelectionRange(end, end);
  }, [displayValue]);

  const onKey = (event: { key: string; metaKey: boolean; ctrlKey: boolean; altKey: boolean; preventDefault: () => void }) => {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      commit();
      return;
    }
    if (event.key === "Backspace") {
      event.preventDefault();
      rollback();
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      abort();
      queueMicrotask(() => inputRef.current?.focus());
      return;
    }
    if (event.key.length === 1) {
      event.preventDefault();
      feed(event.key);
    }
  };

  const runTokens = (tokens: string[]) => {
    reset();
    for (const token of tokens) feed(token);
    inputRef.current?.focus();
  };

  return (
    <div className="min-h-dvh bg-bg text-fg">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-8">
        <header>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-subtle">
            {STANDARD} {STANDARD_VERSION} · local runtime
          </p>
          <h1 className="font-display text-4xl font-medium italic tracking-[-0.03em]">KeySuite</h1>
          <p className="mt-1 text-sm text-muted">Deterministic implication. Receipt only at commit.</p>
          <p className="mt-2 font-mono text-xs text-subtle">
            {GRAMMAR_ARTIFACT} · {GRAMMAR_SHA256.slice(0, 8)}…{GRAMMAR_SHA256.slice(-6)}
          </p>
        </header>

        <div className="flex flex-wrap items-center gap-2">
          {(["IDLE", "COMPOSE", "MODE", "ERROR"] as const).map((name) => (
            <Badge key={name} variant={snapshot.state === name ? (name.toLowerCase() as "idle") : "default"}>
              {name}
            </Badge>
          ))}
        </div>

        <section className="rounded-2xl border border-border bg-surface p-6">
          <p className="text-xs font-medium uppercase tracking-[0.16em] text-subtle">Receipt</p>
          <p className="mt-4 break-all font-mono text-4xl font-medium tracking-tight" aria-live="polite">
            {isError ? "ERROR" : receipt && receipt.length ? receipt : "—"}
          </p>
          <p className="mt-2 text-sm text-muted">Type CC.33 then Commit.</p>

          <label htmlFor="keysuite-content" className="mt-6 block text-xs font-medium uppercase tracking-[0.16em] text-subtle">
            Content
          </label>
          <Input
            id="keysuite-content"
            ref={inputRef}
            aria-label="Content"
            value={displayValue}
            placeholder="Type CC.33"
            autoComplete="off"
            spellCheck={false}
            disabled={isError}
            className="mt-2 font-mono"
            onChange={() => undefined}
            onKeyDown={onKey}
            onPaste={(event) => {
              event.preventDefault();
              const text = event.clipboardData.getData("text");
              for (const ch of text) {
                if (ch === " " || ch === "\n" || ch === "\t") commit();
                else feed(ch);
              }
            }}
          />

          <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-5">
            <Button type="button" variant="secondary" className="w-full" onClick={bind} disabled={isError}>
              Bind
            </Button>
            <Button type="button" variant="secondary" className="w-full" onClick={mode} disabled={isError}>
              Mode
            </Button>
            <Button type="button" variant="commit" className="w-full" onClick={commit} disabled={isError}>
              Commit
            </Button>
            <Button type="button" variant="secondary" className="w-full" onClick={rollback} disabled={isError}>
              Rollback
            </Button>
            <Button type="button" variant="abort" className="w-full" onClick={() => { abort(); queueMicrotask(() => inputRef.current?.focus()); }}>
              Abort
            </Button>
          </div>
        </section>

        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((example) => (
            <Button key={example.label} type="button" variant="secondary" size="sm" className="font-mono" onClick={() => runTokens(example.tokens)}>
              {example.label}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
