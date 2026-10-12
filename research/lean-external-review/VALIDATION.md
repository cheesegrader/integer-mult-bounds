# External-review validation

This packaging update changes delivery scripts, validation reporting and
documentation. The manifested Lean source files for Tasks A and B, including
their WholeHosting dependencies, are byte-for-byte unchanged from the completed
work. The historical proof manifests and receipts remain included and unchanged.

## Proof and source checks

| Check | Result and mode | Evidence |
| --- | --- | --- |
| Source snapshots and regenerated literals | PASS, freshly rerun; six snapshots, 19,002 events | `validation/source-binding.json` |
| Task A | PASS, six modules freshly compiled, zero reused, 21 theorem closures | `validation/task-a.json`, `validation/task-a.log` |
| Task B | PASS, zero modules freshly compiled, 52 reused, all 52 explicitly legacy; 930 closure reports rerun | `validation/task-b.json`, `validation/task-b.log` |
| Resume-policy controls | PASS, 16 policy checks and eight artifact-inventory checks | `../lean-multi-host-source/review-receipts/external-build/reuse-policy-checks.json` |

Both Lean replays use `-t 0`. Task A accepts only `propext` and `Quot.sound`;
Task B also permits `Classical.choice`. Neither accepts project axioms, `sorry`,
`admit`, `native_decide`, or unsafe project proof code. Axiom counts include
generated certificate declarations; they do not measure mathematical novelty.

Task B reused a copy of the coherent retained build, preserving the original
build directory. Its source bytes, copied source bytes, ordered local dependency
hashes and compiled `.olean` hashes matched the successful receipt committed at
`f86e52f19569e801ac8d133d7070aa3fe39db08c`. The runner rejects unmanifested
artifacts that could shadow library imports. It freshly checked the exact Lean
revision, clean pinned Mathlib and all eight dependency revisions, actual
toolchain/library bytes, and search order, and verified the same external
fingerprint before and after the run. Task A and Task B observed identical
toolchain bytes.

**Historical limitation:** the original completed build did not record the
bytes of every external library artifact. Today's fingerprint cannot establish
what those bytes were then. Each reused module therefore retains
`historical_external_environment: unrecorded`; this is an explicitly opted-in
legacy resume, not a fresh compilation and not `leanchecker --fresh`.
The new axiom audit reports the transitive axiom closure of the retained
declarations; it is not a substitute for re-elaborating every source file.
The package provides the default fresh reproduction route for reviewers.
See [the build review](../lean-multi-host-source/EXTERNAL-BUILD-REVIEW.md).

The official Linux Lean archive available during this validation also matches
the documented SHA-256
`4b3fb03c29a1e0a253fb1d11f9bae3725f19a0dc6fc09b3ea16d2c9df3349e2c`.
Standard external dependencies are pinned and fetched publicly; no local
compiled artifacts or private workspace paths are needed to reproduce afresh.

## Package integrity and delivery

`verify_package.py` checks every delivered review file against
`package-manifest.json`, verifies that both historical proof manifests match
their receipts, resolves every local dependency within the package, and checks
the new receipts against the same sources/axiom inventories. Its receipt is
`package-validation.json`. The manifest excludes itself and that receipt to
avoid a circular digest; the exported archive's `SHA256SUMS` includes both.

The delivery validator freshly unpacks the archive, checks all checksums,
runs the inventory and source-regeneration checks from that extracted copy,
and applies `review.patch` in an isolated Git tree made from the exact public
base. It requires the resulting Git tree to equal the final delivery commit's
tree and checks the package inventory again in the patched checkout. Its
`delivery-validation.json` is supplied beside the exported patch/archive so
it can identify their exact final hashes without a commit/archive hash cycle.
This is a fresh delivery test, distinct from the resumed Task B proof replay.

The historical patches in `lean-contribution-archive` are preserved, with
their original bases and hashes. They are not the application sequence for
this delivery: apply only the new cumulative `review.patch` to public base
`12a4934d15006e8c10f9b2264f13f8f341be802b`.

## Repository regression checks

The repository-wide `make verify` was run in an isolated archive of the
pre-packaging contribution commit `f86e52f19569e801ac8d133d7070aa3fe39db08c`.
The relevant upstream generators and Makefile are unchanged by this delivery.
It completed `verify-community`, `verify-producers`, `verify-partial-gauge`,
`verify-three-stage-cover`, and `verify-paired-cube`, then reached
`verify-recycled-bit` before the 600-second limit. It is **INCOMPLETE_TIMEOUT**,
not a passed full repository regression suite; no failure was reported before
interruption. The selected `make gen4-bank-verify` **passed** in a second
isolated archive: exit 0, 402.189 seconds, all nine stages and all nine
stage-omission controls, with pinned inputs unchanged. Its exact outcome and logs are in
[EXTERNAL-REPOSITORY-CHECKS.md](../lean-multi-host-source/EXTERNAL-REPOSITORY-CHECKS.md).

Completing the broad repository sweep remains an integration check, separate
from the passed contribution-specific Lean/source validation. No unrelated
generator or certificate was modified to make that sweep pass.

## Review readiness

The final theorem/README review found no unresolved claim mismatch. It records
the field/chart parameters, reserved clean temporary, external Python extraction,
local input embeddings, retained projection, and immediate-completion boundary.
The bounded upstream refresh at 2026-10-12 00:15:23 UTC found material generic
overlap with PR516 and preserves its attribution. No global novelty claim is made.

The package is intended for external technical review. The main reviewer tasks
are source fidelity and the proposed integration boundary; prior agent reviews
do not replace human review. An independent fresh Task B replay is recommended
before acceptance because this delivery deliberately reports resumed evidence.

Full cover sweeps, subsequent scheduling, global allocation equivalence, physical
costs, all-size compilation, analytic transfer and κ are future mathematical work.
They are not prerequisites for reviewing the explicitly bounded result. PR448's
advertised split-stream gain remains unestablished.
