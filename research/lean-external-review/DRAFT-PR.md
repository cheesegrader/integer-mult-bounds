Title: Verify one PR442 R747 invocation against a multi-host Lean contract

## Change and mathematical scope

The previous single-host contract could not compare PR442's relocation while
retaining every affected host output. This contribution supplies a multi-host
contract with exact single-host recovery (Task A), then connects the literal
stage-2/replica-0/pair-0 forward invocation at
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd` to it (Task B).

The 19,002-event source word is checked for arbitrary dirty Boolean payloads,
with actual owner maps, coordinate transformations, chronological COPY/ERASE
guards, and restoration of one explicitly clean private temporary. The
comparison retains every affected host/data output and streams outside the
union of the two active owner images;
actual original-bank outputs remain auxiliary outputs.

Main declarations:

- `MultiHosting.multi_hosting`, `MultiHosting.SingleHost.whole_hosting_recovered`,
  and `MultiHosting.SingleHost.physical_whole_hosting_recovered`.
- `SourceInvocation.actualContract`, `selected_call_completion`,
  `selected_native_completion`, `selected_native_realization`,
  `selected_matrix_realization`, `selected_original_matrix_realization`,
  `selected_native_clean`, and `selected_temporary_restoration`
  (all latter names in `SourceInvocation`).

Theorems use explicit local input embeddings, an address field with `2 ≠ 0`,
and an invertible invocation chart. Python source extraction is reproducibly
checked, not formally verified. Completion applies the remaining pending
swaps immediately; the pending ranges `[15,22)` and `[1,29)` are manually
supplied rather than derived from the global schedule. Full cover sweeps,
later scheduling, arbitrary global
allocation equivalence, costs, all-size compilation, analytic transfer, and
κ remain unproved. PR448's split-helper gain remains unestablished.

## Validation

Pinned dependency setup and delivery instructions are in
`research/lean-external-review/README.md`. Fresh reproduction:

```sh
python3 research/lean-external-review/reproduce.py \
  --lean /path/to/lean-4.33.0-linux/bin/lean \
  --mathlib /path/to/mathlib4 \
  --build-dir /tmp/review-task-b-fresh \
  --receipt-dir /tmp/review-receipts-fresh
```

Task A has six modules/21 audited theorem closures; Task B has 52/930.
In the recorded packaging validation, Task A and source regeneration were
rerun fresh. Task B reused all 52 local
compiled modules after checking their hashes and reran the 930-declaration
axiom audit. `actualContract` was built as part of its module but is omitted
from that permanent named inventory; adding it remains a follow-up audit task.
The original build recorded Lean/Mathlib revisions but not byte
hashes of the installed Lean 4.33.0 distribution (including Lean/Std libraries),
Mathlib, or its eight dependencies: plausible, LeanSearchClient, importGraph,
proofwidgets, aesop, Qq, batteries, and Cli. Today's hashes cannot establish
which external-library bytes were used for that original compilation.
The reported Task B PASS therefore describes checked reuse and a rerun axiom
audit, not a fresh source build. A successful fresh run of the command above
resolves this: it recompiles all 52 modules and records the current dependency hashes;
it does not repair the old receipt. Only standard Lean axioms are accepted.
See the delivery's validation receipt for exact outcomes; no whole-algorithm
claim follows.
`make gen4-bank-verify` passed separately. The full `make verify` sweep was
stopped at a ten-minute limit during `verify-recycled-bit`; it is incomplete.

The later documentation correction reran package-integrity checks only. Its
metadata record reconciles changed commit citations while preserving the
original proof receipts; it does not supply a fresh Task B build.

The construction and source artifacts are inherited from PR442/PR434 and
their credited predecessors, including Dylan Crow, Jacob Sussman, and Zhihao
Chen; existing notices remain authoritative. PR509/PR513/PR516/PR528 overlap with
generic transport, completion, ownership and realized-word principles.
The bounded refreshed audit distinguishes their supplier premises from
this concrete invocation's certificates. No global novelty claim is made.

Upstream has since selected a newer conditional witness through PR493/PR531.
This verifies an older PR442 invocation as a demonstration of the method.
PR493 explicitly inherits PR442's conditional hosting interface through
PR472, with pinned citations in
[`PRIVACY-AND-PROVENANCE.md`](PRIVACY-AND-PROVENANCE.md); that lineage does
not transfer this proof to a PR493 invocation.

Prepared with substantial OpenAI Codex assistance. I initiated and coordinated
the AI-assisted verification effort; I do not claim to have independently
derived or personally checked the mathematics. Codex agents developed the
proofs and ran the reported checks/reviews. These are not human audits.

Questions for maintainers:

1. Do the source-to-literal binding, permitted slot-isometry choice, native
   ADD/MOVE/COPY semantics, and private-storage initialization faithfully
   represent this selected PR442 invocation?
2. Is retaining all host/data/exterior outputs while exposing actual old-bank
   outputs as auxiliary state the right interface for later scheduling proofs?
3. Where should the concrete supplier and reusable algebra live alongside
   PR509/PR513/PR516/PR528, including the Lean 4.33 toolchain, and should historical dependency
   packages be separated during integration?
