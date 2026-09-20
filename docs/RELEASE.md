# Releasing gdk9-cli

Version stays in `pyproject.toml` (`0.3.0` at time of writing). Prefer **Trusted
Publishing** via GitHub Actions (OIDC, no long-lived PyPI API tokens). Local
`twine` upload remains a fallback.

Package name on indexes: **`gdk9-cli`**.

## Trusted Publishing (preferred)

Workflow: [`.github/workflows/publish.yml`](../.github/workflows/publish.yml)

| Trigger | Target |
| ------- | ------ |
| `workflow_dispatch` with `target=testpypi` | TestPyPI |
| `workflow_dispatch` with `target=pypi` | PyPI |
| GitHub Release `published` | PyPI |

### One-time publisher setup (UI)

Do this **before** the first successful publish run:

1. Create empty GitHub Environments on `ao3575911/gdk9`: `testpypi` and `pypi`
   (Settings → Environments). No secrets required for Trusted Publishing.
2. On [TestPyPI](https://test.pypi.org/) → Publishing → Pending publisher:
   - Project: `gdk9-cli`
   - Owner: `ao3575911` · Repository: `gdk9`
   - Workflow: `publish.yml` · Environment: `testpypi`
3. On [PyPI](https://pypi.org/) → same fields with Environment: `pypi`.

### Dry-run / first upload (TestPyPI)

After the TestPyPI pending publisher is linked:

```bash
gh workflow run publish.yml -f target=testpypi --repo ao3575911/gdk9
gh run watch --repo ao3575911/gdk9
```

Smoke-install:

```bash
python3 -m pip install -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  gdk9-cli==0.3.0
gdk9 --help
```

### Production PyPI

Only after TestPyPI is green. Either:

```bash
gh workflow run publish.yml -f target=pypi --repo ao3575911/gdk9
```

or publish a GitHub Release (triggers the `release` path → environment `pypi`).

Do **not** store long-lived PyPI API tokens in GitHub secrets for this path.

## Local build (always available)

```bash
python3 -m pip install -U pip
python3 -m pip install '.[build]'
python3 -m build
# or
make build
```

Expected artifacts:

```text
dist/gdk9_cli-0.3.0.tar.gz
dist/gdk9_cli-0.3.0-py3-none-any.whl
```

```bash
python3 -m pip install -U twine
python3 -m twine check dist/*
```

## Fallback: twine + API token

Use only if Trusted Publishing is unavailable:

1. Create an API token at TestPyPI or PyPI.
2. Upload:

```bash
python3 -m twine upload --repository testpypi dist/*
# or production:
python3 -m twine upload dist/*
```

## Notes

- Do not bump the package version in the same change as tooling-only release docs
  unless a real release is intended.
- First Trusted Publish can use `0.3.0` if that version is not yet on TestPyPI/PyPI.
