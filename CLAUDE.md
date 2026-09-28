# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`rms-pdsparser` (import name `pdsparser`) parses NASA PDS3 labels into Python
dictionaries. Single package, `src/` layout.

## Detailed rules

`.claude/rules/*.md` hold the authoritative detailed standards (Python style, testing,
documentation, dependencies, environment) and load automatically. The `doc_*` and
`how_to` rules are scoped to the files they govern, so they load only when you touch
`README.md` or `docs/`. Process standards live in `.claude/skills/` and load on demand:
`git-workflow`, `pull-request`, `bug-report`. This file records only what is specific to
this repository or what you would otherwise get wrong.

## Verifying changes

`scripts/run-all-checks.sh` is the single source of truth for which checks must pass. CI
must run exactly that set. Run it before calling a change done.

- It needs a virtualenv at `./venv` (override with `VENV`). Create it with
  `./scripts/setup-venv.sh`, which is idempotent. Never install into system Python.
- Useful flags: `-c/--code`, `-d/--docs`, `-m/--markdown`, `-s/--sequential`, or a single
  check such as `--pytest`, `--ruff-check`, `--mypy` or `--stubtest`.
- `ruff format`, `bandit`, and `vulture` are disabled by default in the script. Leave them
  disabled, and don't run `ruff format` over the tree: the source has not been reformatted.

## Python style

- Maximum line length 90; ruff and `.flake8` must agree. Test files are exempt from E501.
- Ruff is the linter of record. It implements no `E121`-`E133` rule, so
  `flake8 --select=E12,E13 src tests` covers continuation-line indentation alone.
- Rules switched off in `pyproject.toml` carry their reason beside them (e.g. `RUF022`,
  because the order of `__all__` is deliberate). Read the comment before re-enabling one.
- Single quotes. Keep the `#####` banner header at the top of each file.
- **No type annotations under `src/`.** Parameter and return types belong in the Google-style
  docstrings (`Parameters:`, not `Args:`). **Annotate every test function and helper**,
  including `-> None`.
- **Never run `mypy` on `src/`.** `[tool.mypy] strict = true` applies, but `src/` is
  deliberately unannotated. Run it as `MYPYPATH=src mypy tests`.
- The only supported import is `from pdsparser import ...`, so `__init__.pyi` is the only
  stub and must describe the whole public API: every name in `__all__`, in the same order,
  plus `__version__`. It is hand-written, with types taken from the docstrings. `stubtest`
  enforces it, so adding, renaming or re-signing a public name means updating
  `__init__.pyi` in the same change. The private modules (`_PDS3_GRAMMAR`, `_fast_dict`,
  `_utils`) have no stub; a new one goes in both `[tool.mypy] exclude` and the
  `follow_imports = "skip"` override in `pyproject.toml`.

## Testing

- Test inputs and expected outputs (`*-answer.txt`, `*-expanded.txt`) live in the
  top-level `test_files/` directory, not under `tests/`. The answer files are `eval`'d,
  which is why `test_labels.py` imports `datetime`.
- The parse methods are `'strict'`, `'loose'`, `'compound'` (pyparsing grammars in
  `_PDS3_GRAMMAR.py`) and `'fast'` (regex-based, in `_fast_dict.py`). Tests are parametrized
  over them; type a `method` parameter as the `Method` literal in `test_labels.py`.
- `filterwarnings = error`: any new warning fails the suite. Coverage must stay at 90% or
  higher.

## Documentation

Sphinx builds with `-W` and `nitpicky = True`, so any warning or unresolved cross-reference
in a docstring fails the build. `docs/index.rst` includes `README.md` after the
`<!-- start-after-point -->` marker, so README headings feed the Sphinx TOC.

## Repo etiquette

- Versions come from `setuptools_scm`; never hand-edit `src/pdsparser/_version.py`.
- Dependencies go in `pyproject.toml` only; `requirements.txt` contains just `-e .`.
