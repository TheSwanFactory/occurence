# Occurrence Theory

This repository contains a draft research paper and verification script for
Occurrence Theory (OT), defined as an oriented form of Sedenion Settlement
Dynamics (SSD).

The central object is the Aut-invariant settlement channel on the sedenion
zero-divisor crack. The paper separates theorem, exact computation,
measurement, interpretation, and conjecture using explicit ledger tags:

- `[T]` theorem
- `[C]` computation
- `[M]` measurement
- `[I]` interpretation
- `[X]` conjecture

## Files

- `topographo/` - reusable Python **package** (the library) for Cayley-Dickson
  algebra, validation gates, operators, SSD helpers, and the exceptional-algebra
  (Albert / F4 / G2) layer. Ships to PyPI with its own tests under
  `topographo/tests/`.
- `verify/` - the **consumer** side: all Paper verification. Holds the canonical
  first-party audits, the tests that guard them, and independent reviewer
  results. See `verify/README.md` for the naming convention.
- `occurrence-theory.md` - main paper draft (Paper I).
- `verify/occurrence_i_audit.py` - numerical audit and verification script for
  the Paper I algebraic claims. Every printed `[C]`/`[G]` line is a computed
  number checked against a threshold; the script exits nonzero if any fails.
- `verify/occurrence_i_cabarius.md` - independent re-derivation of the paper's
  computational claims (reviewer: cabarius), and the corrections it produced.
- `occurrence_theory_prompt.md` - source prompt and writing constraints used to
  generate the paper.
- `.github/workflows/topographo.yml` - library CI: tests, builds, and releases
  the `topographo` package.
- `.github/workflows/occurrence.yml` - consumer CI: installs `topographo`, runs
  the audit exit-code gate and the `verify/` tests.
- `CHANGELOG.md` - release history for the package and audit artifacts.
- `LICENSE` - MIT license.

## Requirements

The audit script requires Python 3.11 or newer and NumPy, plus the `topographo`
package (which it imports for the verified algebra). The exceptional-algebra
(Albert / F4 / G2) reproduction now lives inside the package as
`topographo.exceptional`.

`uv` is the preferred runner for local audit work:

```bash
uv run python verify/occurrence_i_audit.py
```

For editable package installation:

```bash
uv pip install -e .
```

After installation, the core math layer is importable without running the
Occurrence Theory audit narrative:

```python
from topographo.core import CayleyDicksonAlgebra, verify_gates
from topographo.ssd import SedenionAlgebra
```

For exact finite crack certificates, use `basis_zero_divisors()` to enumerate
the full 84-point design. `sample_crack(n)` samples from that design with
replacement and is intended for stochastic diagnostics, not machine-zero
theorem gates.

API documentation is generated with `pdoc` and published to GitHub Pages:
<https://theswanfactory.github.io/occurrence/>

To build it locally:

```bash
uv run pdoc \
  topographo \
  topographo.core \
  topographo.core.algebra \
  topographo.core.cayley_dickson \
  topographo.core.gates \
  topographo.ssd \
  topographo.ssd.channel \
  topographo.ssd.sedenion \
  topographo.exceptional \
  topographo.exceptional.lab \
  -o site
```

## Run the Audit

From the repository root:

```bash
uv run python verify/occurrence_i_audit.py
```

To save the output:

```bash
uv run python verify/occurrence_i_audit.py > audit_results.txt
```

The audit exits `0` only if every certificate meets its threshold, and `1`
otherwise, so it is safe to gate CI on it. A passing run means the paper's
`[C]`-tagged claims reproduce on this implementation. It does not mean the
paper's `[I]` interpretations are correct; those are not tested.

CI runs two workflows on pull requests and pushes to `main`: `topographo.yml`
(library: tests, build, release) and `occurrence.yml` (consumer: installs the
package, runs this audit as an exit-code gate, and runs the `verify/` tests).

## Status

This is a research workspace, not a packaged library. The paper is the primary
artifact; the script is included to reproduce the computation-backed claims.

## License

MIT. See `LICENSE`.
