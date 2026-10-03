from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .ansi import colorize
from .energy import string_energy, char_energy
from .principles import Principle


def delimiter_set(principle: Principle, energy: int = 1, extra: str | None = None) -> str:
  """Return a string of delimiter characters whose symbol energy equals `energy`.

  - Includes any characters in `extra`.
  - Sorted for stable UI.
  """
  ds = {s for s, v in principle.symbol_energy.items() if int(v) == int(energy)}
  if extra:
    for ch in extra:
      ds.add(ch)
  return "".join(sorted(ds))


@dataclass
class Token:
  kind: str  # 'token' or 'delim'
  text: str
  total: int
  dr: int
  letters: int = 0
  digits: int = 0
  symbols: int = 0
  e_letters: int = 0
  e_digits: int = 0
  e_symbols: int = 0
  dominant: str = "mixed"  # one of: letters, digits, symbols, mixed
  r_letters: float = 0.0
  r_digits: float = 0.0
  r_symbols: float = 0.0


def _compile_pattern(delims: str) -> re.Pattern[str]:
  if not delims:
    # No explicit delimiters -> treat whole text as one token
    return re.compile(r".+", flags=re.DOTALL)
  cls = re.escape(delims)
  # Keep groups of non-delims or groups of delimiters as separate tokens
  return re.compile(rf"[^{cls}]+|[{cls}]+")


def tokenize(
  text: str,
  principle: Principle,
  *,
  energy: int = 1,
  delims: str | None = None,
  keep_delims: bool = True,
  strip_tokens: bool = True,
) -> List[str]:
  """Split `text` using delimiters derived from principle's symbol energy.

  - If `delims` is provided, it overrides derived delimiters.
  - If `keep_delims` is True, delimiter runs are emitted as standalone tokens.
  - If `strip_tokens` is True, non-delim tokens are stripped and empties dropped.
  """
  ds = delims if delims is not None else delimiter_set(principle, energy=energy)
  pat = _compile_pattern(ds)
  raw = pat.findall(text)
  out: List[str] = []
  for piece in raw:
    is_delim = all(ch in ds for ch in piece)
    if is_delim and not keep_delims:
      continue
    if not is_delim and strip_tokens:
      piece = piece.strip()
      if not piece:
        continue
    out.append(piece)
  return out


def _classify(piece: str, principle: Principle) -> Tuple[int, int, int, int, int, int]:
  l = d = s = 0
  el = ed = es = 0
  for ch in piece:
    if ch.isspace():
      continue
    if ch.isalpha():
      l += 1
      el += char_energy(ch, principle)
    elif ch.isdigit():
      d += 1
      ed += char_energy(ch, principle)
    else:
      s += 1
      es += char_energy(ch, principle)
  return l, d, s, el, ed, es


def tokens_with_energy(
  text: str,
  principle: Principle,
  *,
  energy: int = 1,
  delims: str | None = None,
  keep_delims: bool = True,
  strip_tokens: bool = True,
) -> List[Token]:
  """Tokenize and annotate each token with (total, dr)."""
  ds = delims if delims is not None else delimiter_set(principle, energy=energy)
  pat = _compile_pattern(ds)
  toks: List[Token] = []
  for piece in pat.findall(text):
    is_delim = all(ch in ds for ch in piece)
    if is_delim and not keep_delims:
      continue
    if not is_delim and strip_tokens:
      piece = piece.strip()
      if not piece:
        continue
    total, dr = string_energy(piece, principle)
    letters, digits, symbols, e_letters, e_digits, e_symbols = _classify(piece, principle)
    # Dominant class by energy, then by count
    energy_triple = [(e_letters, 'letters'), (e_digits, 'digits'), (e_symbols, 'symbols')]
    max_e = max(e for e, _ in energy_triple)
    winners = [name for e, name in energy_triple if e == max_e]
    if len(winners) == 1 and max_e > 0:
      dominant = winners[0]
    else:
      count_triple = [(letters, 'letters'), (digits, 'digits'), (symbols, 'symbols')]
      max_c = max(c for c, _ in count_triple)
      winners_c = [name for c, name in count_triple if c == max_c and c > 0]
      dominant = winners_c[0] if len(winners_c) == 1 else 'mixed'
    # Ratios by count
    denom = max(1, letters + digits + symbols)
    r_letters = letters / denom
    r_digits = digits / denom
    r_symbols = symbols / denom
    toks.append(Token(
      "delim" if is_delim else "token",
      piece,
      total,
      dr,
      letters=letters,
      digits=digits,
      symbols=symbols,
      e_letters=e_letters,
      e_digits=e_digits,
      e_symbols=e_symbols,
      dominant=dominant,
      r_letters=r_letters,
      r_digits=r_digits,
      r_symbols=r_symbols,
    ))
  return toks


