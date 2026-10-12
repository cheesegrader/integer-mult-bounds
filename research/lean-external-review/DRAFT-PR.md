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
swaps immediately. Full cover sweeps, later scheduling, arbitrary global
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
The packaging validation distinguishes fresh Task A/source regeneration
from hash-checked resumed Task B and discloses the historical external-library
fingerprint gap. Only standard Lean axioms are accepted. See the delivery's
validation receipt for exact outcomes; no whole-algorithm claim follows.
`make gen4-bank-verify` passed separately. The full `make verify` sweep was
stopped at a ten-minute limit during `verify-recycled-bit`; it is incomplete.

The construction and source artifacts are inherited from PR442/PR434 and
their credited predecessors, including Dylan Crow, Jacob Sussman, and Zhihao
Chen; existing notices remain authoritative. PR509/PR513/PR516 overlap with
generic transport, completion, ownership and realized-word principles.
The bounded refreshed audit distinguishes their supplier premises from
this concrete invocation's certificates. No global novelty claim is made.

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
   PR509/PR513/PR516, including the Lean 4.33 toolchain, and should historical dependency
   packages be separated during integration?
