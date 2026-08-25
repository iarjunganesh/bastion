# Clean-clone reproducibility

**Re-run 2026-08-25 against commit `c81b4af`**, the current public `main`.

The first run of this record cited commit `4fe8d59`. That commit was later folded into
`c81b4af` and force-pushed away, so the hash no longer resolves in a fresh clone — a
reproducibility record naming an unreachable commit proves nothing, which is exactly the class
of quiet staleness this file exists to catch. It was re-run rather than re-pointed.

This closes P1.3. Its purpose is narrow and worth stating precisely: prove that a judge who has
never seen the author's machine can clone the public repository and reach a green offline gate
without credentials, without a Google Cloud project, and without a single undocumented step.
Every other reproducibility claim in this repository is a statement about intent. This one is a
measurement.

## Method

The repository was cloned over public HTTPS with no authentication, into a directory outside the
working tree, with no global gitignore configured (`git config --global core.excludesFile` is
unset on this machine, so nothing personal could mask a missing file). The README's setup block
was then followed exactly, under CPython 3.12.12.

## Result

Every gate passed. The output column quotes the tools, not a summary of them.

| Step | Result |
|---|---|
| `git clone` over public HTTPS, unauthenticated | HEAD `c81b4af` on `main` |
| Virtual environment under Python 3.12 | CPython 3.12.12 |
| `pip install -r requirements-dev.txt` | resolved and installed with no conflict |
| `pytest tests --cov --cov-fail-under=100` | 321 passed; 894 statements, 248 branches, 100.00% |
| `ruff check .` | `All checks passed!` |
| `ruff format --check .` | `134 files already formatted` |
| `mypy` over the eight packages | `Success: no issues found in 40 source files` |
| `python scripts/check_docs.py` | `Documentation agrees with the repository.` |
| `python scripts/check_versions.py` | `versions agree across 41 documents and 17 pins.` |
| `python scripts/render_diagrams.py --check` | `Theme variants are current (4 masters).` |
| `python scripts/check_site.py` | `Public site is snapshot-aligned and contains no prohibited data shapes or origins.` |
| `npx markdownlint-cli2 "**/*.md"` | `Summary: 0 issues in 0 files` across 57 files |

Four checks are specific to reproducibility rather than correctness, and all four held:

- **No untracked required file.** `git status --porcelain` was empty after the entire gate ran.
  Nothing the suite, the coverage run, or the diagram check produces escapes `.gitignore`, so a
  contributor's first run cannot leave the tree dirty and cannot hide a missing committed asset.
- **197 tracked files** constitute the whole repository. `.env` is absent, as it must be;
  `.env.example` is present and is the only configuration a live run needs.
- **Diagrams resolve on both GitHub themes.** Light and dark SVG variants of every architecture
  master are committed and README.md selects between them with `<picture>` and
  `prefers-color-scheme`. The masters were renamed from the internal `level-0/1/2` taxonomy to
  semantic names, and `render_diagrams.py --check` reports all four current.
- **The demo-video badge is deliberately unlinked.** It renders as a plain image with the
  wrapping instruction sitting directly above it in an HTML comment, so it becomes a link only
  when a public video URL exists to point it at.

## Two environment findings, neither a repository defect

Both are recorded because a reproducibility record that reports only success is not a
measurement, and because either could waste a judge's time.

**`py -3.12` requires a py-launcher-registered CPython.** The README's Windows setup line is
`py -3.12 -m venv .venv`, which is correct for the standard python.org installer. It fails on a
machine whose 3.12 came from uv, pyenv-win, conda, or the Microsoft Store, because those do not
register with the launcher — on this machine `py -0p` lists only 3.14, and the 3.12 that runs
every gate above is uv-managed. The interpreter was therefore invoked by its absolute path, which
is what `py -3.12` would have resolved to anyway. README.md now names the fallback rather than
assuming the launcher.

**pytest's temporary base directory must be writable.** The first run of the suite in a sandboxed
shell failed at fixture setup with `PermissionError: [WinError 5]` on
`%LOCALAPPDATA%\Temp\pytest-of-<user>`, a directory that already existed and was owned outside the
sandbox. Only the cases using the `tmp_path` fixture were affected, and every one of them passes
when pytest is given a writable base with `--basetemp`. This is an artifact of a restricted
execution environment, not of the repository: the same commit passes cleanly in GitHub Actions and
in an ordinary local shell. It is written down because the failure presents as a dozen unrelated
durability-test errors and a coverage shortfall, which reads like a broken repository and is not.

## Exact testing instructions for Devpost

This block is the answer to the form's reproducible-setup expectation. It requires no Google Cloud
project, no credentials, and no network beyond the clone and the dependency install.

```powershell
git clone https://github.com/iarjunganesh/bastion.git
Set-Location bastion

py -3.12 -m venv .venv          # any CPython 3.12 works; see README for the fallback
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt

pytest tests --cov --cov-report=term-missing --cov-fail-under=100
```

That runs the unit, integration, security, and load suites against the real agent graph with the
cloud seams faked at their boundaries, and fails if configured core coverage drops below 100%. The
remaining gates are the ones CI runs and take seconds each:

```powershell
ruff check .
ruff format --check .
mypy agents gateway identity registry runtime model_armor observability infrastructure
python scripts/check_docs.py
python scripts/check_versions.py
python scripts/render_diagrams.py --check
python scripts/check_site.py
```

## What this run does not prove

It is an offline gate, and offline is exactly its value: it proves the repository is complete and
self-consistent without privileged access. It proves nothing about the deployed fleet. This
repository has now shipped four defects that were true of the code and false of the running system
— recorded as D1, D6, D8, and D9 in [09-capture-backlog.md](09-capture-backlog.md) — so a green
clean-clone gate must never be read as evidence that Google Cloud did anything. The live gate is
separate, needs credentials, and is documented in [OPERATIONS.md](../../docs/OPERATIONS.md).
