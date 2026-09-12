# GDk9 Security

---

## Threat Model

GDk9 is a local CLI tool and embeddable library. It reads text from stdin/files and writes to stdout. The attack surface is small but worth documenting clearly.

### In Scope
- **Malicious principle/plugin files** — JSON/YAML/Python packs loaded from disk.
- **Malicious state files** — state.json with crafted symbol or rule entries.
- **Crypto misuse** — using the EDPC cipher for real secrets.
- **Path traversal** — `--principle`, `--state`, or plugin paths pointing outside the project.

### Out of Scope
- Network access (GDk9 makes no outbound connections).
- Privilege escalation (runs fully in user space, no setuid).
- Side-channel attacks on energy computation.

---

## Plugin Safety

**Python plugins are parsed via AST `literal_eval`, not `exec` or `eval`.** Only the top-level `PLUGIN = { ... }` literal is extracted. No code in the plugin file is ever executed.

JSON and YAML plugins are pure data — no code execution path exists.

**Recommended practice:**
- Only load plugins from trusted sources.
- Use `gdk9 pl validate <path>` before `gdk9 pl load` to see what rules and symbol energies a pack contains.
- Inspect `gdk9 pl info <path>` to review the full plugin schema before enabling auto-boot.

**Auto-boot security:** `~/.gdk9/plugins.json` records enabled plugins by name and absolute path. If a plugin file is replaced at that path, the new version will be loaded on next CLI start. Treat `~/.gdk9/plugins.json` as a security boundary.

---

## State File Security

The state file (`~/.gdk9/state.json`) stores named symbols and implication rules. It is:
- Written with standard user-permissions (umask applies).
- Not encrypted at rest.
- Subject to CRDT merge — merging a state from an untrusted peer could overwrite local symbols if the incoming timestamp is newer.

**Recommendation:** Do not `gdk9 state merge` state files from untrusted peers without reviewing the incoming file first.

---

## Principle File Security

Principle files are pure JSON/YAML data parsed with the standard library. They cannot execute code. However, a malformed principle with extreme `symbol_energy` values could cause very large total energy numbers. GDk9 does not impose numeric upper bounds — keep principle files from trusted sources.

---

## Crypto Module

GDk9 ships two cipher modes:

### EDPC (default, `--mode edpc`)

The **Energy-Derived Path Cipher** is a **playful, non-cryptographic** cipher designed for GDk9 demonstrations and symbolic experiments. It derives a byte stream from the DCG energy path of the key and XORs the plaintext.

**Do not use EDPC for real secrets.** It provides no semantic security:
- Key stream is deterministic and short-cycling.
- No authenticated encryption — ciphertext integrity is not guaranteed.
- Susceptible to known-plaintext and ciphertext-only attacks.

### Secure (`--mode secure`)

Uses **Fernet** (`cryptography.fernet.Fernet`) via the optional `cryptography` package — not AES-256-GCM directly. Fernet provides authenticated encryption (AES-128-CBC + HMAC-SHA256 under the hood) with a timestamped token.

**Payload format** (then outer urlsafe-base64):
- Magic prefix: `G9F` (3 bytes)
- Salt: 16 random bytes
- Fernet token: output of `Fernet.encrypt(...)`

**Key derivation:** PBKDF2-HMAC-SHA256 over the passphrase with the per-message salt, **200_000** iterations, `dklen=32`, then urlsafe-base64-encoded to form the Fernet key. See `gdk9/crypto.py`.

```bash
pip install "gdk9-cli[secure]"
# or: pip install cryptography
gdk9 crypto encrypt "secret message" -k "my-passphrase" --mode secure
```

**Note:** GDk9 crypto is experimental. For high-stakes encryption, use a dedicated tool (age, GPG, libsodium).

---

## Secret Handling

- **Never commit secrets** to the repository. The `.gitignore` excludes `.env`, `secret_key`, `*.sqlite3`, and `__pycache__`.
- The `config/secret_key` file (removed in v0.2.0) must be rotated if it was ever committed.
- State files may contain symbol names that carry semantic meaning — treat `~/.gdk9/state.json` as potentially sensitive in shared environments.

---

## Reporting Vulnerabilities

Open an issue on the project repository with the label `security`. For sensitive reports, contact the maintainer directly at `adamgrange@proton.me` using PGP if available.

Please include:
- GDk9 version (`gdk9 --version`)
- Steps to reproduce
- Impact assessment
