# The representation-theory investigation (a methodology log)

How Conjecture C3 of *Occurrence Theory II* went from `8 ⊕ 6` to a verified,
reframed picture — including the wrong turns. This records the reasoning and
the corrections so reviewers can see how the current C3 / Open Problem 3 text
was arrived at. The machine-checked endpoint is
[`verify/occurrence_ii_reptheory.sage`](../verify/occurrence_ii_reptheory.sage);
this document is the narrative around it.

## 0. Why Sage at all

The numpy audits (`verify/occurrence_ii_audit.py`, `verify/occurrence_ii_claude_code.py`)
already reproduce every `[FORCED]` numerical claim to machine precision. What
they *cannot* do is the two things the paper's open obligations actually need:

- **exact arithmetic** — proving the spectrum is *exactly* `(1/7)·{0,±1,±3,±7}`
  plus `±2√3/7`, not merely equal to `1e-14`; and
- **representation theory** — deciding whether the multiplicities `{1,7,14,21,…}`
  are the G₂ (and SU(3)) representations the paper *names* them, not just
  integers that happen to match.

Those are SageMath's home turf (exact linear algebra over ℚ; Weyl character
rings; branching rules). So the rep-theory / exact track became a separate
SageMath cell, complementing — not replacing — the fast floating-point audit.

## 1. First probe, first correction: `8 ⊕ 6` → `8 ⊕ 3 ⊕ 3̄`

The initial question was C3's claim that the 14-dimensional 𝔭-sector decomposes
as `8 ⊕ 6` under SU(3) ⊂ G₂. A short branching computation showed:

- sanity check: the standard **7** branches as `3 ⊕ 3̄ ⊕ 1` (confirming the
  canonical long-root SU(3));
- the **adjoint 14** branches as `8 ⊕ 3 ⊕ 3̄`, **not** `8 ⊕ 6`.

The `6` is the *symmetric* SU(3) irrep, distinct from `3 ⊕ 3̄` (which is merely
6-*dimensional*). So `8 ⊕ 6` was corrected to `8 ⊕ 3 ⊕ 3̄`.

**This correction contained a hidden assumption** — that the 𝔭-sector *is* the
adjoint 14 — carried over uncritically from the dimension coincidence
`14 = dim 𝔤₂`. That assumption was wrong, and the next step caught it.

## 2. The comprehensive cell, second correction: the 𝔭-sector is `7 ⊕ 7`

Extending the probe into a full exit-code test (`occurrence_ii_reptheory.sage`)
meant building the **concrete** G₂ = Aut(𝕆) action (from `Der(𝕆)`, dim 14) and
reading off *every* eigenspace as a G₂-module — rather than assuming any one of
them. Three things fell out:

- **Sanity:** Φ genuinely commutes with the G₂ action, `‖[S, g⊗g]‖ = 1.3·10⁻¹⁶`.
  The eigenspaces really are G₂-modules; the symmetry was verified, not assumed.
- **The full decomposition** (over the only irreps that occur, `{1,7,14,27}`):

  | eigenvalue | dim | G₂-module | SU(3) content |
  | --- | --- | --- | --- |
  | ±1 | 1 | `1` | `1` |
  | ±𝔭 = ±2√3/7 | 14 | **`7 ⊕ 7`** | `2·(3 ⊕ 3̄ ⊕ 1)` — two matter families, **no octet** |
  | ±3/7 | 21 | `7 ⊕ 14` | `8 ⊕ 2·(3 ⊕ 3̄) ⊕ 1` — **one octet** + two matter families |
  | ±1/7 | 42 | `1 ⊕ 2·7 ⊕ 27` | — |
  | 0 | 100 | `4·1 ⊕ 2·7 ⊕ 2·14 ⊕ 2·27` | — |

  Totals: `End(ℝ¹⁶) = 8·1 ⊕ 12·7 ⊕ 4·14 ⊕ 4·27`.

The distinguished dim-14 𝔭-sector is **`7 ⊕ 7`**, *not* the adjoint. Directly:
`χ_E(g) = 2·χ₇(g)`, while the adjoint character `χ₁₄(g)` is nowhere close.
The `14 = dim 𝔤₂` match is a coincidence.

**This reversed the §1 correction.** Both `8 ⊕ 6` *and* the intermediate
`8 ⊕ 3 ⊕ 3̄` had been attached to the 𝔭-sector; both were wrong, because they
branched the adjoint, which is not what that sector is.

## 3. Where the gauge story actually lives, and the reframe

The four adjoint (`14`) copies live in the **±3/7 sectors** (each `7 ⊕ 14`) and
the `0` sector — not the 𝔭-sector. So a gluon octet appears only in the ±3/7
sectors: `7 ⊕ 14 → 8 ⊕ 2·(3 ⊕ 3̄) ⊕ 1`.

That turned a retraction into a *sharper* conjecture. Open Problem 3 was
reframed (**Gauge structure of spectral sectors**): the 𝔭-sector supplies two
matter families with no octet; the ±3/7 sectors supply one octet plus two matter
families; the open question is whether these admit a unified gauge-theoretic
reading and whether the channel canonically selects the SU(3).

## 4. A side result (§10.2)

The space of G₂-invariant symmetric forms on the pencil `W = 7 ⊕ 7` is
**3-dimensional**. So the Design Theorem's `E[zzᵀ] = P_W/14` is **not** forced by
G₂-invariance alone — the specific measure does real work. That scopes what the
§10.2 proof obligation must actually establish.

## 5. What held, and the lesson

- **The `[FORCED]` firewall held throughout.** Every reversal was in
  `[CONJECTURE]` territory (C3 / the SU(3) reading). The §2–7 mathematics — CPTP,
  the nine-level spectrum (now proven *exactly over ℚ*), the complex structure
  J, the Born identity, the lattice — never moved.
- **The tooling caught the error, not hindsight.** Writing the check as an actual
  computation (build the group action, decompose, assert) forced out the truth
  that prose reasoning from a dimension coincidence had gotten wrong.
- **Lesson recorded:** for a representation-theory claim, compute the module
  structure *before* editing the paper — not after. The dimension of a sector
  does not tell you which representation it is.

## Reproduce

```bash
sage verify/occurrence_ii_reptheory.sage   # exit 0; every check OK
```

Verified with SageMath 10.9. See
[`verify/occurrence_ii_reptheory.md`](../verify/occurrence_ii_reptheory.md) for
the results summary and [`verify/README.md`](../verify/README.md) for the
verification conventions.