def render_table(rows: List[List[str]], use_color: bool = False) -> str:
  """Render a simple table string without printing (for UX-friendly CLI)."""
  widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
  out_lines: List[str] = []
  header = rows[0]
  out_lines.append("  ".join(val.ljust(widths[i]) for i, val in enumerate(header)))
  for r in rows[1:]:
    out_lines.append("  ".join(r[i].ljust(widths[i]) for i in range(len(widths))))
  return "\n".join(out_lines)


def summarize_tokens_table(
  text: str,
  principle: Principle,
  *,
  energy: int = 1,
  delims: str | None = None,
  keep_delims: bool = True,
  strip_tokens: bool = True,
  use_color: bool = False,
) -> List[List[str]]:
  toks = tokens_with_energy(
    text,
    principle,
    energy=energy,
    delims=delims,
    keep_delims=keep_delims,
    strip_tokens=strip_tokens,
  )
  rows: List[List[str]] = [["#", "kind", "token", "total", "dr"]]
  for i, t in enumerate(toks):
    drs = str(t.dr)
    # Gentle color cue on dr for UX readability
    color_map = {"1": "blue", "2": "blue", "3": "cyan", "4": "green", "5": "yellow", "6": "magenta", "7": "red", "8": "red", "9": "bold"}
    rows.append([
      str(i),
      t.kind,
      t.text if len(t.text) <= 40 else (t.text[:37] + "…"),
      str(t.total),
      colorize(drs, color_map.get(drs, None), use_color),
    ])
  return rows


def annotate_text(
  text: str,
  principle: Principle,
  *,
  energy: int = 1,
  delims: str | None = None,
  keep_delims: bool = True,
  strip_tokens: bool = True,
  gap: str = " ",
) -> str:
  """Return a human-friendly annotated string: tokens separated for visibility.

  Delimiters are preserved inline; tokens are joined by `gap`.
  """
  toks = tokens_with_energy(
    text,
    principle,
    energy=energy,
    delims=delims,
    keep_delims=keep_delims,
    strip_tokens=strip_tokens,
  )
  return gap.join(t.text for t in toks)


def to_json_payload(
  text: str,
  principle: Principle,
  *,
  energy: int = 1,
  delims: str | None = None,
  keep_delims: bool = True,
  strip_tokens: bool = True,
) -> str:
  toks = tokens_with_energy(
    text,
    principle,
    energy=energy,
    delims=delims,
    keep_delims=keep_delims,
    strip_tokens=strip_tokens,
  )
  metrics = compute_metrics(text, toks, principle, delims if delims is not None else delimiter_set(principle, energy=energy))
  return json.dumps(
    {
      "delims": delims if delims is not None else delimiter_set(principle, energy=energy),
      "tokens": [t.__dict__ for t in toks],
      "metrics": metrics,
    },
    ensure_ascii=False,
    indent=2,
  )


