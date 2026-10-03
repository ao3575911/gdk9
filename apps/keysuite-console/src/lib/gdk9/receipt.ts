import {
  GRAMMAR_ARTIFACT,
  GRAMMAR_SHA256,
  STANDARD,
  STANDARD_VERSION,
} from "./grammar.ts";

export type ReceiptEnvelope = {
  standard: string;
  standard_version: string;
  grammar: string;
  grammar_sha256: string;
  receipt: string | null;
  commit: boolean;
};

export function receiptEnvelope(receipt: string | null, commit: boolean): ReceiptEnvelope {
  return {
    standard: STANDARD,
    standard_version: STANDARD_VERSION,
    grammar: GRAMMAR_ARTIFACT,
    grammar_sha256: GRAMMAR_SHA256,
    receipt,
    commit,
  };
}
