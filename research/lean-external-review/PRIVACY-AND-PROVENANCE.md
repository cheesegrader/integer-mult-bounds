# Privacy, receipt provenance, and later upstream context

This is a documentation and packaging correction. No Lean compilation, axiom
audit, or new mathematical work was performed for it.

## Published history and current references

The seven contribution commits were replaced with commits using
`AI-assisted verification contributor <verification-contributor@example.invalid>`
as author and committer. Their source trees were unchanged by that rewrite.
The replacement branch ended at `9e9e22295bdbe2b3ab6433cefbf73afdaa1f2457`
before this documentation correction. Current files now cite those replacement
commits, including:

| Checkpoint | Replacement commit |
| --- | --- |
| Task A | `13611a8958fc71046a83d8431d2bd6335e6a3e2f` |
| Task B | `f7330c5f5b1c5e85f91a98c95e8efc0e27c03490` |

Replacing branch history did **not** remove the previous objects from GitHub.
A subsequent unauthenticated check still retrieved the old tip through both
the fork and upstream repository URLs, including its original Git identity.
Earlier snapshots also retain their historical references. The current cleanup
removes those references from this delivery; it does not erase old snapshots,
objects, clones, or copies held by others. The public GitHub account and required
upstream attribution remain visible.

A private, unsent GitHub Support request has been prepared. GitHub must assess
whether these objects qualify for its
[sensitive-data removal process](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
Removal is not guaranteed. This package does not republish the affected old
identifiers or the original personal identity. No Support request, upstream
comment, or pull request was submitted as part of this correction.

## Historical evidence after citation changes

Changing a manifest's commit citation changes its content hash even when all
proof sources are identical. `validation/metadata-reanchor.json`, produced by
`reanchor_metadata.py`, records the resulting bindings. `verify_package.py`
checks the recorded bindings from the package alone; it needs neither the
private commit mapping nor a Git checkout. The metadata-generation check used
the mapping and neutral pre-correction snapshot to establish:

- All 75 included Lean source files are unchanged.
- The Task A, Task B, and source-diagnostic manifests change only their
  commit-anchor field. Their proof payloads remain identical.
- The original Task A and Task B `replay-result.json` receipts and packaging
  `validation/task-a.json` remain byte-for-byte unchanged.
- Eight historical evidence copies change only by exact commit-ID
  substitutions, retaining their original dates, outcomes, and runner hashes.
- Historical log hashes match the original bytes; separate hashes identify
  the published logs after citation substitution. Original recorded log hashes
  are retained, not presented as hashes of the redacted copies.

The offline validator checks current files against this recorded bridge. It
does not independently recreate the private mapping or authenticate a
historical build. A replaced commit citation identifies an equivalent source
tree; it does not mean that a historical command was rerun at that replacement
commit. The metadata record is a new packaging check, not a new proof receipt.
It cannot establish missing historical Lean or Mathlib fingerprints. The resumed
Task B result and documented fresh reproduction retain the limitations in
[VALIDATION.md](VALIDATION.md).

Superseded per-task patch copies have been retired. All required source files,
dependencies, and proof receipts remain included. The supported export is one
cumulative `review.patch` from the exact public base in [README.md](README.md).
The public branch and GitHub ZIP contain the complete current sources; the
smaller generated tarball is an export, not a separately published release.
Original machine paths in raw execution records describe historical runs;
authored build instructions now use portable paths.

## PR493 inherits the interface through PR472

There is an explicit citation, beyond a plausible algorithmic lineage. At
PR493 commit `c3a9a436b84fe44fdc223a5784d84736d1c2d3c7`:

- The [README, lines 147–152](https://github.com/CrocSwap/integer-mult-bounds/blob/c3a9a436b84fe44fdc223a5784d84736d1c2d3c7/research/e8-bit-carrier-skeleton/README.md#L147-L152)
  lists “whole-call correlated-helper hosting (#442)” among inherited assumptions.
- The [NOTICE, lines 42–48](https://github.com/CrocSwap/integer-mult-bounds/blob/c3a9a436b84fe44fdc223a5784d84736d1c2d3c7/research/e8-bit-carrier-skeleton/NOTICE.md#L42-L48)
  identifies PR472 as the intermediary carrying PR442's `hosting_core.py`.
- [SOURCE-pr472.json, lines 40–43](https://github.com/CrocSwap/integer-mult-bounds/blob/c3a9a436b84fe44fdc223a5784d84736d1c2d3c7/research/e8-bit-carrier-skeleton/SOURCE-pr472.json#L40-L43)
  pins that source file's Git blob.

The checked `hosting_core.py` bytes are identical at that PR493 commit, PR472
`259c68488b7aa8a14cf3fcae7fc499381c9bf729`, and PR442
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`: Git blob
`68b536daa9e6546c0aa046934bf840aaa3c3fde3`, SHA-256
`d8b90cd5d152df3c7c351230863d9e61816ad5e1f21d69bea1a86a5daad559a3`.

PR493 therefore explicitly inherits PR442's conditional hosting interface
through PR472. This provenance **does not transfer** our selected-invocation
proof to PR493. Its invocation word, owners, frames, and scheduling need their
own connection. No such connection is claimed here.

## Bounded later overlap check and open follow-up

The later read-only check used upstream main
`f19cb621be2caf3a7291a37c343c1c55afe935e0`, 59 commits beyond this package's
base. Its [PR531 review](https://github.com/CrocSwap/integer-mult-bounds/blob/f19cb621be2caf3a7291a37c343c1c55afe935e0/docs/research/community-pr531-review.md#L118)
records the newer conditional finite witness. This delivery remains a
verification of the older PR442 invocation and a demonstration of the method;
it neither establishes that newer witness's interfaces nor raises κ.

PR528, absent from the earlier overlap snapshot, was checked at draft head
`df5bbdbf837df908ce2324ed880141918a19db5d`. Its
[PR516 complete-bank endpoint theorem](https://github.com/CrocSwap/integer-mult-bounds/blob/df5bbdbf837df908ce2324ed880141918a19db5d/research/lean-complete-bank-endpoint/PR516CompleteBankEndpoint.lean#L48)
derives the complete-bank/rest endpoint from PR516 realization, given owners,
a physical word, recipes and labels, and row/column/operator premises.
This overlaps the generic
connection framework. It does not instantiate this delivery's selected R747
word. The check was a bounded source review, not a Lean rebuild or a global
novelty search. Earlier PR509/513/516 comparisons remain in the linked overlap
review.

The fresh, fully fingerprinted Task B build is still outstanding.
`actualContract` is constructed in the built dependency graph but omitted from
the permanent named axiom inventory. Pending-coordinate ranges `[15,22)` and
`[1,29)` are manually supplied; extraction does not independently derive them
from the global schedule. “One invocation” covers the whole 19,002-instruction
word, without proving interactions between calls. These limitations remain
open and are not repaired by this documentation update. Mathematical work is
paused at the user's request.