def compute_metrics(text: str, toks: List[Token], principle: Principle, dset: str) -> Dict[str, object]:
  """Compute rich token/energy metrics for UX and downstream analysis."""
  # Partition
  content = [t for t in toks if t.kind == 'token']
  delim = [t for t in toks if t.kind == 'delim']
  # Counts
  counts = {
    "total_tokens": len(toks),
    "content_tokens": len(content),
    "delimiter_tokens": len(delim),
  }
  # Energies (sum of totals) and document-level
  from .energy import string_energy
  doc_total, doc_dr = string_energy(text, principle)
  sums = {
    "content_total": int(sum(t.total for t in content)),
    "delimiter_total": int(sum(t.total for t in delim)),
    "document_total": int(doc_total),
    "document_dr": int(doc_dr),
  }
  # DR histogram for content and delimiter tokens
  def hist(items: List[Token]) -> Dict[str, int]:
    h: Dict[str, int] = {str(i): 0 for i in range(1, 10)}
    for t in items:
      k = str(9 if t.dr == 0 else t.dr)
      h[k] += 1
    return h
  histograms = {
    "content_dr": hist(content),
    "delimiter_dr": hist(delim),
  }
  # Length stats for content tokens
  lengths = [len(t.text) for t in content]
  if lengths:
    avg_len = sum(lengths) / len(lengths)
    min_len = min(lengths)
    max_len = max(lengths)
  else:
    avg_len = 0.0
    min_len = 0
    max_len = 0
  length_stats = {"avg": avg_len, "min": min_len, "max": max_len}
  # Top tokens by energy (content only)
  top_content = sorted(content, key=lambda t: (t.total, t.dr, len(t.text)), reverse=True)[:5]
  top_tokens = [{"text": t.text, "total": t.total, "dr": t.dr} for t in top_content]
  # Delimiter character counts
  delim_counts: Dict[str, int] = {}
  for t in delim:
    for ch in t.text:
      delim_counts[ch] = delim_counts.get(ch, 0) + 1
  top_delims = sorted(delim_counts.items(), key=lambda kv: kv[1], reverse=True)[:8]
  # Class aggregates (content and delimiters)
  def class_aggr(items: List[Token]) -> Dict[str, int]:
    return {
      "letters": int(sum(t.letters for t in items)),
      "digits": int(sum(t.digits for t in items)),
      "symbols": int(sum(t.symbols for t in items)),
    }
  def class_energy_aggr(items: List[Token]) -> Dict[str, int]:
    return {
      "letters": int(sum(t.e_letters for t in items)),
      "digits": int(sum(t.e_digits for t in items)),
      "symbols": int(sum(t.e_symbols for t in items)),
    }
  classes = {
    "content": {
      "counts": class_aggr(content),
      "energy": class_energy_aggr(content),
    },
    "delimiters": {
      "counts": class_aggr(delim),
      "energy": class_energy_aggr(delim),
    }
  }
  return {
    "counts": counts,
    "sums": sums,
    "histograms": histograms,
    "lengths": length_stats,
    "top_tokens": top_tokens,
    "delimiters": {
      "set": dset,
      "char_counts": dict(top_delims),
    },
    "classes": classes,
  }


def summarize_metrics_lines(text: str, toks: List[Token], principle: Principle, dset: str, use_color: bool = False) -> List[str]:
  """Return human-readable summary lines for CLI footer."""
  metrics = compute_metrics(text, toks, principle, dset)
  out: List[str] = []
  # Counts
  c = metrics["counts"]  # type: ignore[index]
  out.append(f"tokens={c['total_tokens']} content={c['content_tokens']} delims={c['delimiter_tokens']}")
  # Sums
  s = metrics["sums"]  # type: ignore[index]
  out.append(f"content_total={s['content_total']} delim_total={s['delimiter_total']} doc_total={s['document_total']} doc_dr={s['document_dr']}")
  # DR histogram (content)
  h = metrics["histograms"]["content_dr"]  # type: ignore[index]
  hist_line = "dr_hist=" + ", ".join(f"{k}:{h[str(k)]}" for k in range(1, 10))
  out.append(hist_line)
  # Top tokens (content)
  tops = metrics["top_tokens"]  # type: ignore[index]
  if tops:
    parts = [f"{t['text']}[{t['total']}/{t['dr']}]" for t in tops]
    out.append("top_tokens=" + "; ".join(parts))
  # Class energy breakdown (content)
  cl = metrics["classes"]["content"]["energy"]  # type: ignore[index]
  out.append(f"class_energy letters={cl['letters']} digits={cl['digits']} symbols={cl['symbols']}")
  # Class ratio (content by counts)
  cc = metrics["classes"]["content"]["counts"]  # type: ignore[index]
  denom = max(1, cc['letters'] + cc['digits'] + cc['symbols'])
  out.append(
    "class_ratio "
    f"letters={cc['letters']/denom:.2f} digits={cc['digits']/denom:.2f} symbols={cc['symbols']/denom:.2f}"
  )
  # Delimiter set
  out.append(f"delims={repr(dset)}")
  return out
