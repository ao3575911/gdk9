# Releasing gdk9-cli (PyPI build path)

Version stays in `pyproject.toml` (`0.3.0` at time of writing). This doc covers a
**reproducible local sdist/wheel build** and optional TestPyPI upload. Auto-publish
to PyPI is not required for Spec 6.

## Prerequisites

```bash
python3 -m pip install -U pip
python3 -m pip install '.[build]'
# equivalent: python3 -m pip install build
```

Or use the Makefile (installs `build` if missing):

```bash
make build
```

## Build sdist and wheel

From the repository root:

```bash
python3 -m build
# or
make build
```

Expected artifacts (names follow the version in `pyproject.toml`):

```text
dist/gdk9_cli-0.3.0.tar.gz
dist/gdk9_cli-0.3.0-py3-none-any.whl
```

Inspect without installing:

```bash
python3 -m pip install -U twine
python3 -m twine check dist/*
```

## Optional: upload to TestPyPI

1. Create an API token at https://test.pypi.org/manage/account/#api-tokens
2. Upload:

```bash
python3 -m twine upload --repository testpypi dist/*
```

3. Smoke-install from TestPyPI (pulls deps from real PyPI):

```bash
python3 -m pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  gdk9-cli==0.3.0
gdk9 --help
```

## Optional: upload to PyPI

Only after TestPyPI verification and a conscious version bump:

```bash
python3 -m twine upload dist/*
```

## Notes

- Prefer approach A (local `build` extra + `make build`) over a trusted-publishing
  GitHub Actions workflow until release automation is needed. A publish workflow
  would require the `workflow` GitHub token scope.
- Do not bump the package version in the same change as tooling-only release docs
  unless a real release is intended.